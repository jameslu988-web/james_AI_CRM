from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging

from src.crm.database import get_session, Customer
from ..schemas import CustomerCreate, CustomerUpdate, CustomerOut
from ..exceptions import BusinessException, DatabaseException, ResourceNotFoundException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/customers", response_model=List[CustomerOut])
def list_customers(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,19]"),
    sort: str = Query('["id","ASC"]'),
    db: Session = Depends(get_db),
):
    import json
    from fastapi import Response
    # 解析 React Admin 传参
    try:
        f = json.loads(filter)
    except Exception:
        f = {}
    try:
        r = json.loads(range)
        start, end = int(r[0]), int(r[1])
    except Exception:
        start, end = 0, 19
    try:
        s = json.loads(sort)
        sort_field, sort_order = s[0], s[1]
    except Exception:
        sort_field, sort_order = "id", "DESC"  # 默认按ID倒序（最新的在前）

    query = db.query(Customer)
    # 过滤条件
    search = f.get("search", "")
    company_name = f.get("company_name", "")
    contact_name = f.get("contact_name", "")
    email = f.get("email", "")
    status = f.get("status", "")
    country = f.get("country", "")
    customer_grade = f.get("customer_grade", "")
    
    # 通用搜索（在多个字段中搜索）
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Customer.company_name.ilike(like))
            | (Customer.contact_name.ilike(like))
            | (Customer.email.ilike(like))
        )
    
    # 按具体字段搜索（模糊匹配）
    if company_name:
        query = query.filter(Customer.company_name.ilike(f"%{company_name}%"))
    if contact_name:
        query = query.filter(Customer.contact_name.ilike(f"%{contact_name}%"))
    if email:
        query = query.filter(Customer.email.ilike(f"%{email}%"))
    
    # 精确匹配字段
    if status:
        query = query.filter(Customer.status == status)
    if country:
        query = query.filter(Customer.country.ilike(f"%{country}%"))
    if customer_grade:
        query = query.filter(Customer.customer_grade == customer_grade)

    # 排序
    if sort_field and hasattr(Customer, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(Customer, sort_field).desc())
        else:
            query = query.order_by(getattr(Customer, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    # 设置 Content-Range 头
    response.headers["Content-Range"] = f"customers {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        logger.warning(f"客户不存在: customer_id={customer_id}")
        raise ResourceNotFoundException("客户不存在", details={"customer_id": customer_id})
    return c


@router.post("/customers", response_model=CustomerOut)
def create_customer(customer_in: CustomerCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"创建客户请求", extra={"data": customer_in.dict()})
        
        customer = Customer(**customer_in.dict())
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        logger.info(f"创建客户成功", extra={"customer_id": customer.id, "company_name": customer.company_name})
        return customer
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"创建客户失败: 数据库错误", extra={"error": str(e)})
        raise DatabaseException(f"创建客户失败: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"创建客户失败: 未知错误", extra={"error": str(e), "type": type(e).__name__})
        raise BusinessException(f"创建客户失败: {str(e)}")


@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, customer_upd: CustomerUpdate, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        logger.warning(f"更新客户失败: 客户不存在", extra={"customer_id": customer_id})
        raise ResourceNotFoundException("客户不存在", details={"customer_id": customer_id})
    
    try:
        update_data = customer_upd.dict(exclude_unset=True)
        logger.info(f"更新客户", extra={"customer_id": customer_id, "fields": list(update_data.keys())})
        
        for k, v in update_data.items():
            setattr(c, k, v)
        db.commit()
        db.refresh(c)
        
        logger.info(f"更新客户成功", extra={"customer_id": customer_id})
        return c
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"更新客户失败: 数据库错误", extra={"customer_id": customer_id, "error": str(e)})
        raise DatabaseException(f"更新客户失败: {str(e)}")


@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        logger.warning(f"删除客户失败: 客户不存在", extra={"customer_id": customer_id})
        raise ResourceNotFoundException("客户不存在", details={"customer_id": customer_id})
    
    try:
        logger.warning(f"删除客户", extra={"customer_id": customer_id, "company_name": c.company_name})
        db.delete(c)
        db.commit()
        logger.info(f"删除客户成功", extra={"customer_id": customer_id})
        return {"deleted": True, "id": customer_id}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"删除客户失败: 数据库错误", extra={"customer_id": customer_id, "error": str(e)})
        raise DatabaseException(f"删除客户失败: {str(e)}")
