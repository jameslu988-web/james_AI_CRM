from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from src.crm.database import get_session, EmailTemplate

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


# 预定义的快捷回复模板
DEFAULT_QUICK_REPLIES = [
    {
        "name": "询价回复-专业报价",
        "category": "inquiry",
        "subject": "Re: Product Inquiry",
        "body": """Dear {contact_name},

Thank you for your inquiry about our men's underwear products.

Based on your requirements, here is our quotation:

• Product: Men's Cotton Boxer Briefs
• MOQ: 500 pcs per design
• Price: $3.50-$5.80/pc (depending on quantity)
• Lead time: 25-30 days after sample approval
• Payment: 30% deposit, 70% before shipment

We can provide free samples for your evaluation. Would you like us to send you our latest catalog?

Best regards,
{sender_name}""",
        "variables": json.dumps(["contact_name", "sender_name"]),
        "language": "en",
        "is_active": True
    },
    {
        "name": "询价回复-快速响应",
        "category": "inquiry",
        "subject": "Re: {original_subject}",
        "body": """Hi {contact_name},

Thank you for reaching out! We'd be happy to provide a quotation.

To prepare an accurate quote, could you please share:
• Target quantity per order
• Preferred materials/styles
• Target delivery date
• Your location for shipping calculation

I'll send you a detailed proposal within 24 hours.

Best,
{sender_name}""",
        "variables": json.dumps(["contact_name", "sender_name", "original_subject"]),
        "language": "en",
        "is_active": True
    },
    {
        "name": "样品寄送确认",
        "category": "sample",
        "subject": "Sample Shipment Confirmation",
        "body": """Dear {contact_name},

Thank you for your interest in our samples!

We offer FREE samples, you only need to cover the shipping cost (approximately ${shipping_cost} by DHL/FedEx).

Please provide:
• Full shipping address
• Contact phone number
• Preferred styles/sizes

We'll send the samples within 2-3 business days and provide tracking information.

Best regards,
{sender_name}""",
        "variables": json.dumps(["contact_name", "sender_name", "shipping_cost"]),
        "language": "en",
        "is_active": True
    },
    {
        "name": "订单确认",
        "category": "order",
        "subject": "Order Confirmation - {order_number}",
        "body": """Dear {contact_name},

Thank you for your order! We're excited to work with you.

Order confirmed:
• Order No.: {order_number}
• Quantity: {quantity} pcs
• Total Amount: ${total_amount}
• Deposit: ${deposit_amount} (30%)
• Production time: {production_days} days

Please find the attached Proforma Invoice. Once we receive the deposit, we'll start production immediately.

Looking forward to a successful cooperation!

Best regards,
{sender_name}""",
        "variables": json.dumps(["contact_name", "sender_name", "order_number", "quantity", "total_amount", "deposit_amount", "production_days"]),
        "language": "en",
        "is_active": True
    },
    {
        "name": "物流更新",
        "category": "follow_up",
        "subject": "Shipping Update - Order {order_number}",
        "body": """Dear {contact_name},

Great news! Your order {order_number} has been shipped.

Shipping details:
• Tracking Number: {tracking_number}
• Carrier: {shipping_company}
• Estimated Delivery: {estimated_delivery}

You can track your shipment at: {tracking_url}

If you have any questions, please don't hesitate to contact us.

Best regards,
{sender_name}""",
        "variables": json.dumps(["contact_name", "sender_name", "order_number", "tracking_number", "shipping_company", "estimated_delivery", "tracking_url"]),
        "language": "en",
        "is_active": True
    },
    {
        "name": "催款提醒",
        "category": "follow_up",
        "subject": "Payment Reminder - Order {order_number}",
        "body": """Dear {contact_name},

I hope this email finds you well.

This is a friendly reminder regarding the payment for Order {order_number}.

Payment details:
• Amount Due: ${amount_due}
• Due Date: {due_date}
• Invoice Number: {invoice_number}

Please let me know if you need any assistance with the payment process.

Thank you for your cooperation!

Best regards,
{sender_name}""",
        "variables": json.dumps(["contact_name", "sender_name", "order_number", "amount_due", "due_date", "invoice_number"]),
        "language": "en",
        "is_active": True
    },
    {
        "name": "投诉处理-诚挚道歉",
        "category": "complaint",
        "subject": "Re: {original_subject}",
        "body": """Dear {contact_name},

Thank you for bringing this to our attention. We sincerely apologize for the inconvenience.

We take quality very seriously and are investigating this issue immediately. Here's how we'll resolve it:

1. Send replacement products at no charge
2. Provide compensation/discount on next order
3. Improve our QC process to prevent future issues

Could we schedule a call today to discuss the best solution for you?

Once again, our apologies for this situation.

Best regards,
{sender_name}""",
        "variables": json.dumps(["contact_name", "sender_name", "original_subject"]),
        "language": "en",
        "is_active": True
    },
    {
        "name": "节日问候",
        "category": "general",
        "subject": "Happy {holiday_name}!",
        "body": """Dear {contact_name},

Wishing you and your family a wonderful {holiday_name}!

Thank you for your continued support and partnership. We look forward to working with you in the coming year.

Best wishes,
{sender_name} and Team""",
        "variables": json.dumps(["contact_name", "sender_name", "holiday_name"]),
        "language": "en",
        "is_active": True
    }
]


@router.post("/quick-replies/init")
def init_quick_replies(db: Session = Depends(get_db)):
    """初始化默认快捷回复模板"""
    created = 0
    for template_data in DEFAULT_QUICK_REPLIES:
        # 检查是否已存在
        existing = db.query(EmailTemplate).filter(
            EmailTemplate.name == template_data["name"]
        ).first()
        
        if not existing:
            template = EmailTemplate(
                **template_data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(template)
            created += 1
    
    db.commit()
    return {
        "message": f"成功创建 {created} 个快捷回复模板",
        "total": len(DEFAULT_QUICK_REPLIES)
    }


@router.get("/quick-replies")
def list_quick_replies(
    category: str = Query(None),
    db: Session = Depends(get_db)
):
    """获取快捷回复模板列表"""
    query = db.query(EmailTemplate).filter(EmailTemplate.is_active == True)
    
    if category:
        query = query.filter(EmailTemplate.category == category)
    
    templates = query.all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "subject": t.subject,
            "body": t.body,
            "variables": json.loads(t.variables) if t.variables else [],
            "language": t.language,
            "usage_count": t.usage_count or 0
        }
        for t in templates
    ]


@router.get("/quick-replies/categories")
def get_categories():
    """获取所有模板分类"""
    return {
        "categories": [
            {"id": "inquiry", "name": "询价回复"},
            {"id": "quotation", "name": "报价"},
            {"id": "order", "name": "订单"},
            {"id": "sample", "name": "样品"},
            {"id": "follow_up", "name": "跟进"},
            {"id": "complaint", "name": "投诉处理"},
            {"id": "general", "name": "通用"}
        ]
    }


@router.post("/quick-replies/{template_id}/use")
def use_template(template_id: int, db: Session = Depends(get_db)):
    """使用模板（增加使用次数）"""
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    template.usage_count = (template.usage_count or 0) + 1
    db.commit()
    
    return {"message": "模板使用次数已更新", "usage_count": template.usage_count}
