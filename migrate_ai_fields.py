"""
数据库扩展字段迁移脚本
根据AI智能分析方案添加新字段
"""

from src.crm.database import Base, get_engine
from sqlalchemy import Column, String, Integer, Text, Boolean, Float, JSON
from sqlalchemy import text

def add_extended_ai_fields():
    """添加扩展的AI分析字段到email_history表"""
    
    engine = get_engine()
    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()
        
        try:
            print("📊 开始添加AI扩展字段...")
            
            # 业务阶段字段
            print("  添加业务阶段字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS business_stage VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS secondary_category VARCHAR"))
            
            # 客户意图字段
            print("  添加客户意图字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS purchase_intent_score INTEGER"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS budget_level VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS decision_authority VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS competition_status VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS customer_business_type VARCHAR"))
            
            # 情感态度字段
            print("  添加情感态度字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS tone VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS satisfaction_level VARCHAR"))
            
            # 紧急度评估字段
            print("  添加紧急度字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS response_deadline VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS business_impact VARCHAR"))
            
            # 客户画像字段
            print("  添加客户画像字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS customer_grade_suggestion VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS professionalism VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS communication_style VARCHAR"))
            
            # 内容分析字段（JSON格式）
            print("  添加内容分析字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS mentioned_products TEXT"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS mentioned_quantities VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS mentioned_prices VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS mentioned_timeline VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS questions_asked TEXT"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS concerns TEXT"))
            
            # 行动建议字段
            print("  添加行动建议字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS response_template_suggestion VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS requires_human_review BOOLEAN DEFAULT FALSE"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS human_review_reason TEXT"))
            
            # 风险机会字段
            print("  添加风险机会字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS risk_level VARCHAR"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS risk_factors TEXT"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS opportunity_score INTEGER"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS conversion_probability INTEGER"))
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS estimated_order_value VARCHAR"))
            
            # 完整分析结果（JSON格式）
            print("  添加完整分析结果字段...")
            conn.execute(text("ALTER TABLE email_history ADD COLUMN IF NOT EXISTS full_analysis_json TEXT"))
            
            # 提交事务
            trans.commit()
            print("✅ 所有AI扩展字段添加成功！")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ 添加字段失败: {str(e)}")
            raise


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔧 数据库扩展字段迁移")
    print("="*60 + "\n")
    
    print("⚠️  注意：此操作将修改 email_history 表结构")
    print("请确保：")
    print("  1. PostgreSQL 数据库正在运行")
    print("  2. 已备份数据库")
    print("\n按 Enter 继续...")
    input()
    
    try:
        add_extended_ai_fields()
        
        print("\n" + "="*60)
        print("🎉 迁移完成！")
        print("="*60)
        print("\n新增字段包括：")
        print("  📊 业务阶段分类（business_stage, secondary_category）")
        print("  🎯 客户意图识别（purchase_intent_score, budget_level等）")
        print("  😊 情感态度（tone, satisfaction_level）")
        print("  ⏰ 紧急度评估（response_deadline, business_impact）")
        print("  👤 客户画像（customer_grade_suggestion, professionalism等）")
        print("  📝 内容分析（mentioned_products, questions_asked等）")
        print("  🎬 行动建议（response_template_suggestion, requires_human_review等）")
        print("  ⚠️  风险机会（risk_level, opportunity_score等）")
        print("\n现在可以使用完整的AI智能分析功能！")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
