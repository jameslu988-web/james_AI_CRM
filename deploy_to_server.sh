#!/bin/bash
# 服务器一键部署脚本

set -e  # 遇到错误立即退出

echo "========================================="
echo "  外贸CRM系统 - 服务器部署脚本"
echo "========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  请使用 sudo 运行此脚本"
    exit 1
fi

# 获取当前用户（非root）
ACTUAL_USER=${SUDO_USER:-$USER}
APP_DIR="/var/www/automation-system"

echo "📋 步骤1: 更新系统..."
apt update && apt upgrade -y

echo "📋 步骤2: 安装基础软件..."
apt install -y python3.10 python3.10-venv python3-pip \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    git \
    curl

echo "📋 步骤3: 安装Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi

echo "📋 步骤4: 配置PostgreSQL..."
sudo -u postgres psql << EOF
-- 创建数据库（如果不存在）
SELECT 'CREATE DATABASE crm_system' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'crm_system')\gexec

-- 设置用户权限
ALTER ROLE postgres WITH PASSWORD 'postgres123';
GRANT ALL PRIVILEGES ON DATABASE crm_system TO postgres;
EOF

echo "📋 步骤5: 启动Redis..."
systemctl start redis-server
systemctl enable redis-server

echo "📋 步骤6: 创建应用目录..."
mkdir -p $APP_DIR
chown -R $ACTUAL_USER:$ACTUAL_USER $APP_DIR

echo "📋 步骤7: 配置Systemd服务..."

# 后端服务
cat > /etc/systemd/system/crm-backend.service << EOF
[Unit]
Description=CRM Backend API Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/.venv/bin"
Environment="DB_TYPE=postgresql"
Environment="DB_USER=postgres"
Environment="DB_PASSWORD=postgres123"
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
Environment="DB_NAME=crm_system"
ExecStart=$APP_DIR/.venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery服务
cat > /etc/systemd/system/crm-celery.service << EOF
[Unit]
Description=CRM Celery Worker Service
After=network.target redis.service

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/.venv/bin"
Environment="DB_TYPE=postgresql"
Environment="DB_USER=postgres"
Environment="DB_PASSWORD=postgres123"
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
Environment="DB_NAME=crm_system"
ExecStart=$APP_DIR/.venv/bin/celery -A src.celery_config worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "📋 步骤8: 配置Nginx..."
cat > /etc/nginx/sites-available/crm-system << 'EOF'
server {
    listen 80;
    server_name _;

    # 前端静态文件
    location / {
        root /var/www/automation-system/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:8001/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
EOF

ln -sf /etc/nginx/sites-available/crm-system /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo "📋 步骤9: 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

echo ""
echo "========================================="
echo "✅ 基础环境配置完成！"
echo "========================================="
echo ""
echo "📝 下一步操作："
echo "1. 上传代码到 $APP_DIR"
echo "2. 切换到应用目录: cd $APP_DIR"
echo "3. 创建虚拟环境: python3 -m venv .venv"
echo "4. 激活环境: source .venv/bin/activate"
echo "5. 安装依赖: pip install -r requirements.txt"
echo "6. 初始化数据库: python -c 'from src.crm.database import init_db; init_db()'"
echo "7. 构建前端: cd frontend && npm install && npm run build"
echo "8. 启动服务:"
echo "   sudo systemctl start crm-backend"
echo "   sudo systemctl start crm-celery"
echo "   sudo systemctl start nginx"
echo "9. 启用开机自启:"
echo "   sudo systemctl enable crm-backend"
echo "   sudo systemctl enable crm-celery"
echo "   sudo systemctl enable nginx"
echo ""
echo "🔍 查看服务状态:"
echo "   sudo systemctl status crm-backend"
echo "   sudo systemctl status crm-celery"
echo ""
echo "📊 查看日志:"
echo "   sudo journalctl -u crm-backend -f"
echo "   sudo journalctl -u crm-celery -f"
echo ""
