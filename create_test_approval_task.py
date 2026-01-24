"""
生成测试审核任务 - 用于测试群发单显的审核功能
"""
from dotenv import load_dotenv
load_dotenv()

from src.crm.database import get_session, EmailHistory, ApprovalTask, Customer, PromptTemplate
from datetime import datetime, timedelta
import json
import asyncio

def create_test_approval_task():
    """创建测试审核任务"""
    db = get_session()
    
    try:
        # 1. 创建或获取测试客户
        test_customer = db.query(Customer).filter(
            Customer.email == "test.buyer@example.com"
        ).first()
        
        if not test_customer:
            test_customer = Customer(
                company_name="Test Company Ltd",
                email="test.buyer@example.com",
                contact_name="John Test",
                country="United States",
                phone="+1-555-0123",
                status="customer"
            )
            db.add(test_customer)
            db.commit()
            db.refresh(test_customer)
            print(f"✅ 创建测试客户: {test_customer.email}")
        else:
            print(f"✅ 使用现有测试客户: {test_customer.email}")
        
        # 2. 创建测试收件邮件（来自客户的询盘）
        test_email = EmailHistory(
            customer_id=test_customer.id,
            from_name="John Test",
            from_email="test.buyer@example.com",
            to_email="sales@yourcompany.com",
            subject="Inquiry about Men's Underwear - Bulk Order",
            body="""Hello,

I am interested in purchasing a bulk order of men's underwear for our retail chain. 

We are looking for:
- Product: Men's cotton boxer briefs
- Quantity: 5000 pieces
- Sizes: M, L, XL (mixed)
- Quality: Good quality, comfortable fabric
- Customization: Our brand logo printed

Could you please provide:
1. Product catalog with prices
2. MOQ (Minimum Order Quantity)
3. Lead time for production
4. Shipping options and costs to USA
5. Payment terms

We need competitive pricing as this is for a trial order. If quality is good, we will place regular orders.

Looking forward to your prompt reply.

Best regards,
John Test
Purchasing Manager
Test Company Ltd""",
            html_body="""<p>Hello,</p>
<p>I am interested in purchasing a bulk order of men's underwear for our retail chain.</p>
<p>We are looking for:</p>
<ul>
<li>Product: Men's cotton boxer briefs</li>
<li>Quantity: 5000 pieces</li>
<li>Sizes: M, L, XL (mixed)</li>
<li>Quality: Good quality, comfortable fabric</li>
<li>Customization: Our brand logo printed</li>
</ul>
<p>Could you please provide:</p>
<ol>
<li>Product catalog with prices</li>
<li>MOQ (Minimum Order Quantity)</li>
<li>Lead time for production</li>
<li>Shipping options and costs to USA</li>
<li>Payment terms</li>
</ol>
<p>We need competitive pricing as this is for a trial order. If quality is good, we will place regular orders.</p>
<p>Looking forward to your prompt reply.</p>
<p>Best regards,<br>
John Test<br>
Purchasing Manager<br>
Test Company Ltd</p>""",
            direction="inbound",
            status="sent",
            sent_at=datetime.utcnow(),
            
            # AI分析结果（模拟）
            ai_category="inquiry",
            ai_sentiment="positive",
            purchase_intent="high",
            urgency_level="medium",
            ai_summary="客户询问男士内裤批量订单，数量5000件，需要定制LOGO，要求提供产品目录、价格、MOQ、交货期和运费报价。",
            business_stage="新客询盘",
            replied=False
        )
        db.add(test_email)
        db.commit()
        db.refresh(test_email)
        print(f"✅ 创建测试邮件: ID={test_email.id}")
        
        # 🔥 3. 使用AI生成回复（使用专业外贸回复模板）
        print(f"\n🤖 开始AI生成回复...")
        
        # 获取默认的专业外贸回复模板
        default_template = db.query(PromptTemplate).filter_by(
            is_default=True,
            template_type='reply',
            is_active=True
        ).first()
        
        if default_template:
            print(f"✅ 使用提示词模板: {default_template.name}")
            custom_prompt = {
                'system_prompt': default_template.system_prompt,
                'user_prompt_template': default_template.user_prompt_template
            }
        else:
            print(f"⚠️  未找到默认模板，使用硬编码提示词")
            custom_prompt = None
        
        # 调用AI生成回复
        from src.ai.email_analyzer import get_analyzer
        analyzer = get_analyzer()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                analyzer.generate_reply(
                    subject=test_email.subject or "",
                    body=test_email.body or "",
                    context={
                        'customer_name': test_customer.contact_name,
                        'company_name': test_customer.company_name
                    },
                    tone="professional",
                    custom_prompt=custom_prompt  # 使用自定义提示词
                )
            )
        finally:
            loop.close()
        
        if not result.get('success'):
            print(f"❌ AI生成回复失败: {result.get('error')}")
            db.rollback()
            return None
        
        draft_html = result['reply']
        print(f"✅ AI回复生成成功，长度: {len(draft_html)} 字符")
        
        # 4. 创建审核任务
        draft_subject = f"Re: {test_email.subject}"
        
        # 创建审核任务
        approval_task = ApprovalTask(
            email_id=test_email.id,
            rule_id=None,  # 测试任务不关联规则
            draft_subject=draft_subject,
            draft_body=draft_html,  # 使用HTML作为纯文本
            draft_html=draft_html,
            status='pending',
            approval_method='wechat',  # 企业微信审核
            auto_send_on_approval=True,
            timeout_at=datetime.utcnow() + timedelta(hours=24),
            ai_analysis_summary=json.dumps({
                'category': 'inquiry',
                'sentiment': 'positive',
                'purchase_intent': 'high',
                'urgency_level': 'medium',
                'summary': '新客询盘，需求明确，数量较大，购买意向强烈'
            }, ensure_ascii=False)
        )
        
        db.add(approval_task)
        db.commit()
        db.refresh(approval_task)
        
        print(f"\n{'='*60}")
        print(f"✅ 测试审核任务创建成功！")
        print(f"{'='*60}")
        print(f"📧 原始邮件信息:")
        print(f"   ID: {test_email.id}")
        print(f"   发件人: {test_email.from_name} <{test_email.from_email}>")
        print(f"   主题: {test_email.subject}")
        print(f"   类型: {test_email.ai_category}")
        print(f"   意向: {test_email.purchase_intent}")
        print(f"   紧急度: {test_email.urgency_level}")
        print(f"\n📝 审核任务信息:")
        print(f"   任务ID: {approval_task.id}")
        print(f"   回复主题: {approval_task.draft_subject}")
        print(f"   状态: {approval_task.status}")
        print(f"   审核方式: {approval_task.approval_method}")
        print(f"   超时时间: {approval_task.timeout_at}")
        
        # 🔥 发送企业微信通知
        if approval_task.approval_method == 'wechat':
            try:
                from src.utils.wecom_notification import get_wecom_notification
                
                print(f"\n📤 正在发送企业微信通知...")
                
                wecom = get_wecom_notification()
                result = wecom.send_approval_notification(
                    task_id=approval_task.id,
                    email_subject=test_email.subject,
                    email_from=f"{test_email.from_name} <{test_email.from_email}>",
                    email_category=test_email.ai_category,
                    draft_subject=approval_task.draft_subject,
                    urgency_level=test_email.urgency_level,
                    use_webhook=True
                )
                
                if result:
                    print(f"✅ 企业微信通知已发送！")
                else:
                    print(f"⚠️  企业微信通知发送失败")
                    
            except Exception as e:
                print(f"❌ 发送企业微信通知失败: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🔗 访问链接:")
        print(f"   前端审核页面: http://localhost:5173/#/approval_tasks/{approval_task.id}/show")
        print(f"   移动端审核: http://localhost:5173/mobile-approval.html?id={approval_task.id}")
        print(f"\n{'='*60}")
        print(f"💡 测试说明:")
        print(f"   1. 在前端【审核中心】菜单查看待审核任务")
        print(f"   2. 点击任务查看详情，包括原始邮件和AI生成的回复")
        print(f"   3. 可以选择【通过】、【拒绝】或【修改】")
        print(f"   4. 通过后会自动发送邮件（实际测试时需要配置SMTP）")
        print(f"   5. 如果配置了企业微信，会收到群消息通知")
        print(f"{'='*60}\n")
        
        return approval_task
        
    except Exception as e:
        print(f"❌ 创建测试任务失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_approval_task()
