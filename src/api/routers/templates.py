from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List

from src.crm.database import get_session, EmailTemplate
from ..schemas import TemplateCreate, TemplateUpdate, TemplateOut

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/email_templates", response_model=List[TemplateOut])
def list_templates(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,19]"),
    sort: str = Query('["id","ASC"]'),
    db: Session = Depends(get_db),
):
    import json
    from fastapi import Response
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

    query = db.query(EmailTemplate)
    category = f.get("category", "")
    language = f.get("language", "")
    search = f.get("search", "")
    if category:
        query = query.filter(EmailTemplate.category == category)
    if language:
        query = query.filter(EmailTemplate.language == language)
    if search:
        like = f"%{search}%"
        query = query.filter((EmailTemplate.name.ilike(like)) | (EmailTemplate.subject.ilike(like)))

    if sort_field and hasattr(EmailTemplate, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(EmailTemplate, sort_field).desc())
        else:
            query = query.order_by(getattr(EmailTemplate, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    response.headers["Content-Range"] = f"email_templates {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/email_templates/{tid}", response_model=TemplateOut)
def get_template(tid: int, db: Session = Depends(get_db)):
    t = db.query(EmailTemplate).filter(EmailTemplate.id == tid).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return t


@router.post("/email_templates", response_model=TemplateOut)
def create_template(t_in: TemplateCreate, db: Session = Depends(get_db)):
    t = EmailTemplate(**t_in.dict())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/email_templates/{tid}", response_model=TemplateOut)
def update_template(tid: int, t_upd: TemplateUpdate, db: Session = Depends(get_db)):
    t = db.query(EmailTemplate).filter(EmailTemplate.id == tid).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    for k, v in t_upd.dict(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/email_templates/{tid}")
def delete_template(tid: int, db: Session = Depends(get_db)):
    t = db.query(EmailTemplate).filter(EmailTemplate.id == tid).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(t)
    db.commit()
    return {"deleted": True, "id": tid}
