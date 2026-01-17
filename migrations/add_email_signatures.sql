-- 创建邮件签名表
CREATE TABLE IF NOT EXISTS email_signatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_signatures_user ON email_signatures(user_id);
CREATE INDEX IF NOT EXISTS idx_signatures_default ON email_signatures(user_id, is_default);

-- 为现有用户创建默认签名（假设user_id=1）
INSERT INTO email_signatures (user_id, name, content, is_default, display_order) VALUES
(1, '不使用', '', FALSE, 0),
(1, '默认签名', '<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;"><p>Best regards,</p><p><strong>Zhang Wei</strong></p><p>Sales Manager</p><p>Best Underwear Manufacturer Co., Ltd.</p><p>Email: info@best-underwear-manufacturer.com | Tel: +86 138 xxxx xxxx</p></div>', TRUE, 1),
(1, '正式签名', '<div style="font-family: Times New Roman, serif; font-size: 13px; color: #000;"><hr style="border: none; border-top: 2px solid #333; margin: 20px 0;"/><p><strong>Zhang Wei</strong></p><p>Sales Manager</p><p>Best Underwear Manufacturer Co., Ltd.</p><p>Address: XXX Industrial Park, Guangzhou, China</p><p>Mobile: +86 138 xxxx xxxx | Email: zhang.wei@best-underwear-manufacturer.com</p><p>Website: www.best-underwear-manufacturer.com</p></div>', FALSE, 2),
(1, '简洁签名', '<div style="font-family: Arial, sans-serif; font-size: 13px; color: #666;"><p>--</p><p>Zhang Wei</p><p>info@best-underwear-manufacturer.com</p></div>', FALSE, 3);
