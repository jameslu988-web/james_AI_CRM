"""测试置顶排序功能"""
import requests

def test_pin_sorting():
    """测试置顶邮件是否排在最前面"""
    
    # 1. 登录
    print("🔐 正在登录...")
    login_response = requests.post(
        "http://127.0.0.1:8001/api/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败")
        return
    
    token = login_response.json().get("access_token")
    print("✅ 登录成功")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 2. 获取邮件列表（前10封）
    print("\n📧 获取邮件列表...")
    list_response = requests.get(
        "http://127.0.0.1:8001/api/email_history?range=[0,9]",
        headers=headers
    )
    
    if list_response.status_code != 200:
        print(f"❌ 获取邮件列表失败")
        return
    
    emails = list_response.json()
    print(f"✅ 获取到 {len(emails)} 封邮件\n")
    
    # 3. 显示当前邮件列表顺序
    print("📋 当前邮件列表（前10封）:")
    print("-" * 100)
    for i, email in enumerate(emails[:10], 1):
        is_starred = email.get('is_starred', False)
        pin_icon = "📌" if is_starred else "  "
        subject = email.get('subject', 'N/A')[:50]
        print(f"{pin_icon} {i}. [ID:{email['id']:4d}] {subject}")
    print("-" * 100)
    
    # 4. 找一封未置顶的邮件进行置顶测试
    unpinned_email = None
    for email in emails:
        if not email.get('is_starred', False):
            unpinned_email = email
            break
    
    if not unpinned_email:
        print("\n⚠️  所有邮件都已置顶，无法测试")
        return
    
    test_email_id = unpinned_email['id']
    test_subject = unpinned_email.get('subject', 'N/A')[:50]
    print(f"\n🎯 选择测试邮件: [ID:{test_email_id}] {test_subject}")
    
    # 5. 置顶这封邮件
    print(f"\n📌 正在置顶邮件 ID:{test_email_id}...")
    patch_response = requests.patch(
        f"http://127.0.0.1:8001/api/email_history/{test_email_id}",
        headers=headers,
        json={"is_starred": True}
    )
    
    if patch_response.status_code != 200:
        print(f"❌ 置顶失败")
        return
    
    print("✅ 置顶成功!")
    
    # 6. 再次获取邮件列表，检查排序
    print(f"\n🔍 重新获取邮件列表，检查排序...")
    verify_response = requests.get(
        "http://127.0.0.1:8001/api/email_history?range=[0,9]",
        headers=headers
    )
    
    if verify_response.status_code != 200:
        print(f"❌ 获取邮件列表失败")
        return
    
    new_emails = verify_response.json()
    
    print("\n📋 更新后的邮件列表（前10封）:")
    print("-" * 100)
    for i, email in enumerate(new_emails[:10], 1):
        is_starred = email.get('is_starred', False)
        pin_icon = "📌" if is_starred else "  "
        subject = email.get('subject', 'N/A')[:50]
        is_test = " ⭐" if email['id'] == test_email_id else ""
        print(f"{pin_icon} {i}. [ID:{email['id']:4d}] {subject}{is_test}")
    print("-" * 100)
    
    # 7. 验证置顶邮件是否在顶部
    first_email = new_emails[0]
    if first_email['id'] == test_email_id:
        print(f"\n✅ 验证成功！置顶的邮件 (ID:{test_email_id}) 现在排在第1位！")
    else:
        # 查找测试邮件的位置
        position = None
        for i, email in enumerate(new_emails, 1):
            if email['id'] == test_email_id:
                position = i
                break
        
        if position:
            print(f"\n⚠️  置顶的邮件 (ID:{test_email_id}) 在第 {position} 位")
            # 检查是否所有置顶邮件都在前面
            starred_positions = [i for i, e in enumerate(new_emails, 1) if e.get('is_starred')]
            if starred_positions:
                print(f"   所有置顶邮件的位置: {starred_positions}")
                if position <= max(starred_positions):
                    print("✅ 所有置顶邮件都在未置顶邮件之前，排序正确！")
                else:
                    print("❌ 排序可能有问题")
        else:
            print(f"\n❌ 未找到测试邮件 (ID:{test_email_id})")
    
    # 8. 恢复原状（取消置顶）
    print(f"\n🔄 恢复原状，取消置顶...")
    restore_response = requests.patch(
        f"http://127.0.0.1:8001/api/email_history/{test_email_id}",
        headers=headers,
        json={"is_starred": False}
    )
    
    if restore_response.status_code == 200:
        print("✅ 已取消置顶")
    else:
        print("⚠️  取消置顶失败")

if __name__ == "__main__":
    test_pin_sorting()
