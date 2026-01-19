"""
执行客户分级字段迁移
"""
import os
os.environ['DB_TYPE'] = 'postgresql'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'postgres123'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'crm_system'

import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='crm_system',
    user='postgres',
    password='postgres123'
)

cursor = conn.cursor()

print("📊 开始执行客户分级字段迁移...")

with open('migrations/add_customer_grading_fields.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
    cursor.execute(sql)

conn.commit()
cursor.close()
conn.close()

print("✅ 客户分级字段迁移完成！")
