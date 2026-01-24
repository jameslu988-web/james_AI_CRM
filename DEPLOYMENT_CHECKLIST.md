# 🚀 服务器部署快速检查清单

## ✅ 部署前准备

- [ ] 购买服务器（阿里云/腾讯云/AWS等）
- [ ] 获取服务器IP地址
- [ ] 配置SSH密钥登录
- [ ] （可选）购买域名并解析到服务器IP

## ✅ 服务器基础配置

### 1. 连接到服务器
```bash
ssh root@your_server_ip
# 或
ssh -i your_key.pem ubuntu@your_server_ip
```

### 2. 创建普通用户（可选但推荐）
```bash
adduser yourusername
usermod -aG sudo yourusername
```

### 3. 配置SSH密钥（提高安全性）
```bash
# 在本地生成SSH密钥
ssh-keygen -t rsa -b 4096

# 复制公钥到服务器
ssh-copy-id yourusername@your_server_ip
```

## ✅ 一键部署

### 方式1：使用自动部署脚本

```bash
# 1. 上传部署脚本到服务器
scp deploy_to_server.sh yourusername@your_server_ip:/tmp/

# 2. 连接到服务器
ssh yourusername@your_server_ip

# 3. 执行部署脚本
sudo bash /tmp/deploy_to_server.sh
```

### 方式2：手动部署（按deploy_server.md文档操作）

## ✅ 上传代码

### 方式1：使用SCP
```bash
# 在本地执行（排除不必要的文件）
cd d:/AI_Projects/Automation-systerm
tar --exclude='.venv' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    -czf crm-system.tar.gz .

scp crm-system.tar.gz yourusername@your_server_ip:/var/www/automation-system/

# 在服务器上解压
ssh yourusername@your_server_ip
cd /var/www/automation-system
tar -xzf crm-system.tar.gz
rm crm-system.tar.gz
```

### 方式2：使用Git
```bash
# 在服务器上
cd /var/www/automation-system
git clone https://github.com/yourusername/your-repo.git .
```

### 方式3：使用rsync（推荐，支持增量更新）
```bash
# 在本地执行
rsync -avz --exclude='.venv' \
           --exclude='node_modules' \
           --exclude='__pycache__' \
           --exclude='*.pyc' \
           --exclude='.git' \
           d:/AI_Projects/Automation-systerm/ \
           yourusername@your_server_ip:/var/www/automation-system/
```

## ✅ 安装依赖

```bash
# 连接到服务器
ssh yourusername@your_server_ip

# 进入项目目录
cd /var/www/automation-system

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装Python依赖
pip install --upgrade pip
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

## ✅ 配置环境变量

```bash
# 复制生产环境配置
cd /var/www/automation-system
cp .env.production .env

# 编辑配置文件
nano .env

# 修改以下关键配置：
# - DB_PASSWORD（数据库密码）
# - SECRET_KEY（安全密钥）
# - ALLOWED_HOSTS（允许的域名/IP）
```

## ✅ 初始化数据库

```bash
cd /var/www/automation-system
source .venv/bin/activate

# 创建数据库表
python -c "from src.crm.database import init_db; init_db()"

# 初始化用户（如果需要）
python init_users.py
```

## ✅ 构建前端

```bash
cd /var/www/automation-system/frontend

# 修改API地址（如果需要）
# nano src/config.ts

# 构建生产版本
npm run build

# 验证构建结果
ls -lh dist/
```

## ✅ 启动服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动后端
sudo systemctl start crm-backend
sudo systemctl status crm-backend

# 启动Celery
sudo systemctl start crm-celery
sudo systemctl status crm-celery

# 启动Nginx
sudo systemctl start nginx
sudo systemctl status nginx

# 设置开机自启
sudo systemctl enable crm-backend
sudo systemctl enable crm-celery
sudo systemctl enable nginx
```

## ✅ 测试验证

### 1. 检查端口监听
```bash
sudo netstat -tulpn | grep -E ':(80|8001|5432|6379)'
```

### 2. 测试后端API
```bash
curl http://localhost:8001/api/customers
# 或从本地浏览器访问
# http://your_server_ip:8001/docs
```

### 3. 测试前端页面
```bash
# 在浏览器访问
http://your_server_ip
```

### 4. 检查服务日志
```bash
# 后端日志
sudo journalctl -u crm-backend -n 50 --no-pager

# Celery日志
sudo journalctl -u crm-celery -n 50 --no-pager

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## ✅ 配置HTTPS（可选但推荐）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your_domain.com

# 证书会自动续期，测试续期
sudo certbot renew --dry-run
```

## ✅ 配置定时备份

```bash
# 给备份脚本执行权限
chmod +x /var/www/automation-system/backup_database.sh

# 添加到crontab
crontab -e

# 添加以下行（每天凌晨3点备份）
0 3 * * * /var/www/automation-system/backup_database.sh >> /var/log/backup.log 2>&1
```

## ✅ 安全加固

### 1. 修改SSH端口（可选）
```bash
sudo nano /etc/ssh/sshd_config
# 修改：Port 2222
sudo systemctl restart sshd
```

### 2. 禁用root登录
```bash
sudo nano /etc/ssh/sshd_config
# 修改：PermitRootLogin no
sudo systemctl restart sshd
```

### 3. 配置fail2ban（防止暴力破解）
```bash
sudo apt install fail2ban -y
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

### 4. 配置防火墙
```bash
# 使用UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # 或你修改后的SSH端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## ✅ 性能优化（可选）

### 1. 使用Gunicorn
```bash
pip install gunicorn

# 修改systemd服务文件
sudo nano /etc/systemd/system/crm-backend.service
# ExecStart改为：
# ExecStart=/var/www/automation-system/.venv/bin/gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001

sudo systemctl daemon-reload
sudo systemctl restart crm-backend
```

### 2. 配置数据库连接池
```bash
# 编辑 src/crm/database.py
# 在 create_engine 中添加：
# pool_size=10, max_overflow=20
```

### 3. 配置Redis持久化
```bash
sudo nano /etc/redis/redis.conf
# 启用：
# save 900 1
# save 300 10
# save 60 10000
sudo systemctl restart redis-server
```

## ✅ 监控告警（可选）

### 1. 安装监控工具
```bash
# 安装htop
sudo apt install htop -y

# 安装nethogs（网络监控）
sudo apt install nethogs -y
```

### 2. 配置服务监控
```bash
# 创建监控脚本
cat > /usr/local/bin/service_monitor.sh << 'EOF'
#!/bin/bash
services=("crm-backend" "crm-celery" "nginx" "postgresql" "redis-server")
for service in "${services[@]}"; do
    if ! systemctl is-active --quiet $service; then
        echo "$(date): $service is down!" >> /var/log/service_monitor.log
        systemctl restart $service
    fi
done
EOF

chmod +x /usr/local/bin/service_monitor.sh

# 添加到crontab（每5分钟检查一次）
crontab -e
# */5 * * * * /usr/local/bin/service_monitor.sh
```

## ✅ 常见问题排查

### 问题1：无法访问网站
```bash
# 检查Nginx状态
sudo systemctl status nginx

# 检查端口
sudo netstat -tulpn | grep :80

# 检查防火墙
sudo ufw status

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

### 问题2：后端API报错
```bash
# 查看后端日志
sudo journalctl -u crm-backend -f

# 检查数据库连接
psql -U postgres -d crm_system -h localhost

# 检查环境变量
sudo systemctl show crm-backend | grep Environment
```

### 问题3：Celery任务不执行
```bash
# 查看Celery日志
sudo journalctl -u crm-celery -f

# 检查Redis
redis-cli ping

# 手动测试Celery
cd /var/www/automation-system
source .venv/bin/activate
celery -A src.celery_config worker --loglevel=debug
```

### 问题4：前端页面空白
```bash
# 检查前端构建
ls -lh /var/www/automation-system/frontend/dist/

# 重新构建
cd /var/www/automation-system/frontend
npm run build

# 检查Nginx配置
sudo nginx -t
```

## ✅ 更新部署

```bash
# 1. 备份数据库
/var/www/automation-system/backup_database.sh

# 2. 拉取最新代码
cd /var/www/automation-system
git pull
# 或使用rsync从本地更新

# 3. 更新依赖
source .venv/bin/activate
pip install -r requirements.txt

# 4. 重新构建前端（如果有更新）
cd frontend
npm install
npm run build

# 5. 重启服务
sudo systemctl restart crm-backend
sudo systemctl restart crm-celery
sudo systemctl restart nginx

# 6. 验证
curl http://localhost:8001/api/customers
```

## ✅ 回滚方案

```bash
# 1. 恢复代码
cd /var/www/automation-system
git reset --hard HEAD^

# 2. 恢复数据库
sudo -u postgres psql crm_system < /var/backups/crm_system/backup_file.sql

# 3. 重启服务
sudo systemctl restart crm-backend
sudo systemctl restart crm-celery
```

## 📞 需要帮助？

如果遇到问题：
1. 查看对应服务的日志
2. 检查防火墙和端口配置
3. 验证环境变量配置
4. 确认所有依赖服务正常运行

---

**祝部署顺利！🎉**
