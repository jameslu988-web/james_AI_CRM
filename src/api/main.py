from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from concurrent.futures import ThreadPoolExecutor
from src.crm.database import init_db, get_session, EmailAccount
from datetime import datetime, timedelta
import logging
import asyncio
import uuid
import os

# 导入异常处理器
from .exceptions import (
    BusinessException,
    business_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    global_exception_handler
)

# 导入日志系统
from src.utils.logging_config import setup_logging, set_request_id
from .routers import customers, auth
from .routers import orders
from .routers import emails
from .routers import followups
from .routers import templates
from .routers import campaigns
from .routers import analytics
from .routers import custom_fields
from .routers import leads
from .routers import email_accounts
from .routers import ai_assistant
from .routers import quick_replies
from .routers import signatures
from .routers import products
from .routers import knowledge
from .routers import vector_knowledge
from .routers import prompt_templates
from .routers import prospecting  # 🔥 新增：流量获取路由
from .routers import customer_grading  # 🔥 新增：客户分级系统
from .routers import sales_funnel  # 🔥 新增：销售漏斗可视化
from .routers import tags  # 🔥 新增：客户标签系统
from .routers import auto_reply  # 🔥 新增：自动回复与审核系统
from .routers import translate  # 🔥 新增：翻译功能
from .routers import health  # 🔥 新增：健康检查

# 配置日志系统
setup_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_dir='logs',
    app_name='crm_system'
)
logger = logging.getLogger(__name__)

# 创建调度器和线程池
scheduler = AsyncIOScheduler()
thread_pool = ThreadPoolExecutor(max_workers=3)  # 最多3个并发同步任务


def sync_account_worker(account_id: int, email_address: str, sync_mode: str, is_first_sync: bool):
    """工作线程：在独立线程中执行邮件同步，不阻塞主线程"""
    from .routers.email_accounts import sync_emails_background
    from datetime import datetime, timedelta
    
    try:
        logger.info(f"🔄 [线程] 开始同步账户: {email_address} (模式: {sync_mode})")
        
        # 根据同步模式决定参数
        only_unseen = True
        since_date = None
        limit = 50  # 自动同步默认50封
        
        if sync_mode == 'unread_only':
            # 只同步未读邮件
            only_unseen = True
            since_date = None
        elif sync_mode == 'recent_30days':
            # 同步最近30天的所有邮件
            only_unseen = False
            since_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        elif sync_mode == 'all':
            # 同步所有邮件（不推荐，只用于手动触发）
            only_unseen = False
            since_date = None
        
        # 首次同步：强制限制为最近30天
        if is_first_sync and not since_date:
            since_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
            logger.info(f"   首次同步，限制为最近30天: {since_date}")
        
        sync_emails_background(
            account_id=account_id,
            limit=limit,
            only_unseen=only_unseen,
            since_date=since_date
        )
        logger.info(f"✅ [线程] 账户同步完成: {email_address}")
    except Exception as e:
        logger.error(f"❌ [线程] 账户同步失败: {email_address} - {str(e)}")


async def auto_sync_emails():
    """自动同步邮件任务 - 异步检查并提交到线程池执行"""
    logger.info("🔄 开始自动同步邮件检查...")
    
    # 使用 asyncio 的线程池执行数据库查询，避免阻塞
    loop = asyncio.get_event_loop()
    
    try:
        # 在线程池中执行数据库查询
        accounts = await loop.run_in_executor(
            None,
            lambda: get_accounts_to_sync()
        )
        
        logger.info(f"找到 {len(accounts)} 个需要同步的账户")
        
        # 为每个账户提交异步同步任务到线程池
        for account in accounts:
            loop.run_in_executor(
                thread_pool,
                sync_account_worker,
                account['id'],
                account['email'],
                account['sync_mode'],
                account['is_first_sync']
            )
            logger.info(f"📤 已提交同步任务: {account['email']} (模式: {account['sync_mode']})")
                
    except Exception as e:
        logger.error(f"自动同步任务异常: {str(e)}")


def get_accounts_to_sync():
    """获取需要同步的账户列表（在线程池中执行）"""
    db = get_session()
    accounts_to_sync = []
    
    try:
        # 获取所有启用自动同步的账户
        accounts = db.query(EmailAccount).filter(
            EmailAccount.is_active == True,
            EmailAccount.auto_sync == True
        ).all()
        
        for account in accounts:
            try:
                # 检查是否需要同步
                should_sync = False
                
                if account.last_sync_at is None:
                    should_sync = True
                else:
                    time_since_last_sync = datetime.utcnow() - account.last_sync_at
                    minutes_since_sync = time_since_last_sync.total_seconds() / 60
                    
                    if minutes_since_sync >= account.sync_interval:
                        should_sync = True
                
                if should_sync:
                    accounts_to_sync.append({
                        'id': account.id,
                        'email': account.email_address,
                        'sync_mode': account.sync_mode or 'unread_only',
                        'is_first_sync': not account.first_sync_completed
                    })
                    
            except Exception as e:
                logger.error(f"检查账户失败: {account.email_address} - {str(e)}")
                
    finally:
        db.close()
    
    return accounts_to_sync


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("🚀 启动 FastAPI 应用...")
    init_db()
    
    # 启动调度器
    scheduler.add_job(
        auto_sync_emails,
        'interval',
        minutes=5,  # 每5分钟检查一次（实际同步间隔由sync_interval控制）
        id='auto_sync_emails',
        replace_existing=True
    )
    scheduler.start()
    logger.info("✅ 邮件自动同步调度器已启动（异步模式，每5分钟检查一次）")
    logger.info(f"   线程池大小: {thread_pool._max_workers} 个工作线程")
    
    yield
    
    # 关闭时
    scheduler.shutdown()
    thread_pool.shutdown(wait=True)  # 等待所有同步任务完成
    logger.info("⏹️ 调度器和线程池已关闭")


app = FastAPI(
    title="外贸CRM系统 API",
    version="0.1.0",
    lifespan=lifespan
)

# 注册异常处理器
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 🔥 CORS配置（使用白名单模式）
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:5174').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 使用白名单
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "X-Total-Count", "X-Request-ID"],
    max_age=3600
)

# 🔥 请求ID中间件和日志中间件
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    # 生成或获取请求ID
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    set_request_id(request_id)
    
    # 记录请求
    start_time = datetime.utcnow()
    logger.info(
        f"收到请求: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        }
    )
    
    # 处理请求
    response = await call_next(request)
    
    # 添加请求ID到响应头
    response.headers["X-Request-ID"] = request_id
    
    # 记录响应
    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
    logger.info(
        f"响应请求: {request.method} {request.url.path} - {response.status_code}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration": round(duration, 2)
        }
    )
    
    return response

# 初始化数据库（沿用现有 SQLite/SQLAlchemy）
init_db()

# 路由
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(customers.router, prefix="/api", tags=["customers"]) 
app.include_router(orders.router, prefix="/api", tags=["orders"]) 
app.include_router(emails.router, prefix="/api", tags=["email_history"]) 
app.include_router(followups.router, prefix="/api", tags=["followup_records"]) 
app.include_router(templates.router, prefix="/api", tags=["email_templates"]) 
app.include_router(campaigns.router, prefix="/api", tags=["email_campaigns"]) 
app.include_router(analytics.router, prefix="/api", tags=["analytics"]) 
app.include_router(custom_fields.router, prefix="/api", tags=["custom_fields"])
app.include_router(leads.router, prefix="/api", tags=["leads"])
app.include_router(email_accounts.router, prefix="/api", tags=["email_accounts"])
app.include_router(ai_assistant.router, prefix="/api", tags=["AI助手"])
app.include_router(quick_replies.router, prefix="/api", tags=["快捷回复"]) 
app.include_router(signatures.router, tags=["邮件签名"]) 
app.include_router(products.router, prefix="/api", tags=["产品知识库"])
app.include_router(knowledge.router, prefix="/api", tags=["知识库管理"]) 
app.include_router(vector_knowledge.router, prefix="/api", tags=["向量知识库"]) 
app.include_router(prompt_templates.router, prefix="/api", tags=["提示词模板"])  # 🔥 新增
app.include_router(prospecting.router, prefix="/api", tags=["流量获取"])  # 🔥 新增流量获取路由 
app.include_router(customer_grading.router, prefix="/api", tags=["客户分级"])  # 🔥 新增客户分级系统 
app.include_router(sales_funnel.router, prefix="/api", tags=["销售漏斗"])  # 🔥 新增销售漏斗可视化 
app.include_router(tags.router, prefix="/api", tags=["客户标签"])  # 🔥 新增客户标签系统 
app.include_router(auto_reply.router, prefix="/api", tags=["自动回复与审核"])  # 🔥 新增自动回复与审核系统
# app.include_router(translate.router)  # 🔥 已废弃：使用ai_assistant中的翻译API替代
app.include_router(health.router, prefix="/api", tags=["健康检查"])  # 🔥 新增健康检查
