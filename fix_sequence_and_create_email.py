"""
修复数据库序列并创建测试邮件
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.crm.database import get_session, get_engine, EmailHistory
from src.tasks.ai_tasks import analyze_email_task
from datetime import datetime
from sqlalchemy import text

def fix_sequence_and_create_email():
    """修复序列并创建测试邮件"""
    engine = get_engine()
    db = get_session()
    
    try:
        # 修复序列
        print("🔧 修复数据库序列...")
        with engine.connect() as conn:
            # 查询当前最大ID
            result = conn.execute(text("SELECT MAX(id) FROM email_history"))
            max_id = result.scalar() or 0
            print(f"   当前最大ID: {max_id}")
            
            # 设置序列到最大ID+1
            conn.execute(text(f"SELECT setval('email_history_id_seq', {max_id + 1}, false)"))
            conn.commit()
            print(f"   序列已设置为: {max_id + 1}")
        
        # 创建测试邮件
        print("\n📧 创建测试邮件...")
        test_email = EmailHistory(
            customer_id=None,
            direction='inbound',
            subject='Urgent Inquiry - 5000pcs Men\'s Boxer Briefs for Christmas Order',
            body="""Dear Supplier,

I hope this email finds you well. I'm the purchasing manager at ABC Trading Company based in Los Angeles, USA.

We are urgently looking for a reliable supplier for Men's Boxer Briefs for our upcoming Christmas season. After reviewing your product catalog, we are very interested in your cotton boxer briefs.

Here are our requirements:
- Product: Men's Cotton Boxer Briefs
- Quantity: 5,000 pieces (initial order)
- Sizes: S, M, L, XL (25% each size)
- Colors: Black, Navy Blue, Grey (mixed)
- Material: 95% Cotton, 5% Spandex
- Quality: Premium quality with reinforced stitching

We need the following information URGENTLY:
1. Your best FOB price per piece (we have received quotes from 2 other suppliers)
2. Production lead time
3. Product samples (we can pay for samples and shipping)
4. MOQ for customization (we may need our logo printed)
5. Payment terms
6. Certifications (OEKO-TEX, ISO if available)

Timeline:
- We need to receive samples by next week
- Production must be completed by mid-November
- Delivery to Los Angeles port before December 1st

Our company has been in the clothing retail business for 15 years with annual revenue of $50M. We are looking for long-term partnership. If this trial order goes well, we expect to place quarterly orders of 10,000-20,000 pieces.

Could you please send me your detailed quotation and product catalog by tomorrow? This is very urgent as we need to make a decision by Friday.

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
            sent_at=datetime.now(),
            status='sent',
            priority='normal'
        )
        
        db.add(test_email)
        db.commit()
        db.refresh(test_email)
        
        print(f"✅ 测试邮件创建成功！ID: {test_email.id}")
        print(f"   主题: {test_email.subject}")
        print(f"   发件人: {test_email.from_email}")
        
        # 触发AI分析
        print(f"\n🤖 触发AI分析任务...")
        task = analyze_email_task.delay(test_email.id)
        print(f"   任务ID: {task.id}")
        print(f"   任务状态: {task.status}")
        
        # 等待任务完成
        print("\n⏳ 等待AI分析完成（最多30秒）...")
        try:
            result = task.get(timeout=30)
            print(f"\n✅ AI分析完成！")
            print(f"   结果: {result}")
            
            # 刷新邮件数据
            db.refresh(test_email)
            print(f"\n📊 AI分析结果：")
            print(f"   - 情感: {test_email.ai_sentiment}")
            print(f"   - 类别: {test_email.ai_category}")
            print(f"   - 紧急度: {test_email.urgency_level}")
            print(f"   - 购买意向: {test_email.purchase_intent}")
            print(f"   - 摘要: {test_email.ai_summary}")
            
            print(f"\n🎉 测试完成！请刷新前端页面查看效果！")
            
        except Exception as e:
            print(f"❌ AI分析任务失败: {str(e)}")
            print(f"   邮件已创建，ID: {test_email.id}")
            print(f"   您可以在前端手动触发AI分析")
        
        return test_email.id
        
    except Exception as e:
        print(f"❌ 操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == '__main__':
    print("=" * 70)
    print("🧪 修复序列并创建测试邮件")
    print("=" * 70)
    email_id = fix_sequence_and_create_email()
    if email_id:
        print(f"\n✅ 成功！邮件ID: {email_id}")
    else:
        print("\n❌ 失败！")
