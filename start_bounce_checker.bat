@echo off
echo ========================================
echo   启动退信监听定时任务服务
echo ========================================
echo.

echo [1/2] 确保 Redis 服务已启动...
echo 如果未启动，请先运行 Redis
echo.

echo [2/2] 启动 Celery Beat 定时调度器...
celery -A src.celery_config beat --loglevel=info

pause
