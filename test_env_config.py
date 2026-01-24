"""
测试环境配置加载
验证.env文件是否正确加载
"""
import os
from dotenv import load_dotenv

print("=" * 80)
print("环境配置加载测试")
print("=" * 80)

# 加载.env文件
load_dotenv()

# 测试关键配置项
config_items = [
    ("DB_TYPE", "数据库类型"),
    ("DB_USER", "数据库用户"),
    ("DB_PASSWORD", "数据库密码"),
    ("DB_HOST", "数据库主机"),
    ("DB_PORT", "数据库端口"),
    ("DB_NAME", "数据库名称"),
    ("API_PORT", "API端口"),
    ("REDIS_HOST", "Redis主机"),
    ("REDIS_PORT", "Redis端口"),
]

print("\n配置项检查:")
print("-" * 80)

all_ok = True
for key, name in config_items:
    value = os.getenv(key)
    if value:
        # 隐藏密码
        display_value = "***" if "PASSWORD" in key else value
        print(f"✅ {name:15} ({key:20}): {display_value}")
    else:
        print(f"❌ {name:15} ({key:20}): 未配置")
        all_ok = False

print("-" * 80)

if all_ok:
    print("\n✅ 所有配置项加载成功！")
    print("\n测试数据库连接...")
    
    try:
        from src.crm.database import get_session
        from sqlalchemy import text
        
        db = get_session()
        
        # 测试查询
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        
        if result == 1:
            print("✅ 数据库连接成功！")
        else:
            print("❌ 数据库连接失败")
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
else:
    print("\n❌ 部分配置项缺失，请检查.env文件")

print("\n" + "=" * 80)
