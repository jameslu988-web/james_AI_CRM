"""检查邮件的opened状态"""
from src.crm.database import get_session, EmailHistory

def check_opened_status():
    """检查数据库中邮件的opened状态"""
    db = get_session()
    try:
        # 查询所有邮件的opened状态
        emails = db.query(EmailHistory.id, EmailHistory.subject, EmailHistory.opened).order_by(EmailHistory.id.desc()).limit(10).all()
        
        print("\n" + "="*80)
        print("📊 最近10封邮件的opened状态:")
        print("="*80)
        
        for email in emails:
            status = "✅ 已读" if email.opened else "🔵 未读"
            print(f"ID: {email.id:4d} | {status} | {email.subject[:50]}")
        
        print("="*80 + "\n")
        
        # 统计
        total = db.query(EmailHistory).count()
        opened_count = db.query(EmailHistory).filter(EmailHistory.opened == True).count()
        unopened_count = db.query(EmailHistory).filter(EmailHistory.opened == False).count()
        
        print(f"📈 统计信息:")
        print(f"   总邮件数: {total}")
        print(f"   已读邮件: {opened_count}")
        print(f"   未读邮件: {unopened_count}")
        print()
        
    finally:
        db.close()

if __name__ == "__main__":
    check_opened_status()
