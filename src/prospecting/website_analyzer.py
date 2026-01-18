"""
AI驱动的网站分析器 - 精准识别DTC品牌和产品占比
"""

import os
import json
import re
import httpx
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from openai import OpenAI


class WebsiteAnalyzer:
    """网站AI分析器 - 识别DTC品牌和产品类目"""
    
    def __init__(self):
        self.api_key = os.getenv('AIHUBMIX_API_KEY', 'sk-5dn0RF7nn31mpHNjEfC5Ca1579F447418aE48e7b0d8b18F7')
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=os.getenv('AIHUBMIX_BASE_URL', 'https://aihubmix.com/v1')
        )
        self.timeout = 30.0
    
    async def analyze_website(self, url: str, proxy: Optional[str] = None) -> Dict:
        """
        完整分析网站
        
        Args:
            url: 网站URL
            proxy: SOCKS5代理地址
            
        Returns:
            {
                "is_dtc": bool,  # 是否DTC官网
                "underwear_ratio": int,  # 男士内裤占比 0-100
                "product_categories": [],  # 产品品类列表
                "contact_info": {},  # 联系方式
                "company_info": {},  # 公司信息
                "quality_score": int,  # 综合质量评分 0-100
                "recommendation": str  # 推荐/不推荐
            }
        """
        try:
            # 第1步：获取网页内容
            html_content = await self._fetch_website(url, proxy)
            
            if not html_content:
                return self._get_failed_result("无法访问网站")
            
            # 第2步：提取页面信息
            page_info = self._extract_page_info(html_content, url)
            
            # 第3步：AI深度分析
            ai_analysis = await self._ai_analyze_website(page_info, url)
            
            # 第4步：计算综合评分
            result = self._calculate_final_score(ai_analysis, page_info)
            
            return result
            
        except Exception as e:
            print(f"❌ 网站分析失败 {url}: {str(e)}")
            return self._get_failed_result(str(e))
    
    async def _fetch_website(self, url: str, proxy: Optional[str] = None) -> Optional[str]:
        """获取网页内容"""
        try:
            # 配置代理
            if proxy:
                # httpx 0.28.x 版本使用mounts参数
                mounts = {
                    "http://": httpx.AsyncHTTPTransport(proxy=f"socks5://{proxy}"),
                    "https://": httpx.AsyncHTTPTransport(proxy=f"socks5://{proxy}")
                }
                async with httpx.AsyncClient(mounts=mounts, timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    })
            else:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    })
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"⚠️ HTTP {response.status_code}: {url}")
                return None
                
        except Exception as e:
            print(f"❌ 网页获取失败: {str(e)}")
            return None
    
    def _extract_page_info(self, html: str, url: str) -> Dict:
        """提取页面关键信息"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取文本内容（限制长度，避免token过多）
        text_content = soup.get_text(separator=' ', strip=True)
        text_content = ' '.join(text_content.split())[:5000]  # 限制5000字符
        
        # 提取标题
        title = soup.find('title')
        title_text = title.get_text() if title else ""
        
        # 提取meta描述
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        # 提取所有链接文本（用于识别产品类目）
        links = []
        for a in soup.find_all('a', href=True)[:100]:  # 限制100个链接
            link_text = a.get_text(strip=True)
            if link_text and len(link_text) < 50:
                links.append(link_text)
        
        # 提取邮箱
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html)
        emails = list(set(emails))[:5]  # 去重，限制5个
        
        # 提取电话
        phones = re.findall(r'\+?\d[\d\s\-\(\)]{7,}\d', text_content)
        phones = list(set(phones))[:5]
        
        return {
            "url": url,
            "title": title_text,
            "description": description,
            "text_preview": text_content[:2000],  # AI分析用
            "navigation_links": links[:30],  # 导航链接
            "emails": emails,
            "phones": phones
        }
    
    async def _ai_analyze_website(self, page_info: Dict, url: str) -> Dict:
        """AI深度分析网站"""
        
        prompt = f"""你是一个专业的B2B外贸客户分析专家。请分析以下网站，判断是否是我们的目标客户。

【网站信息】
URL: {url}
标题: {page_info['title']}
描述: {page_info['description']}
导航菜单: {', '.join(page_info['navigation_links'][:20])}
页面内容预览: {page_info['text_preview'][:1500]}

【分析目标】
我们是男士内裤制造商，寻找以下类型的客户：
1. DTC品牌官网（直接面向消费者的电商网站）
2. 网站产品中男士内裤占比30%以上
3. 50%或100%男士内裤产品的网站最佳

【排除类型】
- 新闻网站、博客、内容网站
- 批发商、制造商、供应商网站
- 全品类服装网站（男士内裤占比<30%）
- 目录站、导航站、评测站

【请严格按JSON格式返回分析结果】
{{
  "网站类型": {{
    "is_dtc_brand": true/false,  // 是否DTC品牌官网
    "is_ecommerce": true/false,  // 是否电商网站
    "site_category": "DTC品牌官网|批发商|制造商|新闻媒体|内容站|其他",
    "confidence": 0-100  // 判断置信度
  }},
  
  "产品分析": {{
    "has_mens_underwear": true/false,  // 是否销售男士内裤
    "underwear_ratio_estimate": 0-100,  // 男士内裤产品占比（百分比）
    "product_categories": ["产品类目1", "产品类目2"],  // 所有产品类目
    "primary_category": "主营品类",  // 主营品类
    "is_underwear_focused": true/false  // 是否专注内裤品类
  }},
  
  "目标客户评估": {{
    "is_target_customer": true/false,  // 是否目标客户
    "match_score": 0-100,  // 匹配度评分
    "match_reasons": ["符合原因1", "符合原因2"],  // 符合的理由
    "reject_reasons": ["排除原因1"],  // 不符合的理由（如果有）
    "recommendation": "强烈推荐|推荐|一般|不推荐|拒绝"
  }},
  
  "业务信息": {{
    "brand_name": "品牌名称",
    "target_market": ["目标市场"],  // 如：美国、欧洲
    "price_range": "高端|中端|低端",
    "business_model": "B2C|B2B|B2B2C",
    "estimated_scale": "大型|中型|小型|初创"
  }},
  
  "分析依据": {{
    "key_indicators": ["关键指标1", "关键指标2"],  // 判断依据
    "product_evidence": ["产品证据"],  // 产品相关证据
    "dtc_evidence": ["DTC证据"]  // DTC特征证据
  }}
}}

【分析要点】
1. 仔细检查导航菜单和链接文本，识别产品类目
2. 判断是否有"Shop"、"Products"、"Buy Now"等电商特征
3. 评估男士内裤在所有产品中的占比
4. 识别是否B2C（to Consumer）还是B2B（to Business）
5. 如果导航中有"Men's Underwear"、"Boxer"、"Brief"等，提高匹配度

请只返回JSON，不要其他解释。
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # 清理markdown格式
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 解析JSON
            analysis = json.loads(content)
            return analysis
            
        except Exception as e:
            print(f"❌ AI分析失败: {str(e)}")
            return self._get_default_analysis()
    
    def _calculate_final_score(self, ai_analysis: Dict, page_info: Dict) -> Dict:
        """计算最终评分"""
        
        # 提取AI分析结果
        is_dtc = ai_analysis.get('网站类型', {}).get('is_dtc_brand', False)
        underwear_ratio = ai_analysis.get('产品分析', {}).get('underwear_ratio_estimate', 0)
        is_target = ai_analysis.get('目标客户评估', {}).get('is_target_customer', False)
        match_score = ai_analysis.get('目标客户评估', {}).get('match_score', 0)
        recommendation = ai_analysis.get('目标客户评估', {}).get('recommendation', '不推荐')
        
        # 计算综合质量评分
        quality_score = 0
        
        # DTC品牌 +30分
        if is_dtc:
            quality_score += 30
        
        # 内裤占比评分（最高40分）
        if underwear_ratio >= 50:
            quality_score += 40
        elif underwear_ratio >= 30:
            quality_score += 30
        elif underwear_ratio >= 10:
            quality_score += 15
        
        # 有邮箱 +15分
        if page_info.get('emails'):
            quality_score += 15
        
        # 有电话 +10分
        if page_info.get('phones'):
            quality_score += 10
        
        # AI匹配度加权 +5分
        quality_score += min(5, match_score // 20)
        
        # 返回结果
        return {
            "success": True,
            "url": page_info['url'],
            
            # 核心指标
            "is_dtc": is_dtc,
            "underwear_ratio": underwear_ratio,
            "is_target_customer": is_target,
            "quality_score": min(100, quality_score),
            "recommendation": recommendation,
            
            # 详细信息
            "site_type": ai_analysis.get('网站类型', {}).get('site_category', '未知'),
            "product_categories": ai_analysis.get('产品分析', {}).get('product_categories', []),
            "brand_name": ai_analysis.get('业务信息', {}).get('brand_name', ''),
            "target_market": ai_analysis.get('业务信息', {}).get('target_market', []),
            "price_range": ai_analysis.get('业务信息', {}).get('price_range', ''),
            
            # 联系方式
            "emails": page_info.get('emails', []),
            "phones": page_info.get('phones', []),
            
            # AI分析详情
            "match_reasons": ai_analysis.get('目标客户评估', {}).get('match_reasons', []),
            "reject_reasons": ai_analysis.get('目标客户评估', {}).get('reject_reasons', []),
            "key_indicators": ai_analysis.get('分析依据', {}).get('key_indicators', []),
            
            # 原始数据
            "page_title": page_info.get('title', ''),
            "ai_analysis": ai_analysis
        }
    
    def _get_default_analysis(self) -> Dict:
        """默认分析结果"""
        return {
            "网站类型": {"is_dtc_brand": False, "is_ecommerce": False, "site_category": "未知", "confidence": 0},
            "产品分析": {"has_mens_underwear": False, "underwear_ratio_estimate": 0, "product_categories": [], "is_underwear_focused": False},
            "目标客户评估": {"is_target_customer": False, "match_score": 0, "match_reasons": [], "reject_reasons": ["AI分析失败"], "recommendation": "不推荐"},
            "业务信息": {"brand_name": "", "target_market": [], "price_range": "", "business_model": ""},
            "分析依据": {"key_indicators": [], "product_evidence": [], "dtc_evidence": []}
        }
    
    def _get_failed_result(self, error: str) -> Dict:
        """失败结果"""
        return {
            "success": False,
            "error": error,
            "is_dtc": False,
            "underwear_ratio": 0,
            "is_target_customer": False,
            "quality_score": 0,
            "recommendation": "拒绝"
        }
