#!/bin/bash
# 蓝军每周审计流程脚本
# 自动化执行每周审计任务

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/reports"
AUDIT_LOG="$WORKSPACE/skills/blue-auditor/audit_logs/weekly_audit_$(date +%Y%m%d).log"

echo "=========================================="
echo "蓝军每周审计流程 - $(date)"
echo "=========================================="
echo ""

# 创建目录
mkdir -p "$REPORT_DIR"
mkdir -p "$WORKSPACE/skills/blue-auditor/audit_logs"

# 记录开始时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始每周审计" >> "$AUDIT_LOG"

# 1. 检查所有关键文件存在性
echo "【步骤1】检查关键文件存在性..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查关键文件" >> "$AUDIT_LOG"

CRITICAL_FILES=(
    "checklists/DEEP_ANALYSIS_CHECKLIST.md"
    "checklists/REANSWER_CHECKLIST.md"
    "checklists/FIVE_DIMENSION_CHECKLIST.md"
    "checklists/STARTUP_SELF_CHECK.md"
    "scripts/workflow_lock_check.sh"
    "scripts/search_counter.sh"
    "scripts/sop_guard.sh"
    "scripts/reanswer_check.sh"
    "scripts/deep_analysis_check.sh"
    "skills/blue-auditor/SKILL.md"
    "skills/blue-auditor/blue_army_sop.py"
)

MISSING_FILES=()
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$WORKSPACE/$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - 缺失!"
        MISSING_FILES+=("$file")
    fi
done

# 2. 运行脚本测试
echo ""
echo "【步骤2】运行脚本可执行性测试..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 脚本测试" >> "$AUDIT_LOG"

TEST_SCRIPTS=(
    "scripts/workflow_lock_check.sh"
    "scripts/search_counter.sh"
    "scripts/reanswer_check.sh"
)

for script in "${TEST_SCRIPTS[@]}"; do
    SCRIPT_PATH="$WORKSPACE/$script"
    if [ -x "$SCRIPT_PATH" ]; then
        echo "  ✅ $script 可执行"
    else
        echo "  ❌ $script 不可执行，尝试修复..."
        chmod +x "$SCRIPT_PATH" 2>/dev/null || true
        if [ -x "$SCRIPT_PATH" ]; then
            echo "     已修复"
        else
            echo "     修复失败"
        fi
    fi
done

# 3. 检查PUNISHMENT_RULES
echo ""
echo "【步骤3】检查惩罚规则文件..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查惩罚规则" >> "$AUDIT_LOG"

if [ -f "$WORKSPACE/rules/PUNISHMENT_RULES.md" ]; then
    echo "  ✅ PUNISHMENT_RULES.md 存在"
else
    echo "  ⚠️ PUNISHMENT_RULES.md 不存在"
fi

# 4. 生成审计摘要
echo ""
echo "【步骤4】生成审计摘要..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 生成摘要" >> "$AUDIT_LOG"

SUMMARY_FILE="$REPORT_DIR/weekly_audit_summary_$(date +%Y%m%d).md"

cat > "$SUMMARY_FILE" << EOF
# 蓝军每周审计摘要

**审计日期**: $(date +%Y-%m-%d)  
**审计类型**: 每周例行审计  
**审计人**: 自动审计系统

---

## 关键文件检查

| 状态 | 数量 |
|------|------|
| ✅ 存在 | $(( ${#CRITICAL_FILES[@]} - ${#MISSING_FILES[@]} )) |
| ❌ 缺失 | ${#MISSING_FILES[@]} |
| **总计** | ${#CRITICAL_FILES[@]} |

### 缺失文件列表

EOF

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "无缺失文件" >> "$SUMMARY_FILE"
else
    for file in "${MISSING_FILES[@]}"; do
        echo "- ❌ $file" >> "$SUMMARY_FILE"
    done
fi

cat >> "$SUMMARY_FILE" << EOF

---

## 审计结论

EOF

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "✅ **PASS** - 所有关键文件存在" >> "$SUMMARY_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 审计结果: PASS" >> "$AUDIT_LOG"
else
    echo "❌ **FAIL** - 发现 ${#MISSING_FILES[@]} 个缺失文件" >> "$SUMMARY_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 审计结果: FAIL" >> "$AUDIT_LOG"
fi

cat >> "$SUMMARY_FILE" << EOF

---

**下次审计**: $(date -d '+7 days' +%Y-%m-%d)  
**报告路径**: $SUMMARY_FILE
EOF

# 5. 完成审计
echo ""
echo "=========================================="
echo "审计完成!"
echo "=========================================="
echo "摘要报告: $SUMMARY_FILE"
echo "详细日志: $AUDIT_LOG"
echo ""

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "✅ 所有检查通过"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 审计完成: PASS" >> "$AUDIT_LOG"
    exit 0
else
    echo "❌ 发现 ${#MISSING_FILES[@]} 个问题需要处理"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 审计完成: FAIL (${#MISSING_FILES[@]} issues)" >> "$AUDIT_LOG"
    exit 1
fi
