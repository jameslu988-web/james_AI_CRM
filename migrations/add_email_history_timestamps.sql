-- 为 email_history 表添加标准时间字段
-- 符合数据库设计最佳实践

-- 添加 created_at 字段
ALTER TABLE email_history 
ADD COLUMN created_at TIMESTAMP;

-- 添加 updated_at 字段
ALTER TABLE email_history 
ADD COLUMN updated_at TIMESTAMP;

-- 为现有记录设置默认值
-- 草稿：使用 sent_at 作为 created_at（如果有）
-- 已发送邮件：使用 sent_at 作为 created_at
UPDATE email_history 
SET created_at = COALESCE(sent_at, CURRENT_TIMESTAMP),
    updated_at = COALESCE(sent_at, CURRENT_TIMESTAMP)
WHERE created_at IS NULL;

-- 为草稿清空 sent_at（恢复语义正确性）
UPDATE email_history 
SET sent_at = NULL 
WHERE status = 'draft';

-- 添加注释
COMMENT ON COLUMN email_history.created_at IS '记录创建时间';
COMMENT ON COLUMN email_history.updated_at IS '记录最后更新时间';
COMMENT ON COLUMN email_history.sent_at IS '邮件实际发送时间（草稿为NULL）';
