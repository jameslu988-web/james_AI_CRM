from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
import logging

from src.crm.database import get_session, FollowupRecord
from ..schemas import FollowupCreate, FollowupUpdate, FollowupOut
from ..exceptions import BusinessException, DatabaseException, ResourceNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/followup_records", response_model=List[FollowupOut])
def list_followups(
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

    query = db.query(FollowupRecord)
    # 支持按客户、类型、搜索主题/内容
    customer_id = f.get("customer_id")
    followup_type = f.get("followup_type", "")
    search = f.get("search", "")
    if customer_id:
        query = query.filter(FollowupRecord.customer_id == int(customer_id))
    if followup_type:
        query = query.filter(FollowupRecord.followup_type == followup_type)
    if search:
        like = f"%{search}%"
        query = query.filter((FollowupRecord.subject.ilike(like)) | (FollowupRecord.content.ilike(like)))

    if sort_field and hasattr(FollowupRecord, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(FollowupRecord, sort_field).desc())
        else:
            query = query.order_by(getattr(FollowupRecord, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    response.headers["Content-Range"] = f"followup_records {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/followup_records/{fid}", response_model=FollowupOut)
def get_followup(fid: int, db: Session = Depends(get_db)):
    rec = db.query(FollowupRecord).filter(FollowupRecord.id == fid).first()
    if not rec:
        logger.warning(f"跟进记录不存在", extra={"followup_id": fid})
        raise ResourceNotFoundException("跟进记录不存在", details={"followup_id": fid})
    return rec


@router.post("/followup_records", response_model=FollowupOut)
def create_followup(f_in: FollowupCreate, db: Session = Depends(get_db)):
    try:
        data = f_in.dict()
        if not data.get("created_at"):
            data["created_at"] = datetime.now()
        logger.info(f"创建跟进记录", extra={"customer_id": data.get("customer_id"), "type": data.get("followup_type")})
        rec = FollowupRecord(**data)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        logger.info(f"创建跟进记录成功", extra={"followup_id": rec.id})
        return rec
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"创建跟进记录失败: 数据库错误", extra={"error": str(e)})
        raise DatabaseException(f"创建跟进记录失败: {str(e)}")


@router.put("/followup_records/{fid}", response_model=FollowupOut)
def update_followup(fid: int, f_upd: FollowupUpdate, db: Session = Depends(get_db)):
    rec = db.query(FollowupRecord).filter(FollowupRecord.id == fid).first()
    if not rec:
        logger.warning(f"更新跟进记录失败: 记录不存在", extra={"followup_id": fid})
        raise ResourceNotFoundException("跟进记录不存在", details={"followup_id": fid})
    
    try:
        update_data = f_upd.dict(exclude_unset=True)
        logger.info(f"更新跟进记录", extra={"followup_id": fid, "fields": list(update_data.keys())})
        for k, v in update_data.items():
            setattr(rec, k, v)
        db.commit()
        db.refresh(rec)
        logger.info(f"更新跟进记录成功", extra={"followup_id": fid})
        return rec
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"更新跟进记录失败: 数据库错误", extra={"followup_id": fid, "error": str(e)})
        raise DatabaseException(f"更新跟进记录失败: {str(e)}")


@router.delete("/followup_records/{fid}")
def delete_followup(fid: int, db: Session = Depends(get_db)):
    rec = db.query(FollowupRecord).filter(FollowupRecord.id == fid).first()
    if not rec:
        logger.warning(f"删除跟进记录失败: 记录不存在", extra={"followup_id": fid})
        raise ResourceNotFoundException("跟进记录不存在", details={"followup_id": fid})
    
    try:
        logger.warning(f"删除跟进记录", extra={"followup_id": fid})
        db.delete(rec)
        db.commit()
        logger.info(f"删除跟进记录成功", extra={"followup_id": fid})
        return {"deleted": True, "id": fid}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"删除跟进记录失败: 数据库错误", extra={"followup_id": fid, "error": str(e)})
        raise DatabaseException(f"删除跟进记录失败: {str(e)}")
