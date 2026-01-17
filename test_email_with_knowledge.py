"""
测试邮件回复的知识库集成功能
"""
import asyncio
from src.ai.email_analyzer import EmailAIAnalyzer

async def test_email_reply_with_knowledge():
    """测试使用知识库生成邮件回复"""
    
    analyzer = EmailAIAnalyzer()
    
    # 模拟一个客户询盘邮件
    test_cases = [
        {
            "name": "询问MOQ",
            "subject": "Inquiry about Men's Underwear",
            "body": "Hi, I'm interested in your men's underwear products. What is the MOQ for basic series? And what's your best price?"
        },
        {
            "name": "询问定制",
            "subject": "Custom Order Question",
            "body": "Hello, we want to customize men's boxer briefs with our logo. Can you tell me about the customization process and pricing?"
        },
        {
            "name": "询问交货期",
            "subject": "Lead Time Question",
            "body": "Hi, if we place an order for 5000 pieces, how long will it take to produce and ship?"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试案例 {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"📧 客户邮件主题: {test['subject']}")
        print(f"📧 客户邮件内容: {test['body']}")
        print(f"\n{'🔍 开始生成回复...':-^80}")
        
        # 测试1: 不使用知识库
        print(f"\n{'不使用知识库':=^80}")
        result_without_kb = await analyzer.generate_reply(
            subject=test['subject'],
            body=test['body'],
            use_knowledge_base=False
        )
        
        if result_without_kb['success']:
            print(f"✅ 生成成功")
            print(f"📝 回复内容:\n{result_without_kb['reply'][:500]}...")
        else:
            print(f"❌ 生成失败: {result_without_kb.get('error')}")
        
        # 测试2: 使用知识库
        print(f"\n{'使用知识库':=^80}")
        result_with_kb = await analyzer.generate_reply(
            subject=test['subject'],
            body=test['body'],
            use_knowledge_base=True
        )
        
        if result_with_kb['success']:
            print(f"✅ 生成成功")
            print(f"🔖 是否使用知识库: {result_with_kb['knowledge_used']}")
            print(f"📝 回复内容:\n{result_with_kb['reply'][:500]}...")
            
            # 比较差异
            if result_without_kb['success']:
                print(f"\n{'差异分析':=^80}")
                print(f"不使用知识库长度: {len(result_without_kb['reply'])} 字符")
                print(f"使用知识库长度: {len(result_with_kb['reply'])} 字符")
                
                # 检查知识库内容是否被引用
                if result_with_kb['knowledge_used']:
                    print("✅ 知识库内容已被使用")
                else:
                    print("⚠️ 知识库未检索到相关内容")
        else:
            print(f"❌ 生成失败: {result_with_kb.get('error')}")
        
        print(f"\n")
        
        # 避免频繁调用API
        if i < len(test_cases):
            print("⏳ 等待3秒...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           邮件回复知识库集成测试                                     ║
║                                                                      ║
║  测试目标：                                                          ║
║  1. 验证知识库检索功能是否正常                                       ║
║  2. 对比使用/不使用知识库的回复差异                                  ║
║  3. 确认知识库内容是否正确注入到AI提示词中                           ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(test_email_reply_with_knowledge())
    
    print(f"\n{'='*80}")
    print("✅ 测试完成！")
    print(f"{'='*80}\n")
