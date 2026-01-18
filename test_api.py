#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试API是否正常工作"""
import requests

def test_customers_api():
    """测试客户API"""
    url = "http://127.0.0.1:8001/api/customers"
    params = {
        "filter": "{}",
        "range": "[0,4]",
        "sort": '["id","ASC"]'
    }
    
    try:
        r = requests.get(url, params=params, timeout=5)
        print(f"✅ 客户API测试:")
        print(f"   状态码: {r.status_code}")
        print(f"   Content-Range: {r.headers.get('content-range', 'None')}")
        if r.ok:
            data = r.json()
            print(f"   数据条数: {len(data)}")
            if len(data) > 0:
                print(f"   第一条: {data[0].get('company_name', 'N/A')}")
        else:
            print(f"   错误: {r.text[:200]}")
    except Exception as e:
        print(f"❌ 客户API测试失败: {e}")

def test_leads_api():
    """测试线索API"""
    url = "http://127.0.0.1:8001/api/leads"
    params = {
        "filter": "{}",
        "range": "[0,4]",
        "sort": '["id","ASC"]'
    }
    
    try:
        r = requests.get(url, params=params, timeout=5)
        print(f"\n✅ 线索API测试:")
        print(f"   状态码: {r.status_code}")
        print(f"   Content-Range: {r.headers.get('content-range', 'None')}")
        if r.ok:
            data = r.json()
            print(f"   数据条数: {len(data)}")
            if len(data) > 0:
                print(f"   第一条: {data[0].get('company_name', 'N/A')}")
        else:
            print(f"   错误: {r.text[:200]}")
    except Exception as e:
        print(f"❌ 线索API测试失败: {e}")

def test_email_history_api():
    """测试邮件历史API"""
    url = "http://127.0.0.1:8001/api/email_history"
    params = {
        "_start": "0",
        "_end": "5",
        "_sort": "id",
        "_order": "ASC"
    }
    
    try:
        r = requests.get(url, params=params, timeout=5)
        print(f"\n✅ 邮件历史API测试:")
        print(f"   状态码: {r.status_code}")
        print(f"   Content-Range: {r.headers.get('content-range', 'None')}")
        if r.ok:
            data = r.json()
            print(f"   数据条数: {len(data)}")
            if len(data) > 0:
                print(f"   第一条: {data[0].get('subject', 'N/A')[:50]}")
        else:
            print(f"   错误: {r.text[:200]}")
    except Exception as e:
        print(f"❌ 邮件历史API测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("开始测试后端API")
    print("=" * 60)
    test_customers_api()
    test_leads_api()
    test_email_history_api()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
