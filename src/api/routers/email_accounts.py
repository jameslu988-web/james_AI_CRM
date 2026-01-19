"""邮箱账户管理API - 管理邮件收发账户配置"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from pydantic import BaseModel, EmailStr

from ...crm.database import get_session, EmailAccount, User, EmailHistory, Customer
from ...email_system.receiver import EmailReceiver
from .auth import get_current_active_user

router = APIRouter()


# Pydantic模型
class EmailAccountCreate(BaseModel):
    account_name: str
    email_address: EmailStr
    imap_host: Optional[str] = None
    imap_port: int = 993
    imap_username: Optional[str] = None
    imap_password: str
    smtp_host: Optional[str] = None
    smtp_port: int = 465
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    provider: Optional[str] = None
    auto_sync: bool = True
    sync_interval: int = 5
    sync_mode: str = 'unread_only'  # unread_only/recent_30days/all
    auto_match_customer: bool = True
    auto_create_followup: bool = True


class EmailAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    imap_host: Optional[str] = None
    imap_port: Optional[int] = None
    imap_password: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    auto_sync: Optional[bool] = None
    sync_interval: Optional[int] = None
    sync_mode: Optional[str] = None  # unread_only/recent_30days/all
    auto_match_customer: Optional[bool] = None
    auto_create_followup: Optional[bool] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class EmailAccountResponse(BaseModel):
    id: int
    account_name: str
    email_address: str
    provider: str
    imap_host: Optional[str] = None
    imap_port: Optional[int] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    auto_sync: bool
    sync_interval: int
    sync_mode: str
    last_sync_at: Optional[datetime]
    sync_status: str
    total_received: int
    total_sent: int
    is_active: bool
    is_default: bool
    first_sync_completed: bool
    created_at: datetime


class EmailSyncResult(BaseModel):
    success: bool
    emails_fetched: int
    emails_saved: int
    errors: List[str]
    message: str


# API路由
@router.get("/email_accounts", response_model=List[EmailAccountResponse])
async def get_email_accounts(
    response: Response,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """获取邮箱账户列表"""
    db = get_session()
    
    # 获取总数
    total = db.query(EmailAccount).count()
    
    # 获取分页数据
    accounts = db.query(EmailAccount).offset(skip).limit(limit).all()
    db.close()
    
    # 设置 Content-Range 头部
    response.headers["Content-Range"] = f"email_accounts {skip}-{skip + len(accounts) - 1}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    
    return accounts


@router.get("/email_accounts/{account_id}", response_model=EmailAccountResponse)
async def get_email_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取单个邮箱账户详情"""
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    db.close()
    
    if not account:
        raise HTTPException(status_code=404, detail="邮箱账户不存在")
    
    return account


@router.post("/email_accounts", response_model=EmailAccountResponse)
async def create_email_account(
    account_data: EmailAccountCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建新的邮箱账户"""
    db = get_session()
    
    # 检查邮箱地址是否已存在
    existing = db.query(EmailAccount).filter(
        EmailAccount.email_address == account_data.email_address
    ).first()
    
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="该邮箱账户已存在")
    
    # 测试连接
    try:
        receiver = EmailReceiver(
            email_address=account_data.email_address,
            password=account_data.imap_password,
            provider=account_data.provider,
            imap_host=account_data.imap_host,
            imap_port=account_data.imap_port
        )
        
        if not receiver.connect():
            db.close()
            raise HTTPException(status_code=400, detail="邮箱连接测试失败，请检查配置")
        
        receiver.disconnect()
    except Exception as e:
        db.close()
        raise HTTPException(status_code=400, detail=f"邮箱配置错误: {str(e)}")
    
    # 创建账户
    new_account = EmailAccount(
        account_name=account_data.account_name,
        email_address=account_data.email_address,
        imap_host=account_data.imap_host,
        imap_port=account_data.imap_port,
        imap_username=account_data.imap_username or account_data.email_address,
        imap_password=account_data.imap_password,  # TODO: 加密存储
        smtp_host=account_data.smtp_host,
        smtp_port=account_data.smtp_port,
        smtp_username=account_data.smtp_username or account_data.email_address,
        smtp_password=account_data.smtp_password,  # TODO: 加密存储
        provider=account_data.provider,
        auto_sync=account_data.auto_sync,
        sync_interval=account_data.sync_interval,
        sync_mode=account_data.sync_mode,
        auto_match_customer=account_data.auto_match_customer,
        auto_create_followup=account_data.auto_create_followup,
        created_by=current_user.id
    )
    
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    db.close()
    
    return new_account


@router.put("/email_accounts/{account_id}", response_model=EmailAccountResponse)
async def update_email_account(
    account_id: int,
    account_data: EmailAccountUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新邮箱账户配置"""
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    
    if not account:
        db.close()
        raise HTTPException(status_code=404, detail="邮箱账户不存在")
    
    # 更新字段（过滤空密码）
    update_data = account_data.dict(exclude_unset=True)
    
    # 🔥 关键修复：如果密码字段为空字符串，则不更新（保持原密码）
    if 'imap_password' in update_data and not update_data['imap_password']:
        del update_data['imap_password']
    
    if 'smtp_password' in update_data and not update_data['smtp_password']:
        del update_data['smtp_password']
    
    # 应用更新
    for field, value in update_data.items():
        setattr(account, field, value)
    
    account.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(account)
    db.close()
    
    return account


@router.delete("/email_accounts/{account_id}")
async def delete_email_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """删除邮箱账户"""
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    
    if not account:
        db.close()
        raise HTTPException(status_code=404, detail="邮箱账户不存在")
    
    db.delete(account)
    db.commit()
    db.close()
    
    return {"message": "邮箱账户已删除"}


@router.post("/email_accounts/{account_id}/test")
async def test_email_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """测试邮箱IMAP连接"""
    import imaplib
    import socket
    
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    
    if not account:
        db.close()
        raise HTTPException(status_code=404, detail="邮箱账户不存在")
    
    error_details = []
    
    try:
        # 步骤1: DNS解析测试
        try:
            ip = socket.gethostbyname(account.imap_host)
            error_details.append(f"✅ DNS解析成功: {account.imap_host} -> {ip}")
        except socket.gaierror as e:
            db.close()
            return {
                "success": False,
                "message": f"DNS解析失败: {account.imap_host}",
                "error_type": "dns",
                "details": [
                    "❌ 无法解析域名",
                    "可能原因:",
                    "  • DNS服务器问题",
                    "  • 域名不存在或拼写错误",
                    f"  • 请检查IMAP服务器地址: {account.imap_host}"
                ]
            }
        
        # 步骤2: 端口连接测试
        try:
            sock = socket.create_connection((account.imap_host, account.imap_port), timeout=10)
            sock.close()
            error_details.append(f"✅ 端口 {account.imap_port} 可以连接")
        except socket.timeout:
            db.close()
            return {
                "success": False,
                "message": f"连接超时: {account.imap_host}:{account.imap_port}",
                "error_type": "timeout",
                "details": [
                    "❌ 连接超时（10秒）",
                    "可能原因:",
                    "  • 防火墙阻止了IMAP端口（993）",
                    "  • 服务器无响应",
                    "  • 网络问题"
                ]
            }
        except socket.error as e:
            db.close()
            return {
                "success": False,
                "message": f"端口连接失败: {str(e)}",
                "error_type": "connection",
                "details": [
                    "❌ 无法连接到IMAP端口",
                    "可能原因:",
                    "  • 端口被防火墙阻止",
                    "  • IMAP服务未启动",
                    f"  • 请确认端口号: {account.imap_port}"
                ]
            }
        
        # 步骤3: IMAP SSL连接和登录测试
        try:
            connection = imaplib.IMAP4_SSL(account.imap_host, account.imap_port, timeout=10)
            error_details.append("✅ SSL连接成功")
            
            try:
                connection.login(account.email_address, account.imap_password)
                error_details.append("✅ IMAP登录成功")
                
                # 获取邮箱文件夹
                status, folders = connection.list()
                connection.logout()
                
                db.close()
                return {
                    "success": True,
                    "message": "IMAP连接成功！所有测试通过",
                    "mailbox_count": len(folders) if status == 'OK' else 0,
                    "mailboxes": [f.decode('utf-8') if isinstance(f, bytes) else str(f) for f in folders[:10]] if status == 'OK' else [],
                    "details": error_details
                }
                
            except imaplib.IMAP4.error as e:
                db.close()
                error_msg = str(e).lower()
                
                return {
                    "success": False,
                    "message": "IMAP登录失败",
                    "error_type": "authentication",
                    "details": [
                        f"❌ 登录失败: {str(e)}",
                        "",
                        "可能原因:",
                        "  1. ❌ 邮箱密码错误",
                        "  2. ❌ IMAP服务未启用",
                        "  3. ❌ 邮箱地址错误",
                        "",
                        "解决方案:",
                        "  1. 登录 Hostinger 控制面板",
                        "  2. 进入邮箱管理 -> 确认IMAP已启用",
                        "  3. 检查邮箱密码是否正确",
                        "  4. 尝试重置邮箱密码后重新配置"
                    ]
                }
                
        except imaplib.IMAP4.abort as e:
            db.close()
            return {
                "success": False,
                "message": "IMAP连接中断",
                "error_type": "abort",
                "details": [
                    f"❌ 服务器主动断开连接: {str(e)}",
                    "可能原因:",
                    "  • 服务器拒绝连接",
                    "  • 连接过于频繁",
                    "  • SSL/TLS版本不兼容"
                ]
            }
            
        except Exception as e:
            db.close()
            return {
                "success": False,
                "message": f"SSL连接失败: {str(e)}",
                "error_type": "ssl",
                "details": [
                    f"❌ SSL连接错误: {type(e).__name__}",
                    f"   {str(e)}",
                    "可能原因:",
                    "  • SSL证书问题",
                    "  • 端口配置错误（应使用993）",
                    "  • 服务器不支持当前SSL版本"
                ]
            }
        
    except Exception as e:
        db.close()
        return {
            "success": False,
            "message": f"测试失败: {str(e)}",
            "error_type": "unknown",
            "details": [
                f"❌ 未知错误: {type(e).__name__}",
                f"   {str(e)}"
            ]
        }


@router.post("/email_accounts/{account_id}/test_smtp")
async def test_smtp_connection(
    account_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """测试SMTP连接"""
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    
    if not account:
        db.close()
        raise HTTPException(status_code=404, detail="邮箱账户不存在")
    
    if not account.smtp_host or not account.smtp_password:
        db.close()
        raise HTTPException(status_code=400, detail="SMTP配置不完整，请先配置SMTP服务器和密码")
    
    try:
        import smtplib
        import ssl
        
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        # 测试连接
        if account.smtp_port == 465:
            # SSL连接
            with smtplib.SMTP_SSL(account.smtp_host, account.smtp_port, context=context, timeout=10) as server:
                server.login(
                    account.smtp_username or account.email_address,
                    account.smtp_password
                )
                db.close()
                return {
                    "success": True,
                    "message": f"SMTP连接成功！\n\n服务器: {account.smtp_host}:{account.smtp_port}\n用户名: {account.smtp_username or account.email_address}\n连接类型: SSL",
                    "server": account.smtp_host,
                    "port": account.smtp_port,
                    "connection_type": "SSL"
                }
        elif account.smtp_port == 587:
            # TLS连接
            with smtplib.SMTP(account.smtp_host, account.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(
                    account.smtp_username or account.email_address,
                    account.smtp_password
                )
                db.close()
                return {
                    "success": True,
                    "message": f"SMTP连接成功！\n\n服务器: {account.smtp_host}:{account.smtp_port}\n用户名: {account.smtp_username or account.email_address}\n连接类型: TLS",
                    "server": account.smtp_host,
                    "port": account.smtp_port,
                    "connection_type": "TLS"
                }
        else:
            # 尝试普通连接
            with smtplib.SMTP(account.smtp_host, account.smtp_port, timeout=10) as server:
                server.login(
                    account.smtp_username or account.email_address,
                    account.smtp_password
                )
                db.close()
                return {
                    "success": True,
                    "message": f"SMTP连接成功！\n\n服务器: {account.smtp_host}:{account.smtp_port}\n用户名: {account.smtp_username or account.email_address}",
                    "server": account.smtp_host,
                    "port": account.smtp_port
                }
                
    except smtplib.SMTPAuthenticationError as e:
        db.close()
        return {
            "success": False,
            "message": f"❌ SMTP认证失败！\n\n错误: {str(e)}\n\n请检查：\n1. SMTP密码/授权码是否正确\n2. QQ/163邮箱需使用“授权码”，不是邮箱密码\n3. Gmail需使用“应用专用密码”",
            "error_type": "authentication"
        }
    except smtplib.SMTPConnectError as e:
        db.close()
        return {
            "success": False,
            "message": f"❌ 无法连接到SMTP服务器！\n\n错误: {str(e)}\n\n请检查：\n1. SMTP服务器地址是否正确\n2. SMTP端口是否正确（465/587）\n3. 网络连接是否正常\n4. 防火墙是否阻止连接",
            "error_type": "connection"
        }
    except Exception as e:
        db.close()
        return {
            "success": False,
            "message": f"❌ SMTP测试失败！\n\n错误: {str(e)}",
            "error_type": "unknown"
        }


@router.post("/email_accounts/{account_id}/sync")
async def sync_emails(
    account_id: int,
    background_tasks: BackgroundTasks,
    limit: int = 100,
    only_unseen: bool = True,  # 默认只同步未读邮件
    since_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    手动同步邮件 - 异步后台任务
    
    参数:
        limit: 同步数量限制（默认100，设为0则不限制）
        only_unseen: 是否只同步未读邮件（默认True，推荐）
        since_date: 从哪个日期开始同步（格式：YYYY-MM-DD，可选）
    """
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    
    if not account:
        db.close()
        raise HTTPException(status_code=404, detail="邮箱账户不存在")
    
    # 首次同步：自动设置日期限制（最近30天）
    if not account.first_sync_completed and not since_date:
        from datetime import datetime, timedelta
        since_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # 设置同步状态为进行中
    account.sync_status = 'syncing'
    account.updated_at = datetime.utcnow()
    db.commit()
    db.close()
    
    # 添加到后台任务
    background_tasks.add_task(
        sync_emails_background,
        account_id=account_id,
        limit=limit,
        only_unseen=only_unseen,
        since_date=since_date
    )
    
    return {
        "success": True,
        "message": "邮件同步已开始，请稍后查看邮件历史",
        "status": "syncing",
        "since_date": since_date
    }


def sync_emails_background(
    account_id: int,
    limit: int,
    only_unseen: bool,
    since_date: Optional[str]
):
    """后台同步邮件任务（增加去重逻辑）"""
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    
    if not account:
        db.close()
        return
    
    errors = []
    emails_saved = 0
    emails_duplicated = 0
    
    try:
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
            db.close()
            return
        
        # 获取新邮件
        emails = receiver.fetch_new_emails(
            limit=limit, 
            only_unseen=only_unseen,
            since_date=since_date
        )
        
        # 保存到数据库（增加去重）
        for email_data in emails:
            try:
                # 检查邮件是否已存在（通过 message_id 去重）
                message_id = email_data.get('message_id', '').strip()
                if message_id:
                    existing_email = db.query(EmailHistory).filter(
                        EmailHistory.message_id == message_id
                    ).first()
                    
                    if existing_email:
                        emails_duplicated += 1
                        continue  # 跳过重复邮件
                
                # 查找或创建客户
                customer = None
                if account.auto_match_customer:
                    customer = db.query(Customer).filter(
                        Customer.email == email_data['from_email']
                    ).first()
                
                # 创建邮件历史记录
                email_history = EmailHistory(
                    customer_id=customer.id if customer else None,
                    direction='inbound',
                    subject=email_data['subject'],
                    body=email_data['body'],
                    html_body=email_data.get('html_body'),  # 保存HTML版本
                    sent_at=email_data['date'],
                    from_name=email_data.get('from_name'),  # 🔥 发件人名称
                    from_email=email_data['from_email'],
                    to_name=email_data.get('to_name'),  # 🔥 收件人名称
                    to_email=email_data['to_email'],
                    message_id=message_id if message_id else None,  # 保存 message_id
                    attachments=str(email_data['attachments']) if email_data['attachments'] else None
                )
                
                db.add(email_history)
                emails_saved += 1
                
            except Exception as e:
                errors.append(f"保存邮件失败: {email_data['subject'][:30]}... - {str(e)}")
        
        # 更新账户统计
        account.total_received += emails_saved
        account.last_sync_at = datetime.utcnow()
        account.sync_status = 'active'
        
        # 标记首次同步已完成
        if not account.first_sync_completed:
            account.first_sync_completed = True
        
        db.commit()
        receiver.disconnect()
        print(f"✅ 后台同步完成: 成功同步 {emails_saved}/{len(emails)} 封邮件，跳过重复 {emails_duplicated} 封")
        
    except Exception as e:
        account.sync_status = 'error'
        db.commit()
        print(f"❌ 后台同步失败: {str(e)}")
        
    finally:
        db.close()


@router.post("/email_accounts/{account_id}/toggle")
async def toggle_account_status(
    account_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """启用/禁用邮箱账户"""
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    
    if not account:
        db.close()
        raise HTTPException(status_code=404, detail="邮箱账户不存在")
    
    account.is_active = not account.is_active
    account.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(account)
    db.close()
    
    return {
        "success": True,
        "is_active": account.is_active,
        "message": f"账户已{'启用' if account.is_active else '禁用'}"
    }


@router.post("/email_accounts/{account_id}/check_bounces")
async def check_account_bounces(
    account_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 手动检查指定邮箱账户的退信邮件
    该操作将在后台异步执行
    """
    db = get_session()
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    db.close()
    
    if not account:
        raise HTTPException(status_code=404, detail="邮箱账户不存在")
    
    # 导入任务并添加到后台任务
    from ...tasks.email_tasks import check_bounce_emails_task
    background_tasks.add_task(check_bounce_emails_task, account_id)
    
    return {
        "success": True,
        "message": f"已启动退信检查任务: {account.email_address}",
        "account_id": account_id
    }


@router.post("/email_accounts/check_all_bounces")
async def check_all_accounts_bounces(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """
    🔥 手动检查所有活跃邮箱账户的退信邮件
    该操作将在后台异步执行
    """
    # 导入任务并添加到后台任务
    from ...tasks.email_tasks import check_all_accounts_bounce_emails
    background_tasks.add_task(check_all_accounts_bounce_emails)
    
    return {
        "success": True,
        "message": "已启动所有账户的退信检查任务"
    }
