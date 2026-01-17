"""邮件接收模块使用示例"""
from src.email_system.receiver import EmailReceiver
from src.crm.database import get_session, EmailAccount, Customer, EmailHistory
from datetime import datetime

# ============================================================================
# 示例1: 直接使用 EmailReceiver 类（不通过API）
# ============================================================================

def example_1_basic_usage():
    """基础使用示例 - Gmail"""
    print("=" * 60)
    print("示例1: 基础使用 - 连接Gmail并获取邮件")
    print("=" * 60)
    
    # 配置Gmail账号（需要使用应用专用密码）
    email_address = "your_company@gmail.com"
    app_password = "your_16_digit_app_password"  # Gmail应用专用密码
    
    # 创建接收器
    receiver = EmailReceiver(
        email_address=email_address,
        password=app_password,
        provider='gmail'  # 自动使用Gmail的IMAP配置
    )
    
    # 连接并获取邮件
    if receiver.connect():
        # 获取最新的10封未读邮件
        emails = receiver.fetch_new_emails(limit=10, only_unseen=True)
        
        print(f"\n📧 获取到 {len(emails)} 封新邮件\n")
        
        for i, email in enumerate(emails, 1):
            print(f"邮件 {i}:")
            print(f"  发件人: {email['from_email']}")
            print(f"  主题: {email['subject']}")
            print(f"  日期: {email['date']}")
            print(f"  附件: {len(email['attachments'])} 个")
            print(f"  正文: {email['body'][:100]}...")
            print()
        
        receiver.disconnect()
    else:
        print("❌ 连接失败")


def example_2_outlook():
    """示例2: 连接Outlook/Hotmail"""
    print("=" * 60)
    print("示例2: 连接Outlook邮箱")
    print("=" * 60)
    
    receiver = EmailReceiver(
        email_address="your_company@outlook.com",
        password="your_password",
        provider='outlook'
    )
    
    if receiver.connect():
        emails = receiver.fetch_new_emails(limit=5)
        print(f"✅ 成功获取 {len(emails)} 封邮件")
        receiver.disconnect()


def example_3_aliyun():
    """示例3: 连接阿里云企业邮箱"""
    print("=" * 60)
    print("示例3: 连接阿里云企业邮箱")
    print("=" * 60)
    
    receiver = EmailReceiver(
        email_address="sales@yourcompany.com",
        password="your_password",
        provider='aliyun'
    )
    
    if receiver.connect():
        emails = receiver.fetch_new_emails(limit=10)
        print(f"✅ 成功获取 {len(emails)} 封邮件")
        receiver.disconnect()


def example_4_custom_imap():
    """示例4: 自定义IMAP服务器"""
    print("=" * 60)
    print("示例4: 连接自定义IMAP服务器")
    print("=" * 60)
    
    receiver = EmailReceiver(
        email_address="admin@customdomain.com",
        password="your_password",
        imap_host="mail.customdomain.com",  # 自定义IMAP服务器
        imap_port=993
    )
    
    if receiver.connect():
        # 获取邮箱文件夹列表
        folders = receiver.get_mailbox_list()
        print(f"📁 邮箱文件夹: {folders}")
        
        # 获取邮件
        emails = receiver.fetch_new_emails(mailbox="INBOX", limit=5)
        print(f"✅ 成功获取 {len(emails)} 封邮件")
        
        receiver.disconnect()


# ============================================================================
# 示例5: 通过API使用（推荐方式）
# ============================================================================

"""
通过API使用邮件接收功能的步骤：

1. 创建邮箱账户
POST /api/email_accounts
{
    "account_name": "公司主邮箱",
    "email_address": "sales@company.com",
    "imap_password": "your_password",
    "provider": "gmail",
    "auto_sync": true,
    "sync_interval": 5,
    "auto_match_customer": true
}

2. 测试连接
POST /api/email_accounts/{account_id}/test

3. 手动同步邮件
POST /api/email_accounts/{account_id}/sync?limit=50&only_unseen=true

4. 获取邮箱账户列表
GET /api/email_accounts

5. 更新邮箱配置
PUT /api/email_accounts/{account_id}
{
    "auto_sync": true,
    "sync_interval": 10
}

6. 启用/禁用账户
POST /api/email_accounts/{account_id}/toggle

7. 删除邮箱账户
DELETE /api/email_accounts/{account_id}
"""


# ============================================================================
# 示例6: 自动匹配客户并保存到数据库
# ============================================================================

def example_6_auto_match_and_save():
    """示例6: 自动匹配客户并保存邮件"""
    print("=" * 60)
    print("示例6: 获取邮件并自动匹配客户")
    print("=" * 60)
    
    # 创建接收器
    receiver = EmailReceiver(
        email_address="sales@company.com",
        password="your_password",
        provider='gmail'
    )
    
    if not receiver.connect():
        print("❌ 连接失败")
        return
    
    # 获取新邮件
    emails = receiver.fetch_new_emails(limit=20, only_unseen=True)
    receiver.disconnect()
    
    # 保存到数据库
    db = get_session()
    saved_count = 0
    
    for email_data in emails:
        try:
            # 尝试匹配客户
            customer = db.query(Customer).filter(
                Customer.email == email_data['from_email']
            ).first()
            
            # 创建邮件历史记录
            email_history = EmailHistory(
                customer_id=customer.id if customer else None,
                direction='inbound',
                subject=email_data['subject'],
                body=email_data['body'],
                sent_at=email_data['date'],
                attachments=str(email_data['attachments']) if email_data['attachments'] else None
            )
            
            db.add(email_history)
            saved_count += 1
            
            if customer:
                print(f"✅ 匹配到客户: {customer.company_name} - {email_data['subject']}")
            else:
                print(f"ℹ️  未匹配客户: {email_data['from_email']} - {email_data['subject']}")
                
        except Exception as e:
            print(f"❌ 保存失败: {str(e)}")
    
    db.commit()
    db.close()
    
    print(f"\n✅ 成功保存 {saved_count}/{len(emails)} 封邮件到数据库")


# ============================================================================
# 配置说明
# ============================================================================

"""
常见邮箱配置说明：

1. Gmail
   - IMAP服务器: imap.gmail.com:993
   - 需要开启"两步验证"
   - 使用"应用专用密码"而非账户密码
   - 生成应用密码: https://myaccount.google.com/apppasswords

2. Outlook/Hotmail
   - IMAP服务器: outlook.office365.com:993
   - 直接使用账户密码即可

3. QQ邮箱
   - IMAP服务器: imap.qq.com:993
   - 需要开启IMAP服务
   - 使用"授权码"而非QQ密码

4. 163邮箱
   - IMAP服务器: imap.163.com:993
   - 需要开启IMAP服务
   - 使用"客户端授权密码"

5. 阿里云企业邮箱
   - IMAP服务器: imap.aliyun.com:993
   - 直接使用邮箱密码

6. Yahoo邮箱
   - IMAP服务器: imap.mail.yahoo.com:993
   - 需要生成应用密码
"""


# ============================================================================
# 功能特点
# ============================================================================

"""
✅ 支持的功能：
- 支持Gmail、Outlook、QQ、163、阿里云、Yahoo等主流邮箱
- 支持自定义IMAP服务器
- 自动识别邮箱服务商
- 支持获取未读/所有邮件
- 支持邮件正文解析（纯文本和HTML）
- 支持附件信息提取
- 自动匹配客户
- 自动保存到数据库
- 支持手动和自动同步
- 支持邮箱文件夹列表

⚠️ 注意事项：
1. Gmail需要使用"应用专用密码"
2. QQ/163需要开启IMAP并使用"授权码"
3. 密码应该加密存储（当前TODO）
4. 建议使用专门的业务邮箱
5. 注意邮箱服务商的频率限制
6. 大附件需要单独处理下载逻辑
"""


if __name__ == "__main__":
    print("\n邮件接收模块使用示例\n")
    print("请修改示例中的邮箱账号和密码后运行")
    print("=" * 60)
    
    # 取消注释来运行示例
    # example_1_basic_usage()
    # example_2_outlook()
    # example_3_aliyun()
    # example_4_custom_imap()
    # example_6_auto_match_and_save()
