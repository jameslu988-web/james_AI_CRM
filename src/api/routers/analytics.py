from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.crm.database import get_session
from src.utils.customer_analytics import CustomerAnalytics

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/customers/{customer_id}/analytics")
def customer_analytics(customer_id: int, db: Session = Depends(get_db)):
    ca = CustomerAnalytics(db)
    clv = ca.get_customer_lifetime_value(customer_id)
    health = ca.calculate_customer_health_score(customer_id)
    churn = ca.get_churn_risk(customer_id)
    next_action = ca.recommend_next_action(customer_id)
    return {
        "customer_id": customer_id,
        "clv": clv,
        "health_score": health,
        "churn_risk": churn,
        "next_action": next_action,
    }
