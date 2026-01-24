"""
Redis缓存工具
提供统一的缓存接口和装饰器
"""
import os
import json
import hashlib
import logging
from typing import Optional, Any, Callable
from functools import wraps
import redis

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self, host: str = None, port: int = None, db: int = 1, password: str = None):
        """
        初始化Redis连接
        
        Args:
            host: Redis主机地址
            port: Redis端口
            db: 数据库编号（默认db1用于缓存）
            password: Redis密码
        """
        try:
            self.client = redis.Redis(
                host=host or os.getenv('REDIS_HOST', 'localhost'),
                port=port or int(os.getenv('REDIS_PORT', 6379)),
                db=db,
                password=password or os.getenv('REDIS_PASSWORD'),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            self.client.ping()
            self.available = True
            logger.info(f"Redis缓存系统初始化成功 [host={self.client.connection_pool.connection_kwargs['host']}, db={db}]")
        except Exception as e:
            logger.warning(f"Redis连接失败，缓存功能将降级: {str(e)}")
            self.available = False
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.available:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"获取缓存失败 [{key}]: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认5分钟
        """
        if not self.available:
            return False
        
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"设置缓存失败 [{key}]: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.available:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"删除缓存失败 [{key}]: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的所有缓存
        
        Args:
            pattern: 键模式（如 "user:*"）
        
        Returns:
            删除的键数量
        """
        if not self.available:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"清除缓存失败 [{pattern}]: {str(e)}")
            return 0


# 全局缓存实例
cache = RedisCache()


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        prefix: 缓存键前缀
        *args: 位置参数
        **kwargs: 关键字参数
    
    Returns:
        缓存键字符串
    """
    # 将参数转为字符串
    key_parts = [prefix]
    
    for arg in args:
        if hasattr(arg, '__dict__'):
            # 对象类型，使用repr
            key_parts.append(repr(arg))
        else:
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    
    # 使用MD5生成短键名
    key_string = ":".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
    
    return f"{prefix}:{key_hash}"


def cached(prefix: str, ttl: int = 300):
    """
    同步缓存装饰器
    
    Args:
        prefix: 缓存键前缀
        ttl: 缓存过期时间（秒）
    
    Example:
        @cached(prefix="user", ttl=600)
        def get_user(user_id: int):
            return db.query(User).get(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                cache.set(cache_key, result, ttl)
                logger.debug(f"缓存写入: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def async_cached(prefix: str, ttl: int = 300):
    """
    异步缓存装饰器
    
    Args:
        prefix: 缓存键前缀
        ttl: 缓存过期时间（秒）
    
    Example:
        @async_cached(prefix="email_analysis", ttl=3600)
        async def analyze_email(subject: str, body: str):
            return await ai_service.analyze(subject, body)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value
            
            # 执行异步函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                cache.set(cache_key, result, ttl)
                logger.debug(f"缓存写入: {cache_key}")
            
            return result
        
        return wrapper
    return decorator
