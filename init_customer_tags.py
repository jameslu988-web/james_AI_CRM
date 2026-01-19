"""初始化客户标签表并添加测试数据"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.crm.database import init_db, get_session, CustomerTag
from datetime import datetime

def init_tags():
    """初始化客户标签表"""
    print("🔄 初始化数据库表...")
    init_db()
    print("✅ 数据库表初始化完成")
    
    db = get_session()
    try:
        # 检查是否已有标签
        existing_tags = db.query(CustomerTag).count()
        if existing_tags > 0:
            print(f"⚠️ 已存在 {existing_tags} 个标签")
            return
        
        # 创建默认标签
        default_tags = [
            {
                "name": "VIP客户",
                "color": "#ff4757",
                "description": "高价值客户，需重点维护"
            },
            {
                "name": "重要客户",
                "color": "#ffa502",
                "description": "重要客户，定期跟进"
            },
            {
                "name": "潜在客户",
                "color": "#1e90ff",
                "description": "有潜力的客户，需要培养"
            },
            {
                "name": "长期合作",
                "color": "#2ed573",
                "description": "已建立长期合作关系"
            },
            {
                "name": "新客户",
                "color": "#5f27cd",
                "description": "刚建立联系的新客户"
            },
            {
                "name": "大订单",
                "color": "#ff6348",
                "description": "订单金额较大的客户"
            },
            {
                "name": "快速响应",
                "color": "#00d2d3",
                "description": "回复速度快的客户"
            },
            {
                "name": "价格敏感",
                "color": "#ff9ff3",
                "description": "对价格比较敏感"
            }
        ]
        
        print("\n📝 创建默认标签...")
        for tag_data in default_tags:
            tag = CustomerTag(**tag_data)
            db.add(tag)
            print(f"   ✅ {tag_data['name']} - {tag_data['color']}")
        
        db.commit()
        print(f"\n✅ 成功创建 {len(default_tags)} 个默认标签")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_tags()
