import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import formataddr
from typing import Optional, List, Dict
import os


class EmailSender:
    """邮件发送器 - 集成SMTP服务"""
    
    def __init__(self, smtp_config=None):
        """
        初始化邮件发送器
        参数:
            smtp_config: SMTP配置字典 {host, port, username, password, use_ssl}
        """
        self.smtp_config = smtp_config or {}
        self.sent_count = 0
        self.daily_limit = 500  # 提高限制到500
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        cc_email: Optional[str] = None,
        bcc_email: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        html_body: Optional[str] = None,
        priority: str = 'normal',
        need_receipt: bool = False
    ) -> Dict[str, any]:
        """
        发送邮件
        参数:
            to_email: 收件人（多个用逗号分隔）
            subject: 主题
            body: 正文（纯文本）
            from_email: 发件人邮箱
            from_name: 发件人名称
            cc_email: 抄送（多个用逗号分隔）
            bcc_email: 密送（多个用逗号分隔）
            attachments: 附件路径列表
            html_body: HTML正文（优先使用）
            priority: 优先级 (high/normal/low)
            need_receipt: 是否需要已读回执
        返回:
            dict: {success: bool, message: str, error: Optional[str]}
        """
        # 检查限制
        if self.sent_count >= self.daily_limit:
            return {
                'success': False,
                'message': f'已达到每日发送限制: {self.daily_limit}',
                'error': 'DAILY_LIMIT_REACHED'
            }
        
        # 检查SMTP配置
        if not self.smtp_config or not all(k in self.smtp_config for k in ['host', 'port', 'username', 'password']):
            return {
                'success': False,
                'message': 'SMTP配置不完整，请先配置邮箱账户',
                'error': 'SMTP_CONFIG_MISSING'
            }
        
        try:
            # 创建邮件消息
            message = MIMEMultipart('alternative')
            message['Subject'] = Header(subject, 'utf-8')
            
            # 正确格式化 From 头部，符合 RFC5322 标准
            sender_email = from_email or self.smtp_config['username']
            if from_name:
                # 使用 formataddr 和 Header 正确编码中文名称
                message['From'] = formataddr((str(Header(from_name, 'utf-8')), sender_email))
            else:
                message['From'] = sender_email
            
            message['To'] = to_email
            
            if cc_email:
                message['Cc'] = cc_email
            if bcc_email:
                message['Bcc'] = bcc_email
            
            # 设置优先级
            if priority == 'high':
                message['X-Priority'] = '1'
                message['X-MSMail-Priority'] = 'High'
                message['Importance'] = 'High'
            elif priority == 'low':
                message['X-Priority'] = '5'
                message['X-MSMail-Priority'] = 'Low'
                message['Importance'] = 'Low'
            
            # 设置已读回执
            if need_receipt:
                message['Disposition-Notification-To'] = from_email or self.smtp_config['username']
                message['Return-Receipt-To'] = from_email or self.smtp_config['username']
            
            # 添加正文
            if html_body:
                # 添加纯文本和HTML两个版本
                part1 = MIMEText(body, 'plain', 'utf-8')
                part2 = MIMEText(html_body, 'html', 'utf-8')
                message.attach(part1)
                message.attach(part2)
            else:
                # 只有纯文本
                part = MIMEText(body, 'plain', 'utf-8')
                message.attach(part)
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as file:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(file.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            message.attach(part)
            
            # 连接SMTP服务器并发送
            use_ssl = self.smtp_config.get('use_ssl', True)
            
            if use_ssl and self.smtp_config['port'] == 465:
                # SSL连接
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_config['host'], self.smtp_config['port'], context=context) as server:
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                    
                    # 构建所有收件人列表
                    all_recipients = [email.strip() for email in to_email.split(',')]
                    if cc_email:
                        all_recipients.extend([email.strip() for email in cc_email.split(',')])
                    if bcc_email:
                        all_recipients.extend([email.strip() for email in bcc_email.split(',')])
                    
                    server.sendmail(
                        from_email or self.smtp_config['username'],
                        all_recipients,
                        message.as_string()
                    )
            else:
                # TLS连接
                with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                    server.starttls()
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                    
                    # 构建所有收件人列表
                    all_recipients = [email.strip() for email in to_email.split(',')]
                    if cc_email:
                        all_recipients.extend([email.strip() for email in cc_email.split(',')])
                    if bcc_email:
                        all_recipients.extend([email.strip() for email in bcc_email.split(',')])
                    
                    server.sendmail(
                        from_email or self.smtp_config['username'],
                        all_recipients,
                        message.as_string()
                    )
            
            self.sent_count += 1
            print(f"✅ 邮件发送成功: {to_email}")
            
            return {
                'success': True,
                'message': '邮件发送成功',
                'error': None
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f'SMTP认证失败，请检查邮箱密码或授权码: {str(e)}'
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'error': 'SMTP_AUTH_FAILED'
            }
        except smtplib.SMTPException as e:
            error_msg = f'SMTP错误: {str(e)}'
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'error': 'SMTP_ERROR'
            }
        except Exception as e:
            error_msg = f'发送失败: {str(e)}'
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'error': 'UNKNOWN_ERROR'
            }
    
    def send_bulk(self, email_list):
        """
        批量发送邮件
        参数:
            email_list: 邮件列表 [{to, subject, body, attachments}]
        返回:
            成功数量
        """
        success_count = 0
        for email_data in email_list:
            if self.send_email(
                email_data.get('to'),
                email_data.get('subject'),
                email_data.get('body'),
                email_data.get('attachments')
            ):
                success_count += 1
                # 间隔发送
                import time
                import random
                time.sleep(random.randint(30, 60))
        
        return success_count
    
    def reset_daily_count(self):
        """重置每日计数"""
        self.sent_count = 0
