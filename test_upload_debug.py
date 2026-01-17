import requests
import os

# 准备测试文件
test_file_path = "test_knowledge.txt"

# 确保文件存在
if not os.path.exists(test_file_path):
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write("This is a test document for knowledge base.")

# 准备上传数据
files = {'file': open(test_file_path, 'rb')}
data = {
    'title': 'Test Document',
    'category': 'general',
    'description': 'Test description'
}

# 获取token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY4NjA4OTEwfQ.bQhvCVAyB0bNDUQNBDxrO72yXNYvW-KEnw1bSU3W5hE"

# 发送请求
url = "http://127.0.0.1:8001/api/knowledge/upload"
headers = {'Authorization': f'Bearer {token}'}

print("🔄 发送上传请求...")
try:
    response = requests.post(url, files=files, data=data, headers=headers)
    print(f"✅ 状态码: {response.status_code}")
    print(f"📄 响应内容: {response.text}")
except Exception as e:
    print(f"❌ 请求失败: {str(e)}")
finally:
    files['file'].close()
