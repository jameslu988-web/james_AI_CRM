"""
企业微信通知测试脚本
用于测试企业微信通知功能是否正常工作
"""
from src.utils.wecom_notification import WeComNotification
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_webhook_notification():
    """测试群机器人Webhook通知"""
    print("\n=== 测试企业微信群机器人通知 ===\n")
    
    # 创建通知实例
    wecom = WeComNotification()
    
    # 检查配置
    if not wecom.webhook_url:
        print("❌ 未配置 WECOM_WEBHOOK_URL")
        print("请在 .env 文件中添加：")
        print("WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY")
        return False
    
    print(f"✅ 已配置 Webhook URL: {wecom.webhook_url[:50]}...")
    
    # 测试发送简单文本消息
    print("\n1. 测试发送文本消息...")
    result = wecom.send_custom_message(
        title="📧 测试通知",
        content="这是一条测试消息，用于验证企业微信通知功能。\n发送时间：2026-01-18 15:30:00",
        use_webhook=True
    )
    
    if result:
        print("✅ 文本消息发送成功")
    else:
        print("❌ 文本消息发送失败")
        return False
    
    # 测试发送审核通知
    print("\n2. 测试发送审核通知...")
    result = wecom.send_approval_notification(
        task_id=12345,
        email_subject="询价：关于男士内裤的价格咨询",
        email_from="john@example.com",
        email_category="inquiry",
        draft_subject="Re: 关于男士内裤的价格咨询",
        urgency_level="high",
        use_webhook=True
    )
    
    if result:
        print("✅ 审核通知发送成功")
    else:
        print("❌ 审核通知发送失败")
        return False
    
    # 测试发送审核结果通知
    print("\n3. 测试发送审核结果通知...")
    result = wecom.send_approval_result_notification(
        task_id=12345,
        status="approved",
        approved_by="张三",
        email_subject="Re: 关于男士内裤的价格咨询",
        use_webhook=True
    )
    
    if result:
        print("✅ 审核结果通知发送成功")
    else:
        print("❌ 审核结果通知发送失败")
        return False
    
    print("\n" + "="*50)
    print("✅ 所有测试通过！企业微信群机器人配置正确。")
    print("="*50 + "\n")
    return True


def test_app_notification():
    """测试企业应用消息通知"""
    print("\n=== 测试企业微信应用消息通知 ===\n")
    
    # 创建通知实例
    wecom = WeComNotification()
    
    # 检查配置
    if not wecom.corp_id or not wecom.corp_secret or not wecom.agent_id:
        print("⚠️ 未配置企业应用参数")
        print("如需使用企业应用消息，请在 .env 文件中添加：")
        print("WECOM_CORP_ID=your_corp_id")
        print("WECOM_CORP_SECRET=your_corp_secret")
        print("WECOM_AGENT_ID=your_agent_id")
        return False
    
    print(f"✅ 已配置企业ID: {wecom.corp_id[:10]}...")
    print(f"✅ 已配置应用ID: {wecom.agent_id}")
    
    # 获取Access Token
    print("\n1. 测试获取Access Token...")
    token = wecom.get_access_token()
    
    if not token:
        print("❌ 获取Access Token失败")
        return False
    
    print(f"✅ 获取Access Token成功: {token[:20]}...")
    
    # 测试发送应用消息
    print("\n2. 测试发送应用消息...")
    result = wecom.send_approval_notification(
        task_id=12345,
        email_subject="询价：关于男士内裤的价格咨询",
        email_from="john@example.com",
        email_category="inquiry",
        draft_subject="Re: 关于男士内裤的价格咨询",
        urgency_level="high",
        user_ids="@all",  # 发送给所有人
        use_webhook=False  # 使用企业应用
    )
    
    if result:
        print("✅ 应用消息发送成功")
    else:
        print("❌ 应用消息发送失败")
        return False
    
    print("\n" + "="*50)
    print("✅ 所有测试通过！企业微信应用配置正确。")
    print("="*50 + "\n")
    return True


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("企业微信通知功能测试")
    print("="*60)
    
    # 测试群机器人（推荐）
    webhook_ok = test_webhook_notification()
    
    # 测试企业应用（可选）
    app_ok = test_app_notification()
    
    print("\n" + "="*60)
    print("测试总结：")
    print(f"  群机器人: {'✅ 通过' if webhook_ok else '❌ 失败'}")
    print(f"  企业应用: {'✅ 通过' if app_ok else '⚠️ 未配置或失败'}")
    print("="*60 + "\n")
    
    if webhook_ok:
        print("🎉 恭喜！企业微信通知功能已就绪。")
        print("\n💡 使用建议：")
        print("  1. 群机器人方式最简单，推荐日常使用")
        print("  2. 企业应用方式功能更强大，可按用户发送")
        print("  3. 在自动回复规则中选择'企业微信'审核方式")
        print("  4. 系统会在创建审核任务时自动发送通知\n")
    else:
        print("⚠️ 企业微信通知配置有问题，请检查配置。\n")
        print("📖 配置指南：")
        print("  1. 群机器人方式（推荐）：")
        print("     - 在企业微信群中添加机器人")
        print("     - 复制Webhook地址")
        print("     - 添加到 .env: WECOM_WEBHOOK_URL=...")
        print("\n  2. 企业应用方式（可选）：")
        print("     - 在企业微信管理后台创建应用")
        print("     - 获取 Corp ID、Secret 和 Agent ID")
        print("     - 添加到 .env 文件\n")


if __name__ == "__main__":
    main()
