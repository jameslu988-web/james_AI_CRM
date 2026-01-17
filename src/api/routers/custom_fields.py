"""自定义字段管理路由"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.crm.database import CustomFieldDefinition, get_session

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


class CustomFieldCreate(BaseModel):
    field_name: str
    field_type: str = "text"
    is_visible: bool = True
    display_order: int = 0


class CustomFieldUpdate(BaseModel):
    field_name: str | None = None
    field_type: str | None = None
    is_visible: bool | None = None
    display_order: int | None = None


class CustomFieldOut(BaseModel):
    id: int
    field_name: str
    field_type: str
    is_visible: bool
    display_order: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


@router.get("/custom_fields", response_model=List[CustomFieldOut])
def list_custom_fields(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,19]"),
    sort: str = Query('["display_order","ASC"]'),
    db: Session = Depends(get_db),
):
    """获取所有自定义字段定义"""
    import json
    
    # 解析分页参数
    range_list = json.loads(range)
    start, end = range_list[0], range_list[1]
    
    # 解析排序参数
    sort_list = json.loads(sort)
    sort_field, sort_order = sort_list[0], sort_list[1]
    
    # 构建查询
    query = db.query(CustomFieldDefinition)
    
    # 排序
    if sort_order == "ASC":
        query = query.order_by(getattr(CustomFieldDefinition, sort_field))
    else:
        query = query.order_by(getattr(CustomFieldDefinition, sort_field).desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    items = query.offset(start).limit(end - start + 1).all()
    
    # 设置响应头
    response.headers["Content-Range"] = f"custom_fields {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    
    return items


@router.get("/custom_fields/{field_id}", response_model=CustomFieldOut)
def get_custom_field(field_id: int, db: Session = Depends(get_db)):
    """获取单个自定义字段"""
    field = db.query(CustomFieldDefinition).filter(CustomFieldDefinition.id == field_id).first()
    if not field:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="字段不存在")
    return field


@router.post("/custom_fields", response_model=CustomFieldOut)
def create_custom_field(field_in: CustomFieldCreate, db: Session = Depends(get_db)):
    """创建自定义字段"""
    # 检查字段名是否已存在
    existing = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.field_name == field_in.field_name
    ).first()
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="字段名已存在")
    
    # 创建字段
    field = CustomFieldDefinition(
        field_name=field_in.field_name,
        field_type=field_in.field_type,
        is_visible=field_in.is_visible,
        display_order=field_in.display_order,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return field


@router.put("/custom_fields/{field_id}", response_model=CustomFieldOut)
def update_custom_field(
    field_id: int, field_in: CustomFieldUpdate, db: Session = Depends(get_db)
):
    """更新自定义字段"""
    field = db.query(CustomFieldDefinition).filter(CustomFieldDefinition.id == field_id).first()
    if not field:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="字段不存在")
    
    # 更新字段
    update_data = field_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(field, key, value)
    
    field.updated_at = datetime.now()
    db.commit()
    db.refresh(field)
    return field


@router.delete("/custom_fields/{field_id}")
def delete_custom_field(field_id: int, db: Session = Depends(get_db)):
    """删除自定义字段"""
    field = db.query(CustomFieldDefinition).filter(CustomFieldDefinition.id == field_id).first()
    if not field:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="字段不存在")
    
    db.delete(field)
    db.commit()
    return {"id": field_id}
