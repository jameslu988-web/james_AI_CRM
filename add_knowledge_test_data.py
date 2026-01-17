"""
添加知识库测试数据
"""
import os
import json
from src.crm.database import get_session, Product, KnowledgeFAQ, PricingRule, CaseStudy

# 设置环境变量为 PostgreSQL
os.environ['DB_TYPE'] = 'postgresql'
os.environ['DB_PASSWORD'] = 'postgres123'


def add_sample_products():
    """添加示例产品"""
    db = get_session()
    
    try:
        products = [
            {
                "sku": "MU-BX-001",
                "name_en": "Men's Classic Boxer Brief",
                "name_zh": "男士经典平角内裤",
                "category": "平角内裤",
                "description_en": "Comfortable cotton boxer brief with elastic waistband",
                "description_zh": "舒适棉质平角内裤,弹力腰带",
                "features": json.dumps(["高弹性", "透气舒适", "抗菌防臭", "吸湿排汗"]),
                "sizes": json.dumps(["S", "M", "L", "XL", "XXL", "XXXL"]),
                "colors": json.dumps(["黑色", "白色", "灰色", "藏青"]),
                "materials": json.dumps([
                    {"name": "精梳棉", "composition": "95%棉+5%氨纶", "price_multiplier": 1.0},
                    {"name": "莫代尔", "composition": "95%莫代尔+5%氨纶", "price_multiplier": 1.3},
                    {"name": "竹纤维", "composition": "95%竹纤维+5%氨纶", "price_multiplier": 1.5}
                ]),
                "weight": 80.0,
                "base_price": 2.50,
                "moq": 1000,
                "lead_time_days": 30,
                "sample_lead_time": 7,
                "certifications": json.dumps(["OEKO-TEX", "ISO9001"]),
                "is_active": True
            },
            {
                "sku": "MU-TR-001",
                "name_en": "Men's Sport Brief",
                "name_zh": "男士运动三角内裤",
                "category": "三角内裤",
                "description_en": "Breathable sport brief for active lifestyle",
                "description_zh": "透气运动三角内裤,适合运动场景",
                "features": json.dumps(["超强弹性", "快干透气", "无痕设计"]),
                "sizes": json.dumps(["M", "L", "XL", "XXL"]),
                "colors": json.dumps(["黑色", "蓝色", "灰色"]),
                "materials": json.dumps([
                    {"name": "精梳棉", "composition": "92%棉+8%氨纶", "price_multiplier": 1.0}
                ]),
                "weight": 60.0,
                "base_price": 1.80,
                "moq": 1500,
                "lead_time_days": 25,
                "sample_lead_time": 5,
                "is_active": True
            }
        ]
        
        for p_data in products:
            existing = db.query(Product).filter(Product.sku == p_data['sku']).first()
            if not existing:
                product = Product(**p_data)
                db.add(product)
                print(f"✅ 添加产品: {p_data['name_zh']} ({p_data['sku']})")
            else:
                print(f"⏭️ 产品已存在: {p_data['sku']}")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"❌ 添加产品失败: {str(e)}")
    finally:
        db.close()


def add_sample_faqs():
    """添加示例FAQ"""
    db = get_session()
    
    try:
        faqs = [
            {
                "category": "产品相关",
                "question_en": "What materials do you use?",
                "answer_en": "We offer high-quality materials including combed cotton (95% cotton + 5% spandex), modal, and bamboo fiber. All materials are OEKO-TEX certified.",
                "question_zh": "你们使用什么材质?",
                "answer_zh": "我们提供优质材料包括精梳棉(95%棉+5%氨纶)、莫代尔和竹纤维。所有材料均通过OEKO-TEX认证。",
                "keywords": json.dumps(["material", "cotton", "质量", "材质"]),
                "priority": 10,
                "is_active": True
            },
            {
                "category": "价格与报价",
                "question_en": "What's your MOQ?",
                "answer_en": "Our MOQ is 1000 pieces per style per color. For boxer briefs, MOQ is 1000pcs. For briefs, MOQ is 1500pcs.",
                "question_zh": "你们的最小起订量是多少?",
                "answer_zh": "我们的MOQ是每款每色1000件。平角内裤MOQ为1000件,三角内裤MOQ为1500件。",
                "keywords": json.dumps(["MOQ", "minimum order", "起订量"]),
                "priority": 10,
                "is_active": True
            },
            {
                "category": "样品相关",
                "question_en": "Can you provide samples?",
                "answer_en": "Yes, we can provide samples. Sample price is $15 per piece with 7 days delivery. Sample fee will be refunded when you place bulk order.",
                "question_zh": "你们能提供样品吗?",
                "answer_zh": "可以的,我们可以提供样品。样品价格为每件15美元,7天交付。下批量订单时样品费可退。",
                "keywords": json.dumps(["sample", "样品", "寄样"]),
                "priority": 9,
                "is_active": True
            },
            {
                "category": "定制服务",
                "question_en": "Do you support customization?",
                "answer_en": "Yes, we support printing, embroidery, and jacquard customization. Printing MOQ is 500pcs (+$0.5/pc), embroidery MOQ is 1000pcs (+$0.8/pc).",
                "question_zh": "你们支持定制吗?",
                "answer_zh": "是的,我们支持印花、刺绣和提花定制。印花MOQ为500件(+$0.5/件),刺绣MOQ为1000件(+$0.8/件)。",
                "keywords": json.dumps(["customization", "printing", "定制", "印花"]),
                "priority": 8,
                "is_active": True
            }
        ]
        
        for faq_data in faqs:
            existing = db.query(KnowledgeFAQ).filter(
                KnowledgeFAQ.question_en == faq_data['question_en']
            ).first()
            
            if not existing:
                faq = KnowledgeFAQ(**faq_data)
                db.add(faq)
                print(f"✅ 添加FAQ: {faq_data['question_zh']}")
            else:
                print(f"⏭️ FAQ已存在: {faq_data['question_en']}")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"❌ 添加FAQ失败: {str(e)}")
    finally:
        db.close()


def add_sample_pricing_rules():
    """添加示例价格规则"""
    db = get_session()
    
    try:
        rules = [
            {
                "rule_name": "数量折扣 - 阶梯1",
                "rule_type": "quantity_discount",
                "description": "1000-5000件的数量折扣",
                "config": json.dumps({
                    "tiers": [{"min_qty": 1000, "max_qty": 5000, "discount": 0}]
                }),
                "priority": 5,
                "is_active": True
            },
            {
                "rule_name": "数量折扣 - 阶梯2",
                "rule_type": "quantity_discount",
                "description": "5001-10000件享受10%折扣",
                "config": json.dumps({
                    "tiers": [{"min_qty": 5001, "max_qty": 10000, "discount": 0.10}]
                }),
                "priority": 5,
                "is_active": True
            },
            {
                "rule_name": "数量折扣 - 阶梯3",
                "rule_type": "quantity_discount",
                "description": "10001件以上享受15%折扣",
                "config": json.dumps({
                    "tiers": [{"min_qty": 10001, "discount": 0.15}]
                }),
                "priority": 5,
                "is_active": True
            }
        ]
        
        for rule_data in rules:
            existing = db.query(PricingRule).filter(
                PricingRule.rule_name == rule_data['rule_name']
            ).first()
            
            if not existing:
                rule = PricingRule(**rule_data)
                db.add(rule)
                print(f"✅ 添加价格规则: {rule_data['rule_name']}")
            else:
                print(f"⏭️ 价格规则已存在: {rule_data['rule_name']}")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"❌ 添加价格规则失败: {str(e)}")
    finally:
        db.close()


def add_sample_case_studies():
    """添加示例案例"""
    db = get_session()
    
    try:
        cases = [
            {
                "title_en": "50,000 pcs Boxer Brief Order from US Client",
                "title_zh": "美国客户5万件平角内裤定制案例",
                "customer_type": "批发商",
                "customer_region": "北美",
                "challenge_en": "Client required fast delivery (20 days) with 4-color printing, MOQ was a concern",
                "challenge_zh": "客户要求快速交货(20天内),且需要4色印花定制,MOQ限制较大",
                "solution_en": "1) Prioritized production schedule 2) Pre-stocked cotton fabric 3) Used digital printing to bypass MOQ 4) Arranged overtime production",
                "solution_zh": "1) 协调工厂优先排产 2) 提前备料精梳棉面料 3) 印花工艺改为数码印花,突破MOQ限制 4) 安排加班生产",
                "result_en": "Successfully completed and shipped in 18 days. Client was very satisfied and placed 2 more orders.",
                "result_zh": "成功在18天内完成生产并发货,客户非常满意,后续追加了2个订单",
                "order_quantity": 50000,
                "order_value": 112500.00,
                "products_involved": json.dumps(["MU-BX-001"]),
                "highlights": json.dumps(["快速响应", "灵活定制", "优质交付"]),
                "tags": json.dumps(["大客户", "重复订单", "美国市场"]),
                "is_active": True
            }
        ]
        
        for case_data in cases:
            existing = db.query(CaseStudy).filter(
                CaseStudy.title_en == case_data['title_en']
            ).first()
            
            if not existing:
                case = CaseStudy(**case_data)
                db.add(case)
                print(f"✅ 添加案例: {case_data['title_zh']}")
            else:
                print(f"⏭️ 案例已存在: {case_data['title_en']}")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"❌ 添加案例失败: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    print("📦 开始添加知识库测试数据...\n")
    
    print("1️⃣ 添加产品...")
    add_sample_products()
    
    print("\n2️⃣ 添加FAQ...")
    add_sample_faqs()
    
    print("\n3️⃣ 添加价格规则...")
    add_sample_pricing_rules()
    
    print("\n4️⃣ 添加案例...")
    add_sample_case_studies()
    
    print("\n✅ 测试数据添加完成!")
    print("\n📊 统计:")
    
    db = get_session()
    try:
        print(f"  产品数量: {db.query(Product).count()}")
        print(f"  FAQ数量: {db.query(KnowledgeFAQ).count()}")
        print(f"  价格规则数量: {db.query(PricingRule).count()}")
        print(f"  案例数量: {db.query(CaseStudy).count()}")
    finally:
        db.close()
