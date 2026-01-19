"""客户标签管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from src.crm.database import get_session, CustomerTag, Customer

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


# ============ Schemas ============
class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#1677ff"
    description: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class TagOut(TagBase):
    id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BatchTagRequest(BaseModel):
    customer_ids: List[int]
    tag_ids: List[int]
    action: str  # 'add' or 'remove'


# ============ Tags API ============
@router.get("/tags", response_model=List[TagOut])
def list_tags(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,99]"),
    sort: str = Query('["id","ASC"]'),
    db: Session = Depends(get_db),
):
    """获取标签列表"""
    try:
        f = json.loads(filter)
    except:
        f = {}
    
    try:
        r = json.loads(range)
        start, end = int(r[0]), int(r[1])
    except:
        start, end = 0, 99
    
    try:
        s = json.loads(sort)
        sort_field, sort_order = s[0], s[1]
    except:
        sort_field, sort_order = "id", "ASC"

    query = db.query(CustomerTag)
    
    # 搜索
    search = f.get("q", "")
    if search:
        like = f"%{search}%"
        query = query.filter(CustomerTag.name.ilike(like))

    # 排序
    if sort_field and hasattr(CustomerTag, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(CustomerTag, sort_field).desc())
        else:
            query = query.order_by(getattr(CustomerTag, sort_field).asc())

    # 总数
    total = query.count()
    
    # 分页
    tags = query.offset(start).limit(end - start + 1).all()
    
    # 设置响应头
    response.headers["Content-Range"] = f"tags {start}-{end}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    
    return tags


@router.get("/tags/{tag_id}", response_model=TagOut)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取单个标签"""
    tag = db.query(CustomerTag).filter(CustomerTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag


@router.post("/tags", response_model=TagOut)
def create_tag(tag_in: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    # 检查名称是否已存在
    existing = db.query(CustomerTag).filter(CustomerTag.name == tag_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签名称已存在")
    
    tag = CustomerTag(**tag_in.dict())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.put("/tags/{tag_id}", response_model=TagOut)
def update_tag(tag_id: int, tag_in: TagUpdate, db: Session = Depends(get_db)):
    """更新标签"""
    tag = db.query(CustomerTag).filter(CustomerTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    # 检查名称冲突
    if tag_in.name and tag_in.name != tag.name:
        existing = db.query(CustomerTag).filter(CustomerTag.name == tag_in.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="标签名称已存在")
    
    # 更新字段
    for field, value in tag_in.dict(exclude_unset=True).items():
        setattr(tag, field, value)
    
    tag.updated_at = datetime.now()
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """删除标签"""
    tag = db.query(CustomerTag).filter(CustomerTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    # 从所有客户中移除该标签
    customers = db.query(Customer).all()
    for customer in customers:
        if customer.tags:
            tags_list = [t.strip() for t in customer.tags.split(',') if t.strip()]
            if tag.name in tags_list:
                tags_list.remove(tag.name)
                customer.tags = ','.join(tags_list) if tags_list else None
    
    db.delete(tag)
    db.commit()
    
    return {"message": "标签已删除"}


@router.post("/tags/batch")
def batch_tag_customers(request: BatchTagRequest, db: Session = Depends(get_db)):
    """批量为客户打标签或移除标签"""
    # 获取标签
    tags = db.query(CustomerTag).filter(CustomerTag.id.in_(request.tag_ids)).all()
    if not tags:
        raise HTTPException(status_code=400, detail="标签不存在")
    
    tag_names = [tag.name for tag in tags]
    
    # 获取客户
    customers = db.query(Customer).filter(Customer.id.in_(request.customer_ids)).all()
    if not customers:
        raise HTTPException(status_code=400, detail="客户不存在")
    
    updated_count = 0
    
    for customer in customers:
        # 获取现有标签
        existing_tags = []
        if customer.tags:
            existing_tags = [t.strip() for t in customer.tags.split(',') if t.strip()]
        
        if request.action == 'add':
            # 添加标签（去重）
            for tag_name in tag_names:
                if tag_name not in existing_tags:
                    existing_tags.append(tag_name)
                    updated_count += 1
        elif request.action == 'remove':
            # 移除标签
            for tag_name in tag_names:
                if tag_name in existing_tags:
                    existing_tags.remove(tag_name)
                    updated_count += 1
        
        # 更新客户标签
        customer.tags = ','.join(existing_tags) if existing_tags else None
    
    # 更新标签使用次数
    if request.action == 'add':
        for tag in tags:
            tag.usage_count += len(customers)
    
    db.commit()
    
    return {
        "message": f"批量操作成功",
        "updated_count": updated_count,
        "customers_count": len(customers),
        "tags_count": len(tag_names)
    }
