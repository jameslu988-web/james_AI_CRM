"""
客户分级系统 API
实现客户自动分级、画像生成、参与度评分
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.crm.database import get_session, Customer, EmailHistory, Order
from datetime import datetime
import json

router = APIRouter()


def calculate_engagement_score(customer: Customer, db: Session) -> float:
    """计算客户参与度评分 (0-100)"""
    score = 0
    
    # 1. 邮件互动评分 (40分)
    if customer.email_reply_count and customer.email_sent_count:
        reply_ratio = customer.email_reply_count / max(customer.email_sent_count, 1)
        score += min(reply_ratio * 40, 40)
    
    # 2. 订单历史评分 (30分)
    if customer.order_count:
        score += min(customer.order_count * 10, 30)
    
    # 3. 活跃度评分 (20分)
    if customer.last_active_date:
        days_inactive = (datetime.now() - customer.last_active_date).days
        if days_inactive <= 7:
            score += 20
        elif days_inactive <= 30:
            score += 15
        elif days_inactive <= 90:
            score += 10
        elif days_inactive <= 180:
            score += 5
    
    # 4. 响应速度评分 (10分)
    if customer.response_rate:
        if customer.response_rate > 0.7:
            score += 10
        elif customer.response_rate > 0.5:
            score += 7
        elif customer.response_rate > 0.3:
            score += 4
    
    return min(score, 100)


def calculate_customer_grade(customer: Customer) -> str:
    """计算客户分级 (A/B/C/D)"""
    engagement = customer.engagement_score or 0
    annual_value = customer.actual_annual_value or 0
    order_count = customer.order_count or 0
    
    # A级客户
    if annual_value > 50000 or order_count > 10 or engagement > 80:
        return 'A'
    # B级客户
    if (10000 < annual_value <= 50000) or (5 < order_count <= 10) or (60 < engagement <= 80):
        return 'B'
    # C级客户
    if (5000 < annual_value <= 10000) or (2 < order_count <= 5) or (40 < engagement <= 60):
        return 'C'
    # D级客户（默认）
    return 'D'


def update_customer_statistics(customer_id: int, db: Session):
    """更新客户统计数据"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return
    
    # 统计邮件
    email_sent = db.query(func.count(EmailHistory.id)).filter(
        EmailHistory.customer_id == customer_id,
        EmailHistory.direction == 'outbound'
    ).scalar() or 0
    
    email_received = db.query(func.count(EmailHistory.id)).filter(
        EmailHistory.customer_id == customer_id,
        EmailHistory.direction == 'inbound'
    ).scalar() or 0
    
    email_replied = db.query(func.count(EmailHistory.id)).filter(
        EmailHistory.customer_id == customer_id,
        EmailHistory.direction == 'inbound',
        EmailHistory.replied == True
    ).scalar() or 0
    
    # 统计订单
    order_count = db.query(func.count(Order.id)).filter(
        Order.customer_id == customer_id
    ).scalar() or 0
    
    total_amount = db.query(func.sum(Order.total_amount)).filter(
        Order.customer_id == customer_id
    ).scalar() or 0
    
    # 计算指标
    avg_order_value = total_amount / order_count if order_count > 0 else 0
    response_rate = email_replied / email_sent if email_sent > 0 else 0
    
    # 获取最后活跃时间
    last_email = db.query(EmailHistory).filter(
        EmailHistory.customer_id == customer_id
    ).order_by(EmailHistory.sent_at.desc()).first()
    
    last_active = last_email.sent_at if last_email else customer.created_at
    days_since_contact = (datetime.now() - last_active).days if last_active else 0
    
    # 更新客户
    customer.email_sent_count = email_sent
    customer.email_received_count = email_received
    customer.email_reply_count = email_replied
    customer.order_count = order_count
    customer.total_order_amount = total_amount
    customer.average_order_value = avg_order_value
    customer.response_rate = response_rate
    customer.last_active_date = last_active
    customer.days_since_last_contact = days_since_contact
    customer.actual_annual_value = total_amount
    
    db.commit()


# ⚠️ 注意：特定路由必须放在通配路由之前！
@router.post("/grade-all")
def grade_all_customers(db: Session = Depends(get_session)):
    """为所有客户进行批量分级"""
    customers = db.query(Customer).all()
    
    results = {
        "total": len(customers),
        "upgraded": 0,
        "downgraded": 0,
        "unchanged": 0
    }
    
    for customer in customers:
        old_grade = customer.customer_grade
        
        update_customer_statistics(customer.id, db)
        customer.engagement_score = calculate_engagement_score(customer, db)
        new_grade = calculate_customer_grade(customer)
        customer.customer_grade = new_grade
        customer.last_grading_date = datetime.now()
        
        # 统计变化
        if old_grade and new_grade:
            grade_order = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
            if grade_order.get(new_grade, 0) > grade_order.get(old_grade, 0):
                results["upgraded"] += 1
            elif grade_order.get(new_grade, 0) < grade_order.get(old_grade, 0):
                results["downgraded"] += 1
            else:
                results["unchanged"] += 1
    
    db.commit()
    return results


@router.get("/grade-distribution")
def get_grade_distribution(db: Session = Depends(get_session)):
    """获取客户分级分布统计"""
    grades = ['A', 'B', 'C', 'D']
    distribution = {}
    
    for grade in grades:
        count = db.query(func.count(Customer.id)).filter(
            Customer.customer_grade == grade
        ).scalar() or 0
        
        customers = db.query(Customer).filter(
            Customer.customer_grade == grade
        ).all()
        
        total_value = sum(c.actual_annual_value or 0 for c in customers)
        avg_engagement = sum(c.engagement_score or 0 for c in customers) / len(customers) if customers else 0
        
        distribution[grade] = {
            "count": count,
            "total_value": total_value,
            "avg_engagement": round(avg_engagement, 2),
            "percentage": round((count / db.query(func.count(Customer.id)).scalar() * 100), 2) if count > 0 else 0
        }
    
    return {
        "distribution": distribution,
        "total_customers": db.query(func.count(Customer.id)).scalar(),
        "generated_at": datetime.now().isoformat()
    }


@router.post("/{customer_id}/grade")
def grade_single_customer(customer_id: int, db: Session = Depends(get_session)):
    """为单个客户进行分级评估"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    old_grade = customer.customer_grade
    
    update_customer_statistics(customer_id, db)
    customer.engagement_score = calculate_engagement_score(customer, db)
    new_grade = calculate_customer_grade(customer)
    customer.customer_grade = new_grade
    customer.last_grading_date = datetime.now()
    
    reason_parts = []
    if customer.actual_annual_value and customer.actual_annual_value > 0:
        reason_parts.append(f"年采购额: ${customer.actual_annual_value:.2f}")
    if customer.order_count and customer.order_count > 0:
        reason_parts.append(f"订单数: {customer.order_count}")
    reason_parts.append(f"参与度: {customer.engagement_score:.1f}")
    
    customer.grading_reason = ", ".join(reason_parts)
    
    db.commit()
    db.refresh(customer)
    
    return {
        "customer_id": customer_id,
        "company_name": customer.company_name,
        "old_grade": old_grade,
        "new_grade": new_grade,
        "engagement_score": customer.engagement_score,
        "grading_reason": customer.grading_reason
    }


@router.get("/{customer_id}/profile")
def get_customer_profile(customer_id: int, db: Session = Depends(get_session)):
    """获取客户画像详情"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    # 获取订单历史
    orders = db.query(Order).filter(Order.customer_id == customer_id).limit(5).all()
    
    # 计算客户生命周期
    days_as_customer = 0
    if customer.created_at:
        days_as_customer = (datetime.now() - customer.created_at).days
    
    # 解析行为标签
    behavior_tags = []
    if customer.behavior_tags:
        try:
            behavior_tags = json.loads(customer.behavior_tags)
        except:
            pass
    
    return {
        "basic_info": {
            "customer_id": customer.id,
            "company_name": customer.company_name,
            "contact_name": customer.contact_name,
            "email": customer.email,
            "country": customer.country
        },
        "grading": {
            "grade": customer.customer_grade,
            "engagement_score": customer.engagement_score,
            "last_grading_date": customer.last_grading_date.isoformat() if customer.last_grading_date else None,
            "grading_reason": customer.grading_reason
        },
        "statistics": {
            "email_sent": customer.email_sent_count or 0,
            "email_received": customer.email_received_count or 0,
            "email_reply": customer.email_reply_count or 0,
            "order_count": customer.order_count or 0,
            "total_amount": customer.total_order_amount or 0,
            "response_rate": round(customer.response_rate or 0, 2)
        },
        "activity": {
            "last_active": customer.last_active_date.isoformat() if customer.last_active_date else None,
            "days_since_contact": customer.days_since_last_contact or 0,
            "days_as_customer": days_as_customer
        },
        "value": {
            "lifetime_value": customer.lifetime_value or 0,
            "actual_annual_value": customer.actual_annual_value or 0
        },
        "behavior_tags": behavior_tags
    }
