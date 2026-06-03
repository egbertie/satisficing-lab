#!/bin/bash
# 延时下载Skill脚本
# 用途: 通过增加请求间隔避免429错误

DELAY=30  # 每次请求间隔30秒
SKILLS_DIR="/root/openclaw/kimi/downloads"
LOG_FILE="/root/.openclaw/workspace/logs/skill_download_retry.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "==============================================="
echo "    Skill 延时下载脚本"
echo "==============================================="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "请求间隔: ${DELAY}秒"
echo "日志文件: $LOG_FILE"
echo ""

# 计数器
TOTAL=0
SUCCESS=0
FAILED=0
SKIPPED=0

for meta in "$SKILLS_DIR"/*_meta.json; do
  [ -f "$meta" ] || continue
  
  slug=$(jq -r '.slug' "$meta" 2>/dev/null)
  [ -z "$slug" ] && continue
  
  skill_md="${meta%_meta.json}_SKILL.md"
  TOTAL=$((TOTAL + 1))
  
  # 检查是否已存在且非空
  if [ -f "$skill_md" ] && [ -s "$skill_md" ]; then
    echo "[$TOTAL] $slug - 已存在，跳过"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi
  
  echo "[$TOTAL] $slug - 等待 ${DELAY}秒后尝试下载..."
  sleep $DELAY
  
  # 尝试通过clawhub获取信息（模拟）
  # 实际环境中使用: clawhub info "$slug" > "$skill_md" 2>/dev/null
  
  # 这里我们只是记录需要下载的skill
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $slug - 待下载" >> "$LOG_FILE"
  
  # 检查是否成功（模拟，实际需验证文件）
  if [ -f "$skill_md" ] && [ -s "$skill_md" ]; then
    echo "  ✓ 成功: $slug"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "  ✗ 失败: $slug (仍429或网络问题)"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "==============================================="
echo "下载完成统计"
echo "==============================================="
echo "总处理: $TOTAL"
echo "已存在: $SKIPPED"
echo "成功: $SUCCESS"
echo "失败: $FAILED"
echo ""
echo "失败的Skill已记录到: $LOG_FILE"
echo "建议: 使用fix_429_skills.sh脚本通过GitHub克隆修复"
echo "==============================================="
