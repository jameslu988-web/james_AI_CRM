"""
邮件相关异步任务
包括：邮件发送、邮件同步等
"""

from src.celery_config import celery_app
from src.crm.database import get_session, EmailHistory, EmailAccount
from src.email_system.receiver import EmailReceiver
from src.email_system.bounce_listener import BounceListener  # 🔥 新增
from datetime import datetime
import traceback

# 导入AI分析任务（用于自动触发）
from src.tasks.ai_tasks import analyze_email_task


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_emails_task(self, account_id: int, limit: int = 100, only_unseen: bool = True):
    """
    异步同步邮件任务
    
    参数:
        account_id: 邮箱账户ID
        limit: 同步数量限制
        only_unseen: 是否只同步未读邮件
    """
    db = get_session()
    
    try:
        account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
        
        if not account:
            return {"error": "邮箱账户不存在", "account_id": account_id}
        
        # 更新同步状态
        account.sync_status = 'syncing'
        db.commit()
        
        # 创建接收器
        receiver = EmailReceiver(
            email_address=account.email_address,
            password=account.imap_password,
            provider=account.provider,
            imap_host=account.imap_host,
            imap_port=account.imap_port
        )
        
        if not receiver.connect():
            account.sync_status = 'error'
            db.commit()
            return {"error": "连接失败", "account_id": account_id}
        
        # 获取邮件
        emails = receiver.fetch_new_emails(
            limit=limit,
            only_unseen=only_unseen
        )
        
        emails_saved = 0
        emails_duplicated = 0
        
        # 保存邮件
        for email_data in emails:
            try:
                # 去重检查
                message_id = email_data.get('message_id', '').strip()
                if message_id:
                    existing = db.query(EmailHistory).filter(
                        EmailHistory.message_id == message_id
                    ).first()
                    if existing:
                        emails_duplicated += 1
                        continue
                
                # 创建邮件记录
                email_history = EmailHistory(
                    customer_id=None,
                    direction='inbound',
                    subject=email_data['subject'],
                    body=email_data['body'],
                    html_body=email_data.get('html_body'),
                    sent_at=email_data['date'],
                    from_name=email_data.get('from_name'),  # 🔥 新增：发件人名称
                    from_email=email_data['from_email'],
                    to_name=email_data.get('to_name'),  # 🔥 新增：收件人名称
                    to_email=email_data['to_email'],
                    message_id=message_id if message_id else None,
                    attachments=str(email_data['attachments']) if email_data['attachments'] else None
                )
                
                db.add(email_history)
                db.flush()  # 确保获取到数据库生成的自增 ID (email_history.id)

                # 🔥 新增：使用正确的数据库 ID 处理正文图片
                if email_history.html_body and email_data.get('inline_images'):
                    print(f"🖼️ 处理正文图片: 使用数据库ID={email_history.id}")
                    try:
                        # 调用 receiver 的图片处理方法，使用正确的数据库 ID
                        processed_html = receiver._process_html_images(
                            email_history.html_body, 
                            str(email_history.id),  # 使用数据库 ID，而不是 IMAP ID
                            email_data.get('inline_images', {})
                        )
                        email_history.html_body = processed_html
                        print(f"✅ 图片路径处理完成: 邮件ID={email_history.id}")
                    except Exception as img_err:
                        print(f"⚠️ 图片处理失败: {str(img_err)}")

                emails_saved += 1
                
                # 🔥 关键：自动触发AI分析（异步）
                if email_history.id:
                    print(f"🤖 触发AI分析任务: 邮件ID={email_history.id}")
                    analyze_email_task.delay(email_history.id)
                
            except Exception as e:
                print(f"❌ 保存邮件失败: {str(e)}")
                continue
        
        # 更新统计
        account.total_received += emails_saved
        account.last_sync_at = datetime.utcnow()
        account.sync_status = 'active'
        
        if not account.first_sync_completed:
            account.first_sync_completed = True
        
        db.commit()
        receiver.disconnect()
        
        return {
            "success": True,
            "account_id": account_id,
            "emails_fetched": len(emails),
            "emails_saved": emails_saved,
            "emails_duplicated": emails_duplicated
        }
        
    except Exception as e:
        account.sync_status = 'error'
        db.commit()
        print(f"❌ 同步邮件任务失败: {str(e)}")
        traceback.print_exc()
        
        # 自动重试
        raise self.retry(exc=e)
        
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, email_data: dict):
    """
    异步发送邮件任务
    
    参数:
        email_data: 邮件数据字典
    """
    # TODO: 实现邮件发送逻辑
    try:
        print(f"📧 发送邮件: {email_data.get('subject')}")
        # 这里添加实际的发送逻辑
        return {"success": True, "message": "邮件已发送"}
    except Exception as e:
        print(f"❌ 发送邮件失败: {str(e)}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3)
def check_bounce_emails_task(self, account_id: int):
    """
    🔥 检查退信邮件任务
    
    参数:
        account_id: 邮箱账户ID
    
    返回:
        {
            'success': bool,
            'account_id': int,
            'bounces_found': int,
            'emails_updated': int,
            'details': list
        }
    """
    db = get_session()
    
    try:
        # 获取邮箱账户
        account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
        
        if not account:
            return {"error": "邮箱账户不存在", "account_id": account_id}
        
        print(f"🔍 开始检查退信邮件: {account.email_address}")
        
        # 创建退信监听器
        bounce_listener = BounceListener(
            imap_host=account.imap_host,
            imap_port=account.imap_port,
            email_address=account.email_address,
            password=account.imap_password,
            use_ssl=account.imap_port == 993
        )
        
        if not bounce_listener.connect():
            return {"error": "连接IMAP失败", "account_id": account_id}
        
        # 检查退信邮件
        bounces = bounce_listener.check_bounce_emails()
        bounce_listener.disconnect()
        
        emails_updated = 0
        update_details = []
        
        # 更新数据库中对应邮件的投递状态
        for bounce in bounces:
            try:
                message_id = bounce.get('message_id')
                if not message_id:
                    continue
                
                # 查找原始邮件
                email = db.query(EmailHistory).filter(
                    EmailHistory.message_id == message_id
                ).first()
                
                if email:
                    # 更新投递状态
                    old_status = email.delivery_status
                    email.delivery_status = 'bounced'
                    email.bounce_reason = f"[{bounce['bounce_type'].upper()}] {bounce['smtp_code']}: {bounce['bounce_reason']}"
                    
                    db.commit()
                    emails_updated += 1
                    
                    update_details.append({
                        'email_id': email.id,
                        'recipient': bounce.get('recipient'),
                        'old_status': old_status,
                        'new_status': 'bounced',
                        'bounce_type': bounce['bounce_type'],
                        'smtp_code': bounce.get('smtp_code')
                    })
                    
                    print(f"✅ 更新邮件投递状态: ID={email.id}, {old_status} -> bounced")
                
            except Exception as e:
                print(f"⚠️ 更新邮件失败: {str(e)}")
                continue
        
        result = {
            'success': True,
            'account_id': account_id,
            'bounces_found': len(bounces),
            'emails_updated': emails_updated,
            'details': update_details
        }
        
        print(f"✅ 退信检查完成: 发现 {len(bounces)} 封退信, 更新 {emails_updated} 封邮件")
        return result
        
    except Exception as e:
        print(f"❌ 检查退信任务失败: {str(e)}")
        traceback.print_exc()
        raise self.retry(exc=e)
        
    finally:
        db.close()


@celery_app.task
def check_all_accounts_bounce_emails():
    """
    🔥 检查所有活跃邮箱账户的退信邮件
    该任务由定时调度器触发（每5分钟）
    """
    db = get_session()
    
    try:
        # 查找所有活跃的邮箱账户
        accounts = db.query(EmailAccount).filter(
            EmailAccount.is_active == True
        ).all()
        
        print(f"🔍 开始检查 {len(accounts)} 个邮箱账户的退信邮件")
        
        total_bounces = 0
        total_updated = 0
        
        for account in accounts:
            try:
                result = check_bounce_emails_task(account.id)
                if result.get('success'):
                    total_bounces += result.get('bounces_found', 0)
                    total_updated += result.get('emails_updated', 0)
            except Exception as e:
                print(f"⚠️ 账户 {account.email_address} 检查失败: {str(e)}")
                continue
        
        print(f"✅ 所有账户退信检查完成: 发现 {total_bounces} 封退信, 更新 {total_updated} 封邮件")
        
        return {
            'success': True,
            'accounts_checked': len(accounts),
            'total_bounces': total_bounces,
            'total_updated': total_updated
        }
        
    except Exception as e:
        print(f"❌ 检查所有账户退信失败: {str(e)}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}
        
    finally:
        db.close()
