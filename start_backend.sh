#!/bin/bash
# Linux服务器后端启动脚本

# 设置环境变量
export DB_TYPE='postgresql'
export DB_USER='postgres'
export DB_PASSWORD='your_password_here'  # 记得修改！
export DB_HOST='localhost'
export DB_PORT='5432'
export DB_NAME='crm_system'

echo "🚀 启动外贸CRM系统后端..."
echo "📦 数据库类型: PostgreSQL"
echo "📍 数据库地址: $DB_HOST:$DB_PORT/$DB_NAME"
echo ""

# 激活虚拟环境
source .venv/bin/activate

# 启动服务
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
