#!/bin/bash
# Celery Worker启动脚本（Linux）

# 设置环境变量
export DB_TYPE='postgresql'
export DB_USER='postgres'
export DB_PASSWORD='your_password_here'  # 记得修改！
export DB_HOST='localhost'
export DB_PORT='5432'
export DB_NAME='crm_system'

echo "🔄 启动Celery Worker..."

# 激活虚拟环境
source .venv/bin/activate

# 启动Celery
celery -A src.celery_config worker --loglevel=info
