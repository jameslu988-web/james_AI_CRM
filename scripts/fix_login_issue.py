"""
快速修复登录问题脚本
用途：当用户无法登录时，运行此脚本快速诊断和修复
"""
import subprocess
import sys
import psycopg2
from passlib.context import CryptContext

print("="*60)
print("外贸CRM系统 - 登录问题快速修复工具")
print("="*60)

def check_bcrypt_version():
    """检查bcrypt版本"""
    print("\n[1/5] 检查bcrypt版本...")
    try:
        import bcrypt
        version = bcrypt.__version__ if hasattr(bcrypt, '__version__') else "未知"
        print(f"当前bcrypt版本: {version}")
        
        if version.startswith('5.'):
            print("❌ 检测到bcrypt 5.x版本，不兼容！")
            print("正在降级到4.0.1...")
            subprocess.run([sys.executable, "-m", "pip", "install", "bcrypt==4.0.1", "-q"])
            print("✅ bcrypt已降级到4.0.1")
            return True
        else:
            print("✅ bcrypt版本正常")
            return False
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def test_bcrypt():
    """测试bcrypt是否正常工作"""
    print("\n[2/5] 测试bcrypt功能...")
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
        test_hash = pwd_context.hash("test123")
        result = pwd_context.verify("test123", test_hash)
        if result:
            print("✅ bcrypt工作正常")
            return True
        else:
            print("❌ bcrypt验证失败")
            return False
    except Exception as e:
        print(f"❌ bcrypt测试失败: {str(e)}")
        return False

def reset_admin_password():
    """重置admin密码"""
    print("\n[3/5] 重置admin密码...")
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
        new_password = "admin123"
        new_hash = pwd_context.hash(new_password)
        
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='crm_system',
            user='postgres',
            password='postgres123'
        )
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET hashed_password = %s WHERE username = 'admin'",
            (new_hash,)
        )
        conn.commit()
        conn.close()
        
        print(f"✅ admin密码已重置为: {new_password}")
        return True
    except Exception as e:
        print(f"❌ 密码重置失败: {str(e)}")
        return False

def check_backend():
    """检查后端是否运行"""
    print("\n[4/5] 检查后端服务...")
    try:
        import requests
        response = requests.get("http://localhost:8001/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"⚠️ 后端返回异常状态码: {response.status_code}")
            return False
    except Exception as e:
        print("❌ 后端服务未运行")
        print("请手动启动: python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001")
        return False

def test_login():
    """测试登录"""
    print("\n[5/5] 测试登录功能...")
    try:
        import requests
        response = requests.post(
            "http://localhost:8001/api/auth/login",
            data={"username": "admin", "password": "admin123"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ 登录测试成功！")
            data = response.json()
            print(f"   用户: {data.get('user', {}).get('username')}")
            print(f"   Token: {data.get('access_token')[:50]}...")
            return True
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   错误信息: {response.json().get('detail', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 登录测试失败: {str(e)}")
        return False

# 执行修复流程
if __name__ == "__main__":
    bcrypt_fixed = check_bcrypt_version()
    
    if bcrypt_fixed:
        print("\n⚠️ bcrypt版本已更改，需要重启Python进程")
        print("请重新运行此脚本")
        sys.exit(0)
    
    bcrypt_ok = test_bcrypt()
    if not bcrypt_ok:
        print("\n❌ bcrypt功能异常，请手动修复")
        sys.exit(1)
    
    reset_admin_password()
    backend_ok = check_backend()
    
    if backend_ok:
        login_ok = test_login()
        if login_ok:
            print("\n" + "="*60)
            print("✅ 所有检查通过！登录功能已恢复正常")
            print("="*60)
            print("\n登录凭据:")
            print("  用户名: admin")
            print("  密码: admin123")
            print("  地址: http://localhost:5173")
            print("="*60)
        else:
            print("\n❌ 登录仍然失败，需要进一步检查")
    else:
        print("\n⚠️ 后端服务未运行，请先启动后端")
        print("\n启动命令:")
        print("  cd d:\\AI_Projects\\Automation-systerm")
        print("  python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001")
