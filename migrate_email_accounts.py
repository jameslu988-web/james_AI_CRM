"""数据库迁移 - 添加邮箱账户表"""
from src.crm.database import init_db, get_session, EmailAccount

def migrate():
    """执行迁移"""
    print("🚀 开始迁移：添加邮箱账户表...")
    
    try:
        # 初始化数据库（会创建新表）
        init_db()
        print("✅ 邮箱账户表创建成功")
        
        # 检查表是否创建
        db = get_session()
        count = db.query(EmailAccount).count()
        print(f"📊 当前邮箱账户数量: {count}")
        db.close()
        
        print("✅ 迁移完成！")
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        raise

if __name__ == "__main__":
    migrate()
