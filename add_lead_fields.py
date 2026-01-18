"""
添加Lead表的新字段：country, industry, company_type
用于更好地分类和评分线索
"""
from sqlalchemy import text
from src.crm.database import get_session

def add_lead_fields():
    db = get_session()
    
    try:
        # 添加country字段（国家/地区）
        db.execute(text("""
            ALTER TABLE leads 
            ADD COLUMN IF NOT EXISTS country VARCHAR(50)
        """))
        
        # 添加industry字段（行业）
        db.execute(text("""
            ALTER TABLE leads 
            ADD COLUMN IF NOT EXISTS industry VARCHAR(100)
        """))
        
        # 添加company_type字段（公司类型）
        db.execute(text("""
            ALTER TABLE leads 
            ADD COLUMN IF NOT EXISTS company_type VARCHAR(50)
        """))
        
        db.commit()
        print("✅ 成功添加字段：country, industry, company_type")
        
    except Exception as e:
        print(f"❌ 添加字段失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_lead_fields()
