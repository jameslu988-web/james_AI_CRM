#!/bin/bash
# 数据库备份脚本

BACKUP_DIR="/var/backups/crm_system"
DB_NAME="crm_system"
DB_USER="postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "🔄 开始备份数据库..."
echo "📁 备份文件: $BACKUP_FILE"

# 执行备份
sudo -u postgres pg_dump $DB_NAME > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

echo "✅ 备份完成: ${BACKUP_FILE}.gz"

# 删除7天前的备份
find $BACKUP_DIR -name "${DB_NAME}_*.sql.gz" -mtime +7 -delete
echo "🗑️  已清理7天前的旧备份"

# 显示当前备份列表
echo ""
echo "📋 当前备份列表:"
ls -lh $BACKUP_DIR
