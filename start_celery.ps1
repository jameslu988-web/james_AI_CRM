# Celery Worker 启动脚本
# 用于处理异步任务（AI分析、邮件发送等）

Write-Host "🚀 启动 Celery Worker..." -ForegroundColor Green
Write-Host "📦 Redis: localhost:6379" -ForegroundColor Cyan
Write-Host "📊 任务队列: ai_analysis, ai_reply, email_send, email_sync" -ForegroundColor Cyan
Write-Host ""

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 启动 Celery Worker
celery -A src.celery_config.celery_app worker --loglevel=info --pool=solo --concurrency=1
