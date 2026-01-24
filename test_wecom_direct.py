"""
直接测试企业微信webhook - 排查问题
"""
import requests
import json
from datetime import datetime

# 直接使用webhook地址
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0e1c48f0-196e-4f7c-954d-c273e9309bf5"

def test_simple_text():
    """测试1: 发送简单文本消息"""
    print("\n" + "="*60)
    print("测试1: 发送简单文本消息")
    print("="*60)
    
    content = {
        "msgtype": "text",
        "text": {
            "content": f"🔔 测试消息\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n这是一条测试消息，如果能看到这条消息，说明webhook配置正确！"
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=content, timeout=10)
        result = response.json()
        
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('errcode') == 0:
            print("✅ 消息发送成功！请在企业微信群中查看")
            return True
        else:
            print(f"❌ 发送失败: {result.get('errmsg')}")
            print(f"   错误码: {result.get('errcode')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_markdown():
    """测试2: 发送Markdown格式消息"""
    print("\n" + "="*60)
    print("测试2: 发送Markdown格式消息")
    print("="*60)
    
    content = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"""## 🔔 审核任务测试

> **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **消息类型**: Markdown格式

### 测试内容
- 这是**加粗文本**
- 这是<font color="warning">橙色警告</font>
- 这是<font color="info">蓝色信息</font>

[点击查看详情](http://localhost:5173)"""
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=content, timeout=10)
        result = response.json()
        
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('errcode') == 0:
            print("✅ Markdown消息发送成功！")
            return True
        else:
            print(f"❌ 发送失败: {result.get('errmsg')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_approval_notification():
    """测试3: 发送审核通知（实际格式）"""
    print("\n" + "="*60)
    print("测试3: 发送审核任务通知")
    print("="*60)
    
    task_id = 15
    approval_url = f"http://localhost:5173/mobile-approval.html?id={task_id}"
    
    content = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"""## 🟡 新的邮件审核任务

> **邮件类型**: <font color="info">新客询盘</font>
> **发件人**: John Test <test.buyer@example.com>
> **原邮件主题**: Inquiry about Men's Underwear - Bulk Order
> **AI回复主题**: Re: Inquiry about Men's Underwear - Bulk Order
> **紧急程度**: 🟡 MEDIUM

请及时处理：[点击查看并审核]({approval_url})

---
<font color="comment">审核任务ID: {task_id} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>"""
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=content, timeout=10)
        result = response.json()
        
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('errcode') == 0:
            print("✅ 审核通知发送成功！")
            print(f"\n📱 移动端审核链接: {approval_url}")
            return True
        else:
            print(f"❌ 发送失败: {result.get('errmsg')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def check_webhook_config():
    """检查webhook配置"""
    print("\n" + "="*60)
    print("检查Webhook配置")
    print("="*60)
    print(f"Webhook URL: {WEBHOOK_URL[:80]}...")
    print(f"URL长度: {len(WEBHOOK_URL)} 字符")
    
    # 检查URL格式
    if not WEBHOOK_URL.startswith("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="):
        print("⚠️ Webhook URL格式可能不正确")
        return False
    
    # 提取key
    key = WEBHOOK_URL.split("key=")[-1]
    print(f"机器人Key: {key}")
    print(f"Key长度: {len(key)} 字符")
    
    if len(key) < 30:
        print("⚠️ Key长度异常，可能不完整")
        return False
    
    print("✅ Webhook配置格式正确")
    return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  企业微信群机器人Webhook测试工具")
    print("="*70)
    
    # 检查配置
    if not check_webhook_config():
        print("\n❌ Webhook配置有问题，请检查")
        exit(1)
    
    # 运行测试
    print("\n开始测试...")
    
    test1_result = test_simple_text()
    test2_result = test_markdown()
    test3_result = test_approval_notification()
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    print(f"简单文本消息: {'✅ 成功' if test1_result else '❌ 失败'}")
    print(f"Markdown消息: {'✅ 成功' if test2_result else '❌ 失败'}")
    print(f"审核通知: {'✅ 成功' if test3_result else '❌ 失败'}")
    
    if all([test1_result, test2_result, test3_result]):
        print("\n🎉 所有测试通过！请在企业微信群中查看3条消息")
    else:
        print("\n⚠️ 部分测试失败，请检查：")
        print("   1. Webhook URL是否正确")
        print("   2. 机器人是否已添加到群聊")
        print("   3. 机器人是否被管理员禁用")
        print("   4. 网络连接是否正常")
    
    print("\n" + "="*70)
    print("💡 排查建议:")
    print("="*70)
    print("1. 确认机器人已添加到企业微信群")
    print("2. 在企业微信PC端：群聊 → 右键 → 添加群机器人 → 查看已有机器人")
    print("3. 检查机器人是否被禁用")
    print("4. 重新获取Webhook地址（如果key过期）")
    print("5. 确认群聊类型正确（内部群/外部群）")
    print("="*70 + "\n")
