"""
销售漏斗可视化 API
提供销售漏斗各阶段的数据统计和转化率分析
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.crm.database import get_session, Customer
from typing import List, Dict

router = APIRouter()


# 客户阶段定义（按销售漏斗顺序）
FUNNEL_STAGES = [
    {'key': 'cold', 'name': '冷源客户', 'color': '#6b7280'},
    {'key': 'contacted', 'name': '已联系', 'color': '#3b82f6'},
    {'key': 'replied', 'name': '已回复', 'color': '#8b5cf6'},
    {'key': 'qualified', 'name': '合格线索', 'color': '#f59e0b'},
    {'key': 'negotiating', 'name': '谈判中', 'color': '#ef4444'},
    {'key': 'customer', 'name': '成交客户', 'color': '#10b981'},
]


@router.get("/funnel-data")
def get_funnel_data(db: Session = Depends(get_session)):
    """
    获取销售漏斗数据
    返回各阶段的客户数量和转化率
    """
    funnel_data = []
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    
    # 统计各阶段客户数量
    for i, stage in enumerate(FUNNEL_STAGES):
        count = db.query(func.count(Customer.id)).filter(
            Customer.status == stage['key']
        ).scalar() or 0
        
        # 计算转化率（相对于上一阶段）
        conversion_rate = 0
        if i > 0:
            prev_count = funnel_data[i-1]['count']
            if prev_count > 0:
                conversion_rate = round((count / prev_count) * 100, 2)
        
        # 计算占总客户的百分比
        percentage = round((count / total_customers * 100), 2) if total_customers > 0 else 0
        
        funnel_data.append({
            'stage': stage['key'],
            'name': stage['name'],
            'color': stage['color'],
            'count': count,
            'percentage': percentage,
            'conversion_rate': conversion_rate if i > 0 else 100  # 第一阶段转化率为100%
        })
    
    # 计算流失客户（已流失）
    lost_count = db.query(func.count(Customer.id)).filter(
        Customer.status == 'lost'
    ).scalar() or 0
    
    # 计算整体转化率（从冷源到成交）
    cold_count = funnel_data[0]['count'] if funnel_data else 0
    customer_count = funnel_data[-1]['count'] if funnel_data else 0
    overall_conversion = round((customer_count / cold_count * 100), 2) if cold_count > 0 else 0
    
    return {
        'funnel': funnel_data,
        'total_customers': total_customers,
        'lost_customers': lost_count,
        'overall_conversion_rate': overall_conversion,
        'stage_count': len(FUNNEL_STAGES)
    }


@router.get("/funnel-trends")
def get_funnel_trends(days: int = 30, db: Session = Depends(get_session)):
    """
    获取销售漏斗趋势数据（按时间）
    可用于展示各阶段客户数量的时间变化
    """
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    trends = []
    for stage in FUNNEL_STAGES:
        count = db.query(func.count(Customer.id)).filter(
            Customer.status == stage['key'],
            Customer.created_at >= start_date
        ).scalar() or 0
        
        trends.append({
            'stage': stage['key'],
            'name': stage['name'],
            'count': count
        })
    
    return {
        'period': f'{days}天',
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'trends': trends
    }


@router.get("/stage/{stage_key}/customers")
def get_stage_customers(stage_key: str, db: Session = Depends(get_session)):
    """
    获取指定阶段的客户列表
    用于点击漏斗某一层时展示该阶段的客户
    """
    customers = db.query(Customer).filter(
        Customer.status == stage_key
    ).limit(100).all()
    
    # 找到对应阶段名称
    stage_name = next((s['name'] for s in FUNNEL_STAGES if s['key'] == stage_key), stage_key)
    
    return {
        'stage': stage_key,
        'stage_name': stage_name,
        'count': len(customers),
        'customers': [
            {
                'id': c.id,
                'company_name': c.company_name,
                'contact_name': c.contact_name,
                'email': c.email,
                'customer_grade': c.customer_grade,
                'engagement_score': c.engagement_score
            }
            for c in customers
        ]
    }
