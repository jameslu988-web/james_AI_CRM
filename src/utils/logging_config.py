"""
统一日志配置系统
支持JSON格式日志、敏感数据过滤、请求ID追踪
"""
import os
import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from contextvars import ContextVar
from pathlib import Path
from typing import Optional

# 请求ID上下文变量
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


def set_request_id(request_id: str):
    """设置当前请求ID"""
    request_id_var.set(request_id)


def get_request_id() -> str:
    """获取当前请求ID"""
    return request_id_var.get('')


class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": get_request_id()
        }
        
        # 添加额外字段
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加自定义extra字段
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 
                          'levelname', 'lineno', 'module', 'msecs', 'pathname', 
                          'process', 'processName', 'relativeCreated', 'thread', 
                          'threadName', 'exc_info', 'exc_text', 'stack_info']:
                if key not in log_data:
                    log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False)


class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器"""
    
    SENSITIVE_KEYS = ['password', 'token', 'secret', 'api_key', 'access_token', 'refresh_token']
    
    def filter(self, record: logging.LogRecord) -> bool:
        # 过滤日志消息中的敏感数据
        message = record.getMessage()
        for key in self.SENSITIVE_KEYS:
            if key in message.lower():
                record.msg = record.msg.replace(record.msg, '***FILTERED***')
        return True


def setup_logging(
    log_level: str = None,
    log_dir: str = "logs",
    app_name: str = "crm_system",
    json_format: bool = True
):
    """
    配置日志系统
    
    Args:
        log_level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_dir: 日志目录
        app_name: 应用名称
        json_format: 是否使用JSON格式
    """
    # 获取日志级别
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有handlers
    root_logger.handlers.clear()
    
    # 1. 控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    
    console_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(console_handler)
    
    # 2. 应用日志文件Handler（按大小轮转）
    app_file_handler = RotatingFileHandler(
        filename=log_path / f"{app_name}.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    app_file_handler.setLevel(level)
    app_file_handler.setFormatter(JSONFormatter() if json_format else logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    app_file_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(app_file_handler)
    
    # 3. 错误日志文件Handler
    error_file_handler = RotatingFileHandler(
        filename=log_path / f"{app_name}_error.log",
        maxBytes=50 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(JSONFormatter() if json_format else logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    root_logger.addHandler(error_file_handler)
    
    # 4. 访问日志Handler（按天轮转）
    access_file_handler = TimedRotatingFileHandler(
        filename=log_path / f"{app_name}_access.log",
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    access_file_handler.setLevel(logging.INFO)
    access_file_handler.setFormatter(JSONFormatter() if json_format else logging.Formatter(
        '%(asctime)s - %(message)s'
    ))
    
    # 创建access logger
    access_logger = logging.getLogger('access')
    access_logger.addHandler(access_file_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False
    
    # 设置第三方库日志级别
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    root_logger.info(f"日志系统初始化完成 [Level: {log_level}, Format: {'JSON' if json_format else 'TEXT'}]")


def get_logger(name: str) -> logging.Logger:
    """获取logger实例"""
    return logging.getLogger(name)
