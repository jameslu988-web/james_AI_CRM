from pathlib import Path
import os
from dotenv import load_dotenv

# 🔥 加载.env文件（必须在第一时间执行）
load_dotenv()

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    CheckConstraint,
    create_engine,
    Table,
    text,  # 🔥 新增：用于 server_default
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

# 数据库配置
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # postgresql or sqlite

if DB_TYPE == 'postgresql':
    # PostgreSQL 配置
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres123')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'crm_system')
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # SQLite 配置（备用）
    DB_PATH = Path("data")
    DB_PATH.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{DB_PATH / 'customers.db'}"


# 数据库连接池配置
def get_engine():
    """创建数据库引擎（带连接池优化）"""
    pool_size = int(os.getenv('DATABASE_POOL_SIZE', 20))
    max_overflow = int(os.getenv('DATABASE_MAX_OVERFLOW', 40))
    pool_timeout = int(os.getenv('DATABASE_POOL_TIMEOUT', 30))
    pool_recycle = int(os.getenv('DATABASE_POOL_RECYCLE', 3600))
    
    return create_engine(
        DATABASE_URL, 
        echo=False, 
        future=True,
        pool_size=pool_size,              # 连接池大小
        max_overflow=max_overflow,        # 超出pool_size后最多创建的连接数
        pool_timeout=pool_timeout,        # 获取连接的超时时间（秒）
        pool_recycle=pool_recycle,        # 连接回收时间（1小时）
        pool_pre_ping=True,               # 连接前ping测试
        connect_args={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"  # SQL执行超时(30秒)
        } if DB_TYPE == 'postgresql' else {}
    )


engine = get_engine()
SessionLocal = sessionmaker(
    bind=engine, 
    autoflush=False, 
    autocommit=False,
    expire_on_commit=False  # 避免Session外访问对象报错
)

# 用户角色关联表（多对多）
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String, nullable=False)
    contact_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    website = Column(String)
    country = Column(String)
    industry = Column(String)
    company_size = Column(String)

    status = Column(
        String,
        CheckConstraint(
            "status in ('cold', 'contacted', 'replied', 'qualified', 'negotiating', 'customer', 'lost')"
        ),
    )

    priority = Column(Integer, default=3)
    source = Column(String)
    
    # 新增：客户标签（JSON格式存储）
    tags = Column(Text)  # ["VIP", "大客户", "快速响应"]
    
    # 新增：客户分级（A/B/C/D）
    customer_grade = Column(String)  # A: 核心客户, B: 重要客户, C: 普通客户, D: 潜在客户
    
    # 新增：预计年采购额
    estimated_annual_value = Column(Float)
    
    # 新增：实际年采购额
    actual_annual_value = Column(Float, default=0)
    
    # 新增：最后跟进备注
    last_followup_note = Column(Text)
    
    # 新增：社交媒体
    linkedin_url = Column(String)
    facebook_url = Column(String)
    
    # 新增：自定义字段（JSON格式存储）
    custom_fields = Column(Text)  # {"field_name": "field_value", ...}

    first_contact_date = Column(DateTime)
    last_contact_date = Column(DateTime)
    next_followup_date = Column(DateTime)

    engagement_score = Column(Float, default=0)
    estimated_value = Column(Float)
    
    # 客户行为统计字段
    email_sent_count = Column(Integer, default=0)
    email_received_count = Column(Integer, default=0)
    email_reply_count = Column(Integer, default=0)
    order_count = Column(Integer, default=0)
    total_order_amount = Column(Float, default=0)
    
    # 客户参与度计算字段
    last_active_date = Column(DateTime)
    days_since_last_contact = Column(Integer, default=0)
    response_rate = Column(Float, default=0)
    
    # 客户价值评分字段
    purchase_frequency = Column(Float, default=0)  # 购买频率（次/年）
    average_order_value = Column(Float, default=0)  # 平均订单价值
    lifetime_value = Column(Float, default=0)  # 客户终身价值 CLV
    
    # 客户行为标签
    behavior_tags = Column(Text)  # JSON格式: ["high_value", "fast_response", "decision_maker"]
    
    # 自动分级时间戳
    last_grading_date = Column(DateTime)
    grading_reason = Column(Text)  # 分级原因说明

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    email_history = relationship("EmailHistory", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    followup_records = relationship("FollowupRecord", back_populates="customer")


class EmailHistory(Base):
    __tablename__ = "email_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    direction = Column(
        String,
        CheckConstraint("direction in ('outbound', 'inbound')"),
    )
    subject = Column(String)
    body = Column(Text)  # 纯文本版本（用于搜索和预览）
    html_body = Column(Text, nullable=True)  # HTML版本（优先显示）
    sent_at = Column(DateTime)
    
    # 发件人和收件人邮箱
    from_name = Column(String, nullable=True)  # 发件人名称（从邮件头部解析）
    from_email = Column(String)  # 发件人邮箱地址
    to_name = Column(String, nullable=True)  # 收件人名称（从邮件头部解析）
    to_email = Column(String)  # 收件人邮箱地址
    cc_email = Column(String, nullable=True)  # 抄送
    bcc_email = Column(String, nullable=True)  # 密送
    
    # 邮件唯一标识（用于去重）
    message_id = Column(String, unique=True, nullable=True, index=True)  # IMAP Message-ID
    
    # 邮件状态
    status = Column(String, default='sent', nullable=False, index=True)  # draft/sent/failed
    
    # 🔥 投递状态（新增：跟踪真实投递情况）
    delivery_status = Column(String, default='pending', nullable=True, index=True)  # pending/delivered/bounced/spam/unknown
    delivery_time = Column(DateTime, nullable=True)  # 投递成功时间
    bounce_reason = Column(Text, nullable=True)  # 退信原因
    
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    replied = Column(Boolean, default=False)
    ai_generated = Column(Boolean, default=False)
    attachments = Column(Text)  # JSON格式存储附件路径列表
    priority = Column(String, default='normal', nullable=True)  # high/normal/low
    need_receipt = Column(Boolean, default=False, nullable=True)  # 已读回执
    
    # 新增：邮件效果追踪
    template_id = Column(Integer)  # 邮件模板ID
    campaign_id = Column(Integer)  # 活动ID
    open_count = Column(Integer, default=0)  # 打开次数
    click_count = Column(Integer, default=0)  # 点击次数
    first_opened_at = Column(DateTime)  # 首次打开时间
    last_opened_at = Column(DateTime)  # 最后打开时间
    reply_time = Column(Integer)  # 回复时间（秒）
    bounce_type = Column(String)  # 退信类型：hard/soft/none
    
    # AI智能分析（新增字段，可为空）
    ai_sentiment = Column(String, nullable=True)  # positive/neutral/negative/urgent
    ai_summary = Column(Text, nullable=True)  # AI生成的邮件摘要
    ai_category = Column(String, nullable=True)  # inquiry/quotation/order/complaint/follow_up/sample
    urgency_level = Column(String, nullable=True)  # high/medium/low
    purchase_intent = Column(String, nullable=True)  # high/medium/low
    
    # 业务阶段（扩展AI分析字段）
    business_stage = Column(String, nullable=True)  # 新客询盘/报价跟进/样品阶段/谈判议价/订单确认/生产跟踪/售后服务/老客维护/垃圾营销
    
    # 业务管理（新增字段，可为空）
    tags = Column(Text, nullable=True)  # JSON格式: ["询价", "紧急", "大单"]
    internal_notes = Column(Text, nullable=True)  # 内部备注（不发送给客户）
    follow_up_date = Column(DateTime, nullable=True)  # 计划跟进日期
    is_starred = Column(Boolean, default=False, nullable=True)  # 是否标星
    color_label = Column(String, nullable=True)  # 颜色标签: red/orange/yellow/green/blue/purple
    
    # 软删除（回收站功能）
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)  # 是否已删除
    deleted_at = Column(DateTime, nullable=True)  # 删除时间
    deleted_by = Column(String, nullable=True)  # 删除者
    
    # 🔥 标准时间字段（数据库设计最佳实践）
    created_at = Column(DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'))  # 记录创建时间
    updated_at = Column(DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)  # 记录更新时间

    customer = relationship("Customer", back_populates="email_history")


class PromptTemplate(Base):
    """AI提示词模板表"""
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)  # 模板名称
    description = Column(Text, nullable=True)  # 模板描述
    template_type = Column(String, nullable=False, default='reply')  # 模板类型：reply/analysis/polish
    
    # 提示词内容（支持变量占位符）
    system_prompt = Column(Text, nullable=True)  # 系统提示词
    user_prompt_template = Column(Text, nullable=False)  # 用户提示词模板
    
    # 模板变量说明（JSON格式）
    # 例如：{"subject": "邮件主题", "body": "邮件正文", "tone": "语气"}
    variables = Column(Text, nullable=True)
    
    # 推荐的AI模型
    recommended_model = Column(String, nullable=True, default='gpt-4o-mini')
    
    # 模板状态
    is_active = Column(Boolean, default=True, server_default=text('true'), nullable=False)  # 是否启用
    is_default = Column(Boolean, default=False, server_default=text('false'), nullable=False)  # 是否为默认模板
    
    # 使用统计
    usage_count = Column(Integer, default=0, server_default=text('0'), nullable=False)  # 使用次数
    success_rate = Column(Float, default=0.0, server_default=text('0.0'), nullable=False)  # 成功率
    
    # 创建者
    created_by = Column(String, nullable=True)  # 创建者用户名
    
    # 标准时间字段
    created_at = Column(DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_number = Column(String, unique=True)

    product_details = Column(Text)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_amount = Column(Float)
    
    # 新增：财务管理
    currency = Column(String, default="USD")  # 货币种类
    cost_price = Column(Float)  # 成本价
    profit_amount = Column(Float)  # 利润额
    profit_margin = Column(Float)  # 利润率
    payment_method = Column(String)  # 支付方式：T/T, L/C, PayPal
    payment_terms = Column(String)  # 付款条件：30% deposit, 70% before shipment
    payment_status = Column(String)  # 付款状态：Pending, Partial, Paid
    
    # 新增：物流信息
    shipping_method = Column(String)  # Sea, Air, Express
    tracking_number = Column(String)  # 追踪号
    shipping_company = Column(String)  # DHL, FedEx, Maersk
    shipping_cost = Column(Float)  # 运费
    incoterms = Column(String)  # FOB, CIF, EXW

    status = Column(
        String,
        CheckConstraint(
            "status in ('quotation', 'confirmed', 'production', 'shipped', 'delivered', 'completed')"
        ),
    )

    factory_name = Column(String)
    production_start_date = Column(DateTime)
    estimated_completion_date = Column(DateTime)

    order_date = Column(DateTime)
    payment_date = Column(DateTime)
    ship_date = Column(DateTime)
    delivery_date = Column(DateTime)  # 新增：实际交付日期

    requires_attention = Column(Boolean, default=False)
    notes = Column(Text)

    created_at = Column(DateTime)

    customer = relationship("Customer", back_populates="orders")


class FollowupRecord(Base):
    """跟进记录表 - 记录每次与客户的互动"""
    __tablename__ = "followup_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    followup_type = Column(String)  # Email, Phone, Meeting, WhatsApp, LinkedIn
    subject = Column(String)  # 主题
    content = Column(Text)  # 内容
    result = Column(String)  # 结果：Positive, Neutral, Negative, No Response
    next_action = Column(String)  # 下步行动
    
    created_by = Column(String)  # 跟进人
    created_at = Column(DateTime)
    
    customer = relationship("Customer", back_populates="followup_records")


class EmailTemplate(Base):
    """邮件模板表 - 管理邮件模板"""
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)  # 模板名称
    category = Column(String)  # 分类：Cold Email, Follow-up, Quotation, Thank You
    subject = Column(String)
    body = Column(Text)
    
    language = Column(String, default="en")  # en, zh, es, fr
    variables = Column(Text)  # JSON格式：["{company_name}", "{contact_name}"]
    
    usage_count = Column(Integer, default=0)  # 使用次数
    success_rate = Column(Float)  # 成功率（回复率）
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class EmailCampaign(Base):
    """邮件活动表 - 批量邮件营销活动"""
    __tablename__ = "email_campaigns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    template_id = Column(Integer, ForeignKey("email_templates.id"))
    target_segment = Column(String)  # 目标群体：All, VIP, New Leads
    
    status = Column(String)  # Draft, Scheduled, Running, Completed, Paused
    
    total_sent = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_replied = Column(Integer, default=0)
    total_bounced = Column(Integer, default=0)
    
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    created_at = Column(DateTime)


class CustomFieldDefinition(Base):
    """自定义字段定义表 - 存储客户自定义字段的定义"""
    __tablename__ = "custom_field_definitions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column(String, nullable=False, unique=True)  # 字段名称
    field_type = Column(String, default="text")  # 字段类型：text, number, date, select
    is_visible = Column(Boolean, default=True)  # 是否在列表中显示
    display_order = Column(Integer, default=0)  # 显示顺序
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Lead(Base):
    """线索表 - 管理潜在客户线索"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String, nullable=False)  # 公司名称
    contact_name = Column(String)  # 联系人
    email = Column(String)  # 邮箱
    phone = Column(String)  # 电话
    website = Column(String)  # 网站
    country = Column(String)  # 国家
    industry = Column(String)  # 行业
    company_size = Column(String)  # 公司规模
    
    # 线索特有字段
    lead_source = Column(String)  # 线索来源：Google搜索、展会、推荐、官网询盘、LinkedIn、B2B平台
    lead_status = Column(
        String,
        CheckConstraint(
            "lead_status in ('new', 'contacted', 'in_progress', 'qualified', 'unqualified', 'converted')"
        ),
        default='new'
    )  # 线索状态：新线索、已联系、跟进中、合格、不合格、已转化
    lead_score = Column(Integer, default=0)  # 线索评分（0-100）
    priority = Column(
        String,
        CheckConstraint("priority in ('high', 'medium', 'low')"),
        default='medium'
    )  # 优先级
    
    estimated_budget = Column(Float)  # 预估预算
    decision_timeframe = Column(String)  # 决策时间：立即、1个月内、3个月内、6个月内、待定
    pain_points = Column(Text)  # 痛点需求
    competitor_info = Column(String)  # 竞争对手信息
    product_interest = Column(String)  # 感兴趣的产品
    notes = Column(Text)  # 备注
    
    # 分配与转化
    assigned_to = Column(Integer, ForeignKey("users.id"))  # 分配给（业务员）
    converted = Column(Boolean, default=False)  # 是否已转化
    converted_customer_id = Column(Integer, ForeignKey("customers.id"))  # 转化后的客户ID
    converted_at = Column(DateTime)  # 转化时间
    
    # 时间字段
    first_contact_date = Column(DateTime)  # 首次联系时间
    last_contact_date = Column(DateTime)  # 最后联系时间
    next_followup_date = Column(DateTime)  # 下次跟进时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))  # 创建人


class User(Base):
    """用户表 - 系统登录用户"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)  # 用户名
    email = Column(String, nullable=False, unique=True)  # 邮箱
    hashed_password = Column(String, nullable=False)  # 加密密码
    full_name = Column(String)  # 全名
    
    is_active = Column(Boolean, default=True)  # 是否激活
    is_superuser = Column(Boolean, default=False)  # 是否超级管理员
    
    department = Column(String)  # 部门
    position = Column(String)  # 职位
    phone = Column(String)  # 电话
    avatar = Column(String)  # 头像URL
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)  # 最后登录时间
    
    # 关系
    roles = relationship("Role", secondary=user_roles, back_populates="users")


class Role(Base):
    """角色表 - 用户角色定义"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # 角色名称
    display_name = Column(String)  # 显示名称
    description = Column(Text)  # 角色描述
    
    # 权限配置（JSON格式）
    permissions = Column(Text)  # {"customers": ["view", "create", "edit"], ...}
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    users = relationship("User", secondary=user_roles, back_populates="roles")


class Product(Base):
    """产品知识库表 - 存储产品基础信息"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, unique=True, nullable=False)  # 产品SKU编码
    name_en = Column(String, nullable=False)  # 英文名称
    name_zh = Column(String)  # 中文名称
    category = Column(String)  # 产品分类：平角内裤/三角内裤/运动内裤
    
    # 基础信息
    description_en = Column(Text)  # 英文描述
    description_zh = Column(Text)  # 中文描述
    features = Column(Text)  # 产品特点（JSON格式）
    
    # 规格参数
    sizes = Column(Text)  # 可用尺码（JSON: ["S", "M", "L", "XL", "XXL", "XXXL"]）
    colors = Column(Text)  # 可用颜色（JSON）
    materials = Column(Text)  # 材质选项（JSON: [{"name": "精梳棉", "composition": "95%棉+5%氨纶", "price_multiplier": 1.2}]）
    weight = Column(Float)  # 单件重量（克）
    
    # 价格信息
    base_price = Column(Float, nullable=False)  # 基础价格（USD，基于最低材质和最小订单量）
    currency = Column(String, default="USD")  # 货币单位
    moq = Column(Integer, default=1000)  # 最小起订量（件）
    
    # 生产信息
    lead_time_days = Column(Integer)  # 生产周期（天）
    sample_lead_time = Column(Integer, default=7)  # 样品周期（天）
    
    # 认证与质量
    certifications = Column(Text)  # 认证信息（JSON: ["OEKO-TEX", "BSCI"]）
    quality_standard = Column(String)  # 质量标准
    
    # 图片与文件
    main_image = Column(String)  # 主图URL
    images = Column(Text)  # 产品图片列表（JSON）
    spec_sheet_url = Column(String)  # 规格表文件URL
    
    # 状态
    is_active = Column(Boolean, default=True)  # 是否在售
    is_featured = Column(Boolean, default=False)  # 是否推荐产品
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    faqs = relationship("ProductFAQ", back_populates="product")


class ProductFAQ(Base):
    """产品FAQ表 - 存储产品相关的常见问题"""
    __tablename__ = "product_faqs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # 可为空表示通用FAQ
    
    question_en = Column(Text, nullable=False)  # 英文问题
    question_zh = Column(Text)  # 中文问题
    answer_en = Column(Text, nullable=False)  # 英文答案
    answer_zh = Column(Text)  # 中文答案
    
    category = Column(String)  # 分类：产品规格/价格/物流/定制/质量/其他
    keywords = Column(Text)  # 关键词（JSON，用于检索）
    
    priority = Column(Integer, default=0)  # 优先级（数字越大越重要）
    usage_count = Column(Integer, default=0)  # 使用次数
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    product = relationship("Product", back_populates="faqs")


class PricingRule(Base):
    """价格规则表 - 存储动态定价规则"""
    __tablename__ = "pricing_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # 可为空表示全局规则
    
    rule_name = Column(String, nullable=False)  # 规则名称
    rule_type = Column(String, nullable=False)  # 规则类型：quantity_discount/material_markup/customization_markup/seasonal
    
    # 规则配置（JSON格式）
    # 数量折扣示例: {"tiers": [{"min_qty": 1000, "max_qty": 5000, "discount": 0}, {"min_qty": 5001, "max_qty": 10000, "discount": 0.05}]}
    # 材质加价示例: {"cotton": 1.0, "modal": 1.35, "bamboo": 1.4}
    # 定制加价示例: {"one_color_print": 0.15, "multi_color_print": 0.25, "embroidery": 0.3}
    # 季节调整示例: {"peak_season": {"months": [9,10,11,12], "multiplier": 1.05}, "low_season": {"months": [3,4,5], "multiplier": 0.9}}
    config = Column(Text, nullable=False)
    
    description = Column(Text)  # 规则说明
    priority = Column(Integer, default=0)  # 优先级（数字越大越先应用）
    
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime)  # 生效开始时间
    valid_to = Column(DateTime)  # 生效结束时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CaseStudy(Base):
    """案例库表 - 存储成功案例"""
    __tablename__ = "case_studies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title_en = Column(String, nullable=False)  # 英文标题
    title_zh = Column(String)  # 中文标题
    
    # 客户信息（脱敏）
    customer_type = Column(String)  # 客户类型：批发商/零售商/品牌商/电商平台
    customer_region = Column(String)  # 客户地区：欧洲/北美/南美/亚洲/中东
    customer_industry = Column(String)  # 客户行业
    
    # 项目信息
    challenge_en = Column(Text)  # 客户挑战（英文）
    challenge_zh = Column(Text)  # 客户挑战（中文）
    solution_en = Column(Text)  # 解决方案（英文）
    solution_zh = Column(Text)  # 解决方案（中文）
    result_en = Column(Text)  # 项目成果（英文）
    result_zh = Column(Text)  # 项目成果（中文）
    
    # 订单信息
    order_quantity = Column(Integer)  # 订单数量
    order_value = Column(Float)  # 订单金额（USD）
    products_involved = Column(Text)  # 涉及产品（JSON）
    
    # 亮点
    highlights = Column(Text)  # 案例亮点（JSON: ["快速交付", "定制服务", "质量保证"]）
    testimonial_en = Column(Text)  # 客户评价（英文）
    testimonial_zh = Column(Text)  # 客户评价（中文）
    
    # 图片
    featured_image = Column(String)  # 主图URL
    images = Column(Text)  # 案例图片（JSON）
    
    # 分类与标签
    category = Column(String)  # 案例分类
    tags = Column(Text)  # 标签（JSON: ["大订单", "欧美市场", "定制"]）
    
    # 使用统计
    usage_count = Column(Integer, default=0)  # 被引用次数
    
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # 是否精选案例
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeFAQ(Base):
    """通用知识库FAQ表 - 存储非产品相关的通用问答"""
    __tablename__ = "knowledge_faqs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    category = Column(String, nullable=False)  # 分类：付款方式/物流/认证/定制流程/公司介绍/其他
    
    question_en = Column(Text, nullable=False)  # 英文问题
    question_zh = Column(Text)  # 中文问题
    answer_en = Column(Text, nullable=False)  # 英文答案
    answer_zh = Column(Text)  # 中文答案
    
    # 检索优化
    keywords = Column(Text)  # 关键词（JSON: ["payment", "T/T", "PayPal"]）
    related_questions = Column(Text)  # 相关问题ID（JSON）
    
    # 使用统计
    priority = Column(Integer, default=0)  # 优先级
    usage_count = Column(Integer, default=0)  # 使用次数
    satisfaction_score = Column(Float)  # 满意度评分（0-5）
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailAccount(Base):
    """邮箱账户配置表 - 管理收发邮件的邮箱账户"""
    __tablename__ = "email_accounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_name = Column(String, nullable=False)  # 账户名称（如：公司主邮箱、销售邮箱）
    email_address = Column(String, nullable=False, unique=True)  # 邮箱地址
    
    # IMAP接收配置
    imap_host = Column(String)  # IMAP服务器地址
    imap_port = Column(Integer, default=993)  # IMAP端口
    imap_username = Column(String)  # IMAP用户名（通常是邮箱地址）
    imap_password = Column(String)  # IMAP密码或授权码（需加密存储）
    
    # SMTP发送配置
    smtp_host = Column(String)  # SMTP服务器地址
    smtp_port = Column(Integer, default=465)  # SMTP端口
    smtp_username = Column(String)  # SMTP用户名
    smtp_password = Column(String)  # SMTP密码（需加密存储）
    
    # 邮箱服务商
    provider = Column(String)  # gmail/outlook/qq/aliyun/163/yahoo/custom
    
    # 同步设置
    auto_sync = Column(Boolean, default=True)  # 是否自动同步
    sync_interval = Column(Integer, default=5)  # 同步间隔（分钟）
    sync_mode = Column(String, default='unread_only')  # 同步模式：unread_only(只未读)/recent_30days(最近30天)/all(全部)
    last_sync_at = Column(DateTime)  # 最后同步时间
    sync_status = Column(String, default='active')  # 同步状态：active/paused/error
    first_sync_completed = Column(Boolean, default=False)  # 是否已完成首次同步
    
    # 邮件处理规则
    auto_match_customer = Column(Boolean, default=True)  # 自动匹配客户
    auto_create_followup = Column(Boolean, default=True)  # 自动创建跟进记录
    
    # 使用统计
    total_received = Column(Integer, default=0)  # 接收邮件总数
    total_sent = Column(Integer, default=0)  # 发送邮件总数
    
    # 状态
    is_active = Column(Boolean, default=True)  # 是否启用
    is_default = Column(Boolean, default=False)  # 是否默认账户
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))  # 创建人


class KnowledgeDocument(Base):
    """向量知识库文档表 - 存储上传的文档"""
    __tablename__ = "knowledge_documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)  # 文档标题
    filename = Column(String, nullable=False)  # 原始文件名
    file_type = Column(String)  # 文件类型：pdf/docx/txt
    file_size = Column(Integer)  # 文件大小（字节）
    file_hash = Column(String, unique=True)  # 文件哈希（用于去重）
    
    category = Column(String)  # 分类：产品手册/FAQ/价格表/案例/公司介绍/其他
    tags = Column(Text)  # 标签（JSON）
    
    # 文档内容
    content = Column(Text)  # 解析后的文本内容
    summary = Column(Text)  # AI生成的摘要
    
    # 处理状态
    status = Column(String, default='pending')  # pending/processing/completed/failed
    chunk_count = Column(Integer, default=0)  # 分块数量
    error_message = Column(Text)  # 错误信息
    
    # 存储路径
    file_path = Column(String)  # 文件存储路径
    
    # 使用统计
    usage_count = Column(Integer, default=0)  # 被检索次数
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # 关系
    chunks = relationship("KnowledgeChunk", back_populates="document")


class KnowledgeChunk(Base):
    """向量知识库分块表 - 存储文档分块和向量"""
    __tablename__ = "knowledge_chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"), nullable=False)
    
    content = Column(Text, nullable=False)  # 分块文本内容
    chunk_index = Column(Integer)  # 分块序号
    
    # 向量（使用JSON存储）
    embedding = Column(Text)  # JSON格式存储向量数组
    
    # 元数据
    chunk_metadata = Column(Text)  # JSON格式存储额外信息（如页码、章节等）
    
    # 统计
    token_count = Column(Integer)  # token数量
    char_count = Column(Integer)  # 字符数
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    document = relationship("KnowledgeDocument", back_populates="chunks")


class EmailSignature(Base):
    """邮件签名表 - 管理用户的邮件签名"""
    __tablename__ = "email_signatures"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户
    name = Column(String(100), nullable=False)  # 签名名称
    content = Column(Text, nullable=False)  # 签名内容（HTML格式）
    is_default = Column(Boolean, default=False, server_default=text('false'), nullable=False)  # 是否为默认签名
    display_order = Column(Integer, default=0, server_default=text('0'), nullable=False)  # 显示顺序
    
    # 标准时间字段
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


class CustomerTag(Base):
    """客户标签表 - 管理客户标签"""
    __tablename__ = "customer_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)  # 标签名称
    color = Column(String(20), default="#1677ff")  # 标签颜色
    description = Column(Text)  # 标签描述
    
    # 统计字段
    usage_count = Column(Integer, default=0)  # 使用次数
    
    # 标准时间字段
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


class AutoReplyRule(Base):
    """自动回复规则表 - 管理AI自动回复触发规则"""
    __tablename__ = "auto_reply_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(100), nullable=False)  # 规则名称
    email_category = Column(String(50), nullable=False, index=True)  # 邮件类型：inquiry/quotation/sample等
    
    # 规则开关
    is_enabled = Column(Boolean, default=True, server_default=text('true'), nullable=False)  # 是否启用
    auto_generate_reply = Column(Boolean, default=True, server_default=text('true'), nullable=False)  # 是否自动生成回复
    require_approval = Column(Boolean, default=True, server_default=text('true'), nullable=False)  # 是否需要人工审核
    
    # 审核设置
    approval_method = Column(String(20), default='system')  # 审核方式：wechat/email/system
    approval_timeout_hours = Column(Integer, default=24)  # 审核超时时间（小时）
    
    # 优先级
    priority = Column(Integer, default=0)  # 规则优先级（数字越大优先级越高）
    
    # 额外触发条件（JSON格式）
    conditions = Column(Text, nullable=True)  # {"purchase_intent_min": 50, "not_spam": true}
    
    # 统计字段
    triggered_count = Column(Integer, default=0)  # 触发次数
    approved_count = Column(Integer, default=0)  # 通过审核次数
    rejected_count = Column(Integer, default=0)  # 拒绝次数
    
    # 标准时间字段
    created_at = Column(DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class ApprovalTask(Base):
    """审核任务表 - 管理AI生成邮件的人工审核"""
    __tablename__ = "approval_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey("email_history.id"), nullable=False, index=True)  # 关联原始邮件
    rule_id = Column(Integer, ForeignKey("auto_reply_rules.id"), nullable=True)  # 关联触发的规则
    
    # 草稿内容
    draft_subject = Column(String(500), nullable=False)  # 回复邮件主题
    draft_body = Column(Text, nullable=False)  # 回复邮件正文（纯文本）
    draft_html = Column(Text, nullable=True)  # 回复邮件正文（HTML）
    
    # 审核状态
    status = Column(String(20), default='pending', nullable=False, index=True)  # pending/approved/rejected/revised/expired
    
    # 审核方式
    approval_method = Column(String(20), default='system')  # 审核方式
    
    # 通知状态
    notification_sent_at = Column(DateTime, nullable=True)  # 通知发送时间
    notification_status = Column(String(20), nullable=True)  # success/failed
    
    # 审核信息
    approved_by = Column(String(100), nullable=True)  # 审核人
    approved_at = Column(DateTime, nullable=True)  # 审核时间
    rejection_reason = Column(Text, nullable=True)  # 拒绝原因
    
    # 修改历史
    revision_count = Column(Integer, default=0)  # 修改次数
    revision_history = Column(Text, nullable=True)  # 修改历史（JSON格式）
    
    # 自动发送设置
    auto_send_on_approval = Column(Boolean, default=True, server_default=text('true'), nullable=False)  # 审核通过后自动发送
    sent_at = Column(DateTime, nullable=True)  # 实际发送时间
    sent_email_id = Column(Integer, nullable=True)  # 发送后的邮件ID
    
    # 超时设置
    timeout_at = Column(DateTime, nullable=True)  # 超时时间点
    
    # AI分析摘要（用于审核参考）
    ai_analysis_summary = Column(Text, nullable=True)  # AI分析摘要（JSON格式）
    
    # 标准时间字段
    created_at = Column(DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)


def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session (legacy)"""
    return SessionLocal()
