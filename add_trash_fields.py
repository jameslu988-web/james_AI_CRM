"""
邮件回收站功能数据库迁移脚本
为 email_history 表添加软删除字段

使用方法：
python add_trash_fields.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/customers.db")

def migrate_database():
    """添加回收站相关字段"""
    if not DB_PATH.exists():
        print("❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🔧 开始数据库迁移...")
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(email_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 添加 is_deleted 字段
        if 'is_deleted' not in columns:
            cursor.execute("""
                ALTER TABLE email_history 
                ADD COLUMN is_deleted BOOLEAN DEFAULT 0 NOT NULL
            """)
            print("✅ 已添加 is_deleted 字段")
        else:
            print("ℹ️  is_deleted 字段已存在")
        
        # 添加 deleted_at 字段
        if 'deleted_at' not in columns:
            cursor.execute("""
                ALTER TABLE email_history 
                ADD COLUMN deleted_at DATETIME
            """)
            print("✅ 已添加 deleted_at 字段")
        else:
            print("ℹ️  deleted_at 字段已存在")
        
        # 添加 deleted_by 字段
        if 'deleted_by' not in columns:
            cursor.execute("""
                ALTER TABLE email_history 
                ADD COLUMN deleted_by TEXT
            """)
            print("✅ 已添加 deleted_by 字段")
        else:
            print("ℹ️  deleted_by 字段已存在")
        
        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email_history_is_deleted 
            ON email_history(is_deleted)
        """)
        print("✅ 已创建 is_deleted 索引")
        
        conn.commit()
        print("\n✅ 数据库迁移完成！")
        print("\n📝 新增功能：")
        print("1. 邮件删除改为软删除（移入回收站）")
        print("2. 可从回收站恢复误删的邮件")
        print("3. 支持永久删除和清空回收站")
        print("\n🔗 访问路径：邮件管理 > 回收站")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("邮件回收站功能 - 数据库迁移")
    print("=" * 60)
    print()
    
    success = migrate_database()
    
    if success:
        print("\n" + "=" * 60)
        print("迁移成功！现在可以使用邮件回收站功能了。")
        print("=" * 60)
    else:
        print("\n❌ 迁移失败，请检查错误信息")
