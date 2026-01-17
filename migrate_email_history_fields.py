"""
数据库迁移脚本 - 为EmailHistory表添加from_email和to_email字段
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/customers.db")

def migrate():
    """执行迁移"""
    if not DB_PATH.exists():
        print("❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(email_history)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 添加from_email字段
        if 'from_email' not in columns:
            print("📝 添加 from_email 字段...")
            cursor.execute("ALTER TABLE email_history ADD COLUMN from_email TEXT")
            print("✅ from_email 字段添加成功")
        else:
            print("ℹ️  from_email 字段已存在")
        
        # 添加to_email字段
        if 'to_email' not in columns:
            print("📝 添加 to_email 字段...")
            cursor.execute("ALTER TABLE email_history ADD COLUMN to_email TEXT")
            print("✅ to_email 字段添加成功")
        else:
            print("ℹ️  to_email 字段已存在")
        
        conn.commit()
        print("\n✅ 数据库迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("数据库迁移：EmailHistory表添加邮箱字段")
    print("=" * 60)
    migrate()
