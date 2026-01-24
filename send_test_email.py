"""
发送测试邮件 - 测试自动回复全流程
此脚本会模拟一封客户询价邮件，触发AI自动回复流程
"""
from datetime import datetime, timedelta
from src.crm.database import get_session, EmailHistory, Customer, AutoReplyRule, ApprovalTask
import json
import os
from dotenv import load_dotenv

# 🔥 加载环境变量
load_dotenv()

print(f"\n🔑 检查配置: WECOM_WEBHOOK_URL = {os.getenv('WECOM_WEBHOOK_URL')[:60] if os.getenv('WECOM_WEBHOOK_URL') else 'None'}...\n")


def create_test_email():
    """创建测试邮件并触发自动回复"""
    print("\n" + "="*60)
    print("📧 创建测试邮件 - 触发自动回复全流程")
    print("="*60 + "\n")
    
    db = get_session()
    
    try:
        # 1. 检查是否有客户记录，没有则创建
        test_customer = db.query(Customer).filter(
            Customer.email == "john.smith@example.com"
        ).first()
        
        if not test_customer:
            print("📝 创建测试客户...")
            test_customer = Customer(
                company_name="ABC Trading Co., Ltd",
                contact_name="John Smith",
                email="john.smith@example.com",
                phone="+1-555-0123",
                country="USA",
                industry="Retail",
                status="contacted",
                priority=3,
                source="email",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(test_customer)
            db.commit()
            db.refresh(test_customer)
            print(f"✅ 测试客户已创建: {test_customer.company_name} (ID={test_customer.id})")
        else:
            print(f"✅ 使用现有客户: {test_customer.company_name} (ID={test_customer.id})")
        
        # 2. 创建测试邮件
        print("\n📧 创建测试询价邮件...")
        
        test_email = EmailHistory(
            customer_id=test_customer.id,
            direction='inbound',
            from_name='John Smith',
            from_email='john.smith@example.com',
            to_name='Sales Team',
            to_email='sales@yourcompany.com',
            subject='Inquiry: Men\'s Underwear Bulk Order',
            body="""Dear Sales Team,

I hope this email finds you well.

I am writing to inquire about your men's underwear products. We are a retail company based in the United States, and we are interested in placing a bulk order.

Could you please provide me with the following information:

1. Product catalog with specifications
2. Pricing for different order quantities (MOQ: 1000 pieces, 5000 pieces, 10000 pieces)
3. Available colors and sizes
4. Lead time and shipping options
5. Payment terms

We are looking for high-quality cotton underwear with custom logo printing. Our target market is mid-to-high-end customers.

Please send me your best quotation at your earliest convenience. If possible, we would also like to request some samples before placing the official order.

Looking forward to hearing from you soon.

Best regards,
John Smith
Purchasing Manager
ABC Trading Co., Ltd
Phone: +1-555-0123
Email: john.smith@example.com""",
            html_body=None,
            sent_at=datetime.now(),
            message_id=f"test-{datetime.now().timestamp()}@example.com",
            status='sent',
            delivery_status='delivered',
            replied=False,
            ai_generated=False,
            # AI分析结果（模拟）
            ai_category='inquiry',
            ai_sentiment='positive',
            urgency_level='medium',
            purchase_intent='high',
            ai_summary='客户询价男士内裤批量订单，要求提供产品目录、报价、样品等信息',
            business_stage='新客询盘'
        )
        
        db.add(test_email)
        db.commit()
        db.refresh(test_email)
        
        print(f"✅ 测试邮件已创建: ID={test_email.id}")
        print(f"   主题: {test_email.subject}")
        print(f"   发件人: {test_email.from_name} <{test_email.from_email}>")
        print(f"   分类: {test_email.ai_category}")
        print(f"   意向: {test_email.purchase_intent}")
        
        # 3. 检查自动回复规则
        print("\n🔍 检查自动回复规则...")
        inquiry_rule = db.query(AutoReplyRule).filter(
            AutoReplyRule.email_category == 'inquiry',
            AutoReplyRule.is_enabled == True
        ).first()
        
        if not inquiry_rule:
            print("⚠️  未找到启用的询价类邮件自动回复规则")
            print("   请在系统中创建并启用'新客询盘'的自动回复规则")
            print("   规则配置:")
            print("   - 邮件类型: inquiry (新客询盘)")
            print("   - 审核方式: wechat (企业微信)")
            print("   - 启用规则: 是")
            print("   - 自动生成回复: 是")
            print("   - 需要审核: 是")
            return
        
        print(f"✅ 找到匹配的自动回复规则:")
        print(f"   规则名称: {inquiry_rule.rule_name}")
        print(f"   审核方式: {inquiry_rule.approval_method}")
        print(f"   审核超时: {inquiry_rule.approval_timeout_hours} 小时")
        
        # 4. 生成AI回复并创建审核任务
        print("\n🤖 生成AI自动回复...")
        print("   (这可能需要几秒钟...)")
        
        try:
            # 直接调用AI生成回复
            from src.ai.email_analyzer import EmailAIAnalyzer
            
            analyzer = EmailAIAnalyzer()
            
            # 生成回复
            import asyncio
            reply_result = asyncio.run(analyzer.generate_reply(
                subject=test_email.subject,
                body=test_email.body,
                tone='professional',
                use_knowledge_base=False
            ))
            
            if not reply_result.get('success'):
                print(f"❌ AI生成回复失败: {reply_result.get('message')}")
                return
            
            # 🔥 修复：reply_result['reply'] 是字符串，不是字典
            draft_subject = f"Re: {test_email.subject}"
            reply_content = reply_result.get('reply', '')
            draft_body = reply_content  # 纯文本版本（从HTML提取）
            draft_html = reply_content  # HTML版本
            
            print(f"✅ AI回复生成成功")
            print(f"   主题: {draft_subject}")
            print(f"   正文长度: {len(draft_body)} 字符")
            
            # 创建审核任务
            approval_task = ApprovalTask(
                email_id=test_email.id,
                rule_id=inquiry_rule.id,
                draft_subject=draft_subject,
                draft_body=draft_body,
                draft_html=draft_html,
                status='pending',
                approval_method=inquiry_rule.approval_method,
                auto_send_on_approval=True,
                timeout_at=datetime.utcnow() + timedelta(hours=inquiry_rule.approval_timeout_hours or 24),
                ai_analysis_summary=json.dumps({
                    'category': test_email.ai_category,
                    'sentiment': test_email.ai_sentiment,
                    'purchase_intent': test_email.purchase_intent,
                    'urgency_level': test_email.urgency_level,
                    'summary': test_email.ai_summary
                }, ensure_ascii=False)
            )
            
            db.add(approval_task)
            db.commit()
            db.refresh(approval_task)
            
            print(f"✅ 审核任务已创建: ID={approval_task.id}")
            
            # 发送企业微信通知
            if inquiry_rule.approval_method == 'wechat':
                try:
                    from src.utils.wecom_notification import get_wecom_notification
                    
                    wecom = get_wecom_notification()
                    wecom.send_approval_notification(
                        task_id=approval_task.id,
                        email_subject=test_email.subject,
                        email_from=test_email.from_email,
                        email_category=test_email.ai_category,
                        draft_subject=draft_subject,
                        urgency_level=test_email.urgency_level or 'medium',
                        use_webhook=True
                    )
                    print("✅ 企业微信通知已发送")
                except Exception as e:
                    print(f"⚠️  企业微信通知发送失败: {str(e)}")
            
            print("\n✅ AI自动回复生成成功!")
            print(f"   邮件ID: {test_email.id}")
            print(f"   规则ID: {inquiry_rule.id}")
            print(f"   审核任务ID: {approval_task.id}")
            
            # 5. 显示企业微信通知状态
            print("\n📱 企业微信通知:")
            if inquiry_rule.approval_method == 'wechat':
                print("   ✅ 已发送审核通知到企业微信群")
                print("   请查看您的企业微信群消息")
            else:
                print(f"   ⚠️  当前审核方式为: {inquiry_rule.approval_method}")
                print("   如需企业微信通知，请将规则的审核方式改为'wechat'")
            
            # 6. 提供审核链接
            print("\n🔗 审核链接:")
            print(f"   http://localhost:5173/#/approval_tasks/{approval_task.id}/show")
            print("\n" + "="*60)
            print("✅ 测试邮件创建成功！完整流程已触发。")
            print("="*60)
            print("\n📋 后续步骤:")
            print("   1. 查看企业微信群的审核通知")
            print("   2. 点击链接进入审核页面")
            print("   3. 查看AI生成的回复内容")
            print("   4. 点击'通过'或'拒绝'完成审核")
            print("   5. 审核通过后，邮件会自动发送（如已配置SMTP）")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ AI自动回复生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            print("\n可能的原因:")
            print("   1. OpenAI API配置问题")
            print("   2. 自动回复规则配置有误")
            print("   3. 数据库连接问题")
            
    except Exception as e:
        print(f"\n❌ 创建测试邮件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def show_system_status():
    """显示系统状态"""
    print("\n" + "="*60)
    print("📊 系统状态检查")
    print("="*60 + "\n")
    
    db = get_session()
    
    try:
        # 检查自动回复规则
        rules = db.query(AutoReplyRule).filter(AutoReplyRule.is_enabled == True).all()
        print(f"✅ 启用的自动回复规则: {len(rules)} 个")
        for rule in rules:
            print(f"   - {rule.rule_name} ({rule.email_category}) - 审核方式: {rule.approval_method}")
        
        if not rules:
            print("   ⚠️  没有启用的自动回复规则")
            print("   请先在系统中创建并启用规则")
        
        # 检查邮件总数
        from src.crm.database import EmailHistory
        total_emails = db.query(EmailHistory).count()
        print(f"\n✅ 邮件历史总数: {total_emails} 封")
        
        # 检查审核任务
        from src.crm.database import ApprovalTask
        pending_tasks = db.query(ApprovalTask).filter(
            ApprovalTask.status == 'pending'
        ).count()
        print(f"✅ 待审核任务: {pending_tasks} 个")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n")
    print("🚀 自动回复全流程测试工具")
    print("="*60)
    
    # 显示系统状态
    show_system_status()
    
    # 询问是否继续
    print("\n")
    response = input("是否创建测试邮件并触发自动回复? (y/n): ").strip().lower()
    
    if response == 'y':
        create_test_email()
    else:
        print("\n已取消。")
