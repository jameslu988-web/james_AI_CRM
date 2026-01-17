"""
创建测试邮件并触发AI分析
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.crm.database import get_session, EmailHistory
from src.tasks.ai_tasks import analyze_email_task
from datetime import datetime

def create_test_email():
    """创建一封测试邮件"""
    db = get_session()
    
    try:
        # 创建一封外贸询价邮件（高购买意向）- 不指定ID让数据库自动生成
        test_email = EmailHistory(
            customer_id=None,
            direction='inbound',
            subject='Urgent Inquiry - 5000pcs Men\'s Boxer Briefs for Christmas Order',
            body="""Dear Supplier,

I hope this email finds you well. I'm the purchasing manager at ABC Trading Company based in Los Angeles, USA.

We are urgently looking for a reliable supplier for Men's Boxer Briefs for our upcoming Christmas season. After reviewing your product catalog, we are very interested in your cotton boxer briefs.

Here are our requirements:
- Product: Men's Cotton Boxer Briefs
- Quantity: 5,000 pieces for initial order (potential for 20,000+ pcs annually)
- Material: 95% Cotton + 5% Spandex
- Sizes: M, L, XL, XXL (ratio 1:2:2:1)
- Colors: Black, Navy Blue, Grey (1:1:1)
- Customization: Our logo printed on waistband
- Packaging: Individual OPP bag + color box

**Urgent Questions:**
1. What's your best FOB price for 5,000pcs?
2. Can you provide free samples? (We'll pay shipping)
3. Production lead time after order confirmation?
4. Do you have OEKO-TEX certification?
5. Payment terms? (We prefer 30% deposit, 70% before shipment)

**Timeline:**
We need to place the order by October 15th to meet our Christmas season launch on December 1st. This is very urgent!

We're comparing 3 suppliers and will make a decision by next Monday. If your price is competitive and quality is good, we can establish a long-term partnership with monthly orders.

Please send your quotation and product samples ASAP.

Looking forward to your prompt response.

Best regards,
John Smith
Purchasing Manager
ABC Trading Company
Tel: +1-310-555-1234
Email: john.smith@abctrading.com
www.abctrading.com""",
            from_email='john.smith@abctrading.com',
            to_email='sales@yourcompany.com',
            sent_at=datetime.utcnow(),
            status='sent',
            opened=False,
            replied=False
        )
        
        db.add(test_email)
        db.commit()
        db.refresh(test_email)
        
        print(f"✅ 测试邮件创建成功！")
        print(f"   邮件ID: {test_email.id}")
        print(f"   主题: {test_email.subject}")
        print(f"   发件人: {test_email.from_email}")
        
        return test_email.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建邮件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


def trigger_ai_analysis(email_id: int):
    """触发AI分析任务"""
    print(f"\n🤖 提交AI分析任务...")
    
    # 使用Celery异步任务
    result = analyze_email_task.delay(email_id)
    
    print(f"✅ AI分析任务已提交")
    print(f"   Task ID: {result.id}")
    print(f"   状态: {result.state}")
    
    # 等待任务完成
    print(f"\n⏳ 等待AI分析完成（最多30秒）...")
    
    import time
    for i in range(30):
        time.sleep(1)
        status = result.state
        print(f"   [{i+1}s] 状态: {status}", end='\r')
        
        if status in ['SUCCESS', 'FAILURE']:
            print()
            break
    
    # 显示结果
    if result.successful():
        data = result.result
        print(f"\n✅ AI分析完成！")
        print(f"\n📊 分析结果：")
        
        if data.get('analysis'):
            analysis = data['analysis']
            print(f"   ✓ 业务阶段: {analysis.get('business_stage', 'N/A')}")
            print(f"   ✓ 情感: {analysis.get('sentiment', 'N/A')}")
            print(f"   ✓ 类别: {analysis.get('category', 'N/A')}")
            print(f"   ✓ 紧急度: {analysis.get('urgency_level', 'N/A')}")
            print(f"   ✓ 购买意向: {analysis.get('purchase_intent', 'N/A')} (评分: {analysis.get('purchase_intent_score', 0)})")
            print(f"   ✓ 客户分级: {analysis.get('customer_grade_suggestion', 'N/A')}")
            print(f"   ✓ 决策权限: {analysis.get('decision_authority', 'N/A')}")
            print(f"   ✓ 竞争状态: {analysis.get('competition_status', 'N/A')}")
            print(f"   ✓ 响应期限: {analysis.get('response_deadline', 'N/A')}")
            print(f"   ✓ 机会评分: {analysis.get('opportunity_score', 0)}/100")
            print(f"   ✓ 转化概率: {analysis.get('conversion_probability', 0)}%")
            print(f"   ✓ AI摘要: {analysis.get('summary', 'N/A')}")
            
            if analysis.get('requires_human_review'):
                print(f"   ⚠️  需要人工审核: {analysis.get('human_review_reason', '重要邮件')}")
        
        return True
    else:
        print(f"\n❌ AI分析失败: {result.state}")
        if hasattr(result, 'info'):
            print(f"   错误: {result.info}")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("🧪 创建测试邮件并触发AI分析")
    print("=" * 70)
    print()
    
    # 检查环境变量
    import os
    os.environ['DB_TYPE'] = 'postgresql'
    os.environ['DB_PASSWORD'] = 'postgres123'
    
    # 创建测试邮件
    email_id = create_test_email()
    
    if email_id:
        # 触发AI分析
        success = trigger_ai_analysis(email_id)
        
        if success:
            print("\n" + "=" * 70)
            print("🎉 测试完成！")
            print("=" * 70)
            print()
            print("现在请：")
            print("1. 刷新前端邮件列表页面")
            print("2. 查看新创建的邮件（主题: Urgent Inquiry - 5000pcs Men's Boxer Briefs...）")
            print("3. 您将看到邮件下方显示AI分析的彩色徽章：")
            print("   - 业务阶段（紫色）")
            print("   - 情感态度（带表情图标）")
            print("   - 购买意向（绿色 high + 评分）")
            print("   - 紧急度（红色 high）")
            print("   - 客户分级（A级/B级）")
            print("   - 机会评分")
            print("   - 人工审核标记（如需要）")
            print()
            return 0
        else:
            print("\n❌ AI分析失败，请检查Celery Worker是否正在运行")
            return 1
    else:
        print("\n❌ 创建测试邮件失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
