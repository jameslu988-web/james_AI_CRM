"""
修复数据库中的 other/general 分类
将所有 'other' 和 'general' 改为 'spam'（垃圾营销）
"""

from src.crm.database import get_session, EmailHistory

def fix_category():
    """修复邮件分类"""
    db = get_session()
    
    try:
        # 统计需要修复的数据
        other_count = db.query(EmailHistory).filter(EmailHistory.ai_category == 'other').count()
        general_count = db.query(EmailHistory).filter(EmailHistory.ai_category == 'general').count()
        
        print(f"📊 找到需要修复的数据:")
        print(f"   - 'other' 分类: {other_count} 封邮件")
        print(f"   - 'general' 分类: {general_count} 封邮件")
        print(f"   - 总计: {other_count + general_count} 封邮件")
        
        if other_count == 0 and general_count == 0:
            print("✅ 没有需要修复的数据")
            return
        
        # 修复 'other' -> 'spam'
        if other_count > 0:
            print(f"\n🔧 正在修复 'other' 分类...")
            db.query(EmailHistory).filter(
                EmailHistory.ai_category == 'other'
            ).update({
                'ai_category': 'spam'
            })
            print(f"✅ 已修复 {other_count} 封邮件: other -> spam")
        
        # 修复 'general' -> 'spam'
        if general_count > 0:
            print(f"\n🔧 正在修复 'general' 分类...")
            db.query(EmailHistory).filter(
                EmailHistory.ai_category == 'general'
            ).update({
                'ai_category': 'spam'
            })
            print(f"✅ 已修复 {general_count} 封邮件: general -> spam")
        
        # 提交更改
        db.commit()
        
        # 验证
        remaining_other = db.query(EmailHistory).filter(EmailHistory.ai_category == 'other').count()
        remaining_general = db.query(EmailHistory).filter(EmailHistory.ai_category == 'general').count()
        spam_count = db.query(EmailHistory).filter(EmailHistory.ai_category == 'spam').count()
        
        print(f"\n📊 修复后统计:")
        print(f"   - 'other' 分类: {remaining_other} 封")
        print(f"   - 'general' 分类: {remaining_general} 封")
        print(f"   - 'spam' 分类: {spam_count} 封")
        
        if remaining_other == 0 and remaining_general == 0:
            print(f"\n🎉 所有数据修复成功！")
        else:
            print(f"\n⚠️  仍有数据未修复，请检查")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 修复失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 邮件分类修复工具")
    print("=" * 60)
    print("功能：将数据库中的 'other' 和 'general' 分类改为 'spam'")
    print("=" * 60)
    print()
    
    fix_category()
    
    print()
    print("=" * 60)
    print("✅ 修复完成！")
    print("=" * 60)
