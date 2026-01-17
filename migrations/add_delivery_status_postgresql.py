"""
PostgreSQL数据库迁移脚本：添加邮件投递状态字段
执行方式：python migrations/add_delivery_status_postgresql.py
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.crm.database import get_engine

def add_delivery_status_columns():
    """添加投递状态相关字段到 email_history 表"""
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'email_history'
            """))
            existing_columns = [row[0] for row in result]
            
            fields_to_add = []
            
            if 'delivery_status' not in existing_columns:
                fields_to_add.append(('delivery_status', """
                    ALTER TABLE email_history 
                    ADD COLUMN delivery_status VARCHAR DEFAULT 'pending'
                """))
            
            if 'delivery_time' not in existing_columns:
                fields_to_add.append(('delivery_time', """
                    ALTER TABLE email_history 
                    ADD COLUMN delivery_time TIMESTAMP
                """))
            
            if 'bounce_reason' not in existing_columns:
                fields_to_add.append(('bounce_reason', """
                    ALTER TABLE email_history 
                    ADD COLUMN bounce_reason TEXT
                """))
            
            if not fields_to_add:
                print("✅ 所有字段已存在，无需迁移")
                return True
            
            # 执行添加字段
            for field_name, sql in fields_to_add:
                print(f"📝 添加字段: {field_name}")
                conn.execute(text(sql))
                conn.commit()
                print(f"✅ 字段 {field_name} 添加成功")
            
            # 🔥 更新现有邮件的投递状态
            print("\n📝 更新现有邮件的投递状态...")
            
            # status='sent' 的出站邮件设置为 'pending'
            result = conn.execute(text("""
                UPDATE email_history 
                SET delivery_status = 'pending' 
                WHERE status = 'sent' AND direction = 'outbound' AND delivery_status IS NULL
            """))
            conn.commit()
            updated_sent = result.rowcount
            
            # status='failed' 的出站邮件设置为 'failed'
            result = conn.execute(text("""
                UPDATE email_history 
                SET delivery_status = 'failed' 
                WHERE status = 'failed' AND direction = 'outbound' AND delivery_status IS NULL
            """))
            conn.commit()
            updated_failed = result.rowcount
            
            print(f"✅ 更新完成:")
            print(f"   - {updated_sent} 封已发送邮件设置为 'pending'")
            print(f"   - {updated_failed} 封失败邮件设置为 'failed'")
            
            # 创建索引以提升查询性能
            print("\n📝 创建索引...")
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_delivery_status 
                    ON email_history(delivery_status)
                """))
                conn.commit()
                print("✅ 索引创建成功: idx_delivery_status")
            except Exception as e:
                print(f"⚠️ 索引创建失败（可能已存在）: {e}")
            
            print("\n🎉 数据库迁移完成！")
            return True
            
    except Exception as e:
        print(f"❌ 数据库迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 开始执行PostgreSQL数据库迁移：添加邮件投递状态字段")
    print("=" * 60)
    print()
    
    success = add_delivery_status_columns()
    
    print()
    print("=" * 60)
    if success:
        print("✅ 迁移成功！可以重启后端服务以应用更改")
    else:
        print("❌ 迁移失败！请检查错误信息")
    print("=" * 60)
