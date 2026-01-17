"""
检查用户账号
"""
import os
from src.crm.database import get_session, User

# 设置环境变量
os.environ['DB_TYPE'] = 'postgresql'
os.environ['DB_PASSWORD'] = 'postgres123'

def check_users():
    db = get_session()
    try:
        users = db.query(User).all()
        print(f"\n📊 当前系统用户数量: {len(users)}\n")
        
        if len(users) == 0:
            print("⚠️ 没有找到任何用户！")
            print("\n💡 需要创建管理员账号才能登录")
        else:
            print("用户列表:")
            for user in users:
                print(f"  - 用户名: {user.username}")
                print(f"    邮箱: {user.email}")
                print(f"    全名: {user.full_name}")
                print(f"    是否激活: {user.is_active}")
                print(f"    是否管理员: {user.is_superuser}")
                print()
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
