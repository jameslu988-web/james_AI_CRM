from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging

from src.crm.database import get_session, EmailTemplate
from ..schemas import TemplateCreate, TemplateUpdate, TemplateOut
from ..exceptions import BusinessException, DatabaseException, ResourceNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)


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
        logger.warning(f"邮件模板不存在", extra={"template_id": tid})
        raise ResourceNotFoundException("邮件模板不存在", details={"template_id": tid})
    return t


@router.post("/email_templates", response_model=TemplateOut)
def create_template(t_in: TemplateCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"创建邮件模板", extra={"name": t_in.name, "category": t_in.category})
        t = EmailTemplate(**t_in.dict())
        db.add(t)
        db.commit()
        db.refresh(t)
        logger.info(f"创建邮件模板成功", extra={"template_id": t.id, "name": t.name})
        return t
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"创建邮件模板失败: 数据库错误", extra={"error": str(e)})
        raise DatabaseException(f"创建邮件模板失败: {str(e)}")


@router.put("/email_templates/{tid}", response_model=TemplateOut)
def update_template(tid: int, t_upd: TemplateUpdate, db: Session = Depends(get_db)):
    t = db.query(EmailTemplate).filter(EmailTemplate.id == tid).first()
    if not t:
        logger.warning(f"更新邮件模板失败: 模板不存在", extra={"template_id": tid})
        raise ResourceNotFoundException("邮件模板不存在", details={"template_id": tid})
    
    try:
        update_data = t_upd.dict(exclude_unset=True)
        logger.info(f"更新邮件模板", extra={"template_id": tid, "fields": list(update_data.keys())})
        for k, v in update_data.items():
            setattr(t, k, v)
        db.commit()
        db.refresh(t)
        logger.info(f"更新邮件模板成功", extra={"template_id": tid})
        return t
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"更新邮件模板失败: 数据库错误", extra={"template_id": tid, "error": str(e)})
        raise DatabaseException(f"更新邮件模板失败: {str(e)}")


@router.delete("/email_templates/{tid}")
def delete_template(tid: int, db: Session = Depends(get_db)):
    t = db.query(EmailTemplate).filter(EmailTemplate.id == tid).first()
    if not t:
        logger.warning(f"删除邮件模板失败: 模板不存在", extra={"template_id": tid})
        raise ResourceNotFoundException("邮件模板不存在", details={"template_id": tid})
    
    try:
        logger.warning(f"删除邮件模板", extra={"template_id": tid, "name": t.name})
        db.delete(t)
        db.commit()
        logger.info(f"删除邮件模板成功", extra={"template_id": tid})
        return {"deleted": True, "id": tid}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"删除邮件模板失败: 数据库错误", extra={"template_id": tid, "error": str(e)})
        raise DatabaseException(f"删除邮件模板失败: {str(e)}")
