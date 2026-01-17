"""数据库迁移脚本 - 添加自定义字段定义表"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "customers.db"

def migrate():
    """添加 custom_field_definitions 表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查表是否已存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='custom_field_definitions'
        """)
        
        if cursor.fetchone():
            print("✓ custom_field_definitions 表已存在")
        else:
            # 创建自定义字段定义表
            cursor.execute("""
                CREATE TABLE custom_field_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_name VARCHAR NOT NULL UNIQUE,
                    field_type VARCHAR DEFAULT 'text',
                    is_visible BOOLEAN DEFAULT 1,
                    display_order INTEGER DEFAULT 0,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """)
            conn.commit()
            print("✓ custom_field_definitions 表创建成功")
        
        conn.close()
        print("✓ 数据库迁移完成")
        
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        conn.rollback()
        conn.close()
        raise

if __name__ == "__main__":
    migrate()
