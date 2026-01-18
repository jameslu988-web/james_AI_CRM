#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""执行SQL迁移：添加company_type字段"""

import psycopg2

def execute_migration():
    """执行数据库迁移"""
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='crm_system',
            user='postgres',
            password='postgres123'
        )
        cursor = conn.cursor()
        
        # 读取并执行SQL文件
        with open('migrations/add_company_type.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            cursor.execute(sql)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ 数据库迁移成功：company_type字段已添加")
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

if __name__ == "__main__":
    execute_migration()
