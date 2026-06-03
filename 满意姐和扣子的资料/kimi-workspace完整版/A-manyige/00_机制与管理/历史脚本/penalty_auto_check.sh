#!/bin/bash
# L4惩罚层自动执行脚本
# 自动检测违规并触发惩罚

PENALTY_LOG="/root/.openclaw/workspace/logs/penalty_log.jsonl"
TRUST_SCORE_FILE="/root/.openclaw/workspace/logs/trust_score"
mkdir -p /root/.openclaw/workspace/logs

# 初始化信任积分（如果不存在）
if [ ! -f "$TRUST_SCORE_FILE" ]; then
    echo "50" > "$TRUST_SCORE_FILE"
fi

CURRENT_SCORE=$(cat "$TRUST_SCORE_FILE")
TODAY=$(date +%Y%m%d)

echo "=== L4惩罚层自动执行 ==="
echo "时间: $(date)"
echo "当前信任积分: $CURRENT_SCORE"
echo ""

PENALTY_TRIGGERED=0

# 检查1: 虚报检测（声称完成但未创建文件）
echo "【检查1】虚报检测"
# 读取今日memory文件中的声称
MEMORY_FILE="/root/.openclaw/workspace/memory/$(date +%Y-%m-%d).md"
if [ -f "$MEMORY_FILE" ]; then
    # 检查是否有"已创建"但未验证的声称
    CLAIMS=$(grep -c "已创建" "$MEMORY_FILE" 2>/dev/null || echo "0")
    echo "  发现 $CLAIMS 个声称"
    
    # 这里可以添加更复杂的验证逻辑
    # 目前记录日志，人工复核
    if [ "$CLAIMS" -gt 0 ]; then
        echo "{\"time\":\"$(date -Iseconds)\",\"type\":\"claim_check\",\"count\":$CLAIMS,\"score\":$CURRENT_SCORE}" >> "$PENALTY_LOG"
    fi
fi

# 检查2: 偷工减料检测（搜索次数不足）
echo "【检查2】偷工减料检测"
SEARCH_COUNT_FILE="/root/.openclaw/workspace/.search_counter"
if [ -f "$SEARCH_COUNT_FILE" ]; then
    COUNT=$(cat "$SEARCH_COUNT_FILE" 2>/dev/null || echo "0")
    if [ "$COUNT" -lt 5 ]; then
        echo "  ⚠️ 搜索次数不足: $COUNT/5"
        echo "{\"time\":\"$(date -Iseconds)\",\"type\":\"insufficient_search\",\"count\":$COUNT,\"penalty\":-5}" >> "$PENALTY_LOG"
        CURRENT_SCORE=$((CURRENT_SCORE - 5))
        PENALTY_TRIGGERED=1
    else
        echo "  ✅ 搜索次数达标: $COUNT"
    fi
fi

# 检查3: 未按SOP执行检测
echo "【检查3】SOP合规检测"
# 检查最近创建的.sh文件是否有对应的.plan
RECENT_SCRIPTS=$(find /root/.openclaw/workspace/scripts -name "*.sh" -mtime -1 2>/dev/null)
for script in $RECENT_SCRIPTS; do
    script_name=$(basename "$script" .sh)
    plan_file="/root/.openclaw/workspace/.plans/${script_name}.plan"
    if [ ! -f "$plan_file" ]; then
        echo "  ⚠️ $script 缺少.plan文件"
        echo "{\"time\":\"$(date -Iseconds)\",\"type\":\"no_plan_file\",\"script\":\"$script\",\"penalty\":-10}" >> "$PENALTY_LOG"
        CURRENT_SCORE=$((CURRENT_SCORE - 10))
        PENALTY_TRIGGERED=1
    fi
done

# 更新信任积分
echo "$CURRENT_SCORE" > "$TRUST_SCORE_FILE"

echo ""
if [ $PENALTY_TRIGGERED -eq 1 ]; then
    echo "⚠️ 发现违规，信任积分更新: $CURRENT_SCORE"
    echo "{\"time\":\"$(date -Iseconds)\",\"type\":\"daily_summary\",\"final_score\":$CURRENT_SCORE,\"triggered\":true}" >> "$PENALTY_LOG"
else
    echo "✅ 今日无违规，信任积分: $CURRENT_SCORE"
    echo "{\"time\":\"$(date -Iseconds)\",\"type\":\"daily_summary\",\"final_score\":$CURRENT_SCORE,\"triggered\":false}" >> "$PENALTY_LOG"
fi

echo ""
echo "惩罚日志: $PENALTY_LOG"
