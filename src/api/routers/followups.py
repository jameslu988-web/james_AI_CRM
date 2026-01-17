from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.crm.database import get_session, FollowupRecord
from ..schemas import FollowupCreate, FollowupUpdate, FollowupOut

router = APIRouter()


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
        raise HTTPException(status_code=404, detail="Followup not found")
    return rec


@router.post("/followup_records", response_model=FollowupOut)
def create_followup(f_in: FollowupCreate, db: Session = Depends(get_db)):
    data = f_in.dict()
    if not data.get("created_at"):
        data["created_at"] = datetime.now()
    rec = FollowupRecord(**data)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.put("/followup_records/{fid}", response_model=FollowupOut)
def update_followup(fid: int, f_upd: FollowupUpdate, db: Session = Depends(get_db)):
    rec = db.query(FollowupRecord).filter(FollowupRecord.id == fid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Followup not found")
    for k, v in f_upd.dict(exclude_unset=True).items():
        setattr(rec, k, v)
    db.commit()
    db.refresh(rec)
    return rec


@router.delete("/followup_records/{fid}")
def delete_followup(fid: int, db: Session = Depends(get_db)):
    rec = db.query(FollowupRecord).filter(FollowupRecord.id == fid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Followup not found")
    db.delete(rec)
    db.commit()
    return {"deleted": True, "id": fid}
