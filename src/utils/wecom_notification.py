"""
企业微信通知系统
支持企业应用消息和群机器人Webhook两种方式
"""
import requests
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# 🔥 加载环境变量
load_dotenv()


class WeComNotification:
    """企业微信通知类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化企业微信通知
        
        Args:
            config: 配置字典，包含以下可选项：
                - corp_id: 企业ID
                - corp_secret: 应用Secret
                - agent_id: 应用AgentID
                - webhook_url: 群机器人Webhook地址
                - frontend_url: 前端系统地址（用于生成审核链接）
        """
        self.config = config or {}
        
        # 企业应用配置
        self.corp_id = self.config.get('corp_id') or os.getenv('WECOM_CORP_ID')
        self.corp_secret = self.config.get('corp_secret') or os.getenv('WECOM_CORP_SECRET')
        self.agent_id = self.config.get('agent_id') or os.getenv('WECOM_AGENT_ID')
        
        # 群机器人配置
        self.webhook_url = self.config.get('webhook_url') or os.getenv('WECOM_WEBHOOK_URL')
        
        # 前端系统地址
        self.frontend_url = self.config.get('frontend_url') or os.getenv('FRONTEND_URL', 'http://localhost:5173')
        
        # Access Token缓存
        self._access_token = None
        self._token_expires_at = None
    
    def get_access_token(self) -> Optional[str]:
        """
        获取企业微信Access Token
        
        Returns:
            Access Token字符串，失败返回None
        """
        # 检查缓存
        if self._access_token and self._token_expires_at:
            if datetime.now().timestamp() < self._token_expires_at:
                return self._access_token
        
        if not self.corp_id or not self.corp_secret:
            print("⚠️ 企业微信应用未配置 CORP_ID 或 CORP_SECRET")
            return None
        
        try:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            params = {
                'corpid': self.corp_id,
                'corpsecret': self.corp_secret
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                self._access_token = result['access_token']
                # 提前5分钟过期，避免边界问题
                self._token_expires_at = datetime.now().timestamp() + result.get('expires_in', 7200) - 300
                print(f"✅ 获取企业微信Access Token成功")
                return self._access_token
            else:
                print(f"❌ 获取Access Token失败: {result.get('errmsg')}")
                return None
                
        except Exception as e:
            print(f"❌ 获取Access Token异常: {str(e)}")
            return None
    
    def send_app_message(self, user_ids: str, content: Dict[str, Any]) -> bool:
        """
        通过企业应用发送消息
        
        Args:
            user_ids: 用户ID，多个用|分隔，如 "user1|user2"，或使用 "@all" 发送给全部
            content: 消息内容字典
            
        Returns:
            是否发送成功
        """
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        if not self.agent_id:
            print("⚠️ 未配置企业微信应用 AGENT_ID")
            return False
        
        try:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
            
            data = {
                "touser": user_ids,
                "msgtype": content.get('msgtype', 'text'),
                "agentid": int(self.agent_id),
                **content
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                print(f"✅ 企业微信应用消息发送成功")
                return True
            else:
                print(f"❌ 发送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            print(f"❌ 发送企业微信应用消息异常: {str(e)}")
            return False
    
    def send_webhook_message(self, content: Dict[str, Any]) -> bool:
        """
        通过群机器人Webhook发送消息
        
        Args:
            content: 消息内容字典
            
        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("⚠️ 未配置企业微信群机器人 WEBHOOK_URL")
            return False
        
        try:
            response = requests.post(self.webhook_url, json=content, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                print(f"✅ 企业微信群机器人消息发送成功")
                return True
            else:
                print(f"❌ 发送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            print(f"❌ 发送企业微信群机器人消息异常: {str(e)}")
            return False
    
    def send_approval_notification(
        self, 
        task_id: int, 
        email_subject: str,
        email_from: str,
        email_category: str,
        draft_subject: str,
        urgency_level: str = "medium",
        user_ids: str = "@all",
        use_webhook: bool = True
    ) -> bool:
        """
        发送审核通知
        
        Args:
            task_id: 审核任务ID
            email_subject: 原始邮件主题
            email_from: 发件人
            email_category: 邮件类型
            draft_subject: 回复主题
            urgency_level: 紧急程度 (high/medium/low)
            user_ids: 接收用户ID（应用消息使用）
            use_webhook: 是否使用群机器人（默认true）
            
        Returns:
            是否发送成功
        """
        # 生成审核链接 - 使用移动端优化页面
        # 🔥 修复：使用实际IP地址，支持内网手机访问
        # 从frontend_url提取IP地址
        import re
        ip_match = re.search(r'https?://([\d\.]+|[\w\-\.]+):(\d+)', self.frontend_url)
        if ip_match:
            host = ip_match.group(1)
            port = ip_match.group(2)
            # 使用api_host参数传递后端IP地址
            approval_url = f"http://{host}:{port}/mobile-approval.html?id={task_id}&api_host={host}"
        else:
            approval_url = f"{self.frontend_url}/mobile-approval.html?id={task_id}"
        
        # 紧急程度标识
        urgency_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(urgency_level, '🟡')
        
        # 邮件类型中文名
        category_map = {
            'inquiry': '新客询盘',
            'quotation': '报价跟进',
            'sample': '样品阶段',
            'order': '订单确认',
            'complaint': '售后服务',
            'follow_up': '老客维护',
            'spam': '垃圾营销'
        }
        category_name = category_map.get(email_category, email_category)
        
        if use_webhook:
            # 使用Markdown格式的群机器人消息
            content = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"""## {urgency_emoji} 新的邮件审核任务
                    
> **邮件类型**: <font color="info">{category_name}</font>
> **发件人**: {email_from}
> **原邮件主题**: {email_subject}
> **AI回复主题**: {draft_subject}
> **紧急程度**: {urgency_emoji} {urgency_level.upper()}

请及时处理：[点击查看并审核]({approval_url})

---
<font color="comment">审核任务ID: {task_id} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>"""
                }
            }
            return self.send_webhook_message(content)
        else:
            # 使用企业应用文本卡片消息
            content = {
                "msgtype": "textcard",
                "textcard": {
                    "title": f"{urgency_emoji} 新的邮件审核任务",
                    "description": f"""邮件类型: {category_name}
发件人: {email_from}
原邮件: {email_subject}
AI回复: {draft_subject}
紧急程度: {urgency_level.upper()}

请及时处理审核任务""",
                    "url": approval_url,
                    "btntxt": "立即审核"
                }
            }
            return self.send_app_message(user_ids, content)
    
    def send_approval_result_notification(
        self, 
        task_id: int,
        status: str,
        approved_by: str,
        email_subject: str,
        use_webhook: bool = True
    ) -> bool:
        """
        发送审核结果通知
        
        Args:
            task_id: 审核任务ID
            status: 审核状态 (approved/rejected)
            approved_by: 审核人
            email_subject: 邮件主题
            use_webhook: 是否使用群机器人
            
        Returns:
            是否发送成功
        """
        status_map = {
            'approved': '✅ 已通过',
            'rejected': '❌ 已拒绝'
        }
        status_text = status_map.get(status, status)
        
        if use_webhook:
            content = {
                "msgtype": "text",
                "text": {
                    "content": f"""{status_text} - 邮件审核结果

任务ID: {task_id}
邮件主题: {email_subject}
审核人: {approved_by}
处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                }
            }
            return self.send_webhook_message(content)
        else:
            content = {
                "msgtype": "text",
                "text": {
                    "content": f"{status_text}\n任务ID: {task_id}\n邮件: {email_subject}\n审核人: {approved_by}"
                }
            }
            return self.send_app_message("@all", content)
    
    def send_custom_message(self, title: str, content: str, use_webhook: bool = True) -> bool:
        """
        发送自定义消息
        
        Args:
            title: 消息标题
            content: 消息内容
            use_webhook: 是否使用群机器人
            
        Returns:
            是否发送成功
        """
        if use_webhook:
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"{title}\n\n{content}"
                }
            }
            return self.send_webhook_message(message)
        else:
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"{title}\n{content}"
                }
            }
            return self.send_app_message("@all", message)


# 全局实例（可选）
_wecom_instance = None

def get_wecom_notification() -> WeComNotification:
    """获取企业微信通知单例"""
    global _wecom_instance
    if _wecom_instance is None:
        _wecom_instance = WeComNotification()
    return _wecom_instance
