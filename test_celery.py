"""
Celery 异步任务测试脚本
测试 Redis + Celery 的完整功能
"""

from src.celery_config import celery_app
from src.tasks.email_tasks import sync_emails_task, send_email_task
from src.tasks.ai_tasks import analyze_email_task, generate_reply_task
from celery.result import AsyncResult
import time
import sys

def test_celery_connection():
    """测试 Celery 与 Redis 连接"""
    print("\n" + "="*60)
    print("🔗 测试1：Celery + Redis 连接")
    print("="*60)
    
    try:
        # 检查 Celery 配置
        print(f"📦 Broker: {celery_app.conf.broker_url}")
        print(f"📊 Backend: {celery_app.conf.result_backend}")
        
        # Ping Redis
        inspector = celery_app.control.inspect()
        active_workers = inspector.active()
        
        if active_workers:
            print(f"✅ 发现 {len(active_workers)} 个活跃的 Worker")
            for worker_name in active_workers.keys():
                print(f"   - {worker_name}")
        else:
            print("❌ 未发现活跃的 Worker（请确保 start_celery.ps1 已运行）")
            return False
        
        print("✅ Redis 连接正常")
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False


def test_registered_tasks():
    """测试已注册的任务"""
    print("\n" + "="*60)
    print("📋 测试2：已注册的任务")
    print("="*60)
    
    try:
        inspector = celery_app.control.inspect()
        registered = inspector.registered()
        
        if registered:
            for worker_name, tasks in registered.items():
                print(f"\n🔧 Worker: {worker_name}")
                for task in tasks:
                    print(f"   ✅ {task}")
            return True
        else:
            print("❌ 未找到已注册的任务")
            return False
            
    except Exception as e:
        print(f"❌ 获取任务列表失败: {str(e)}")
        return False


def test_simple_task():
    """测试简单的异步任务"""
    print("\n" + "="*60)
    print("🚀 测试3：发送简单异步任务")
    print("="*60)
    
    try:
        # 发送一个简单的邮件发送任务
        print("📤 发送任务: send_email_task")
        
        email_data = {
            "subject": "测试邮件",
            "to": "test@example.com",
            "body": "这是一封测试邮件"
        }
        
        # 异步调用
        result = send_email_task.delay(email_data)
        print(f"✅ 任务已提交，Task ID: {result.id}")
        print(f"📊 任务状态: {result.state}")
        
        # 等待任务完成（最多10秒）
        print("⏳ 等待任务完成...")
        
        for i in range(10):
            time.sleep(1)
            status = result.state
            print(f"   [{i+1}s] 状态: {status}")
            
            if status in ['SUCCESS', 'FAILURE']:
                break
        
        if result.successful():
            print(f"✅ 任务执行成功！")
            print(f"📊 结果: {result.result}")
            return True
        elif result.failed():
            print(f"❌ 任务执行失败: {result.result}")
            return False
        else:
            print(f"⏸️ 任务仍在执行中，状态: {result.state}")
            return False
            
    except Exception as e:
        print(f"❌ 任务发送失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_task():
    """测试 AI 分析任务"""
    print("\n" + "="*60)
    print("🤖 测试4：AI 分析任务")
    print("="*60)
    
    try:
        # 假设邮件ID为1
        email_id = 1
        
        print(f"📤 发送任务: analyze_email_task (email_id={email_id})")
        result = analyze_email_task.delay(email_id)
        
        print(f"✅ 任务已提交，Task ID: {result.id}")
        print("⏳ 等待任务完成...")
        
        for i in range(10):
            time.sleep(1)
            status = result.state
            print(f"   [{i+1}s] 状态: {status}")
            
            if status in ['SUCCESS', 'FAILURE']:
                break
        
        if result.successful():
            print(f"✅ AI 分析任务完成！")
            print(f"📊 结果: {result.result}")
            return True
        else:
            print(f"❌ 任务状态: {result.state}")
            return False
            
    except Exception as e:
        print(f"❌ 任务失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_task_queue():
    """测试任务队列和并发"""
    print("\n" + "="*60)
    print("⚡ 测试5：并发任务队列")
    print("="*60)
    
    try:
        # 同时发送3个任务
        tasks = []
        
        for i in range(3):
            email_data = {"subject": f"测试邮件 #{i+1}"}
            result = send_email_task.delay(email_data)
            tasks.append(result)
            print(f"✅ 任务 #{i+1} 已提交: {result.id}")
        
        print("\n⏳ 等待所有任务完成...")
        
        for i in range(15):
            time.sleep(1)
            completed = sum(1 for t in tasks if t.ready())
            print(f"   [{i+1}s] 已完成: {completed}/{len(tasks)}")
            
            if completed == len(tasks):
                break
        
        # 检查结果
        success_count = 0
        for idx, task in enumerate(tasks):
            if task.successful():
                success_count += 1
                print(f"✅ 任务 #{idx+1}: 成功")
            else:
                print(f"❌ 任务 #{idx+1}: {task.state}")
        
        print(f"\n📊 总结: {success_count}/{len(tasks)} 个任务成功")
        return success_count == len(tasks)
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 Celery 异步任务系统测试")
    print("="*60)
    print("\n⚠️  请确保以下服务已启动：")
    print("   1. Redis 服务（端口 6379）")
    print("   2. Celery Worker（运行 start_celery.ps1）")
    print("   3. PostgreSQL 数据库")
    print("\n按 Enter 继续测试...")
    input()
    
    results = []
    
    # 运行所有测试
    results.append(("连接测试", test_celery_connection()))
    
    if results[-1][1]:  # 如果连接成功
        results.append(("任务注册测试", test_registered_tasks()))
        results.append(("简单任务测试", test_simple_task()))
        results.append(("AI任务测试", test_ai_task()))
        results.append(("并发队列测试", test_task_queue()))
    
    # 输出总结
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
        print("\n🎉 恭喜！所有测试通过，Celery 异步任务系统运行正常！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置和日志")
        return 1


if __name__ == "__main__":
    sys.exit(main())
