import requests
import os

# 创建一个新的测试文件
test_file_path = "test_new_document.txt"

with open(test_file_path, 'w', encoding='utf-8') as f:
    f.write("""# 新的测试文档

## 产品信息
这是一个全新的测试文档，用于验证向量知识库的上传功能。

### 特性
- 支持多种文件格式
- 自动向量化
- 语义搜索

### 优势
1. 快速检索
2. 智能匹配
3. 易于管理
""")

# 准备上传数据
files = {'file': open(test_file_path, 'rb')}
data = {
    'title': '新测试文档2026',
    'category': 'general',
    'description': '这是一个用于测试的新文档'
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
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n🎉 上传成功!")
        print(f"📋 文档ID: {result['document']['id']}")
        print(f"📊 分块数量: {result['document']['chunk_count']}")
except Exception as e:
    print(f"❌ 请求失败: {str(e)}")
finally:
    files['file'].close()
    
# 清理测试文件
if os.path.exists(test_file_path):
    os.remove(test_file_path)
    print(f"\n🗑️  已清理测试文件")
