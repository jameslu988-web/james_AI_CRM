"""直接在数据库中更新邮件为已读"""
from src.crm.database import get_session, EmailHistory

def test_direct_update():
    """直接更新数据库"""
    db = get_session()
    try:
        # 找一封未读邮件
        email = db.query(EmailHistory).filter(EmailHistory.opened == False).first()
        
        if not email:
            print("❌ 没有未读邮件")
            return
        
        print(f"\n📧 找到未读邮件:")
        print(f"   ID: {email.id}")
        print(f"   主题: {email.subject}")
        print(f"   opened: {email.opened}")
        
        # 更新为已读
        print(f"\n🔄 正在更新为已读...")
        email.opened = True
        db.commit()
        db.refresh(email)
        
        print(f"✅ 更新成功! opened = {email.opened}")
        
        # 验证：重新查询
        print(f"\n🔍 重新查询验证...")
        email_check = db.query(EmailHistory).filter(EmailHistory.id == email.id).first()
        print(f"   ID: {email_check.id}")
        print(f"   opened: {email_check.opened}")
        
        if email_check.opened:
            print("\n✅ 验证成功：数据库已正确更新！")
        else:
            print("\n❌ 验证失败：数据库没有更新！")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_direct_update()
