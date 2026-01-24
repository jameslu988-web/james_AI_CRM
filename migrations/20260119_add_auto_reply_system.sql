-- 自动回复系统数据库迁移脚本
-- 创建时间：2026-01-19

-- 1. 创建自动回复规则表
CREATE TABLE IF NOT EXISTS auto_reply_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    email_category VARCHAR(50) NOT NULL,
    
    -- 规则开关
    is_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    auto_generate_reply BOOLEAN DEFAULT TRUE NOT NULL,
    require_approval BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- 审核设置
    approval_method VARCHAR(20) DEFAULT 'system',
    approval_timeout_hours INTEGER DEFAULT 24,
    
    -- 优先级
    priority INTEGER DEFAULT 0,
    
    -- 额外触发条件（JSON）
    conditions TEXT,
    
    -- 统计字段
    triggered_count INTEGER DEFAULT 0,
    approved_count INTEGER DEFAULT 0,
    rejected_count INTEGER DEFAULT 0,
    
    -- 标准时间字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- 创建索引
CREATE INDEX idx_auto_reply_rules_category ON auto_reply_rules(email_category);
CREATE INDEX idx_auto_reply_rules_enabled ON auto_reply_rules(is_enabled);

-- 2. 创建审核任务表
CREATE TABLE IF NOT EXISTS approval_tasks (
    id SERIAL PRIMARY KEY,
    email_id INTEGER NOT NULL REFERENCES email_history(id),
    rule_id INTEGER REFERENCES auto_reply_rules(id),
    
    -- 草稿内容
    draft_subject VARCHAR(500) NOT NULL,
    draft_body TEXT NOT NULL,
    draft_html TEXT,
    
    -- 审核状态
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    
    -- 审核方式
    approval_method VARCHAR(20) DEFAULT 'system',
    
    -- 通知状态
    notification_sent_at TIMESTAMP,
    notification_status VARCHAR(20),
    
    -- 审核信息
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- 修改历史
    revision_count INTEGER DEFAULT 0,
    revision_history TEXT,
    
    -- 自动发送设置
    auto_send_on_approval BOOLEAN DEFAULT TRUE NOT NULL,
    sent_at TIMESTAMP,
    sent_email_id INTEGER,
    
    -- 超时设置
    timeout_at TIMESTAMP,
    
    -- AI分析摘要
    ai_analysis_summary TEXT,
    
    -- 标准时间字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_approval_tasks_email_id ON approval_tasks(email_id);
CREATE INDEX idx_approval_tasks_status ON approval_tasks(status);
CREATE INDEX idx_approval_tasks_created_at ON approval_tasks(created_at);

-- 3. 插入默认规则（3个类型）
INSERT INTO auto_reply_rules (rule_name, email_category, is_enabled, priority) VALUES
('新客询盘自动回复', 'inquiry', true, 10),
('报价跟进自动回复', 'quotation', true, 8),
('样品阶段自动回复', 'sample', true, 6);

-- 完成
SELECT '✅ 自动回复系统数据库迁移完成' AS status;
