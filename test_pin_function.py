"""测试置顶功能"""
import requests
import json

def test_pin_feature():
    """测试置顶按钮功能"""
    
    # 1. 登录获取token
    print("🔐 正在登录...")
    login_response = requests.post(
        "http://127.0.0.1:8001/api/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json().get("access_token")
    print(f"✅ 登录成功")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 2. 获取邮件列表，找一封测试邮件
    print("\n📧 获取邮件列表...")
    list_response = requests.get(
        "http://127.0.0.1:8001/api/email_history?range=[0,4]",
        headers=headers
    )
    
    if list_response.status_code != 200:
        print(f"❌ 获取邮件列表失败: {list_response.status_code}")
        return
    
    emails = list_response.json()
    if not emails:
        print("❌ 没有找到邮件")
        return
    
    test_email = emails[0]
    email_id = test_email['id']
    current_starred = test_email.get('is_starred', False)
    
    print(f"✅ 找到测试邮件:")
    print(f"   ID: {email_id}")
    print(f"   主题: {test_email.get('subject', 'N/A')}")
    print(f"   当前置顶状态: {current_starred}")
    
    # 3. 测试置顶功能（切换状态）
    new_starred = not current_starred
    print(f"\n📌 测试置顶功能: 将置顶状态改为 {new_starred}...")
    
    patch_response = requests.patch(
        f"http://127.0.0.1:8001/api/email_history/{email_id}",
        headers=headers,
        json={"is_starred": new_starred}
    )
    
    print(f"   响应状态码: {patch_response.status_code}")
    
    if patch_response.status_code == 200:
        result = patch_response.json()
        print(f"✅ 置顶状态更新成功!")
        print(f"   新的置顶状态: {result.get('is_starred')}")
        
        # 4. 验证更新（再次获取邮件详情）
        print(f"\n🔍 验证更新结果...")
        verify_response = requests.get(
            f"http://127.0.0.1:8001/api/email_history/{email_id}",
            headers=headers
        )
        
        if verify_response.status_code == 200:
            verified_email = verify_response.json()
            verified_starred = verified_email.get('is_starred')
            print(f"   数据库中的置顶状态: {verified_starred}")
            
            if verified_starred == new_starred:
                print("✅ 验证成功！置顶功能工作正常！")
            else:
                print(f"❌ 验证失败！期望: {new_starred}, 实际: {verified_starred}")
        else:
            print(f"❌ 验证失败: {verify_response.status_code}")
            
    else:
        print(f"❌ 置顶失败: {patch_response.status_code}")
        print(patch_response.text)
    
    # 5. 恢复原始状态
    print(f"\n🔄 恢复原始状态...")
    restore_response = requests.patch(
        f"http://127.0.0.1:8001/api/email_history/{email_id}",
        headers=headers,
        json={"is_starred": current_starred}
    )
    
    if restore_response.status_code == 200:
        print(f"✅ 已恢复原始状态: {current_starred}")
    else:
        print(f"⚠️  恢复失败: {restore_response.status_code}")

if __name__ == "__main__":
    test_pin_feature()
