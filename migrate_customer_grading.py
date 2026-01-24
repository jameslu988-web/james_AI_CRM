"""
执行客户分级字段迁移
"""
import os
from dotenv import load_dotenv

# 🔥 加载环境配置
load_dotenv()

import psycopg2

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', '5432')),
    database=os.getenv('DB_NAME', 'crm_system'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'postgres123')
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
