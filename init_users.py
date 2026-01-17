"""初始化用户和角色数据"""
import json
from datetime import datetime

from src.crm.database import get_session, init_db, User, Role
from src.api.routers.auth import get_password_hash


def init_roles():
    """初始化角色"""
    db = get_session()
    
    roles_data = [
        {
            "name": "super_admin",
            "display_name": "超级管理员",
            "description": "系统最高权限，可以管理所有功能",
            "permissions": json.dumps({
                "customers": ["view_all", "create", "edit", "delete", "export"],
                "orders": ["view_all", "create", "edit", "delete", "export"],
                "emails": ["view_all", "send", "delete"],
                "followups": ["view_all", "create", "edit", "delete"],
                "templates": ["view", "create", "edit", "delete"],
                "campaigns": ["view", "create", "edit", "delete", "execute"],
                "analytics": ["view_all"],
                "settings": ["manage"],
                "users": ["view", "create", "edit", "delete"]
            })
        },
        {
            "name": "admin",
            "display_name": "管理员",
            "description": "部门管理员，可以管理本部门的数据",
            "permissions": json.dumps({
                "customers": ["view_department", "create", "edit", "export"],
                "orders": ["view_department", "create", "edit", "export"],
                "emails": ["view_department", "send"],
                "followups": ["view_department", "create", "edit"],
                "templates": ["view", "create", "edit"],
                "campaigns": ["view", "create", "edit"],
                "analytics": ["view_department"],
                "settings": ["view"]
            })
        },
        {
            "name": "senior_sales",
            "display_name": "高级业务员",
            "description": "高级业务员，可以查看团队数据",
            "permissions": json.dumps({
                "customers": ["view_team", "create", "edit"],
                "orders": ["view_team", "create", "edit"],
                "emails": ["view_own", "send"],
                "followups": ["view_team", "create", "edit"],
                "templates": ["view", "use"],
                "campaigns": ["view"],
                "analytics": ["view_team"]
            })
        },
        {
            "name": "sales",
            "display_name": "普通业务员",
            "description": "普通业务员，只能查看和管理自己的数据",
            "permissions": json.dumps({
                "customers": ["view_own", "create", "edit"],
                "orders": ["view_own", "create", "edit"],
                "emails": ["view_own", "send"],
                "followups": ["view_own", "create", "edit"],
                "templates": ["view", "use"],
                "campaigns": ["view"],
                "analytics": ["view_own"]
            })
        }
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"创建角色: {role_data['display_name']}")
        else:
            print(f"角色已存在: {role_data['display_name']}")
    
    db.commit()
    print("✅ 角色初始化完成")


def init_admin_user():
    """初始化管理员账号"""
    db = get_session()
    
    # 检查是否已有管理员账号
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("⚠️  管理员账号已存在")
        return
    
    # 获取超级管理员角色
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    
    # 创建管理员账号
    admin_user = User(
        username="admin",
        email="admin@company.com",
        hashed_password=get_password_hash("admin123"),  # 默认密码：admin123
        full_name="系统管理员",
        is_active=True,
        is_superuser=True,
        department="管理部",
        position="系统管理员",
        created_at=datetime.utcnow()
    )
    
    if super_admin_role:
        admin_user.roles.append(super_admin_role)
    
    db.add(admin_user)
    db.commit()
    
    print("✅ 管理员账号创建成功")
    print("   用户名: admin")
    print("   密码: admin123")
    print("   ⚠️  请登录后立即修改密码！")


def init_demo_users():
    """初始化演示账号"""
    db = get_session()
    
    demo_users = [
        {
            "username": "sales01",
            "email": "sales01@company.com",
            "password": "sales123",
            "full_name": "张三",
            "department": "销售一部",
            "position": "业务员",
            "role_name": "sales"
        },
        {
            "username": "sales02",
            "email": "sales02@company.com",
            "password": "sales123",
            "full_name": "李四",
            "department": "销售一部",
            "position": "高级业务员",
            "role_name": "senior_sales"
        },
        {
            "username": "manager01",
            "email": "manager01@company.com",
            "password": "manager123",
            "full_name": "王经理",
            "department": "销售一部",
            "position": "部门经理",
            "role_name": "admin"
        }
    ]
    
    for user_data in demo_users:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            print(f"⚠️  用户已存在: {user_data['username']}")
            continue
        
        role = db.query(Role).filter(Role.name == user_data["role_name"]).first()
        
        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            department=user_data["department"],
            position=user_data["position"],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        if role:
            new_user.roles.append(role)
        
        db.add(new_user)
        print(f"✅ 创建用户: {user_data['username']} ({user_data['full_name']})")
    
    db.commit()
    print("✅ 演示账号初始化完成")


if __name__ == "__main__":
    print("🚀 开始初始化用户和角色...")
    
    # 初始化数据库
    init_db()
    
    # 初始化角色
    init_roles()
    
    # 初始化管理员账号
    init_admin_user()
    
    # 初始化演示账号
    init_demo_users()
    
    print("\n✅ 所有初始化完成！")
    print("\n📝 账号列表:")
    print("   admin / admin123 (超级管理员)")
    print("   manager01 / manager123 (部门经理)")
    print("   sales02 / sales123 (高级业务员)")
    print("   sales01 / sales123 (普通业务员)")
