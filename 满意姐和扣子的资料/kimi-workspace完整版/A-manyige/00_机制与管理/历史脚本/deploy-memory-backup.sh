#!/bin/bash
# MEMORY.md自动备份机制部署脚本
# 部署时间: 2026-03-15
# 优先级: P0-紧急

echo "💾 部署MEMORY.md自动备份机制..."

# 1. 创建备份目录
mkdir -p /root/.openclaw/workspace/backups/memory
mkdir -p /root/.openclaw/workspace/logs/backups

# 2. 创建备份脚本
cat > /root/.openclaw/workspace/scripts/backup-memory.sh << 'EOF'
#!/bin/bash
# MEMORY.md每小时自动备份脚本

SOURCE="/root/.openclaw/workspace/MEMORY.md"
BACKUP_DIR="/root/.openclaw/workspace/backups/memory"
LOG="/root/.openclaw/workspace/logs/backups/memory-backup.log"

# 生成时间戳
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_FILE="$BACKUP_DIR/MEMORY-$TIMESTAMP.md"

# 检查源文件
if [ ! -f "$SOURCE" ]; then
    echo "[$(date)] ❌ 错误: $SOURCE 不存在" >> "$LOG"
    exit 1
fi

# 执行备份
cp "$SOURCE" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date)] ✅ 备份成功: $BACKUP_FILE" >> "$LOG"
    
    # 保留最近48个备份（2天），删除旧的
    ls -t $BACKUP_DIR/MEMORY-*.md | tail -n +49 | xargs -r rm
    
    # 同时备份到GitHub（如果配置了自动提交）
    if [ -d "/root/.openclaw/workspace/.git" ]; then
        cd /root/.openclaw/workspace
        git add MEMORY.md
        git commit -m "auto: MEMORY.md backup $TIMESTAMP" --quiet
        git push --quiet 2>/dev/null || echo "[$(date)] ⚠️ GitHub推送失败（可能网络问题）" >> "$LOG"
    fi
    
    exit 0
else
    echo "[$(date)] ❌ 备份失败" >> "$LOG"
    exit 1
fi
EOF

chmod +x /root/.openclaw/workspace/scripts/backup-memory.sh

# 3. 添加到Cron（每小时备份）
echo "添加MEMORY.md自动备份Cron..."
(
    crontab -l 2>/dev/null
    echo ""
    echo "# MEMORY.md自动备份机制 - P0紧急"
    echo "17 * * * * /root/.openclaw/workspace/scripts/backup-memory.sh"
) | crontab -

echo "✅ MEMORY.md自动备份机制部署完成"
echo ""
echo "配置详情:"
echo "  - 备份频率: 每小时（整点17分）"
echo "  - 保留数量: 最近48个备份（2天）"
echo "  - 备份位置: /root/.openclaw/workspace/backups/memory/"
echo "  - 日志位置: /root/.openclaw/workspace/logs/backups/memory-backup.log"
echo "  - GitHub同步: 自动提交并推送"
