"""
发送带有正确IP地址的企业微信通知
"""
import requests
from datetime import datetime

# 使用实际IP地址
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0e1c48f0-196e-4f7c-954d-c273e9309bf5"
TASK_ID = 17
API_HOST = "192.168.1.110"  # 你的电脑IP地址

# 生成审核链接
approval_url = f"http://{API_HOST}:5173/mobile-approval.html?id={TASK_ID}&api_host={API_HOST}"

print(f"📱 审核链接: {approval_url}")
print(f"\n发送企业微信通知...")

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
<font color="comment">审核任务ID: {TASK_ID} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>"""
    }
}

try:
    response = requests.post(WEBHOOK_URL, json=content, timeout=10)
    result = response.json()
    
    if result.get('errcode') == 0:
        print("✅ 企业微信通知发送成功！")
        print(f"\n📱 请在手机上点击链接，应该能正常打开了")
        print(f"\n💡 链接说明：")
        print(f"   - 使用了你的电脑IP: {API_HOST}")
        print(f"   - 确保手机和电脑在同一个WiFi网络")
        print(f"   - 确保前端服务在运行 (端口5173)")
        print(f"   - 确保后端服务在运行 (端口8001)")
    else:
        print(f"❌ 发送失败: {result.get('errmsg')}")
        
except Exception as e:
    print(f"❌ 发送失败: {e}")
