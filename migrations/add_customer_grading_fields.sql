-- 客户分级体系相关字段迁移
-- 日期：2026-01-18

-- 添加客户画像相关字段
ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_grade VARCHAR(10) DEFAULT 'D';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS engagement_score FLOAT DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS estimated_annual_value FLOAT DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS actual_annual_value FLOAT DEFAULT 0;

-- 添加客户行为统计字段
ALTER TABLE customers ADD COLUMN IF NOT EXISTS email_sent_count INTEGER DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS email_received_count INTEGER DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS email_reply_count INTEGER DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS order_count INTEGER DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_order_amount FLOAT DEFAULT 0;

-- 添加客户参与度计算字段
ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_active_date TIMESTAMP;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS days_since_last_contact INTEGER DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS response_rate FLOAT DEFAULT 0;

-- 添加客户价值评分字段
ALTER TABLE customers ADD COLUMN IF NOT EXISTS purchase_frequency FLOAT DEFAULT 0;  -- 购买频率（次/年）
ALTER TABLE customers ADD COLUMN IF NOT EXISTS average_order_value FLOAT DEFAULT 0;  -- 平均订单价值
ALTER TABLE customers ADD COLUMN IF NOT EXISTS lifetime_value FLOAT DEFAULT 0;  -- 客户终身价值CLV

-- 添加客户行为标签
ALTER TABLE customers ADD COLUMN IF NOT EXISTS behavior_tags TEXT;  -- JSON格式: ["高价值", "快速回复", "决策者"]

-- 添加自动分级时间戳
ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_grading_date TIMESTAMP;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS grading_reason TEXT;  -- 分级原因说明

-- 创建索引以优化查询
CREATE INDEX IF NOT EXISTS idx_customer_grade ON customers(customer_grade);
CREATE INDEX IF NOT EXISTS idx_engagement_score ON customers(engagement_score DESC);
CREATE INDEX IF NOT EXISTS idx_last_active_date ON customers(last_active_date DESC);

-- 为现有客户初始化默认值
UPDATE customers SET 
    customer_grade = 'D',
    engagement_score = 0,
    email_sent_count = 0,
    email_received_count = 0,
    email_reply_count = 0,
    order_count = 0,
    total_order_amount = 0,
    response_rate = 0,
    lifetime_value = 0
WHERE customer_grade IS NULL;

COMMENT ON COLUMN customers.customer_grade IS '客户分级: A=核心客户, B=重要客户, C=普通客户, D=潜在客户';
COMMENT ON COLUMN customers.engagement_score IS '参与度评分 (0-100)';
COMMENT ON COLUMN customers.lifetime_value IS '客户终身价值 CLV';
COMMENT ON COLUMN customers.response_rate IS '邮件回复率 (0-1)';
