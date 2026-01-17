"""
SQLite → PostgreSQL 数据迁移脚本
执行前请确保：
1. PostgreSQL 已安装并运行
2. 已创建目标数据库 crm_system
3. 已安装 psycopg2-binary
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import json

# 配置
SQLITE_DB = "data/customers.db"
PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres123',
    'dbname': 'crm_system'
}

# 表迁移顺序（按外键依赖排序）
TABLES = [
    'users',
    'roles',
    'user_roles',
    'customers',
    'email_history',
    'orders',
    'followup_records',
    'email_templates',
    'email_campaigns',
    'custom_field_definitions',
    'leads',
    'email_accounts'
]

def create_postgresql_database():
    """创建 PostgreSQL 数据库"""
    print("📦 步骤1：创建 PostgreSQL 数据库...")
    
    try:
        # 连接到 postgres 默认数据库
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password'],
            dbname='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{PG_CONFIG['dbname']}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"   ⚠️  数据库 {PG_CONFIG['dbname']} 已存在，将先删除...")
            # 断开所有连接
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{PG_CONFIG['dbname']}'
                AND pid <> pg_backend_pid()
            """)
            cursor.execute(f"DROP DATABASE {PG_CONFIG['dbname']}")
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE {PG_CONFIG['dbname']} ENCODING 'UTF8'")
        print(f"   ✅ 数据库 {PG_CONFIG['dbname']} 创建成功！")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 创建数据库失败: {e}")
        raise

def create_postgresql_tables():
    """在 PostgreSQL 中创建表结构"""
    print("\n📋 步骤2：创建 PostgreSQL 表结构...")
    
    from src.crm.database import Base, get_engine
    import os
    
    # 设置环境变量为 PostgreSQL
    os.environ['DB_TYPE'] = 'postgresql'
    os.environ['DB_PASSWORD'] = PG_CONFIG['password']
    
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        print("   ✅ 所有表结构创建成功！")
    except Exception as e:
        print(f"   ❌ 创建表结构失败: {e}")
        raise

def get_sqlite_table_columns(cursor, table_name):
    """获取 SQLite 表的列信息"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def convert_value(value, column_name):
    """转换值类型（处理布尔值和日期）"""
    if value is None:
        return None
    
    # 布尔值转换
    if isinstance(value, int) and column_name in [
        'is_active', 'is_default', 'is_superuser', 'opened', 'clicked', 
        'replied', 'ai_generated', 'need_receipt', 'is_deleted', 
        'is_starred', 'requires_attention', 'auto_sync', 'auto_match_customer',
        'auto_create_followup', 'first_sync_completed', 'converted', 'is_visible'
    ]:
        return bool(value)
    
    return value

def migrate_table_data(sqlite_conn, pg_conn, table_name):
    """迁移单个表的数据"""
    print(f"   📊 迁移表: {table_name}")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    try:
        # 检查表是否存在
        sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not sqlite_cursor.fetchone():
            print(f"      ⚠️  表 {table_name} 不存在，跳过")
            return 0
        
        # 获取列信息
        columns = get_sqlite_table_columns(sqlite_cursor, table_name)
        
        # 读取所有数据
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"      📭 表 {table_name} 无数据")
            return 0
        
        # 准备插入语句
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join([f'"{col}"' for col in columns])
        insert_sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
        
        # 转换数据
        converted_rows = []
        for row in rows:
            converted_row = tuple(
                convert_value(value, columns[i]) 
                for i, value in enumerate(row)
            )
            converted_rows.append(converted_row)
        
        # 批量插入
        execute_batch(pg_cursor, insert_sql, converted_rows, page_size=1000)
        pg_conn.commit()
        
        print(f"      ✅ 成功迁移 {len(rows)} 条记录")
        return len(rows)
        
    except Exception as e:
        pg_conn.rollback()
        print(f"      ❌ 迁移失败: {e}")
        raise
    finally:
        sqlite_cursor.close()
        pg_cursor.close()

def update_sequences(pg_conn):
    """更新 PostgreSQL 序列（自增ID）"""
    print("\n🔄 步骤4：更新序列...")
    
    cursor = pg_conn.cursor()
    
    for table in TABLES:
        try:
            # 获取表的最大ID
            cursor.execute(f"SELECT MAX(id) FROM {table}")
            max_id = cursor.fetchone()[0]
            
            if max_id:
                # 更新序列
                cursor.execute(f"SELECT setval('{table}_id_seq', {max_id}, true)")
                print(f"   ✅ {table}: 序列更新到 {max_id}")
        except Exception as e:
            # 某些表可能没有 id 字段或序列
            pass
    
    pg_conn.commit()
    cursor.close()

def verify_migration(sqlite_conn, pg_conn):
    """验证数据迁移完整性"""
    print("\n✅ 步骤5：验证数据完整性...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    all_match = True
    
    for table in TABLES:
        try:
            # SQLite 计数
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            # PostgreSQL 计数
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = pg_cursor.fetchone()[0]
            
            if sqlite_count == pg_count:
                print(f"   ✅ {table}: {sqlite_count} 条记录匹配")
            else:
                print(f"   ❌ {table}: SQLite={sqlite_count}, PostgreSQL={pg_count} 不匹配！")
                all_match = False
                
        except Exception as e:
            print(f"   ⚠️  {table}: 验证失败 ({e})")
    
    sqlite_cursor.close()
    pg_cursor.close()
    
    return all_match

def main():
    """主迁移流程"""
    print("=" * 60)
    print("🚀 SQLite → PostgreSQL 数据迁移工具")
    print("=" * 60)
    
    try:
        # 步骤1: 创建数据库
        create_postgresql_database()
        
        # 步骤2: 创建表结构
        create_postgresql_tables()
        
        # 步骤3: 迁移数据
        print("\n📦 步骤3：迁移表数据...")
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        pg_conn = psycopg2.connect(**PG_CONFIG)
        
        total_records = 0
        for table in TABLES:
            count = migrate_table_data(sqlite_conn, pg_conn, table)
            total_records += count
        
        print(f"\n   📊 总计迁移 {total_records} 条记录")
        
        # 步骤4: 更新序列
        update_sequences(pg_conn)
        
        # 步骤5: 验证数据
        all_match = verify_migration(sqlite_conn, pg_conn)
        
        # 关闭连接
        sqlite_conn.close()
        pg_conn.close()
        
        # 总结
        print("\n" + "=" * 60)
        if all_match:
            print("🎉 迁移完成！所有数据验证通过！")
            print("\n📝 后续步骤：")
            print("   1. 停止后端服务")
            print("   2. 设置环境变量 DB_TYPE=postgresql")
            print("   3. 重启后端：uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload")
            print("   4. 刷新前端页面测试")
        else:
            print("⚠️  迁移完成，但部分数据验证未通过，请检查！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
