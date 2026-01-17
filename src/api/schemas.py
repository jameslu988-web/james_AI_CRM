from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class CustomerBase(BaseModel):
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[str] = "cold"
    source: Optional[str] = None
    tags: Optional[str] = None  # 逗号分隔或JSON字符串
    customer_grade: Optional[str] = None  # A/B/C/D
    last_followup_note: Optional[str] = None
    linkedin_url: Optional[str] = None
    facebook_url: Optional[str] = None
    custom_fields: Optional[str] = None  # JSON字符串


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[str] = None
    customer_grade: Optional[str] = None
    last_followup_note: Optional[str] = None
    linkedin_url: Optional[str] = None
    facebook_url: Optional[str] = None
    custom_fields: Optional[str] = None


class CustomerOut(CustomerBase):
    id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_id: Optional[int] = None
    order_number: Optional[str] = None
    product_details: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    currency: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int

    class Config:
        from_attributes = True


class EmailBase(BaseModel):
    customer_id: Optional[int] = None
    direction: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    html_body: Optional[str] = None  # HTML版本邮件
    sent_at: Optional[datetime] = None
    from_name: Optional[str] = None  # 发件人名称（从邮件头部解析）
    from_email: Optional[str] = None
    to_name: Optional[str] = None  # 收件人名称（从邮件头部解析）
    to_email: Optional[str] = None
    cc_email: Optional[str] = None  # 抄送
    bcc_email: Optional[str] = None  # 密送
    status: Optional[str] = 'sent'  # draft/sent/failed
    ai_generated: Optional[bool] = False
    attachments: Optional[str] = None
    template_id: Optional[int] = None
    campaign_id: Optional[int] = None
    priority: Optional[str] = 'normal'  # high/normal/low
    need_receipt: Optional[bool] = False  # 已读回执
    # 🔥 添加邮件状态字段
    opened: Optional[bool] = None
    clicked: Optional[bool] = None
    replied: Optional[bool] = None
    is_starred: Optional[bool] = None  # 置顶标记
    tags: Optional[str] = None  # 标签
    follow_up_date: Optional[datetime] = None  # 跟进日期
    color_label: Optional[str] = None  # 颜色标签
    # 🔥 投递状态字段（新增）
    delivery_status: Optional[str] = None  # pending/delivered/bounced/spam/unknown
    delivery_time: Optional[datetime] = None  # 投递成功时间
    bounce_reason: Optional[str] = None  # 退信原因

class EmailCreate(EmailBase):
    pass

class EmailUpdate(EmailBase):
    # 🔥 软删除字段（回收站功能）
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None

class EmailOut(EmailBase):
    id: int
    # AI分析字段
    ai_sentiment: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None
    urgency_level: Optional[str] = None
    purchase_intent: Optional[str] = None
    purchase_intent_score: Optional[int] = None
    business_stage: Optional[str] = None
    secondary_category: Optional[str] = None
    budget_level: Optional[str] = None
    decision_authority: Optional[str] = None
    competition_status: Optional[str] = None
    customer_business_type: Optional[str] = None
    tone: Optional[str] = None
    satisfaction_level: Optional[str] = None
    response_deadline: Optional[str] = None
    business_impact: Optional[str] = None
    customer_type: Optional[str] = None
    customer_grade_suggestion: Optional[str] = None
    professionalism: Optional[str] = None
    communication_style: Optional[str] = None
    next_action: Optional[str] = None
    response_template_suggestion: Optional[str] = None
    requires_human_review: Optional[bool] = None
    human_review_reason: Optional[str] = None
    risk_level: Optional[str] = None
    opportunity_score: Optional[int] = None
    conversion_probability: Optional[int] = None
    estimated_order_value: Optional[str] = None
    tags: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    is_starred: Optional[bool] = None
    color_label: Optional[str] = None
    opened: Optional[bool] = None
    clicked: Optional[bool] = None
    replied: Optional[bool] = None
    # 🔥 标准时间字段
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FollowupBase(BaseModel):
    customer_id: Optional[int] = None
    followup_type: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    result: Optional[str] = None
    next_action: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None

class FollowupCreate(FollowupBase):
    pass

class FollowupUpdate(FollowupBase):
    pass

class FollowupOut(FollowupBase):
    id: int

    class Config:
        from_attributes = True


class TemplateBase(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    language: Optional[str] = None
    variables: Optional[str] = None
    usage_count: Optional[int] = 0
    success_rate: Optional[float] = None
    is_active: Optional[bool] = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(TemplateBase):
    pass

class TemplateOut(TemplateBase):
    id: int

    class Config:
        from_attributes = True


# 🔥 提示词模板 Schema
class PromptTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str = 'reply'  # reply/analysis/polish
    system_prompt: Optional[str] = None
    user_prompt_template: str
    variables: Optional[str] = None  # JSON格式的变量说明
    recommended_model: Optional[str] = 'gpt-4o-mini'
    is_active: bool = True
    is_default: bool = False


class PromptTemplateCreate(PromptTemplateBase):
    created_by: Optional[str] = None


class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    variables: Optional[str] = None
    recommended_model: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class PromptTemplateOut(PromptTemplateBase):
    id: int
    usage_count: int
    success_rate: float
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CampaignBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_id: Optional[int] = None
    target_segment: Optional[str] = None
    status: Optional[str] = None
    total_sent: Optional[int] = 0
    total_opened: Optional[int] = 0
    total_clicked: Optional[int] = 0
    total_replied: Optional[int] = 0
    total_bounced: Optional[int] = 0
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(CampaignBase):
    pass

class CampaignOut(CampaignBase):
    id: int

    class Config:
        from_attributes = True
