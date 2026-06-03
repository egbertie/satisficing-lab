#!/bin/bash
# 满意解研究所 - 每日自动备份脚本
# 运行时间：每天凌晨2点

BACKUP_DIR="/root/.openclaw/workspace"
LOG_FILE="/root/.openclaw/workspace/logs/backup.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 开始每日备份..." >> $LOG_FILE

cd $BACKUP_DIR

# 检查是否有变更
if [ -z "$(git status --porcelain)" ]; then
    echo "[$DATE] 无变更，跳过备份" >> $LOG_FILE
    exit 0
fi

# 添加所有变更
git add -A

# 提交
git commit -m "Daily backup $DATE

自动备份内容：
- 所有Markdown文档
- 记忆文件
- 配置文件
- Skill文件

备份系统：满意解研究所灾备重建方案V1.0"

# 推送到GitHub
if git push origin main; then
    echo "[$DATE] ✅ 备份成功" >> $LOG_FILE
else
    echo "[$DATE] ❌ 备份失败，请检查网络或GitHub状态" >> $LOG_FILE
fi
