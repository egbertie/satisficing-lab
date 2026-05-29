#!/bin/bash
# 满意红 · 免疫系统 L2 · 全站质量体检
# 每日自动运行，检测已知威胁模式

WORKSPACE="/Users/egbertielau/.openclaw/workspace"
REPORT="$WORKSPACE/memory/_data/quality_scan_$(date +%Y%m%d).json"
ISSUES=0
RESULTS=""

echo "🛡️ 免疫系统 L2 · 全站质量体检"
echo "   时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. event.target 检测
echo "📋 检查 1: event.target 残留..."
ET_FILES=$(grep -rl 'event\.target' "$WORKSPACE/site/"*.html 2>/dev/null | wc -l | tr -d ' ')
if [ "$ET_FILES" -gt 0 ]; then
    echo "   ⚠️ 发现 $ET_FILES 个文件含 event.target"
    RESULTS="$RESULTS\n  ⚠️ event.target: $ET_FILES files"
    ISSUES=$((ISSUES + 1))
else
    echo "   ✅ 0 个文件"
fi

# 2. crypto.subtle 检测
echo "📋 检查 2: crypto.subtle 残留..."
CR_FILES=$(grep -rl 'crypto\.subtle' "$WORKSPACE/site/"*.html 2>/dev/null | wc -l | tr -d ' ')
if [ "$CR_FILES" -gt 0 ]; then
    echo "   ⚠️ 发现 $CR_FILES 个文件含 crypto.subtle"
    RESULTS="$RESULTS\n  ⚠️ crypto.subtle: $CR_FILES files"
    ISSUES=$((ISSUES + 1))
else
    echo "   ✅ 0 个文件"
fi

# 3. SHA-256 检测
echo "📋 检查 3: SHA-256 残留..."
SH_FILES=$(grep -rl 'SHA-256\|sha256' "$WORKSPACE/site/"*.html 2>/dev/null | wc -l | tr -d ' ')
if [ "$SH_FILES" -gt 0 ]; then
    echo "   ⚠️ 发现 $SH_FILES 个文件含 SHA-256"
    RESULTS="$RESULTS\n  ⚠️ SHA-256: $SH_FILES files"
    ISSUES=$((ISSUES + 1))
else
    echo "   ✅ 0 个文件"
fi

# 4. 备份新鲜度
echo "📋 检查 4: 备份新鲜度..."
LAST_BACKUP=$(find "$WORKSPACE/site/.bak" -name "*.html" -mtime -1 2>/dev/null | wc -l | tr -d ' ')
if [ "$LAST_BACKUP" -eq 0 ]; then
    echo "   ⚠️ 24小时内无备份"
    RESULTS="$RESULTS\n  ⚠️ 备份超过24小时"
    ISSUES=$((ISSUES + 1))
else
    echo "   ✅ 最近备份: ${LAST_BACKUP} 个文件"
fi

# 5. Git 状态
echo "📋 检查 5: Git 未提交变更..."
cd "$WORKSPACE"
GIT_DIRTY=$(git status --porcelain -- '*.html' 2>/dev/null | wc -l | tr -d ' ')
if [ "$GIT_DIRTY" -gt 0 ]; then
    echo "   ⚠️ $GIT_DIRTY 个 HTML 有未提交变更"
    RESULTS="$RESULTS\n  ⚠️ 未提交: $GIT_DIRTY HTML files"
else
    echo "   ✅ 干净"
fi

# 6. localStorage 种子数据完整性
echo "📋 检查 6: 数据完整性..."
DATA_DIR="$WORKSPACE/memory/_data"
if [ -f "$DATA_DIR/dashboard_seed_v2.json" ]; then
    echo "   ✅ seed_v2 存在"
else
    echo "   ⚠️ seed_v2 缺失"
    RESULTS="$RESULTS\n  ⚠️ 种子数据缺失"
    ISSUES=$((ISSUES + 1))
fi

# Summary
echo ""
echo "=========================================="
if [ "$ISSUES" -eq 0 ]; then
    echo "✅ 免疫系统: 全部正常"
    HEALTH="clean"
else
    echo "⚠️ 免疫系统: $ISSUES 项异常"
    HEALTH="warning"
fi

# Write report
cat > "$REPORT" << JSONEOF
{
  "scan_time": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "health": "$HEALTH",
  "issues": $ISSUES,
  "checks": {
    "event_target": "$([ "$ET_FILES" -eq 0 ] && echo 'pass' || echo 'fail')",
    "crypto_subtle": "$([ "$CR_FILES" -eq 0 ] && echo 'pass' || echo 'fail')",
    "sha256": "$([ "$SH_FILES" -eq 0 ] && echo 'pass' || echo 'fail')",
    "backup_freshness": "$([ "$LAST_BACKUP" -gt 0 ] && echo 'pass' || echo 'fail')",
    "git_clean": "$([ "$GIT_DIRTY" -eq 0 ] && echo 'pass' || echo 'fail')",
    "data_integrity": "$([ -f "$DATA_DIR/dashboard_seed_v2.json" ] && echo 'pass' || echo 'fail')"
  }
}
JSONEOF

echo "📄 报告: $REPORT"
echo ""
echo "🛡️ 免疫系统 L2 扫描完成"
