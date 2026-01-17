"""
测试前端知识库集成的后端API
"""
import asyncio
import requests

async def test_generate_reply_api():
    """测试生成回复API"""
    
    # 模拟客户询盘
    test_email = {
        "subject": "Inquiry about Men's Underwear MOQ",
        "body": "Hi, I'm interested in your men's underwear products. What is the MOQ for basic series? And what's your best price?",
        "use_knowledge_base": True,  # 启用知识库
        "tone": "professional"
    }
    
    print("="*80)
    print("测试：生成AI回复（启用知识库）")
    print("="*80)
    print(f"📧 客户邮件主题: {test_email['subject']}")
    print(f"📧 客户邮件内容: {test_email['body']}")
    print(f"📚 知识库状态: {'已启用' if test_email['use_knowledge_base'] else '已禁用'}")
    print()
    
    # 调用API
    url = "http://127.0.0.1:8001/api/ai/generate-reply"
    
    try:
        response = requests.post(url, json=test_email)
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*80)
            print("✅ API调用成功")
            print("="*80)
            
            print(f"\n🔖 是否成功: {result.get('success')}")
            print(f"🔖 是否使用知识库: {result.get('knowledge_used')}")
            print(f"🔖 模型: {result.get('model')}")
            
            if result.get('knowledge_context'):
                print(f"\n📚 引用的知识片段数量: {len(result['knowledge_context'])}")
                for idx, knowledge in enumerate(result['knowledge_context'], 1):
                    print(f"\n  知识片段 {idx}:")
                    print(f"    - 文档: {knowledge.get('document_title', 'N/A')}")
                    print(f"    - 相似度: {knowledge.get('similarity', 0):.2f}")
                    print(f"    - 内容预览: {knowledge.get('content', '')[:100]}...")
            
            print(f"\n📝 生成的回复:\n")
            print("-"*80)
            print(result.get('reply', ''))
            print("-"*80)
            
            # 测试禁用知识库的情况
            print("\n\n" + "="*80)
            print("测试：生成AI回复（禁用知识库）")
            print("="*80)
            
            test_email['use_knowledge_base'] = False
            response2 = requests.post(url, json=test_email)
            
            if response2.status_code == 200:
                result2 = response2.json()
                print(f"\n🔖 是否使用知识库: {result2.get('knowledge_used')}")
                print(f"\n📝 生成的回复（无知识库）:\n")
                print("-"*80)
                print(result2.get('reply', '')[:500] + "...")
                print("-"*80)
                
                # 对比分析
                print("\n\n" + "="*80)
                print("📊 对比分析")
                print("="*80)
                print(f"启用知识库回复长度: {len(result.get('reply', ''))} 字符")
                print(f"禁用知识库回复长度: {len(result2.get('reply', ''))} 字符")
                print(f"差异: {len(result.get('reply', '')) - len(result2.get('reply', ''))} 字符")
                
        else:
            error = response.json()
            print(f"\n❌ API调用失败")
            print(f"错误信息: {error.get('detail', '未知错误')}")
            
    except Exception as e:
        print(f"\n❌ 请求异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║          前端知识库集成 - 后端API测试                                ║
║                                                                      ║
║  测试目标：                                                          ║
║  1. 验证 /api/ai/generate-reply 端点是否正常工作                     ║
║  2. 确认知识库参数是否正确传递和使用                                 ║
║  3. 验证返回的knowledge_context是否包含正确信息                      ║
║  4. 对比启用/禁用知识库的回复差异                                    ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(test_generate_reply_api())
    
    print("\n" + "="*80)
    print("✅ 测试完成！")
    print("="*80)
