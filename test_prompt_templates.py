"""测试提示词模板API和数据库"""
import requests
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_database():
    """检查数据库中的提示词模板"""
    print("\n=== 检查数据库中的提示词模板 ===")
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'crm_system'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres123')
        )
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'prompt_templates'
            )
        """)
        table_exists = cursor.fetchone()[0]
        print(f"提示词模板表存在: {table_exists}")
        
        if table_exists:
            # 检查数据
            cursor.execute("SELECT COUNT(*) FROM prompt_templates")
            count = cursor.fetchone()[0]
            print(f"提示词模板数量: {count}")
            
            # 显示前5条记录
            cursor.execute("""
                SELECT id, name, template_type, is_active, is_default 
                FROM prompt_templates 
                LIMIT 5
            """)
            templates = cursor.fetchall()
            print("\n前5条记录:")
            for t in templates:
                print(f"  ID: {t[0]}, 名称: {t[1]}, 类型: {t[2]}, 启用: {t[3]}, 默认: {t[4]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_api():
    """检查API是否正常"""
    print("\n=== 检查API ===")
    try:
        response = requests.get('http://localhost:8001/api/prompt-templates', timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据数量: {len(data)}")
            if data:
                print(f"第一条数据: {data[0]}")
        else:
            print(f"错误响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始诊断提示词模板问题...")
    db_ok = check_database()
    api_ok = check_api()
    
    print("\n=== 诊断结果 ===")
    print(f"数据库: {'✅ 正常' if db_ok else '❌ 异常'}")
    print(f"API: {'✅ 正常' if api_ok else '❌ 异常'}")
