from datetime import datetime, timedelta
from sqlalchemy import func


class CustomerAnalytics:
    """客户分析工具 - 提供专业的客户洞察"""
    
    def __init__(self, db_session):
        self.session = db_session
    
    def get_customer_lifetime_value(self, customer_id):
        """计算客户生命周期价值（CLV）"""
        from src.crm.database import Order, Customer
        
        customer = self.session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            return 0
        
        # 实际贡献
        orders = self.session.query(Order).filter_by(customer_id=customer_id).all()
        total_value = sum(float(o.total_amount or 0) for o in orders)
        
        # 更新客户实际年采购额
        customer.actual_annual_value = total_value
        
        return total_value
    
    def calculate_customer_health_score(self, customer_id):
        """计算客户健康度评分（0-100）"""
        from src.crm.database import Customer, EmailHistory, Order
        
        customer = self.session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            return 0
        
        score = 0
        
        # 1. 订单活跃度（30分）
        orders = self.session.query(Order).filter_by(customer_id=customer_id).all()
        if len(orders) > 0:
            score += 15
        if len(orders) > 3:
            score += 10
        if len(orders) > 10:
            score += 5
        
        # 2. 邮件互动度（30分）
        emails = self.session.query(EmailHistory).filter_by(customer_id=customer_id).all()
        replied_count = sum(1 for e in emails if e.replied)
        if emails:
            reply_rate = replied_count / len(emails)
            score += int(reply_rate * 30)
        
        # 3. 最近活跃度（20分）
        if customer.last_contact_date:
            days_since = (datetime.now() - customer.last_contact_date).days
            if days_since < 7:
                score += 20
            elif days_since < 30:
                score += 15
            elif days_since < 90:
                score += 10
        
        # 4. 订单金额（20分）
        total_amount = sum(float(o.total_amount or 0) for o in orders)
        if total_amount > 50000:
            score += 20
        elif total_amount > 20000:
            score += 15
        elif total_amount > 5000:
            score += 10
        
        return min(score, 100)
    
    def get_churn_risk(self, customer_id):
        """预测客户流失风险（Low/Medium/High）"""
        from src.crm.database import Customer
        
        customer = self.session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            return "Unknown"
        
        risk_score = 0
        
        # 1. 长时间未联系
        if customer.last_contact_date:
            days_since = (datetime.now() - customer.last_contact_date).days
            if days_since > 90:
                risk_score += 3
            elif days_since > 60:
                risk_score += 2
            elif days_since > 30:
                risk_score += 1
        else:
            risk_score += 2
        
        # 2. 邮件无回复
        from src.crm.database import EmailHistory
        recent_emails = self.session.query(EmailHistory).filter(
            EmailHistory.customer_id == customer_id,
            EmailHistory.direction == 'outbound'
        ).order_by(EmailHistory.sent_at.desc()).limit(5).all()
        
        replied_count = sum(1 for e in recent_emails if e.replied)
        if recent_emails and replied_count == 0:
            risk_score += 2
        
        # 3. 状态判断
        if customer.status in ['lost']:
            risk_score += 5
        elif customer.status in ['cold']:
            risk_score += 1
        
        # 分类
        if risk_score >= 5:
            return "High"
        elif risk_score >= 3:
            return "Medium"
        else:
            return "Low"
    
    def recommend_next_action(self, customer_id):
        """推荐下一步行动"""
        from src.crm.database import Customer, Order
        
        customer = self.session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            return "无可用建议"
        
        # 根据状态和最后联系时间推荐
        if customer.status == 'cold':
            return "发送开发信，介绍产品优势"
        elif customer.status == 'contacted':
            return "跟进邮件回复，询问需求细节"
        elif customer.status == 'replied':
            return "准备报价方案，发送样品册"
        elif customer.status == 'qualified':
            return "安排视频会议，洽谈合作细节"
        elif customer.status == 'negotiating':
            recent_orders = self.session.query(Order).filter_by(
                customer_id=customer_id
            ).order_by(Order.order_date.desc()).limit(1).all()
            if recent_orders and recent_orders[0].status == 'quotation':
                return "跟进报价，提供优惠方案促成订单"
            return "推进合同签署，确认订单细节"
        elif customer.status == 'customer':
            return "定期回访，询问产品使用情况，推荐新品"
        elif customer.status == 'lost':
            return "分析失败原因，6个月后重新激活"
        
        return "持续跟进，保持联系"
    
    def get_top_customers(self, limit=10, metric='revenue'):
        """获取TOP客户"""
        from src.crm.database import Customer, Order
        
        customers = self.session.query(Customer).all()
        customer_scores = []
        
        for customer in customers:
            orders = self.session.query(Order).filter_by(customer_id=customer.id).all()
            
            if metric == 'revenue':
                score = sum(float(o.total_amount or 0) for o in orders)
            elif metric == 'order_count':
                score = len(orders)
            elif metric == 'health':
                score = self.calculate_customer_health_score(customer.id)
            else:
                score = 0
            
            customer_scores.append({
                'customer': customer,
                'score': score
            })
        
        # 排序
        customer_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return customer_scores[:limit]
