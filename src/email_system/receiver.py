"""邮件接收器 - 支持IMAP协议接收邮件（Gmail、Outlook、阿里云邮箱等）"""
import imaplib
import email
from email.header import decode_header
from datetime import datetime
import json
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session


class EmailReceiver:
    """邮件接收器 - 使用IMAP协议"""
    
    # 常见邮箱服务器配置
    IMAP_SERVERS = {
        'gmail': {
            'host': 'imap.gmail.com',
            'port': 993,
            'ssl': True
        },
        'outlook': {
            'host': 'outlook.office365.com',
            'port': 993,
            'ssl': True
        },
        'qq': {
            'host': 'imap.qq.com',
            'port': 993,
            'ssl': True
        },
        'aliyun': {
            'host': 'imap.aliyun.com',
            'port': 993,
            'ssl': True
        },
        '163': {
            'host': 'imap.163.com',
            'port': 993,
            'ssl': True
        },
        'yahoo': {
            'host': 'imap.mail.yahoo.com',
            'port': 993,
            'ssl': True
        }
    }
    
    def __init__(self, email_address: str, password: str, provider: str = None, 
                 imap_host: str = None, imap_port: int = 993):
        """
        初始化邮件接收器
        
        参数:
            email_address: 邮箱地址
            password: 密码或授权码
            provider: 邮箱服务商 (gmail/outlook/qq/aliyun/163/yahoo)
            imap_host: 自定义IMAP服务器地址
            imap_port: 自定义IMAP端口
        """
        self.email_address = email_address
        self.password = password
        
        # 自动识别邮箱服务商
        if provider:
            self.provider = provider.lower()
        else:
            self.provider = self._detect_provider(email_address)
        
        # 获取IMAP配置
        if imap_host:
            self.imap_host = imap_host
            self.imap_port = imap_port
        elif self.provider in self.IMAP_SERVERS:
            config = self.IMAP_SERVERS[self.provider]
            self.imap_host = config['host']
            self.imap_port = config['port']
        else:
            raise ValueError(f"未知的邮箱服务商: {self.provider}，请手动指定IMAP服务器")
        
        self.connection = None
    
    def _detect_provider(self, email_address: str) -> str:
        """自动检测邮箱服务商"""
        domain = email_address.split('@')[-1].lower()
        
        if 'gmail' in domain:
            return 'gmail'
        elif 'outlook' in domain or 'hotmail' in domain or 'live' in domain:
            return 'outlook'
        elif 'qq.com' in domain:
            return 'qq'
        elif 'aliyun' in domain:
            return 'aliyun'
        elif '163.com' in domain:
            return '163'
        elif 'yahoo' in domain:
            return 'yahoo'
        else:
            return 'custom'
    
    def connect(self) -> bool:
        """连接到IMAP服务器"""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            self.connection.login(self.email_address, self.password)
            print(f"✅ 成功连接到邮箱: {self.email_address}")
            return True
        except imaplib.IMAP4.error as e:
            print(f"❌ IMAP登录失败: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 连接失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            try:
                self.connection.logout()
                print(f"✅ 已断开连接: {self.email_address}")
            except:
                pass
    
    def _decode_str(self, text):
        """解码邮件文本（支持RFC 2047编码）"""
        if text is None:
            return ""
        
        # 如果已经是字符串，尝试解码RFC 2047格式（=?utf-8?B?...?=）
        if isinstance(text, str):
            # 检查是否包含编码标记
            if '=?' in text and '?=' in text:
                try:
                    decoded_parts = decode_header(text)
                    result = []
                    for part, encoding in decoded_parts:
                        if isinstance(part, bytes):
                            # 尝试使用指定的编码，如果失败则尝试常见编码
                            if encoding:
                                try:
                                    result.append(part.decode(encoding))
                                except:
                                    result.append(part.decode('utf-8', errors='ignore'))
                            else:
                                # 尝试常见编码
                                for enc in ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']:
                                    try:
                                        result.append(part.decode(enc))
                                        break
                                    except:
                                        continue
                                else:
                                    result.append(part.decode('utf-8', errors='ignore'))
                        else:
                            result.append(str(part))
                    return ''.join(result)
                except Exception as e:
                    print(f"⚠️ 解码失败: {str(e)}")
                    return text
            return text
        
        # 如果是bytes，直接解码
        if isinstance(text, bytes):
            for enc in ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']:
                try:
                    return text.decode(enc)
                except:
                    continue
            return text.decode('utf-8', errors='ignore')
        
        return str(text)
    
    def _extract_email_address(self, email_str: str) -> str:
        """从邮件地址字符串中提取纯邮箱地址"""
        if not email_str:
            return ""
        
        # 匹配 <email@example.com> 或 email@example.com 格式
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email_str)
        if match:
            return match.group(0)
        return email_str
    
    def _parse_email_name_and_address(self, email_str: str) -> tuple:
        """从邮件地址字符串中解析名称和邮箱地址
        
        参数:
            email_str: 邮件地址字符串，如 'Jazmin Louise <jazmin@example.com>' 或 'jazmin@example.com'
        
        返回:
            (name, email) 元组
        
        示例:
            'Jazmin Louise <jazmin@eleads.com>' -> ('Jazmin Louise', 'jazmin@eleads.com')
            'jazmin@eleads.com' -> ('', 'jazmin@eleads.com')
        """
        if not email_str:
            return "", ""
        
        # 尝试匹配 "名称 <邮箱>" 格式
        match = re.match(r'(.+?)\s*<([\w\.-]+@[\w\.-]+\.\w+)>', email_str)
        if match:
            name = match.group(1).strip()
            # 移除可能的引号
            name = name.strip('"').strip("'")
            email_addr = match.group(2)
            return name, email_addr
        
        # 如果没有名称，只有邮箱地址
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email_str)
        if match:
            return "", match.group(0)
        
        return "", email_str
    
    def _parse_email_body(self, msg) -> tuple:
        """解析邮件正文（支持HTML和纯文本）"""
        text_body = ""
        html_body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # 跳过附件
                if "attachment" in content_disposition:
                    continue
                
                try:
                    body = part.get_payload(decode=True)
                    if body:
                        charset = part.get_content_charset() or 'utf-8'
                        body = body.decode(charset, errors='ignore')
                        
                        if content_type == "text/plain":
                            text_body = body
                        elif content_type == "text/html":
                            html_body = body
                except:
                    continue
        else:
            content_type = msg.get_content_type()
            try:
                body = msg.get_payload(decode=True)
                if body:
                    charset = msg.get_content_charset() or 'utf-8'
                    body = body.decode(charset, errors='ignore')
                    
                    if content_type == "text/plain":
                        text_body = body
                    elif content_type == "text/html":
                        html_body = body
            except:
                pass
        
        # 优先使用纯文本，如果没有则使用HTML（可以后续用BeautifulSoup清理）
        return text_body or html_body, html_body
    
    def _parse_attachments(self, msg, email_id: str = None) -> tuple:
        """解析邮件附件并保存到文件系统（包括内嵌图片）
        
        Args:
            msg: 邮件消息对象
            email_id: 邮件ID（用于创建附件目录）
            
        Returns:
            (attachments, inline_images): 附件列表和内嵌图片映射字典
        """
        import os
        from pathlib import Path
        import uuid
        import time
        
        attachments = []
        inline_images = {}  # CID -> 文件路径映射
        
        # 创建附件存储目录
        attachments_dir = Path('attachments')
        attachments_dir.mkdir(exist_ok=True)
        
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                content_type = part.get_content_type()
                content_id = part.get("Content-ID", "")
                
                # 🔥 检查是否是内嵌图片（有 Content-ID 且是图片类型）
                # 关键判断：内嵌图片一定有 Content-ID，用于 HTML 中的 cid: 引用
                # 兼容性判断：某些邮件客户端将内嵌图片的 Content-Type 设为 application/octet-stream
                # 因此需要同时检查文件扩展名
                
                # 获取文件名（可能为空）
                temp_filename = part.get_filename()
                if temp_filename:
                    temp_filename = self._decode_str(temp_filename).lower()
                
                # 判断是否为图片类型（通过 Content-Type 或文件扩展名）
                is_image_type = (
                    content_type.startswith('image/') or
                    (temp_filename and any(temp_filename.endswith(ext) for ext in 
                     ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.ico']))
                )
                
                # 最终判断：必须有 Content-ID 且是图片类型
                is_inline_image = content_id and is_image_type
                
                # 检查是否是附件或内嵌图片
                if "attachment" in content_disposition or part.get_filename() or is_inline_image:
                    filename = part.get_filename()
                    
                    # 如果是内嵌图片但没有文件名，从CID生成
                    if is_inline_image and not filename:
                        # 清理CID（移除尖括号）
                        cid = content_id.strip('<>')
                        # 从CID生成文件名
                        ext = content_type.split('/')[-1]  # image/jpeg -> jpeg
                        filename = f"inline_{cid.split('@')[0]}.{ext}"
                    
                    if filename:
                        # 解码附件名
                        filename = self._decode_str(filename)
                        
                        # 获取二进制数据
                        payload = part.get_payload(decode=True)
                        size = len(payload) if payload else 0
                        
                        # 生成唯一文件名（避免重名）
                        timestamp = int(time.time() * 1000)
                        unique_id = str(uuid.uuid4())[:8]
                        file_ext = os.path.splitext(filename)[1]
                        safe_filename = f"{timestamp}_{unique_id}{file_ext}"
                        
                        # 保存到文件系统
                        file_path = attachments_dir / safe_filename
                        if payload:
                            try:
                                with open(file_path, 'wb') as f:
                                    f.write(payload)
                                print(f"💾 文件已保存: {file_path}")
                            except Exception as e:
                                print(f"⚠️ 保存文件失败: {str(e)}")
                                file_path = None
                        
                        file_info = {
                            'filename': filename,
                            'stored_filename': safe_filename,
                            'file_path': str(file_path) if file_path else None,
                            'content_type': content_type,
                            'size': size
                        }
                        
                        # 🔥 如果是内嵌图片，添加到映射字典
                        if is_inline_image and content_id:
                            cid = content_id.strip('<>')
                            inline_images[cid] = safe_filename
                            print(f"🖼️ 内嵌图片: {cid} -> {safe_filename}")
                        else:
                            # 普通附件
                            attachments.append(file_info)
                            print(f"📎 附件: {filename} ({size} bytes) -> {safe_filename}")
        
        return attachments, inline_images
    
    def _download_external_images(self, html_content: str, email_id: str) -> dict:
        """下载外部图片并保存到本地
        
        Args:
            html_content: HTML内容
            email_id: 邮件ID
            
        Returns:
            {original_url: stored_filename} 图片URL映射字典
        """
        import re
        import requests
        from pathlib import Path
        import uuid
        import time
        from urllib.parse import urlparse
        
        if not html_content:
            return {}
        
        image_mapping = {}
        attachments_dir = Path('attachments')
        attachments_dir.mkdir(exist_ok=True)
        
        # 提取所有 img 标签的 src
        img_pattern = r'<img[^>]+src=["\']([^"\'>]+)["\']'
        img_urls = re.findall(img_pattern, html_content, re.IGNORECASE)
        
        for url in img_urls:
            # 跳过 cid: 引用（已经处理）和 data: URL
            if url.startswith('cid:') or url.startswith('data:'):
                continue
            
            # 只处理 http/https 链接
            if not url.startswith('http://') and not url.startswith('https://'):
                continue
            
            try:
                print(f"🌐 下载外部图片: {url}")
                
                # 下载图片（设置超时和 User-Agent）
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10, stream=True)
                
                if response.status_code == 200:
                    # 获取文件扩展名
                    content_type = response.headers.get('Content-Type', '')
                    if 'image' in content_type:
                        ext = content_type.split('/')[-1].split(';')[0]  # image/jpeg -> jpeg
                    else:
                        # 从 URL 提取扩展名
                        parsed = urlparse(url)
                        ext = Path(parsed.path).suffix.lstrip('.') or 'jpg'
                    
                    # 生成唯一文件名
                    timestamp = int(time.time() * 1000)
                    unique_id = str(uuid.uuid4())[:8]
                    safe_filename = f"external_{timestamp}_{unique_id}.{ext}"
                    
                    # 保存图片
                    file_path = attachments_dir / safe_filename
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    image_mapping[url] = safe_filename
                    print(f"✅ 图片已保存: {safe_filename}")
                else:
                    print(f"⚠️ 下载失败 ({response.status_code}): {url}")
                    
            except Exception as e:
                print(f"❌ 下载图片失败: {url} - {str(e)}")
                continue
        
        return image_mapping
    
    def _process_html_images(self, html_content: str, email_id: str, inline_images: dict) -> str:
        """处理HTML中的所有图片引用
        
        Args:
            html_content: HTML内容
            email_id: 邮件ID
            inline_images: CID到文件名的映射
            
        Returns:
            处理后的HTML内容
        """
        if not html_content:
            return html_content
        
        processed_html = html_content
        
        # 1. 处理 cid: 引用（内嵌图片）- 使用简单的字符串替换
        for cid, stored_filename in inline_images.items():
            old_src = f'cid:{cid}'
            new_src = f'/api/email_history/{email_id}/images/{stored_filename}'
            processed_html = processed_html.replace(old_src, new_src)
            print(f"🔄 CID替换: {old_src} -> {new_src}")
        
        # 2. 下载并替换外部图片
        external_images = self._download_external_images(processed_html, email_id)
        
        for original_url, stored_filename in external_images.items():
            # 替换为 API 路径
            new_url = f'/api/email_history/{email_id}/images/{stored_filename}'
            processed_html = processed_html.replace(original_url, new_url)
            print(f"🔄 URL替换: {original_url[:50]}... -> {new_url}")
        
        return processed_html
    
    def fetch_new_emails(self, mailbox: str = "INBOX", limit: int = 100, 
                         only_unseen: bool = False, since_date: str = None) -> List[Dict]:
        """
        获取新邮件
        
        参数:
            mailbox: 邮箱文件夹 (INBOX/Sent/Trash等)
            limit: 获取数量限制（设为0则不限制）
            only_unseen: 只获取未读邮件
            since_date: 从哪个日期开始（格式：YYYY-MM-DD）
        
        返回:
            邮件列表
        """
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            # 选择邮箱文件夹
            self.connection.select(mailbox)
            
            # 搜索邮件
            search_criteria = "UNSEEN" if only_unseen else "ALL"
            
            # 如果指定了日期，添加日期过滤
            if since_date:
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(since_date, "%Y-%m-%d")
                    date_str = date_obj.strftime("%d-%b-%Y")  # IMAP日期格式
                    if only_unseen:
                        search_criteria = f'(UNSEEN SINCE "{date_str}")'
                    else:
                        search_criteria = f'(SINCE "{date_str}")'
                except Exception as e:
                    print(f"⚠️ 日期格式错误，忽略日期过滤: {str(e)}")
            
            status, messages = self.connection.search(None, search_criteria)
            
            if status != 'OK':
                print(f"❌ 搜索邮件失败")
                return []
            
            email_ids = messages[0].split()
            
            if not email_ids:
                print(f"📭 没有找到新邮件")
                return []
            
            # 限制数量（获取最新的N封）
            if limit > 0:
                email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            
            for email_id in reversed(email_ids):  # 从最新的开始
                try:
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # 解析邮件
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # 提取邮件信息
                    subject = self._decode_str(msg.get('Subject', ''))
                    
                    # 解析发件人（同时提取名称和邮箱）
                    from_str = self._decode_str(msg.get('From', ''))
                    from_name, from_addr = self._parse_email_name_and_address(from_str)
                    
                    # 解析收件人（同时提取名称和邮箱）
                    to_str = self._decode_str(msg.get('To', ''))
                    to_name, to_addr = self._parse_email_name_and_address(to_str)
                    
                    date_str = msg.get('Date', '')
                    
                    # 解析日期
                    email_date = None
                    try:
                        email_date = email.utils.parsedate_to_datetime(date_str)
                    except:
                        email_date = datetime.now()
                    
                    # 解析正文
                    text_body, html_body = self._parse_email_body(msg)
                    
                    # 🔥 解析附件和内嵌图片
                    attachments, inline_images = self._parse_attachments(msg, email_id.decode())
                    
                    # 🔥 不在这里处理图片，等保存到数据库后使用正确的 DB ID 处理
                    # 将 inline_images 映射传递给调用方，供后续处理

                    email_data = {
                        'email_id': email_id.decode(),
                        'subject': subject,
                        'from_name': from_name,  # 新增：发件人名称
                        'from_email': from_addr,
                        'to_name': to_name,  # 新增：收件人名称
                        'to_email': to_addr,
                        'date': email_date,
                        'body': text_body,
                        'html_body': html_body,
                        'attachments': attachments,
                        'inline_images': inline_images,  # 🔥 新增：传递 CID 映射
                        'has_attachments': len(attachments) > 0,
                        'message_id': msg.get('Message-ID', ''),
                        'in_reply_to': msg.get('In-Reply-To', '')
                    }
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    print(f"❌ 解析邮件失败: {str(e)}")
                    continue
            
            print(f"✅ 成功获取 {len(emails)} 封邮件")
            return emails
            
        except Exception as e:
            print(f"❌ 获取邮件失败: {str(e)}")
            return []
    
    def mark_as_read(self, email_id: str):
        """标记邮件为已读"""
        try:
            self.connection.store(email_id, '+FLAGS', '\\Seen')
        except Exception as e:
            print(f"❌ 标记已读失败: {str(e)}")
    
    def get_mailbox_list(self) -> List[str]:
        """获取邮箱文件夹列表"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            status, mailboxes = self.connection.list()
            if status == 'OK':
                return [self._decode_str(m.split(b'"')[-2]) for m in mailboxes]
            return []
        except Exception as e:
            print(f"❌ 获取文件夹列表失败: {str(e)}")
            return []


def test_email_receiver():
    """测试邮件接收器"""
    print("=" * 60)
    print("邮件接收器测试")
    print("=" * 60)
    
    # 示例配置（实际使用时需要真实账号）
    email_address = "your_email@gmail.com"
    password = "your_app_password"  # Gmail需要使用应用专用密码
    
    receiver = EmailReceiver(email_address, password, provider='gmail')
    
    if receiver.connect():
        # 获取邮箱文件夹
        print("\n📁 邮箱文件夹:")
        folders = receiver.get_mailbox_list()
        for folder in folders[:5]:  # 只显示前5个
            print(f"  - {folder}")
        
        # 获取新邮件
        print("\n📧 获取新邮件:")
        emails = receiver.fetch_new_emails(limit=5, only_unseen=True)
        
        for i, email_data in enumerate(emails, 1):
            print(f"\n邮件 {i}:")
            print(f"  发件人: {email_data['from_email']}")
            print(f"  主题: {email_data['subject']}")
            print(f"  日期: {email_data['date']}")
            print(f"  附件: {len(email_data['attachments'])} 个")
            print(f"  正文预览: {email_data['body'][:100]}...")
        
        receiver.disconnect()
    else:
        print("❌ 连接失败，请检查账号配置")


if __name__ == "__main__":
    test_email_receiver()
