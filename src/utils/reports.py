from datetime import datetime, timedelta
from sqlalchemy import func


class ReportGenerator:
    """报表生成器"""
    
    def __init__(self, db_session):
        self.session = db_session
    
    def get_weekly_stats(self):
        """获取周统计数据"""
        from src.crm.database import Customer, EmailHistory, Order
        
        # 本周起止时间
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        stats = {}
        
        # 新增客户
        new_customers = self.session.query(Customer).filter(
            Customer.created_at >= week_start
        ).count()
        stats['new_customers'] = new_customers
        
        # 发送邮件
        sent_emails = self.session.query(EmailHistory).filter(
            EmailHistory.direction == 'outbound',
            EmailHistory.sent_at >= week_start
        ).count()
        stats['emails_sent'] = sent_emails
        
        # 收到回复
        replied_emails = self.session.query(EmailHistory).filter(
            EmailHistory.direction == 'inbound',
            EmailHistory.sent_at >= week_start
        ).count()
        stats['emails_replied'] = replied_emails
        
        # 回复率
        stats['reply_rate'] = (replied_emails / sent_emails * 100) if sent_emails > 0 else 0
        
        # 新增订单
        new_orders = self.session.query(Order).filter(
            Order.order_date >= week_start
        ).count()
        stats['new_orders'] = new_orders
        
        # 订单金额
        order_amount = self.session.query(func.sum(Order.total_amount)).filter(
            Order.order_date >= week_start
        ).scalar() or 0
        stats['order_amount'] = float(order_amount)
        
        return stats
    
    def get_monthly_stats(self):
        """获取月统计数据"""
        from src.crm.database import Customer, EmailHistory, Order
        
        # 本月起止时间
        today = datetime.now()
        month_start = today.replace(day=1)
        
        stats = {}
        
        # 总客户数
        total_customers = self.session.query(Customer).count()
        stats['total_customers'] = total_customers
        
        # 本月新增
        new_customers = self.session.query(Customer).filter(
            Customer.created_at >= month_start
        ).count()
        stats['new_customers'] = new_customers
        
        # 活跃线索
        active_status = ['contacted', 'replied', 'qualified', 'negotiating']
        active_leads = self.session.query(Customer).filter(
            Customer.status.in_(active_status)
        ).count()
        stats['active_leads'] = active_leads
        
        # 本月订单
        month_orders = self.session.query(Order).filter(
            Order.order_date >= month_start
        ).all()
        stats['month_orders_count'] = len(month_orders)
        
        # 本月订单金额
        month_amount = sum(float(o.total_amount or 0) for o in month_orders)
        stats['month_amount'] = month_amount
        
        # 订单状态分布
        status_dist = {}
        for order in month_orders:
            status_dist[order.status] = status_dist.get(order.status, 0) + 1
        stats['status_distribution'] = status_dist
        
        return stats
    
    def generate_weekly_report(self):
        """生成周报文本"""
        stats = self.get_weekly_stats()
        
        report = f"""
📈 **本周业绩报告**
{'=' * 40}

**客户开发**
- 新增客户: {stats['new_customers']}

**邮件营销**
- 发送邮件: {stats['emails_sent']}
- 收到回复: {stats['emails_replied']}
- 回复率: {stats['reply_rate']:.1f}%

**销售转化**
- 新增订单: {stats['new_orders']}
- 订单金额: ${stats['order_amount']:.2f}

---
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        return report
    
    def get_customer_funnel(self):
        """获取客户漏斗数据"""
        from src.crm.database import Customer
        
        funnel = {}
        all_customers = self.session.query(Customer).all()
        
        for status in ['cold', 'contacted', 'replied', 'qualified', 'negotiating', 'customer', 'lost']:
            count = sum(1 for c in all_customers if (c.status or 'cold') == status)
            funnel[status] = count
        
        return funnel
