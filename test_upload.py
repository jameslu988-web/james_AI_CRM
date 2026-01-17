"""测试向量知识库上传功能"""
import requests
import sys

def test_upload():
    """测试文档上传"""
    print("📤 测试文档上传...")
    
    # 读取测试文档
    with open('test_knowledge.txt', 'rb') as f:
        files = {'file': ('test_knowledge.txt', f, 'text/plain')}
        data = {
            'title': '外贸男士内衣产品知识库',
            'category': 'product',
            'description': '包含产品信息、FAQ、价格政策等完整知识'
        }
        
        try:
            response = requests.post(
                'http://127.0.0.1:8001/api/knowledge/upload',
                files=files,
                data=data,
                headers={'Authorization': 'Bearer test'}
            )
            
            print(f"响应状态: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ 上传成功！")
                print(f"文档ID: {result['document']['id']}")
                print(f"文档标题: {result['document']['title']}")
                print(f"知识片段数: {result['document']['chunk_count']}")
                return True
            else:
                print(f"\n❌ 上传失败")
                return False
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_search():
    """测试向量搜索"""
    print("\n🔍 测试向量搜索...")
    
    queries = [
        "What is the MOQ for basic series?",
        "运动系列的价格是多少",
        "样品政策"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        try:
            response = requests.post(
                'http://127.0.0.1:8001/api/knowledge/search',
                json={'query': query, 'limit': 3},
                headers={'Authorization': 'Bearer test'}
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ 找到 {len(results)} 条相关知识:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. 相似度: {result['similarity']:.3f}")
                    print(f"     内容: {result['content'][:100]}...")
            else:
                print(f"❌ 搜索失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")

if __name__ == '__main__':
    print("🧪 向量知识库功能测试\n")
    
    # 测试上传
    if test_upload():
        # 测试搜索
        test_search()
    else:
        print("\n上传失败，跳过搜索测试")
        sys.exit(1)
    
    print("\n✅ 测试完成！")
