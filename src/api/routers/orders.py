from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List

from src.crm.database import get_session, Order
from ..schemas import OrderCreate, OrderUpdate, OrderOut

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/orders", response_model=List[OrderOut])
def list_orders(
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

    query = db.query(Order)
    search = f.get("search", "")
    status = f.get("status", "")
    if search:
        like = f"%{search}%"
        query = query.filter((Order.order_number.ilike(like)) | (Order.factory_name.ilike(like)))
    if status:
        query = query.filter(Order.status == status)

    if sort_field and hasattr(Order, sort_field):
        if sort_order == "DESC":
            query = query.order_by(getattr(Order, sort_field).desc())
        else:
            query = query.order_by(getattr(Order, sort_field).asc())

    total = query.count()
    items = query.offset(start).limit(end - start + 1).all()

    response.headers["Content-Range"] = f"orders {start}-{min(end, start + len(items) - 1)}/{total}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return items


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return o


@router.post("/orders", response_model=OrderOut)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    order = Order(**order_in.dict())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.put("/orders/{order_id}", response_model=OrderOut)
def update_order(order_id: int, order_upd: OrderUpdate, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    for k, v in order_upd.dict(exclude_unset=True).items():
        setattr(o, k, v)
    db.commit()
    db.refresh(o)
    return o


@router.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(o)
    db.commit()
    return {"deleted": True, "id": order_id}
