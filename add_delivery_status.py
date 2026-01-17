"""
数据库迁移脚本：添加邮件投递状态字段
执行方式：python add_delivery_status.py
"""
import sqlite3
import os

# 数据库路径
DB_PATH = "crm.db"

def add_delivery_status_columns():
    """添加投递状态相关字段到 email_history 表"""
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(email_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        fields_to_add = []
        
        if 'delivery_status' not in columns:
            fields_to_add.append(('delivery_status', "ALTER TABLE email_history ADD COLUMN delivery_status TEXT DEFAULT 'pending'"))
        
        if 'delivery_time' not in columns:
            fields_to_add.append(('delivery_time', "ALTER TABLE email_history ADD COLUMN delivery_time DATETIME"))
        
        if 'bounce_reason' not in columns:
            fields_to_add.append(('bounce_reason', "ALTER TABLE email_history ADD COLUMN bounce_reason TEXT"))
        
        if not fields_to_add:
            print("✅ 所有字段已存在，无需迁移")
            return True
        
        # 执行添加字段
        for field_name, sql in fields_to_add:
            print(f"📝 添加字段: {field_name}")
            cursor.execute(sql)
            print(f"✅ 字段 {field_name} 添加成功")
        
        # 🔥 更新现有邮件的投递状态
        # status='sent' 的邮件设置为 'pending'（等待确认）
        # status='failed' 的邮件设置为 'failed'（发送失败）
        # status='draft' 的邮件保持为 NULL
        print("\n📝 更新现有邮件的投递状态...")
        cursor.execute("""
            UPDATE email_history 
            SET delivery_status = 'pending' 
            WHERE status = 'sent' AND direction = 'outbound'
        """)
        updated_sent = cursor.rowcount
        
        cursor.execute("""
            UPDATE email_history 
            SET delivery_status = 'failed' 
            WHERE status = 'failed' AND direction = 'outbound'
        """)
        updated_failed = cursor.rowcount
        
        conn.commit()
        print(f"✅ 更新完成:")
        print(f"   - {updated_sent} 封已发送邮件设置为 'pending'")
        print(f"   - {updated_failed} 封失败邮件设置为 'failed'")
        
        # 创建索引以提升查询性能
        print("\n📝 创建索引...")
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_delivery_status ON email_history(delivery_status)")
            print("✅ 索引创建成功: idx_delivery_status")
        except Exception as e:
            print(f"⚠️ 索引创建失败（可能已存在）: {e}")
        
        conn.close()
        print("\n🎉 数据库迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 开始执行数据库迁移：添加邮件投递状态字段")
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
