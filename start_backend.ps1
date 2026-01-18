# 外贸CRM系统后端启动脚本
# 使用 PostgreSQL 数据库

# 设置环境变量
$env:DB_TYPE = 'postgresql'
$env:DB_USER = 'postgres'
$env:DB_PASSWORD = 'postgres123'
$env:DB_HOST = 'localhost'
$env:DB_PORT = '5432'
$env:DB_NAME = 'crm_system'

Write-Host "🚀 启动外贸CRM系统后端..." -ForegroundColor Green
Write-Host "📦 数据库类型: PostgreSQL" -ForegroundColor Cyan
Write-Host "📍 数据库地址: $env:DB_HOST:$env:DB_PORT/$env:DB_NAME" -ForegroundColor Cyan
Write-Host ""

# 激活虚拟环境并启动
.\.venv\Scripts\Activate.ps1
uvicorn src.api.main:app --host 0.0.0.0 --port 8001
