"""
Celery 配置文件
用于异步任务处理（AI分析、邮件发送等）
"""

from celery import Celery
from celery.schedules import crontab  # 🔥 新增
import os

# Redis 配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 0)
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# 创建 Celery 应用
celery_app = Celery(
    'crm_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['src.tasks.email_tasks', 'src.tasks.ai_tasks']
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 时区
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务路由 - 暂时使用默认队列，后续可按需调整
    # task_routes={
    #     'src.tasks.ai_tasks.analyze_email_task': {'queue': 'ai_analysis'},
    #     'src.tasks.ai_tasks.generate_reply_task': {'queue': 'ai_reply'},
    #     'src.tasks.email_tasks.send_email_task': {'queue': 'email_send'},
    #     'src.tasks.email_tasks.sync_emails_task': {'queue': 'email_sync'},
    # },
    
    # 任务结果过期时间
    result_expires=3600,  # 1小时
    
    # 任务超时
    task_time_limit=300,  # 5分钟硬超时
    task_soft_time_limit=240,  # 4分钟软超时
    
    # 任务重试
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # 工作进程
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # 日志
    worker_hijack_root_logger=False,
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
    
    # 🔥 定时任务调度
    beat_schedule={
        # 每5分钟检查退信邮件
        'check-bounce-emails-every-5-minutes': {
            'task': 'src.tasks.email_tasks.check_all_accounts_bounce_emails',
            'schedule': 300.0,  # 300秒 = 5分钟
        },
    },
)

# 任务自动发现
celery_app.autodiscover_tasks(['src.tasks'])
