"""
创建知识库相关数据表
"""
from dotenv import load_dotenv

# 🔥 加载环境配置
load_dotenv()

from src.crm.database import get_engine, Base

def create_knowledge_tables():
    """创建知识库相关的表"""
    try:
        print("🔧 开始创建知识库表...")
        engine = get_engine()
        
        # 只创建新增的表（不影响现有表）
        from src.crm.database import Product, ProductFAQ, PricingRule, CaseStudy, KnowledgeFAQ
        
        Base.metadata.create_all(engine, tables=[
            Product.__table__,
            ProductFAQ.__table__,
            PricingRule.__table__,
            CaseStudy.__table__,
            KnowledgeFAQ.__table__,
        ])
        
        print("✅ 知识库表创建成功！")
        print("\n创建的表：")
        print("  1. products - 产品知识库")
        print("  2. product_faqs - 产品FAQ")
        print("  3. pricing_rules - 价格规则")
        print("  4. case_studies - 案例库")
        print("  5. knowledge_faqs - 通用知识库FAQ")
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        raise

if __name__ == "__main__":
    create_knowledge_tables()
