"""
系统健康检查API
监控数据库、Redis、磁盘等组件状态
"""
from fastapi import APIRouter, status
from sqlalchemy import text
import psutil
import os
from datetime import datetime
from typing import Dict, Any

from src.crm.database import get_engine, SessionLocal
from src.crm.session_manager import DatabaseSessionManager
from src.utils.cache import cache

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("/")
def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/detailed")
def detailed_health_check() -> Dict[str, Any]:
    """
    详细健康检查（包含各组件状态）
    
    Returns:
        包含所有组件健康状态的字典
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # 检查数据库
    try:
        with DatabaseSessionManager.get_db() as db:
            db.execute(text("SELECT 1")).scalar()
        
        # 获取连接池状态
        engine = get_engine()
        pool = engine.pool
        
        health_status["components"]["database"] = {
            "status": "healthy",
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "pool_usage": f"{pool.checkedout()}/{pool.size() + pool.overflow()}"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # 检查Redis
    try:
        if cache.available:
            cache.client.ping()
            info = cache.client.info('memory')
            health_status["components"]["redis"] = {
                "status": "healthy",
                "used_memory_human": info.get('used_memory_human'),
                "connected_clients": cache.client.client_list().__len__()
            }
        else:
            health_status["components"]["redis"] = {
                "status": "degraded",
                "message": "Redis不可用，缓存功能已降级"
            }
    except Exception as e:
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # 检查磁盘空间
    try:
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        health_status["components"]["disk"] = {
            "status": "healthy" if disk_percent < 90 else "warning",
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk_percent
        }
        
        if disk_percent >= 90:
            health_status["status"] = "warning"
    except Exception as e:
        health_status["components"]["disk"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    # 检查内存
    try:
        memory = psutil.virtual_memory()
        health_status["components"]["memory"] = {
            "status": "healthy" if memory.percent < 90 else "warning",
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent": memory.percent
        }
        
        if memory.percent >= 90:
            health_status["status"] = "warning"
    except Exception as e:
        health_status["components"]["memory"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    return health_status


@router.get("/db")
def database_health():
    """数据库健康检查"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1")).scalar()
        db.close()
        
        return {
            "status": "healthy",
            "message": "数据库连接正常"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/redis")
def redis_health():
    """Redis健康检查"""
    try:
        if not cache.available:
            return {
                "status": "degraded",
                "message": "Redis不可用，缓存功能已降级"
            }
        
        cache.client.ping()
        return {
            "status": "healthy",
            "message": "Redis连接正常"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
