class NotificationSystem:
    """通知系统 - 支持多渠道推送"""
    
    def __init__(self, config=None):
        """
        初始化通知系统
        参数:
            config: 配置字典 {telegram_token, telegram_chat_id}
        """
        self.config = config or {}
        self.telegram_enabled = bool(self.config.get('telegram_token'))
    
    def send_telegram(self, message, parse_mode='Markdown'):
        """
        发送Telegram通知
        参数:
            message: 消息内容
            parse_mode: 格式化模式
        返回:
            bool: 是否成功
        """
        if not self.telegram_enabled:
            print(f"[Telegram未配置] {message}")
            return False
        
        try:
            # 占位实现 - 实际需集成 telegram API
            print(f"[Telegram通知] {message}")
            return True
        except Exception as e:
            print(f"Telegram发送失败: {e}")
            return False
    
    def send_alert(self, title, content, level='info'):
        """
        发送警报通知
        参数:
            title: 标题
            content: 内容
            level: 级别 (info/warning/error)
        """
        icons = {'info': 'ℹ️', 'warning': '⚠️', 'error': '🔴'}
        icon = icons.get(level, 'ℹ️')
        
        message = f"{icon} **{title}**\n\n{content}"
        return self.send_telegram(message)
    
    def send_daily_summary(self, stats):
        """
        发送每日摘要
        参数:
            stats: 统计数据字典
        """
        message = f"""
📊 **每日工作摘要**

**客户开发**
- 新增客户: {stats.get('new_customers', 0)}
- 活跃线索: {stats.get('active_leads', 0)}

**邮件营销**
- 发送邮件: {stats.get('emails_sent', 0)}
- 收到回复: {stats.get('emails_replied', 0)}
- 回复率: {stats.get('reply_rate', 0):.1f}%

**订单管理**
- 新增订单: {stats.get('new_orders', 0)}
- 延期订单: {stats.get('delayed_orders', 0)}
- 订单总额: ${stats.get('order_amount', 0):.2f}

---
⏰ {stats.get('date', 'Today')}
"""
        return self.send_telegram(message)
    
    def send_order_alert(self, order_number, customer_name, alert_type='delayed'):
        """
        发送订单提醒
        参数:
            order_number: 订单号
            customer_name: 客户名称
            alert_type: 提醒类型
        """
        alerts = {
            'delayed': '⚠️ 订单已延期',
            'shipped': '📦 订单已发货',
            'completed': '✅ 订单已完成'
        }
        
        title = alerts.get(alert_type, '订单更新')
        message = f"""
{title}

**订单号**: {order_number}
**客户**: {customer_name}

请及时跟进处理。
"""
        return self.send_telegram(message)
