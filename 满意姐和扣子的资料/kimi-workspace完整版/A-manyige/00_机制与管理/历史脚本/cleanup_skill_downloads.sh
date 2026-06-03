#!/bin/bash
# Skill下载文件清理脚本
# 位置: /root/.openclaw/workspace/scripts/cleanup_skill_downloads.sh
# 用途: 定期清理不再使用的skill上传文件

set -e

# 配置
DOWNLOAD_DIR="/root/openclaw/kimi/downloads"
RETENTION_DAYS=7
LOG_FILE="/var/log/skill_cleanup.log"
DRY_RUN=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --days)
      RETENTION_DAYS="$2"
      shift 2
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录开始
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始清理skill下载文件" | tee -a "$LOG_FILE"
echo "保留天数: $RETENTION_DAYS" | tee -a "$LOG_FILE"
echo "模拟模式: $DRY_RUN" | tee -a "$LOG_FILE"

# 检查目录是否存在
if [[ ! -d "$DOWNLOAD_DIR" ]]; then
  echo "[ERROR] 下载目录不存在: $DOWNLOAD_DIR" | tee -a "$LOG_FILE"
  exit 1
fi

# 统计清理前状态
BEFORE_COUNT=$(find "$DOWNLOAD_DIR" -type f | wc -l)
BEFORE_SIZE=$(du -sh "$DOWNLOAD_DIR" 2>/dev/null | cut -f1)
echo "清理前: $BEFORE_COUNT 个文件, 占用 $BEFORE_SIZE" | tee -a "$LOG_FILE"

# 执行清理
if [[ "$DRY_RUN" == "true" ]]; then
  # 模拟模式：只显示将要删除的文件
  echo "[DRY RUN] 以下文件将被删除:" | tee -a "$LOG_FILE"
  find "$DOWNLOAD_DIR" -type f -mtime +$RETENTION_DAYS -ls | tee -a "$LOG_FILE" || true
  DELETED_COUNT=$(find "$DOWNLOAD_DIR" -type f -mtime +$RETENTION_DAYS | wc -l)
else
  # 实际清理
  DELETED_COUNT=0
  while IFS= read -r file; do
    if [[ -f "$file" ]]; then
      rm -f "$file"
      ((DELETED_COUNT++))
      echo "[DELETED] $file" >> "$LOG_FILE"
    fi
  done < <(find "$DOWNLOAD_DIR" -type f -mtime +$RETENTION_DAYS)
fi

# 统计清理后状态
AFTER_COUNT=$(find "$DOWNLOAD_DIR" -type f | wc -l)
AFTER_SIZE=$(du -sh "$DOWNLOAD_DIR" 2>/dev/null | cut -f1)

# 记录结果
echo "清理后: $AFTER_COUNT 个文件, 占用 $AFTER_SIZE" | tee -a "$LOG_FILE"
echo "删除文件数: $DELETED_COUNT" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 清理完成" | tee -a "$LOG_FILE"
echo "---" >> "$LOG_FILE"

# 如果删除超过1000个文件，发送警告
if [[ $DELETED_COUNT -gt 1000 ]]; then
  echo "[WARNING] 单次删除文件过多($DELETED_COUNT)，请检查配置" | tee -a "$LOG_FILE"
fi

exit 0
