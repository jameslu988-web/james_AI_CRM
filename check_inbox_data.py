from dotenv import load_dotenv

# 🔥 加载环境配置
load_dotenv()

from src.crm.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # 检查收件箱中各业务阶段的邮件数量
    result = conn.execute(text("""
        SELECT business_stage, COUNT(*) 
        FROM email_history 
        WHERE business_stage IS NOT NULL AND direction='inbound' 
        GROUP BY business_stage
    """))
    rows = result.fetchall()
    
    print("📊 收件箱(inbound)中各业务阶段的邮件数量:")
    for row in rows:
        print(f"  {row[0]}: {row[1]}封")
    
    if not rows:
        print("  ❌ 没有数据！")
        print("\n🔍 检查原因：")
        
        # 检查有business_stage的邮件
        result2 = conn.execute(text("SELECT COUNT(*) FROM email_history WHERE business_stage IS NOT NULL"))
        count_with_stage = result2.fetchone()[0]
        print(f"  有business_stage的邮件: {count_with_stage}封")
        
        # 检查inbound邮件
        result3 = conn.execute(text("SELECT COUNT(*) FROM email_history WHERE direction='inbound'"))
        count_inbound = result3.fetchone()[0]
        print(f"  收件箱(inbound)邮件: {count_inbound}封")
        
        # 检查邮件的direction分布
        result4 = conn.execute(text("SELECT direction, COUNT(*) FROM email_history GROUP BY direction"))
        print("\n📊 邮件方向分布:")
        for row in result4.fetchall():
            print(f"  {row[0]}: {row[1]}封")
