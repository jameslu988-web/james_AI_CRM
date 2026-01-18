"""
Google搜索客户挖掘 - 使用Google Custom Search API
"""

import os
import re
import httpx
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GoogleScraper:
    """Google搜索爬虫 - 使用官方Custom Search API"""
    
    def __init__(self):
        # Google Custom Search API配置
        self.api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyCpy6Tjsmee1db1G8WoRpougu8EihfpzZA')
        self.search_engine_id = os.getenv('GOOGLE_CSE_ID', 'a2ee9bf9e675c4043')
        self.base_url = 'https://www.googleapis.com/customsearch/v1'
        self.proxy_url = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def set_proxy(self, proxy_url: str):
        """设置SOCKS5代理"""
        self.proxy_url = proxy_url
        logger.info(f"✅ 代理已设置: {proxy_url}")
    
    def search_google(self, keyword: str, num_results: int = 10) -> List[Dict]:
        """
        使用Google Custom Search API搜索（支持分页）
        
        参数:
            keyword: 搜索关键词
            num_results: 期望结果数量（会分多次请求）
        
        返回:
            搜索结果列表
        """
        results = []
        
        try:
            # 配置httpx客户端（支持SOCKS5代理）
            if self.proxy_url:
                proxies = {
                    "http://": self.proxy_url,
                    "https://": self.proxy_url
                }
                client = httpx.Client(proxies=proxies, timeout=30.0)
            else:
                client = httpx.Client(timeout=30.0)
            
            # Google API每次最多返回10条，需要分页
            pages_needed = (num_results + 9) // 10  # 向上取整
            
            logger.info(f"🔍 搜索关键词: {keyword} (需要 {pages_needed} 页)")
            
            for page in range(pages_needed):
                start_index = page * 10 + 1  # Google的start从1开始
                
                # 构建API请求
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': keyword,
                    'num': 10,  # 每页10条
                    'start': start_index
                }
                
                logger.info(f"📄 请求第 {page+1}/{pages_needed} 页 (start={start_index})")
                response = client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'items' in data:
                        for item in data['items']:
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'keyword': keyword
                            })
                        
                        logger.info(f"✅ 第{page+1}页找到 {len(data['items'])} 条结果")
                    else:
                        logger.warning(f"⚠️ 第{page+1}页没有结果")
                        break  # 没有更多结果了
                else:
                    logger.error(f"❌ 第{page+1}页请求失败: {response.status_code}")
                    break
                
                # 已经获得足够结果
                if len(results) >= num_results:
                    break
            
            client.close()
            logger.info(f"✅ 搜索完成，共找到 {len(results)} 条结果")
            
        except Exception as e:
            logger.error(f"❌ 搜索失败 '{keyword}': {str(e)}")
        
        return results[:num_results]  # 确保不超过请求数量
    
    def find_prospects(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """
        批量搜索多个关键词
        
        参数:
            keywords: 关键词列表
            limit: 总结果数量限制
        
        返回:
            所有搜索结果（去重）
        """
        all_results = []
        seen_urls = set()
        
        for keyword in keywords:
            if len(all_results) >= limit:
                break
            
            # 每个关键词搜索10条
            results = self.search_google(keyword, num_results=10)
            
            # 去重并添加
            for result in results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)
                    
                    if len(all_results) >= limit:
                        break
        
        logger.info(f"🎯 搜索完成，共获得 {len(all_results)} 条唯一结果")
        return all_results[:limit]
