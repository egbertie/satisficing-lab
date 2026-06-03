#!/bin/bash
# 每小时执行简报脚本 - responses版本
# 发送执行进度给Egbertie，减少对话Token消耗

cd /root/.openclaw/workspace

# 生成简报
HOUR=$(date +%H)
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

BRIEFING_FILE="responses/briefings/briefing-${TIMESTAMP}.md"

cat > "$BRIEFING_FILE" << EOF
# 执行简报 - ${DATE} ${HOUR}:00

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 当前执行项
$(cat diary/execution/EXECUTION_LOG.md 2>/dev/null | head -40)

## 今日完成统计
- Skill完成: $(ls skills/*/ 2>/dev/null | grep -c "SKILL.md" 2>/dev/null || echo 0)
- Cron运行: $(crontab -l 2>/dev/null | grep -c "openclaw" || echo 0)
- 测试通过: $(find skills -name "test_*.py" 2>/dev/null | wc -l)

## 待决策项
$(cat responses/decisions/PENDING.md 2>/dev/null || echo "无")

## 下一步
继续推进全量建设

---
**查看方式**: 读取此文件即可，无需对话
EOF

echo "✅ 简报已保存: $BRIEFING_FILE"
