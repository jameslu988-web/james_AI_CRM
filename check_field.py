import os
os.environ['DB_TYPE'] = 'postgresql'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'postgres123'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'crm_system'

from src.crm.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'email_history' AND column_name = 'business_stage'"))
    row = result.fetchone()
    if row:
        print("✅ business_stage字段已存在")
    else:
        print("❌ business_stage字段不存在")
        print("\n正在添加字段...")
        conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS business_stage VARCHAR"))
        conn.commit()
        print("✅ 字段添加完成")
