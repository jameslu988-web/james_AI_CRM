"""手动测试PATCH端点"""
import requests

def test_patch_endpoint():
    """直接调用PATCH端点测试"""
    
    # 获取token（需要先登录）
    login_url = "http://127.0.0.1:8001/api/auth/login"
    login_data = {
        "username": "admin",  # 替换为你的用户名
        "password": "admin123"  # 替换为你的密码
    }
    
    print("🔐 正在登录...")
    response = requests.post(login_url, data=login_data)
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        return
    
    token = response.json().get("access_token")
    print(f"✅ 登录成功，Token: {token[:20]}...")
    
    # 测试PATCH端点
    email_id = 1196  # 使用ID 1196测试
    patch_url = f"http://127.0.0.1:8001/api/email_history/{email_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {"opened": True}
    
    print(f"\n🔄 正在PATCH邮件 ID={email_id}...")
    print(f"   URL: {patch_url}")
    print(f"   Data: {data}")
    
    response = requests.patch(patch_url, json=data, headers=headers)
    
    print(f"\n📊 响应状态: {response.status_code}")
    print(f"📄 响应内容:")
    print(response.json())
    
    # 验证数据库
    from src.crm.database import get_session, EmailHistory
    db = get_session()
    try:
        email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
        if email:
            print(f"\n✅ 数据库验证:")
            print(f"   邮件ID: {email.id}")
            print(f"   主题: {email.subject}")
            print(f"   opened状态: {email.opened}")
        else:
            print(f"\n❌ 未找到邮件 ID={email_id}")
    finally:
        db.close()

if __name__ == "__main__":
    test_patch_endpoint()
