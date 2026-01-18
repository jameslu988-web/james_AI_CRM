#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加 company_type 字段到 leads 表
按照标准流程：先修改数据库，再修改ORM模型
"""
from sqlalchemy import text
from src.crm.database import get_session

def add_company_type_field():
    """在leads表中添加company_type字段"""
    db = get_session()
    
    try:
        # 检查字段是否已存在
        check_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='leads' AND column_name='company_type'
        """
        result = db.execute(text(check_sql)).fetchone()
        
        if result:
            print("✅ company_type 字段已存在")
            return True
        
        # 添加字段
        alter_sql = """
        ALTER TABLE leads 
        ADD COLUMN company_type VARCHAR(50)
        """
        db.execute(text(alter_sql))
        db.commit()
        
        print("✅ 成功添加 company_type 字段到 leads 表")
        print("   类型: VARCHAR(50)")
        print("   说明: 存储客户类型（DTC品牌/批发商/零售商/制造商）")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 添加字段失败: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = add_company_type_field()
    if success:
        print("\n📋 下一步：")
        print("1. 在 src/crm/database.py 的 Lead 模型中添加字段定义")
        print("2. 重启后端服务")
        print("3. 测试验证")
