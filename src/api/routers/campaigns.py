from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List

from src.crm.database import get_session, EmailCampaign
from ..schemas import CampaignCreate, CampaignUpdate, CampaignOut

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/email_campaigns", response_model=List[CampaignOut])
def list_campaigns(
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

    query = db.query(EmailCampaign)
    status = f.get("status", "")
    search = f.get("search", "")
    if status:
        query = query.filter(EmailCampaign.status == status)
    if search:
        like = f"%{search}%"
        query = query.filter(EmailCampaign.name.ilike(like))

    if sort_field and hasattr(EmailCampaign, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(EmailCampaign, sort_field).desc())
        else:
            query = query.order_by(getattr(EmailCampaign, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    response.headers["Content-Range"] = f"email_campaigns {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/email_campaigns/{cid}", response_model=CampaignOut)
def get_campaign(cid: int, db: Session = Depends(get_db)):
    c = db.query(EmailCampaign).filter(EmailCampaign.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return c


@router.post("/email_campaigns", response_model=CampaignOut)
def create_campaign(c_in: CampaignCreate, db: Session = Depends(get_db)):
    c = EmailCampaign(**c_in.dict())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/email_campaigns/{cid}", response_model=CampaignOut)
def update_campaign(cid: int, c_upd: CampaignUpdate, db: Session = Depends(get_db)):
    c = db.query(EmailCampaign).filter(EmailCampaign.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for k, v in c_upd.dict(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/email_campaigns/{cid}")
def delete_campaign(cid: int, db: Session = Depends(get_db)):
    c = db.query(EmailCampaign).filter(EmailCampaign.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(c)
    db.commit()
    return {"deleted": True, "id": cid}
