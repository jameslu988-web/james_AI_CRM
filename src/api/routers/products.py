"""产品知识库 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from src.crm.database import get_session, Product

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


# Pydantic Schemas
class ProductBase(BaseModel):
    sku: str
    name_en: str
    name_zh: Optional[str] = None
    category: Optional[str] = None
    description_en: Optional[str] = None
    description_zh: Optional[str] = None
    features: Optional[str] = None
    sizes: Optional[str] = None
    colors: Optional[str] = None
    materials: Optional[str] = None
    weight_gram: Optional[int] = None
    packaging_unit: Optional[str] = None
    moq: int
    base_price: float
    production_days: Optional[int] = None
    sample_price: Optional[float] = None
    sample_days: Optional[int] = None
    main_image_url: Optional[str] = None
    images: Optional[str] = None
    certifications: Optional[str] = None
    customization_options: Optional[str] = None
    is_active: Optional[bool] = True
    notes: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name_en: Optional[str] = None
    name_zh: Optional[str] = None
    category: Optional[str] = None
    description_en: Optional[str] = None
    description_zh: Optional[str] = None
    features: Optional[str] = None
    sizes: Optional[str] = None
    colors: Optional[str] = None
    materials: Optional[str] = None
    weight_gram: Optional[int] = None
    packaging_unit: Optional[str] = None
    moq: Optional[int] = None
    base_price: Optional[float] = None
    production_days: Optional[int] = None
    sample_price: Optional[float] = None
    sample_days: Optional[int] = None
    main_image_url: Optional[str] = None
    images: Optional[str] = None
    certifications: Optional[str] = None
    customization_options: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# API 端点
@router.get("/products", response_model=List[ProductOut])
def list_products(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,19]"),
    sort: str = Query('["id","ASC"]'),
    db: Session = Depends(get_db),
):
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
        sort_field, sort_order = "id", "ASC"

    query = db.query(Product)
    
    # 过滤条件
    category = f.get("category", "")
    search = f.get("search", "")
    
    if category:
        query = query.filter(Product.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Product.sku.ilike(like)) | 
            (Product.name_en.ilike(like)) | 
            (Product.name_zh.ilike(like))
        )

    # 排序
    if sort_field and hasattr(Product, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(Product, sort_field).desc())
        else:
            query = query.order_by(getattr(Product, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    response.headers["Content-Range"] = f"products {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/products/{pid}", response_model=ProductOut)
def get_product(pid: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@router.post("/products", response_model=ProductOut)
def create_product(p_in: ProductCreate, db: Session = Depends(get_db)):
    # 检查SKU是否已存在
    existing = db.query(Product).filter(Product.sku == p_in.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"SKU {p_in.sku} already exists")
    
    p = Product(**p_in.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/products/{pid}", response_model=ProductOut)
def update_product(pid: int, p_upd: ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for k, v in p_upd.dict(exclude_unset=True).items():
        setattr(p, k, v)
    
    db.commit()
    db.refresh(p)
    return p


@router.delete("/products/{pid}")
def delete_product(pid: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    return {"deleted": True, "id": pid}
