"""
为收件箱(inbound)的邮件设置business_stage，以便测试筛选功能
"""
from dotenv import load_dotenv

# 🔥 加载环境配置
load_dotenv()

from src.crm.database import get_engine
from sqlalchemy import text

# 9种业务类型
business_stages = [
    '新客询盘',
    '报价跟进',
    '样品阶段',
    '谈判议价',
    '订单确认',
    '生产跟踪',
    '售后服务',
    '老客维护',
    '垃圾营销'
]

engine = get_engine()
with engine.connect() as conn:
    # 获取收件箱中前45封邮件（确保每种类型至少有5封）
    result = conn.execute(text("SELECT id, subject FROM email_history WHERE direction='inbound' ORDER BY id DESC LIMIT 45"))
    emails = result.fetchall()
    
    if not emails:
        print("❌ 收件箱中没有邮件记录")
    else:
        print(f"📧 找到 {len(emails)} 封收件箱邮件，正在更新...")
        
        # 为每封邮件分配一个业务阶段（循环使用）
        for idx, email in enumerate(emails):
            email_id = email[0]
            subject = email[1]
            stage = business_stages[idx % len(business_stages)]
            
            conn.execute(
                text("UPDATE email_history SET business_stage = :stage WHERE id = :id"),
                {"stage": stage, "id": email_id}
            )
            print(f"  ✅ ID {email_id}: {subject[:50] if subject else '(无主题)'}... -> {stage}")
        
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ 更新完成！收件箱业务阶段分布如下：")
        print("="*60)
        
        # 统计每个阶段的邮件数量
        for stage in business_stages:
            result = conn.execute(
                text("SELECT COUNT(*) FROM email_history WHERE business_stage = :stage AND direction='inbound'"),
                {"stage": stage}
            )
            count = result.fetchone()[0]
            print(f"  {stage}: {count} 封")
        
        print("\n🎯 现在可以在收件箱中测试筛选功能了！")
