"""线索管理路由"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import or_, and_
from ...crm.database import get_session, Lead, Customer, User
import json

router = APIRouter()


def parse_range_header(range_header: Optional[str]) -> tuple:
    """解析 React Admin 的 Range 请求头"""
    if not range_header:
        return 0, 19
    try:
        start, end = map(int, range_header.strip('[]').split(','))
        return start, end
    except:
        return 0, 19


def parse_sort_header(sort_header: Optional[str]) -> tuple:
    """解析 React Admin 的 Sort 请求头"""
    if not sort_header:
        return 'id', 'ASC'
    try:
        field, order = json.loads(sort_header)
        return field, order
    except:
        return 'id', 'ASC'


@router.get("/leads")
def get_leads(
    range: Optional[str] = Header(None),
    sort: Optional[str] = Header(None),
    filter: Optional[str] = Header(None)
):
    """获取线索列表"""
    from fastapi.responses import Response
    db = get_session()
    
    # 解析参数
    start, end = parse_range_header(range)
    sort_field, sort_order = parse_sort_header(sort)
    
    # 构建查询
    query = db.query(Lead)
    
    # 过滤
    if filter:
        try:
            filter_dict = json.loads(filter)
            
            # 搜索过滤
            if 'q' in filter_dict:
                search = f"%{filter_dict['q']}%"
                query = query.filter(
                    or_(
                        Lead.company_name.ilike(search),
                        Lead.contact_name.ilike(search),
                        Lead.email.ilike(search)
                    )
                )
            
            # 线索状态过滤
            if 'lead_status' in filter_dict:
                query = query.filter(Lead.lead_status == filter_dict['lead_status'])
            
            # 优先级过滤
            if 'priority' in filter_dict:
                query = query.filter(Lead.priority == filter_dict['priority'])
            
            # 线索来源过滤
            if 'lead_source' in filter_dict:
                query = query.filter(Lead.lead_source == filter_dict['lead_source'])
            
            # 负责人过滤
            if 'assigned_to' in filter_dict:
                query = query.filter(Lead.assigned_to == filter_dict['assigned_to'])
            
            # 是否已转化过滤
            if 'converted' in filter_dict:
                query = query.filter(Lead.converted == filter_dict['converted'])
                
        except json.JSONDecodeError:
            pass
    
    # 获取总数
    total = query.count()
    
    # 排序
    if hasattr(Lead, sort_field):
        order_column = getattr(Lead, sort_field)
        if sort_order == 'DESC':
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
    # 分页
    leads = query.offset(start).limit(end - start + 1).all()
    
    # 转换为字典
    result = []
    for lead in leads:
        lead_dict = {
            'id': lead.id,
            'company_name': lead.company_name,
            'contact_name': lead.contact_name,
            'email': lead.email,
            'phone': lead.phone,
            'website': lead.website,
            'country': lead.country,
            'industry': lead.industry,
            'company_size': lead.company_size,
            'lead_source': lead.lead_source,
            'lead_status': lead.lead_status,
            'lead_score': lead.lead_score,
            'priority': lead.priority,
            'estimated_budget': lead.estimated_budget,
            'decision_timeframe': lead.decision_timeframe,
            'pain_points': lead.pain_points,
            'competitor_info': lead.competitor_info,
            'product_interest': lead.product_interest,
            'notes': lead.notes,
            'assigned_to': lead.assigned_to,
            'converted': lead.converted,
            'converted_customer_id': lead.converted_customer_id,
            'converted_at': lead.converted_at.isoformat() if lead.converted_at else None,
            'first_contact_date': lead.first_contact_date.isoformat() if lead.first_contact_date else None,
            'last_contact_date': lead.last_contact_date.isoformat() if lead.last_contact_date else None,
            'next_followup_date': lead.next_followup_date.isoformat() if lead.next_followup_date else None,
            'created_at': lead.created_at.isoformat() if lead.created_at else None,
            'updated_at': lead.updated_at.isoformat() if lead.updated_at else None,
            'created_by': lead.created_by,
        }
        result.append(lead_dict)
    
    # 返回结果，包含 Content-Range 头
    return Response(
        content=json.dumps(result),
        media_type="application/json",
        headers={
            "Content-Range": f"leads {start}-{min(end, total-1)}/{total}",
            "Access-Control-Expose-Headers": "Content-Range"
        }
    )


@router.get("/leads/{lead_id}")
def get_lead(lead_id: int):
    """获取单个线索详情"""
    db = get_session()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")
    
    return {
        'id': lead.id,
        'company_name': lead.company_name,
        'contact_name': lead.contact_name,
        'email': lead.email,
        'phone': lead.phone,
        'website': lead.website,
        'country': lead.country,
        'industry': lead.industry,
        'company_size': lead.company_size,
        'lead_source': lead.lead_source,
        'lead_status': lead.lead_status,
        'lead_score': lead.lead_score,
        'priority': lead.priority,
        'estimated_budget': lead.estimated_budget,
        'decision_timeframe': lead.decision_timeframe,
        'pain_points': lead.pain_points,
        'competitor_info': lead.competitor_info,
        'product_interest': lead.product_interest,
        'notes': lead.notes,
        'assigned_to': lead.assigned_to,
        'converted': lead.converted,
        'converted_customer_id': lead.converted_customer_id,
        'converted_at': lead.converted_at.isoformat() if lead.converted_at else None,
        'first_contact_date': lead.first_contact_date.isoformat() if lead.first_contact_date else None,
        'last_contact_date': lead.last_contact_date.isoformat() if lead.last_contact_date else None,
        'next_followup_date': lead.next_followup_date.isoformat() if lead.next_followup_date else None,
        'created_at': lead.created_at.isoformat() if lead.created_at else None,
        'updated_at': lead.updated_at.isoformat() if lead.updated_at else None,
        'created_by': lead.created_by,
    }


@router.post("/leads")
def create_lead(data: dict):
    """创建新线索"""
    db = get_session()
    
    # 创建线索对象
    lead = Lead(
        company_name=data.get('company_name'),
        contact_name=data.get('contact_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        website=data.get('website'),
        country=data.get('country'),
        industry=data.get('industry'),
        company_size=data.get('company_size'),
        lead_source=data.get('lead_source'),
        lead_status=data.get('lead_status', 'new'),
        lead_score=data.get('lead_score', 0),
        priority=data.get('priority', 'medium'),
        estimated_budget=data.get('estimated_budget'),
        decision_timeframe=data.get('decision_timeframe'),
        pain_points=data.get('pain_points'),
        competitor_info=data.get('competitor_info'),
        product_interest=data.get('product_interest'),
        notes=data.get('notes'),
        assigned_to=data.get('assigned_to'),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return {
        'id': lead.id,
        'company_name': lead.company_name,
        'lead_status': lead.lead_status,
        'created_at': lead.created_at.isoformat()
    }


@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, data: dict):
    """更新线索"""
    db = get_session()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")
    
    # 更新字段
    for key, value in data.items():
        if hasattr(lead, key) and key not in ['id', 'created_at', 'created_by']:
            setattr(lead, key, value)
    
    lead.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(lead)
    
    return {'id': lead.id, 'message': '更新成功'}


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int):
    """删除线索"""
    db = get_session()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")
    
    db.delete(lead)
    db.commit()
    
    return {'id': lead_id, 'message': '删除成功'}


@router.post("/leads/{lead_id}/convert")
def convert_lead_to_customer(lead_id: int):
    """将线索转化为客户"""
    db = get_session()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="线索不存在")
    
    if lead.converted:
        raise HTTPException(status_code=400, detail="该线索已经转化为客户")
    
    # 创建新客户
    customer = Customer(
        company_name=lead.company_name,
        contact_name=lead.contact_name,
        email=lead.email,
        phone=lead.phone,
        website=lead.website,
        country=lead.country,
        industry=lead.industry,
        company_size=lead.company_size,
        status='contacted',  # 默认状态为已联系
        source=lead.lead_source,
        priority=3 if lead.priority == 'medium' else (5 if lead.priority == 'high' else 1),
        estimated_value=lead.estimated_budget,
        first_contact_date=lead.first_contact_date,
        last_contact_date=lead.last_contact_date,
        next_followup_date=lead.next_followup_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(customer)
    db.flush()  # 获取新创建的customer.id
    
    # 更新线索状态
    lead.converted = True
    lead.converted_customer_id = customer.id
    lead.converted_at = datetime.utcnow()
    lead.lead_status = 'converted'
    lead.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        'lead_id': lead.id,
        'customer_id': customer.id,
        'message': '线索已成功转化为客户',
        'customer': {
            'id': customer.id,
            'company_name': customer.company_name,
            'email': customer.email
        }
    }


@router.get("/leads/stats/summary")
def get_leads_stats():
    """获取线索统计数据"""
    db = get_session()
    
    # 总线索数
    total_leads = db.query(Lead).count()
    
    # 新线索数
    new_leads = db.query(Lead).filter(Lead.lead_status == 'new').count()
    
    # 待跟进线索数（已联系和跟进中）
    pending_leads = db.query(Lead).filter(
        Lead.lead_status.in_(['contacted', 'in_progress'])
    ).count()
    
    # 合格线索数
    qualified_leads = db.query(Lead).filter(Lead.lead_status == 'qualified').count()
    
    # 已转化线索数
    converted_leads = db.query(Lead).filter(Lead.converted == True).count()
    
    # 转化率
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    # 平均评分
    avg_score_result = db.query(Lead.lead_score).filter(Lead.lead_score > 0).all()
    avg_score = sum([score[0] for score in avg_score_result]) / len(avg_score_result) if avg_score_result else 0
    
    # 按来源统计
    source_stats = {}
    sources = db.query(Lead.lead_source, db.func.count(Lead.id)).group_by(Lead.lead_source).all()
    for source, count in sources:
        source_stats[source or '未知'] = count
    
    return {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'pending_leads': pending_leads,
        'qualified_leads': qualified_leads,
        'converted_leads': converted_leads,
        'conversion_rate': round(conversion_rate, 2),
        'avg_score': round(avg_score, 1),
        'source_distribution': source_stats
    }
