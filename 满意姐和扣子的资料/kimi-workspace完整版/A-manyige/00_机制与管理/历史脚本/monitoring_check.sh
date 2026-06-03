#!/bin/bash
# 监控中心 - 定期检查脚本
# 执行时间: 每30分钟
# 用途: 自动检查各任务进展并更新仪表板

DASHBOARD="/root/.openclaw/workspace/dashboard/MONITORING_CENTER_STATUS.md"
LOG_FILE="/root/.openclaw/workspace/logs/monitoring_$(date +%Y%m%d).log"
REPORT_DIR="/root/.openclaw/workspace/reports"

mkdir -p "$(dirname "$LOG_FILE")"

echo "===============================================" | tee -a "$LOG_FILE"
echo "    监控中心 - 定期检查 ($(date '+%Y-%m-%d %H:%M:%S'))"
echo "===============================================" | tee -a "$LOG_FILE"

# 检查T1: 文档Skill化
echo "【T1检查】文档Skill化冲刺..." | tee -a "$LOG_FILE"
SKILL_COUNT=$(ls /root/.openclaw/workspace/skills/ 2>/dev/null | wc -l)
echo "  当前Skill数量: $SKILL_COUNT" | tee -a "$LOG_FILE"
# 检查P0批次是否已安装
P0_INSTALLED=0
for skill in brave-search automate-excel csvtoexcel copywriting duckdb-cli-ai-skills cron-scheduling markdown-converter markdown-exporter mermaid-diagrams; do
    if [ -d "/root/.openclaw/workspace/skills/$skill" ]; then
        P0_INSTALLED=$((P0_INSTALLED + 1))
    fi
done
echo "  P0批次已安装: $P0_INSTALLED/9" | tee -a "$LOG_FILE"

# 检查T2: 自建替代率
echo "【T2检查】自建替代率冲刺..." | tee -a "$LOG_FILE"
BUILTIN_COUNT=$(ls /root/.openclaw/workspace/skills/ 2>/dev/null | grep -E "(zero-idle|self-assessment|continuous-improvement|information-intelligence|task-priority|expert-digital-twin|decision-quality|knowledge-distiller|skill-evolution|intent-recognition|cross-skill|daily-reminder|resource-utilization|management-philosophy|first-principle|workspace-integrity)" | wc -l)
echo "  自建核心Skill: $BUILTIN_COUNT/19" | tee -a "$LOG_FILE"

# 检查T3: 上下文优化
echo "【T3检查】上下文优化..." | tee -a "$LOG_FILE"
if [ -f "/root/.openclaw/workspace/docs/CONTEXT_MANAGEMENT_RULES.md" ]; then
    echo "  ✅ 上下文管理规则已创建" | tee -a "$LOG_FILE"
fi
if [ -d "/root/.openclaw/workspace/archive/2026-03" ]; then
    ARCHIVED=$(ls /root/.openclaw/workspace/archive/2026-03/ 2>/dev/null | wc -l)
    echo "  ✅ 归档文件: $ARCHIVED个" | tee -a "$LOG_FILE"
fi

# 检查T4: P0行动项
echo "【T4检查】P0行动项..." | tee -a "$LOG_FILE"
if [ -x "/root/.openclaw/workspace/scripts/install_p0_batch.sh" ]; then
    echo "  ✅ P0安装脚本就绪" | tee -a "$LOG_FILE"
fi

# 更新仪表板时间戳
if [ -f "$DASHBOARD" ]; then
    sed -i "s/下次更新:.*/下次更新: $(date '+%Y-%m-%d %H:%M')/" "$DASHBOARD"
    echo "  ✅ 仪表板已更新" | tee -a "$LOG_FILE"
fi

echo "===============================================" | tee -a "$LOG_FILE"
echo "检查完成: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 如果P0批次全部安装完成，发送通知
if [ "$P0_INSTALLED" -eq 9 ]; then
    echo "🎉 P0批次Skill全部安装完成！" | tee -a "$LOG_FILE"
    echo "M3里程碑已达成" | tee -a "$LOG_FILE"
fi
