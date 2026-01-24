"""
统一异常处理系统
提供业务异常基类和全局异常处理器
"""
from datetime import datetime
from typing import Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(
        self, 
        message: str, 
        code: str = "BUSINESS_ERROR", 
        status_code: int = 400,
        details: Optional[dict] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(BusinessException):
    """数据库操作异常"""
    
    def __init__(self, message: str = "数据库操作失败", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class AIAnalysisException(BusinessException):
    """AI分析服务异常"""
    
    def __init__(self, message: str = "AI分析服务暂时不可用", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="AI_SERVICE_ERROR",
            status_code=503,
            details=details
        )


class AuthenticationException(BusinessException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""
    
    def __init__(self, resource: str, resource_id: any):
        super().__init__(
            message=f"{resource} (ID: {resource_id}) 不存在",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "id": resource_id}
        )


class ValidationException(BusinessException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details={"field": field} if field else {}
        )


# ============================================================================
# 全局异常处理器
# ============================================================================

async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理器"""
    logger.warning(
        f"业务异常: {exc.code} - {exc.message}",
        extra={
            "code": exc.code,
            "path": str(request.url.path),
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"请求验证失败: {request.url.path}",
        extra={"errors": errors}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "errors": errors,
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """SQLAlchemy异常处理器"""
    logger.error(
        f"数据库错误: {str(exc)}",
        exc_info=True,
        extra={"path": str(request.url.path)}
    )
    
    # 生产环境隐藏详细错误信息
    import os
    is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "DATABASE_ERROR",
            "message": "数据库操作失败" if is_production else str(exc),
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器（捕获所有未处理的异常）"""
    logger.error(
        f"未捕获异常: {type(exc).__name__} - {str(exc)}",
        exc_info=True,
        extra={"path": str(request.url.path)}
    )
    
    # 生产环境隐藏详细错误信息
    import os
    is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "系统内部错误" if is_production else f"{type(exc).__name__}: {str(exc)}",
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
