-- 创建提示词模板表
CREATE TABLE IF NOT EXISTS prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    template_type VARCHAR NOT NULL DEFAULT 'reply',
    system_prompt TEXT,
    user_prompt_template TEXT NOT NULL,
    variables TEXT,
    recommended_model VARCHAR DEFAULT 'gpt-4o-mini',
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    created_by VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_prompt_templates_type ON prompt_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_active ON prompt_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_default ON prompt_templates(is_default);

-- 插入默认的邮件回复提示词模板
INSERT INTO prompt_templates (
    name,
    description,
    template_type,
    system_prompt,
    user_prompt_template,
    variables,
    recommended_model,
    is_default
) VALUES (
    '专业外贸回复模板',
    '适用于外贸业务的专业邮件回复，支持知识库集成',
    'reply',
    '你是一个专业的外贸业务员。请根据收到的客户邮件，生成一封专业的英文回复邮件。',
    '原邮件信息：
主题: {subject}
正文: {body}

{knowledge_context}

{customer_context}

回复要求：
1. 语气：{tone_desc}
2. 语言：使用流利的英文
3. 格式：**必须使用HTML格式**，使用<p>标签分段，使用<br>换行
4. 内容：针对客户的问题给出专业回复
5. 结构：
   - 开头：专业的问候语（Dear XXX,）
   - 正文：使用<p>标签将不同主题分成多个段落
   - 列表：如果有多个要点，使用<ul><li>或编号列表
   - 结尾：专业的结束语（Best regards, Sincerely等）和完整签名块
6. 签名格式：
   ```html
   <p>Best regards,</p>
   <p>
   [Your Name]<br>
   [Your Position]<br>
   [Your Company]<br>
   Email: sales@underwearexport.com<br>
   WhatsApp: +86 138 xxxx xxxx
   </p>
   ```

**重要**: 
- 每个段落必须用<p>标签包裹
- 段落之间会自动有间距
- 不要将所有内容挤在一个段落中
- 生成的内容必须是完整的HTML格式
- 不要包含"Subject:"等标记

请直接生成HTML格式的邮件正文。',
    '{"subject": "邮件主题", "body": "邮件正文", "tone_desc": "语气描述", "knowledge_context": "知识库内容", "customer_context": "客户上下文"}',
    'gpt-4o-mini',
    TRUE
);

-- 插入简洁回复模板
INSERT INTO prompt_templates (
    name,
    description,
    template_type,
    system_prompt,
    user_prompt_template,
    variables,
    recommended_model,
    is_default
) VALUES (
    '简洁快速回复模板',
    '适用于快速回复，简洁明了',
    'reply',
    '你是一个专业的外贸业务员。请生成简洁明了的英文回复邮件。',
    '客户邮件：
主题: {subject}
内容: {body}

{knowledge_context}

要求：
1. 语气：{tone_desc}
2. 简洁明了，直接回答客户问题
3. 使用HTML格式，<p>标签分段
4. 包含专业的问候和结束语
5. 避免冗长的解释

请直接生成HTML格式的邮件正文。',
    '{"subject": "邮件主题", "body": "邮件正文", "tone_desc": "语气描述", "knowledge_context": "知识库内容"}',
    'gpt-4o-mini',
    FALSE
);

-- 插入友好热情模板
INSERT INTO prompt_templates (
    name,
    description,
    template_type,
    system_prompt,
    user_prompt_template,
    variables,
    recommended_model,
    is_default
) VALUES (
    '友好热情回复模板',
    '适用于建立长期关系的客户，语气更加友好热情',
    'reply',
    '你是一个热情友好的外贸业务员。请生成温暖亲切的英文回复邮件，让客户感受到你的热情和诚意。',
    '客户邮件：
主题: {subject}
内容: {body}

{knowledge_context}

{customer_context}

回复要求：
1. 语气：友好、热情、真诚
2. 适当使用表达感情的词汇（excited, delighted, pleasure等）
3. 使用HTML格式，<p>标签分段
4. 体现对客户的重视和关注
5. 邀请进一步沟通

请直接生成HTML格式的邮件正文。',
    '{"subject": "邮件主题", "body": "邮件正文", "knowledge_context": "知识库内容", "customer_context": "客户上下文"}',
    'gpt-4o-mini',
    FALSE
);

COMMENT ON TABLE prompt_templates IS 'AI提示词模板配置表';
COMMENT ON COLUMN prompt_templates.template_type IS '模板类型：reply(回复)/analysis(分析)/polish(润色)';
COMMENT ON COLUMN prompt_templates.system_prompt IS '系统级提示词，定义AI角色';
COMMENT ON COLUMN prompt_templates.user_prompt_template IS '用户提示词模板，支持变量占位符';
COMMENT ON COLUMN prompt_templates.variables IS 'JSON格式的变量说明';
COMMENT ON COLUMN prompt_templates.is_default IS '是否为默认模板（每种类型只能有一个默认）';
