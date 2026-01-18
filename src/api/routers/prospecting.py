"""流量获取API - 谷歌搜索抓取潜在客户"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()

# 线程池用于执行同步的爬虫任务
thread_pool = ThreadPoolExecutor(max_workers=2)

class ProspectingConfig(BaseModel):
    """流量获取配置"""
    keywords: List[str]
    limit: int = 50
    use_proxy: bool = False
    proxy_url: Optional[str] = None

class ProspectResult(BaseModel):
    """搜索结果"""
    title: str
    url: str
    keyword: str
    snippet: str
    email: Optional[str] = None
    phone: Optional[str] = None

# 全局变量存储当前任务状态
current_task_status = {
    "running": False,
    "progress": 0,
    "total": 0,
    "results": [],
    "error": None
}

def run_google_scraper(keywords: List[str], limit: int, use_proxy: bool, proxy_url: Optional[str]):
    """在线程中执行Google搜索并将结果存入Lead表（简化版 - 仅关键词过滤）"""
    global current_task_status
    
    try:
        current_task_status["running"] = True
        current_task_status["progress"] = 0
        current_task_status["total"] = limit
        current_task_status["results"] = []
        current_task_status["error"] = None
        current_task_status["phase"] = "搜索中"
        
        from src.prospecting.google_scraper import GoogleScraper
        from src.crm.database import get_session, Lead
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        scraper = GoogleScraper()
        
        # 配置代理
        if use_proxy and proxy_url:
            scraper.set_proxy(proxy_url)
            logger.info(f"使用代理: {proxy_url}")
        
        # 第1步：执行搜索
        logger.info(f"🔍 开始搜索，关键词: {keywords}, 目标: {limit}条")
        results = scraper.find_prospects(keywords=keywords, limit=limit)
        logger.info(f"✅ 搜索完成，获得 {len(results)} 条原始结果")
        
        current_task_status["phase"] = "关键词过滤中"
        current_task_status["total_found"] = len(results)
        
        # 第2步：简单关键词过滤（不使用AI）
        db = get_session()
        leads_created = 0
        leads_skipped = 0
        leads_rejected = 0
        
        # 内裤相关关键词
        underwear_keywords = [
            'underwear', 'boxer', 'brief', 'trunk', 'lingerie', 
            '内裤', '内衣', 'boxers', 'briefs', 'trunks'
        ]
        
        for idx, result in enumerate(results):
            current_task_status["progress"] = idx + 1
            
            url = result.get('url', '')
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            if not url:
                leads_skipped += 1
                continue
            
            try:
                # 检查是否已存在
                existing = db.query(Lead).filter(Lead.website == url).first()
                if existing:
                    leads_skipped += 1
                    logger.info(f"⏭️ 跳过重复: {url}")
                    continue
                
                # 🔑 关键词过滤：必须包含内裤相关关键词
                combined_text = f"{title} {snippet} {url}".lower()
                has_underwear = any(kw in combined_text for kw in underwear_keywords)
                
                if not has_underwear:
                    logger.info(f"❌ 拒绝（无关）: {title[:50]}")
                    leads_rejected += 1
                    continue
                
                logger.info(f"✅ 通过过滤: {title[:50]}")
                
                # 保存线索
                lead = Lead(
                    company_name=title[:200] if title else 'Unknown',
                    website=url,
                    email=None,
                    phone=None,
                    country=None,
                    industry='内衣/内裤',
                    lead_source='Google搜索+关键词过滤',
                    lead_status='new',
                    lead_score=50,  # 基础分
                    priority='medium',
                    notes=f"🔍 搜索结果:\n{snippet}\n\n⚠️ 需要人工验证",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(lead)
                
                try:
                    db.flush()
                    leads_created += 1
                    logger.info(f"💾 保存线索: {title[:30]}")
                except Exception as db_error:
                    db.rollback()
                    if 'duplicate key' in str(db_error).lower():
                        logger.warning(f"跳过重复（ID冲突）: {title[:30]}")
                        leads_skipped += 1
                    else:
                        logger.error(f"保存失败: {str(db_error)}")
                    continue
                
            except Exception as e:
                logger.error(f"处理失败: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"🎉 任务完成: 创建 {leads_created} 条, 跳过 {leads_skipped} 条, 拒绝 {leads_rejected} 条")
        
        current_task_status["results"] = results
        current_task_status["progress"] = len(results)
        current_task_status["leads_created"] = leads_created
        current_task_status["leads_skipped"] = leads_skipped
        current_task_status["leads_rejected"] = leads_rejected
        current_task_status["running"] = False
        current_task_status["phase"] = "完成"
        
        return {
            "total_found": len(results),
            "leads_created": leads_created,
            "leads_skipped": leads_skipped,
            "leads_rejected": leads_rejected,
            "conversion_rate": f"{(leads_created / len(results) * 100):.1f}%" if results else "0%"
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        current_task_status["running"] = False
        current_task_status["error"] = str(e)
        logger.error(f"爬虫任务失败: {str(e)}")
        raise


@router.post("/prospecting/start")
async def start_prospecting(config: ProspectingConfig, background_tasks: BackgroundTasks):
    """
    启动流量获取任务
    """
    global current_task_status
    
    if current_task_status["running"]:
        raise HTTPException(status_code=400, detail="已有任务正在运行，请等待完成")
    
    # 在后台线程中执行
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        thread_pool,
        run_google_scraper,
        config.keywords,
        config.limit,
        config.use_proxy,
        config.proxy_url
    )
    
    return {
        "message": "流量获取任务已启动",
        "config": config.dict()
    }


@router.get("/prospecting/status")
async def get_prospecting_status():
    """
    获取当前任务状态
    """
    return current_task_status


@router.get("/prospecting/results")
async def get_prospecting_results():
    """
    获取搜索结果
    """
    return {
        "total": len(current_task_status["results"]),
        "results": current_task_status["results"]
    }


@router.post("/prospecting/stop")
async def stop_prospecting():
    """
    停止当前任务
    """
    global current_task_status
    # TODO: 实现任务停止逻辑
    current_task_status["running"] = False
    return {"message": "任务已停止"}


class ProxyTestRequest(BaseModel):
    """代理测试请求"""
    proxy_url: str

class ProxyConfigRequest(BaseModel):
    """代理配置请求"""
    proxy_url: str
    enabled: bool = True

# 全局代理配置（实际应该存储在数据库中）
proxy_config = {
    "proxy_url": "socks5://127.0.0.1:10808",
    "enabled": False
}

@router.get("/prospecting/proxy-config")
async def get_proxy_config():
    """
    获取代理配置
    """
    return proxy_config

@router.post("/prospecting/proxy-config")
async def save_proxy_config(request: ProxyConfigRequest):
    """
    保存代理配置
    """
    global proxy_config
    proxy_config["proxy_url"] = request.proxy_url
    proxy_config["enabled"] = request.enabled
    
    # TODO: 实际应该保存到数据库中
    
    return {
        "success": True,
        "message": "代理配置已保存",
        "config": proxy_config
    }

@router.post("/prospecting/test-proxy")
async def test_proxy(request: ProxyTestRequest):
    """
    测试代理连接
    """
    import httpx
    
    try:
        # httpx 0.28.x版本中，使用mounts参数配置代理
        mounts = {
            "http://": httpx.AsyncHTTPTransport(proxy=request.proxy_url),
            "https://": httpx.AsyncHTTPTransport(proxy=request.proxy_url),
        }
        
        async with httpx.AsyncClient(mounts=mounts, timeout=10.0) as client:
            response = await client.get("https://www.google.com")
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "代理连接成功",
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "message": f"代理返回状态码: {response.status_code}"
                }
    except Exception as e:
        return {
            "success": False,
            "message": f"代理连接失败: {str(e)}"
        }
