-- 为leads表添加company_type字段
ALTER TABLE leads ADD COLUMN IF NOT EXISTS company_type VARCHAR(50);

-- 验证字段是否添加成功
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='leads' AND column_name='company_type';
