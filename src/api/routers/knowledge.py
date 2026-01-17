"""知识库相关 API 路由 - FAQ、价格规则、案例库"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
import json

from src.crm.database import get_session, KnowledgeFAQ, PricingRule, CaseStudy

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


# ============ FAQ Schemas ============
class FAQBase(BaseModel):
    category: str
    language: str
    question_en: str
    answer_en: str
    question_zh: Optional[str] = None
    answer_zh: Optional[str] = None
    keywords: Optional[str] = None
    priority: Optional[int] = 0
    is_active: Optional[bool] = True
    related_products: Optional[str] = None
    notes: Optional[str] = None


class FAQCreate(FAQBase):
    pass


class FAQUpdate(BaseModel):
    category: Optional[str] = None
    language: Optional[str] = None
    question_en: Optional[str] = None
    answer_en: Optional[str] = None
    question_zh: Optional[str] = None
    answer_zh: Optional[str] = None
    keywords: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    related_products: Optional[str] = None
    notes: Optional[str] = None


class FAQOut(FAQBase):
    id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Pricing Rule Schemas ============
class PricingRuleBase(BaseModel):
    rule_name: str
    rule_type: str
    description: Optional[str] = None
    conditions: Optional[str] = None
    pricing_logic: Optional[str] = None
    priority: Optional[int] = 0
    is_active: Optional[bool] = True
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class PricingRuleCreate(PricingRuleBase):
    pass


class PricingRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    rule_type: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[str] = None
    pricing_logic: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class PricingRuleOut(PricingRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Case Study Schemas ============
class CaseStudyBase(BaseModel):
    title: str
    customer_name: Optional[str] = None
    customer_country: Optional[str] = None
    business_stage: str
    product_skus: Optional[str] = None
    order_quantity: Optional[int] = None
    order_value: Optional[float] = None
    challenge: Optional[str] = None
    solution: Optional[str] = None
    result: Optional[str] = None
    key_points: Optional[str] = None
    email_excerpts: Optional[str] = None
    success_score: Optional[int] = 8
    lessons_learned: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class CaseStudyCreate(CaseStudyBase):
    pass


class CaseStudyUpdate(BaseModel):
    title: Optional[str] = None
    customer_name: Optional[str] = None
    customer_country: Optional[str] = None
    business_stage: Optional[str] = None
    product_skus: Optional[str] = None
    order_quantity: Optional[int] = None
    order_value: Optional[float] = None
    challenge: Optional[str] = None
    solution: Optional[str] = None
    result: Optional[str] = None
    key_points: Optional[str] = None
    email_excerpts: Optional[str] = None
    success_score: Optional[int] = None
    lessons_learned: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class CaseStudyOut(CaseStudyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ FAQ API 端点 ============
@router.get("/knowledge_faqs", response_model=List[FAQOut])
def list_faqs(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,19]"),
    sort: str = Query('["id","ASC"]'),
    db: Session = Depends(get_db),
):
    try:
        f = json.loads(filter)
    except:
        f = {}
    try:
        r = json.loads(range)
        start, end = int(r[0]), int(r[1])
    except:
        start, end = 0, 19
    try:
        s = json.loads(sort)
        sort_field, sort_order = s[0], s[1]
    except:
        sort_field, sort_order = "id", "ASC"

    query = db.query(KnowledgeFAQ)
    
    category = f.get("category", "")
    language = f.get("language", "")
    search = f.get("search", "")
    
    if category:
        query = query.filter(KnowledgeFAQ.category == category)
    if language:
        query = query.filter(KnowledgeFAQ.language == language)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (KnowledgeFAQ.question_en.ilike(like)) | 
            (KnowledgeFAQ.answer_en.ilike(like)) |
            (KnowledgeFAQ.question_zh.ilike(like)) |
            (KnowledgeFAQ.answer_zh.ilike(like))
        )

    if sort_field and hasattr(KnowledgeFAQ, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(KnowledgeFAQ, sort_field).desc())
        else:
            query = query.order_by(getattr(KnowledgeFAQ, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    response.headers["Content-Range"] = f"knowledge_faqs {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/knowledge_faqs/{fid}", response_model=FAQOut)
def get_faq(fid: int, db: Session = Depends(get_db)):
    faq = db.query(KnowledgeFAQ).filter(KnowledgeFAQ.id == fid).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


@router.post("/knowledge_faqs", response_model=FAQOut)
def create_faq(faq_in: FAQCreate, db: Session = Depends(get_db)):
    faq = KnowledgeFAQ(**faq_in.dict())
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.put("/knowledge_faqs/{fid}", response_model=FAQOut)
def update_faq(fid: int, faq_upd: FAQUpdate, db: Session = Depends(get_db)):
    faq = db.query(KnowledgeFAQ).filter(KnowledgeFAQ.id == fid).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    for k, v in faq_upd.dict(exclude_unset=True).items():
        setattr(faq, k, v)
    
    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/knowledge_faqs/{fid}")
def delete_faq(fid: int, db: Session = Depends(get_db)):
    faq = db.query(KnowledgeFAQ).filter(KnowledgeFAQ.id == fid).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    db.delete(faq)
    db.commit()
    return {"deleted": True, "id": fid}


# ============ Pricing Rule API 端点 ============
@router.get("/pricing_rules", response_model=List[PricingRuleOut])
def list_pricing_rules(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,19]"),
    sort: str = Query('["id","ASC"]'),
    db: Session = Depends(get_db),
):
    try:
        f = json.loads(filter)
    except:
        f = {}
    try:
        r = json.loads(range)
        start, end = int(r[0]), int(r[1])
    except:
        start, end = 0, 19
    try:
        s = json.loads(sort)
        sort_field, sort_order = s[0], s[1]
    except:
        sort_field, sort_order = "id", "ASC"

    query = db.query(PricingRule)
    
    rule_type = f.get("rule_type", "")
    search = f.get("search", "")
    
    if rule_type:
        query = query.filter(PricingRule.rule_type == rule_type)
    if search:
        like = f"%{search}%"
        query = query.filter(PricingRule.rule_name.ilike(like))

    if sort_field and hasattr(PricingRule, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(PricingRule, sort_field).desc())
        else:
            query = query.order_by(getattr(PricingRule, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    response.headers["Content-Range"] = f"pricing_rules {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/pricing_rules/{rid}", response_model=PricingRuleOut)
def get_pricing_rule(rid: int, db: Session = Depends(get_db)):
    rule = db.query(PricingRule).filter(PricingRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    return rule


@router.post("/pricing_rules", response_model=PricingRuleOut)
def create_pricing_rule(rule_in: PricingRuleCreate, db: Session = Depends(get_db)):
    rule = PricingRule(**rule_in.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/pricing_rules/{rid}", response_model=PricingRuleOut)
def update_pricing_rule(rid: int, rule_upd: PricingRuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(PricingRule).filter(PricingRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    
    for k, v in rule_upd.dict(exclude_unset=True).items():
        setattr(rule, k, v)
    
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/pricing_rules/{rid}")
def delete_pricing_rule(rid: int, db: Session = Depends(get_db)):
    rule = db.query(PricingRule).filter(PricingRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    db.delete(rule)
    db.commit()
    return {"deleted": True, "id": rid}


# ============ Case Study API 端点 ============
@router.get("/case_studies", response_model=List[CaseStudyOut])
def list_case_studies(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,19]"),
    sort: str = Query('["id","ASC"]'),
    db: Session = Depends(get_db),
):
    try:
        f = json.loads(filter)
    except:
        f = {}
    try:
        r = json.loads(range)
        start, end = int(r[0]), int(r[1])
    except:
        start, end = 0, 19
    try:
        s = json.loads(sort)
        sort_field, sort_order = s[0], s[1]
    except:
        sort_field, sort_order = "id", "ASC"

    query = db.query(CaseStudy)
    
    business_stage = f.get("business_stage", "")
    search = f.get("search", "")
    
    if business_stage:
        query = query.filter(CaseStudy.business_stage == business_stage)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (CaseStudy.title.ilike(like)) | 
            (CaseStudy.customer_name.ilike(like)) |
            (CaseStudy.product_skus.ilike(like))
        )

    if sort_field and hasattr(CaseStudy, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(CaseStudy, sort_field).desc())
        else:
            query = query.order_by(getattr(CaseStudy, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    response.headers["Content-Range"] = f"case_studies {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/case_studies/{cid}", response_model=CaseStudyOut)
def get_case_study(cid: int, db: Session = Depends(get_db)):
    case = db.query(CaseStudy).filter(CaseStudy.id == cid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case study not found")
    return case


@router.post("/case_studies", response_model=CaseStudyOut)
def create_case_study(case_in: CaseStudyCreate, db: Session = Depends(get_db)):
    case = CaseStudy(**case_in.dict())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.put("/case_studies/{cid}", response_model=CaseStudyOut)
def update_case_study(cid: int, case_upd: CaseStudyUpdate, db: Session = Depends(get_db)):
    case = db.query(CaseStudy).filter(CaseStudy.id == cid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case study not found")
    
    for k, v in case_upd.dict(exclude_unset=True).items():
        setattr(case, k, v)
    
    db.commit()
    db.refresh(case)
    return case


@router.delete("/case_studies/{cid}")
def delete_case_study(cid: int, db: Session = Depends(get_db)):
    case = db.query(CaseStudy).filter(CaseStudy.id == cid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case study not found")
    db.delete(case)
    db.commit()
    return {"deleted": True, "id": cid}
