"""
测试 AI 邮件分析功能
"""

from src.tasks.ai_tasks import analyze_email_task, generate_reply_task
import time

def test_ai_analysis():
    """测试 AI 邮件分析"""
    print("\n" + "="*60)
    print("🤖 测试 AI 邮件分析功能")
    print("="*60)
    
    # 使用数据库中的真实邮件（ID=1）
    email_id = 1
    
    print(f"\n📤 提交 AI 分析任务 (email_id={email_id})...")
    result = analyze_email_task.delay(email_id)
    
    print(f"✅ 任务已提交: {result.id}")
    print(f"📊 初始状态: {result.state}")
    
    # 等待任务完成
    print("\n⏳ 等待 AI 分析完成...")
    
    for i in range(30):  # 最多等待30秒
        time.sleep(1)
        status = result.state
        print(f"   [{i+1}s] 状态: {status}", end="\r")
        
        if status in ['SUCCESS', 'FAILURE']:
            print()  # 换行
            break
    
    # 显示结果
    print("\n" + "="*60)
    if result.successful():
        data = result.result
        print("✅ AI 分析成功！")
        print("\n📊 分析结果：")
        
        if data.get('analysis'):
            analysis = data['analysis']
            print(f"   情感: {analysis.get('sentiment', 'N/A')}")
            print(f"   类别: {analysis.get('category', 'N/A')}")
            print(f"   紧急度: {analysis.get('urgency_level', 'N/A')}")
            print(f"   购买意向: {analysis.get('purchase_intent', 'N/A')}")
            print(f"   摘要: {analysis.get('summary', 'N/A')}")
            
            if analysis.get('key_points'):
                print(f"\n   关键点:")
                for point in analysis['key_points']:
                    print(f"      - {point}")
            
            if analysis.get('suggested_tags'):
                print(f"\n   建议标签: {', '.join(analysis['suggested_tags'])}")
            
            if analysis.get('next_action'):
                print(f"\n   下一步: {analysis['next_action']}")
        else:
            print(f"   结果: {data}")
    else:
        print(f"❌ AI 分析失败: {result.state}")
        if hasattr(result, 'info'):
            print(f"   错误: {result.info}")
    
    print("="*60)
    return result.successful()


def test_ai_reply():
    """测试 AI 回复生成"""
    print("\n" + "="*60)
    print("🤖 测试 AI 回复生成功能")
    print("="*60)
    
    email_id = 1
    
    print(f"\n📤 提交 AI 回复生成任务 (email_id={email_id})...")
    result = generate_reply_task.delay(email_id, tone="professional")
    
    print(f"✅ 任务已提交: {result.id}")
    
    # 等待任务完成
    print("\n⏳ 等待 AI 回复生成...")
    
    for i in range(30):
        time.sleep(1)
        status = result.state
        print(f"   [{i+1}s] 状态: {status}", end="\r")
        
        if status in ['SUCCESS', 'FAILURE']:
            print()
            break
    
    # 显示结果
    print("\n" + "="*60)
    if result.successful():
        data = result.result
        print("✅ AI 回复生成成功！")
        print("\n📧 生成的回复：")
        print("-" * 60)
        print(data.get('reply', 'N/A'))
        print("-" * 60)
    else:
        print(f"❌ AI 回复生成失败: {result.state}")
    
    print("="*60)
    return result.successful()


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🧪 AI 邮件分析系统测试")
    print("="*60)
    print("\n⚠️  请确保以下服务已启动：")
    print("   1. Redis 服务")
    print("   2. Celery Worker")
    print("   3. PostgreSQL 数据库")
    print("   4. aihubmix.com API 可访问")
    print("\n按 Enter 继续测试...")
    input()
    
    results = []
    
    # 测试 AI 分析
    results.append(("AI 邮件分析", test_ai_analysis()))
    
    # 测试 AI 回复生成
    results.append(("AI 回复生成", test_ai_reply()))
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n🎯 总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 恭喜！AI 邮件分析系统运行正常！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
