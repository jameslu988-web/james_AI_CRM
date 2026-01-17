"""
退信邮件监听器
监听邮箱中的退信通知，自动更新邮件投递状态
"""
import re
from datetime import datetime
from typing import Dict, List, Optional
from email import message_from_bytes
from email.header import decode_header
import imaplib
import email

class BounceListener:
    """退信邮件监听器"""
    
    def __init__(self, imap_host: str, imap_port: int, email_address: str, password: str, use_ssl: bool = True):
        """
        初始化退信监听器
        
        Args:
            imap_host: IMAP服务器地址
            imap_port: IMAP端口
            email_address: 邮箱地址
            password: 邮箱密码
            use_ssl: 是否使用SSL
        """
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.email_address = email_address
        self.password = password
        self.use_ssl = use_ssl
        self.connection = None
    
    def connect(self):
        """连接到IMAP服务器"""
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            else:
                self.connection = imaplib.IMAP4(self.imap_host, self.imap_port)
            
            self.connection.login(self.email_address, self.password)
            print(f"✅ 退信监听器已连接: {self.email_address}")
            return True
        except Exception as e:
            print(f"❌ 退信监听器连接失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开IMAP连接"""
        if self.connection:
            try:
                self.connection.logout()
            except:
                pass
    
    def check_bounce_emails(self) -> List[Dict]:
        """
        检查退信邮件
        
        Returns:
            退信邮件列表，每个元素包含：
            {
                'message_id': '原始邮件的Message-ID',
                'bounce_type': 'hard' 或 'soft',
                'bounce_reason': '退信原因',
                'recipient': '收件人邮箱',
                'smtp_code': 'SMTP错误码'
            }
        """
        if not self.connection:
            if not self.connect():
                return []
        
        bounce_emails = []
        
        try:
            # 选择收件箱
            self.connection.select('INBOX')
            
            # 搜索退信邮件的特征
            # 1. 发件人是 MAILER-DAEMON 或 postmaster
            search_criteria = [
                '(FROM "MAILER-DAEMON")',
                '(FROM "postmaster")',
                '(FROM "Mail Delivery System")',
                '(SUBJECT "Undelivered")',
                '(SUBJECT "Failure")',
                '(SUBJECT "Returned mail")',
                '(SUBJECT "Delivery Status Notification")'
            ]
            
            for criteria in search_criteria:
                try:
                    status, messages = self.connection.search(None, criteria)
                    if status == 'OK' and messages[0]:
                        email_ids = messages[0].split()
                        # 只处理最近的50封退信邮件
                        for email_id in email_ids[-50:]:
                            bounce_info = self._parse_bounce_email(email_id)
                            if bounce_info:
                                bounce_emails.append(bounce_info)
                                # 标记为已读
                                self.connection.store(email_id, '+FLAGS', '\\Seen')
                except Exception as e:
                    print(f"⚠️ 搜索退信邮件失败 ({criteria}): {str(e)}")
                    continue
            
            print(f"📧 检查到 {len(bounce_emails)} 封退信邮件")
            
        except Exception as e:
            print(f"❌ 检查退信邮件失败: {str(e)}")
        
        return bounce_emails
    
    def _parse_bounce_email(self, email_id: bytes) -> Optional[Dict]:
        """
        解析退信邮件
        
        Args:
            email_id: 邮件ID
            
        Returns:
            退信信息字典，如果不是退信邮件则返回None
        """
        try:
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return None
            
            email_body = msg_data[0][1]
            email_message = message_from_bytes(email_body)
            
            # 提取邮件内容
            content = self._get_email_content(email_message)
            
            # 解析退信信息
            bounce_info = {
                'message_id': None,
                'bounce_type': 'unknown',
                'bounce_reason': '',
                'recipient': None,
                'smtp_code': None,
                'raw_content': content[:500]  # 保存部分原始内容用于调试
            }
            
            # 提取原始邮件的 Message-ID
            message_id = self._extract_message_id(content)
            if message_id:
                bounce_info['message_id'] = message_id
            
            # 提取收件人邮箱
            recipient = self._extract_recipient(content)
            if recipient:
                bounce_info['recipient'] = recipient
            
            # 提取SMTP错误码和原因
            smtp_code, bounce_reason = self._extract_smtp_error(content)
            if smtp_code:
                bounce_info['smtp_code'] = smtp_code
                bounce_info['bounce_reason'] = bounce_reason
                
                # 根据SMTP错误码判断bounce类型
                bounce_info['bounce_type'] = self._classify_bounce_type(smtp_code)
            
            # 如果没有找到Message-ID，则不是有效的退信邮件
            if not bounce_info['message_id']:
                return None
            
            return bounce_info
            
        except Exception as e:
            print(f"⚠️ 解析退信邮件失败: {str(e)}")
            return None
    
    def _get_email_content(self, email_message) -> str:
        """提取邮件内容（纯文本）"""
        content = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            content += payload.decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                payload = email_message.get_payload(decode=True)
                if payload:
                    content = payload.decode('utf-8', errors='ignore')
            except:
                pass
        
        return content
    
    def _extract_message_id(self, content: str) -> Optional[str]:
        """提取原始邮件的Message-ID"""
        patterns = [
            r'Message-ID:\s*<([^>]+)>',
            r'Message-Id:\s*<([^>]+)>',
            r'Original-Message-ID:\s*<([^>]+)>',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_recipient(self, content: str) -> Optional[str]:
        """提取收件人邮箱地址"""
        patterns = [
            r'(?:To|TO):\s*<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?',
            r'(?:Recipient|RECIPIENT):\s*<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?',
            r'user\s+<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_smtp_error(self, content: str) -> tuple:
        """
        提取SMTP错误码和错误信息
        
        Returns:
            (smtp_code, error_message)
        """
        # 常见的SMTP错误码模式
        patterns = [
            r'(5[0-9]{2})\s+([^\n]+)',  # 5xx错误
            r'(4[0-9]{2})\s+([^\n]+)',  # 4xx错误
            r'#(5\.[0-9]\.[0-9])\s+([^\n]+)',  # 增强状态码
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return (match.group(1), match.group(2).strip())
        
        # 尝试查找常见的错误描述
        error_keywords = [
            'user unknown',
            'mailbox unavailable',
            'mailbox full',
            'address rejected',
            'does not exist',
            'invalid recipient',
            'no such user',
        ]
        
        for keyword in error_keywords:
            if keyword in content.lower():
                # 提取包含关键词的行
                for line in content.split('\n'):
                    if keyword in line.lower():
                        return ('550', line.strip())
        
        return (None, 'Unknown bounce reason')
    
    def _classify_bounce_type(self, smtp_code: str) -> str:
        """
        根据SMTP错误码分类bounce类型
        
        Args:
            smtp_code: SMTP错误码
            
        Returns:
            'hard' (硬退信，永久性错误) 或 'soft' (软退信，临时性错误)
        """
        if not smtp_code:
            return 'unknown'
        
        # 5xx 错误通常是硬退信（永久性错误）
        hard_bounce_codes = [
            '550',  # 邮箱不存在
            '551',  # 用户不在本地
            '552',  # 邮箱已满（超过配额）
            '553',  # 邮箱名称不正确
            '554',  # 交易失败
        ]
        
        # 4xx 错误通常是软退信（临时性错误）
        soft_bounce_codes = [
            '421',  # 服务暂时不可用
            '450',  # 邮箱暂时不可用
            '451',  # 操作中止
            '452',  # 系统存储不足
        ]
        
        for code in hard_bounce_codes:
            if smtp_code.startswith(code):
                return 'hard'
        
        for code in soft_bounce_codes:
            if smtp_code.startswith(code):
                return 'soft'
        
        # 默认：5开头的是硬退信，4开头的是软退信
        if smtp_code.startswith('5'):
            return 'hard'
        elif smtp_code.startswith('4'):
            return 'soft'
        
        return 'unknown'


def test_bounce_listener():
    """测试退信监听器"""
    # 示例配置（需要替换为实际配置）
    listener = BounceListener(
        imap_host='imap.example.com',
        imap_port=993,
        email_address='your-email@example.com',
        password='your-password',
        use_ssl=True
    )
    
    if listener.connect():
        bounces = listener.check_bounce_emails()
        print(f"\n检测到 {len(bounces)} 封退信邮件:")
        for bounce in bounces:
            print(f"\n- Message-ID: {bounce['message_id']}")
            print(f"  收件人: {bounce['recipient']}")
            print(f"  类型: {bounce['bounce_type']}")
            print(f"  错误码: {bounce['smtp_code']}")
            print(f"  原因: {bounce['bounce_reason']}")
        
        listener.disconnect()


if __name__ == '__main__':
    test_bounce_listener()
