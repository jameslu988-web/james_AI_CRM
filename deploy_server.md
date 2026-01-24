# 🚀 服务器部署指南（个人使用版）

## 📋 前提条件

### 1. 服务器基本要求
- **操作系统**: Ubuntu 20.04/22.04 或 CentOS 7/8（推荐Ubuntu）
- **内存**: 最低 2GB（推荐 4GB）
- **硬盘**: 最低 20GB
- **CPU**: 1核心即可（推荐2核心）

### 2. 需要开放的端口
```bash
# 在服务器防火墙和云服务商安全组中开放：
- 22    (SSH登录)
- 80    (HTTP - 可选，用于反向代理)
- 443   (HTTPS - 可选，用于反向代理)
- 5173  (前端开发服务器 - 生产环境不需要)
- 8001  (后端API)
```

---

## 🛠️ 部署步骤

### 步骤1：安装基础软件

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 安装Redis (Memurai的替代品)
sudo apt install redis-server -y

# 安装Node.js (前端需要)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装Nginx (反向代理 - 可选但推荐)
sudo apt install nginx -y

# 安装Git
sudo apt install git -y
```

### 步骤2：配置PostgreSQL数据库

```bash
# 切换到postgres用户
sudo -u postgres psql

# 在PostgreSQL命令行中执行：
CREATE DATABASE crm_system;
CREATE USER postgres WITH PASSWORD 'your_strong_password_here';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE crm_system TO postgres;
\q

# 允许远程访问（如果需要从本地连接数据库）
sudo nano /etc/postgresql/14/main/postgresql.conf
# 找到 listen_addresses，改为：
# listen_addresses = '*'

sudo nano /etc/postgresql/14/main/pg_hba.conf
# 在文件末尾添加：
# host    all             all             0.0.0.0/0            md5

# 重启PostgreSQL
sudo systemctl restart postgresql
```

### 步骤3：配置Redis

```bash
# 启动Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 测试Redis
redis-cli ping
# 应该返回 PONG
```

### 步骤4：部署应用代码

```bash
# 创建应用目录
sudo mkdir -p /var/www/automation-system
sudo chown $USER:$USER /var/www/automation-system
cd /var/www/automation-system

# 克隆代码（或上传代码）
# 方式1：使用Git
git clone <your-git-repo-url> .

# 方式2：使用SCP从本地上传
# 在本地执行：
# scp -r d:/AI_Projects/Automation-systerm/* user@server_ip:/var/www/automation-system/

# 创建Python虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 步骤5：配置环境变量

```bash
# 创建环境配置文件
nano /var/www/automation-system/.env

# 添加以下内容：
DB_TYPE=postgresql
DB_USER=postgres
DB_PASSWORD=your_strong_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crm_system

# Google搜索API（如果使用）
GOOGLE_API_KEY=your_api_key
GOOGLE_CSE_ID=your_cse_id
```

### 步骤6：初始化数据库

```bash
cd /var/www/automation-system
source .venv/bin/activate

# 创建数据库表
python -c "from src.crm.database import init_db; init_db()"

# 初始化用户（如果有脚本）
python init_users.py
```

### 步骤7：配置后端服务（使用Systemd）

```bash
# 创建后端服务文件
sudo nano /etc/systemd/system/crm-backend.service
```

添加以下内容：

```ini
[Unit]
Description=CRM Backend API Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/var/www/automation-system
Environment="PATH=/var/www/automation-system/.venv/bin"
Environment="DB_TYPE=postgresql"
Environment="DB_USER=postgres"
Environment="DB_PASSWORD=your_strong_password_here"
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
Environment="DB_NAME=crm_system"
ExecStart=/var/www/automation-system/.venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 创建Celery服务文件
sudo nano /etc/systemd/system/crm-celery.service
```

添加以下内容：

```ini
[Unit]
Description=CRM Celery Worker Service
After=network.target redis.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/var/www/automation-system
Environment="PATH=/var/www/automation-system/.venv/bin"
Environment="DB_TYPE=postgresql"
Environment="DB_USER=postgres"
Environment="DB_PASSWORD=your_strong_password_here"
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
Environment="DB_NAME=crm_system"
ExecStart=/var/www/automation-system/.venv/bin/celery -A src.celery_config worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl start crm-backend
sudo systemctl start crm-celery
sudo systemctl enable crm-backend
sudo systemctl enable crm-celery

# 检查服务状态
sudo systemctl status crm-backend
sudo systemctl status crm-celery
```

### 步骤8：构建并部署前端

```bash
cd /var/www/automation-system/frontend

# 安装依赖
npm install

# 修改API地址（指向服务器IP）
nano src/config.ts
# 或直接修改 vite.config.ts 中的代理配置

# 构建生产版本
npm run build

# 构建后的文件在 dist/ 目录
```

### 步骤9：配置Nginx反向代理

```bash
sudo nano /etc/nginx/sites-available/crm-system
```

添加以下配置：

```nginx
server {
    listen 80;
    server_name your_domain.com;  # 或者服务器IP

    # 前端静态文件
    location / {
        root /var/www/automation-system/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
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
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/crm-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 步骤10：配置HTTPS（可选但推荐）

```bash
# 使用Let's Encrypt免费SSL证书
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your_domain.com

# 证书会自动续期
```

---

## 🔧 日常维护命令

### 查看服务状态
```bash
# 后端状态
sudo systemctl status crm-backend

# Celery状态
sudo systemctl status crm-celery

# 查看日志
sudo journalctl -u crm-backend -f
sudo journalctl -u crm-celery -f
```

### 重启服务
```bash
# 重启后端
sudo systemctl restart crm-backend

# 重启Celery
sudo systemctl restart crm-celery

# 重启Nginx
sudo systemctl restart nginx
```

### 更新代码
```bash
cd /var/www/automation-system

# 拉取最新代码
git pull

# 重启服务
sudo systemctl restart crm-backend
sudo systemctl restart crm-celery

# 如果前端有更新
cd frontend
npm run build
```

### 数据库备份
```bash
# 备份数据库
sudo -u postgres pg_dump crm_system > backup_$(date +%Y%m%d).sql

# 恢复数据库
sudo -u postgres psql crm_system < backup_20240101.sql
```

---

## 🔒 安全建议

### 1. 修改默认端口
```bash
# 修改SSH端口（可选）
sudo nano /etc/ssh/sshd_config
# Port 2222
sudo systemctl restart sshd
```

### 2. 配置防火墙
```bash
# 使用UFW
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. 使用环境变量存储敏感信息
- 不要在代码中硬编码密码
- 使用 `.env` 文件，并添加到 `.gitignore`

### 4. 定期更新
```bash
# 定期更新系统
sudo apt update && sudo apt upgrade -y
```

---

## 📱 访问方式

部署完成后，你可以通过以下方式访问：

- **前端页面**: `http://your_server_ip` 或 `http://your_domain.com`
- **后端API**: `http://your_server_ip/api` 或 `http://your_domain.com/api`
- **API文档**: `http://your_server_ip/docs` 或 `http://your_domain.com/docs`

---

## 🆘 常见问题

### 问题1：无法连接数据库
```bash
# 检查PostgreSQL是否运行
sudo systemctl status postgresql

# 检查连接
psql -U postgres -d crm_system -h localhost
```

### 问题2：端口被占用
```bash
# 查看端口占用
sudo netstat -tulpn | grep :8001

# 杀掉进程
sudo kill -9 <PID>
```

### 问题3：权限问题
```bash
# 修改文件所有者
sudo chown -R your_username:your_username /var/www/automation-system
```

---

## 📊 性能优化建议

1. **使用Gunicorn代替Uvicorn（可选）**
```bash
pip install gunicorn
# 修改 systemd 服务文件：
# ExecStart=/var/www/automation-system/.venv/bin/gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

2. **配置Redis持久化**
```bash
sudo nano /etc/redis/redis.conf
# 启用 RDB 和 AOF
```

3. **配置数据库连接池**
在 `src/crm/database.py` 中优化连接池配置

---

## 🎯 下一步

1. ✅ 配置域名（可选）
2. ✅ 设置自动备份脚本
3. ✅ 配置监控告警（如使用 Prometheus + Grafana）
4. ✅ 配置日志收集（如使用 ELK Stack）

---

**部署完成后，记得修改所有默认密码！**
