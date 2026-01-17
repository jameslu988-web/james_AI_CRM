"""检查特定邮件的opened状态"""
from src.crm.database import get_session, EmailHistory

def check_email(email_id):
    """检查指定邮件的状态"""
    db = get_session()
    try:
        email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
        
        if not email:
            print(f"❌ 未找到邮件 ID={email_id}")
            return
        
        print(f"\n📧 邮件详情 (ID={email_id}):")
        print(f"   主题: {email.subject[:50] if email.subject else '(无主题)'}")
        print(f"   opened: {email.opened}")
        print(f"   clicked: {email.clicked}")
        print(f"   replied: {email.replied}")
        print()
        
    finally:
        db.close()

if __name__ == "__main__":
    # 检查最近几封邮件
    for email_id in [1196, 1195, 1194, 2]:
        check_email(email_id)
