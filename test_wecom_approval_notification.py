"""
测试企业微信群消息通知
发送审核任务到企业微信群
"""
from dotenv import load_dotenv

# 🔥 加载环境配置
load_dotenv()

from src.crm.database import get_session, ApprovalTask, EmailHistory
from src.utils.wecom_notification import get_wecom_notification

def send_test_wecom_notification():
    """发送测试企业微信通知"""
    db = get_session()
    
    try:
        # 获取最新的待审核任务
        task = db.query(ApprovalTask).filter(
            ApprovalTask.status == 'pending'
        ).order_by(ApprovalTask.id.desc()).first()
        
        if not task:
            print("❌ 没有找到待审核任务，请先运行 create_test_approval_task.py")
            return
        
        # 获取关联的邮件
        email = db.query(EmailHistory).filter(
            EmailHistory.id == task.email_id
        ).first()
        
        if not email:
            print("❌ 找不到关联的邮件")
            return
        
        print(f"📧 准备发送审核通知...")
        print(f"   任务ID: {task.id}")
        print(f"   邮件主题: {email.subject}")
        print(f"   发件人: {email.from_email}")
        print(f"   类型: {email.ai_category}")
        print(f"   紧急度: {email.urgency_level}")
        print()
        
        # 获取企业微信通知实例
        wecom = get_wecom_notification()
        
        # 发送审核通知
        result = wecom.send_approval_notification(
            task_id=task.id,
            email_subject=email.subject,
            email_from=f"{email.from_name} <{email.from_email}>",
            email_category=email.ai_category or "inquiry",
            draft_subject=task.draft_subject,
            urgency_level=email.urgency_level or "medium",
            use_webhook=True  # 使用群机器人
        )
        
        if result:
            print("✅ 企业微信通知发送成功！")
            print(f"\n请在企业微信群中查看消息")
            print(f"点击链接可以直接在手机上审核：")
            print(f"http://localhost:5173/mobile-approval.html?id={task.id}")
            print()
            print("⚠️ 注意：如果是内网访问，需要配置内网穿透或使用公网IP")
        else:
            print("❌ 企业微信通知发送失败")
            print("   请检查 .env.wecom 配置文件")
            print("   确保 WECOM_WEBHOOK_URL 已正确配置")
            
    except Exception as e:
        print(f"❌ 发送通知失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("  企业微信审核通知测试")
    print("="*60)
    print()
    send_test_wecom_notification()
