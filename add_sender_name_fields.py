"""
为 email_history 表添加发件人和收件人名称字段
用于存储从邮件头部解析出的真实姓名

使用方法：
python add_sender_name_fields.py
"""
from src.crm.database import get_engine
from sqlalchemy import text

def add_name_fields():
    """添加发件人和收件人名称字段"""
    engine = get_engine()
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            print("🔧 开始添加发件人和收件人名称字段...")
            
            # 添加 from_name 字段（发件人名称）
            print("  添加 from_name 字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS from_name VARCHAR"))
            
            # 添加 to_name 字段（收件人名称）
            print("  添加 to_name 字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS to_name VARCHAR"))
            
            trans.commit()
            print("✅ 字段添加成功！")
            print("\n📝 新增字段:")
            print("  - from_name: 发件人名称（如：Jazmin Louise）")
            print("  - to_name: 收件人名称")
            print("\n🔄 下次同步邮件时，这些字段会自动填充")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ 添加字段失败: {str(e)}")
            raise

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📧 数据库迁移：添加发件人/收件人名称字段")
    print("="*60 + "\n")
    
    print("⚠️  注意：此操作将修改 email_history 表结构")
    print("请确保：")
    print("  1. PostgreSQL 数据库正在运行")
    print("  2. 已备份数据库")
    print("\n按 Enter 继续...")
    input()
    
    add_name_fields()
    
    print("\n" + "="*60)
    print("✅ 迁移完成")
    print("="*60)
