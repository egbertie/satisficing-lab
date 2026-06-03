#!/bin/bash
# 第二项全量任务：Skill文档完整性验证
# 检查每个Skill是否有完整的SKILL.md文档

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/reports"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="$REPORT_DIR/skill_doc_completeness_report_${TIMESTAMP}.md"

echo "=== 第二项全量任务：Skill文档完整性验证 ==="
echo "时间: $(date)"
echo ""

mkdir -p "$REPORT_DIR"

# 获取所有一级Skill目录
SKILL_DIRS=$(find "$WORKSPACE/skills" -maxdepth 1 -type d | tail -n +2 | sort)
TOTAL_SKILLS=$(echo "$SKILL_DIRS" | wc -l)

cat > "$REPORT_FILE" << EOF
# Skill文档完整性验证报告

**验证时间**: $(date)
**验证范围**: 所有一级Skill目录
**验证标准**: 完整的SKILL.md应包含触发条件、执行动作、验证方式

---

## 验证结果

| Skill名称 | SKILL.md存在 | 触发条件 | 执行动作 | 验证方式 | 状态 |
|-----------|--------------|----------|----------|----------|------|

EOF

echo "正在验证 $TOTAL_SKILLS 个Skill的文档完整性..."

COMPLETE=0
INCOMPLETE=0
SKILL_INDEX=0

for skill_dir in $SKILL_DIRS; do
    SKILL_INDEX=$((SKILL_INDEX + 1))
    skill_name=$(basename "$skill_dir")
    skill_md="$skill_dir/SKILL.md"
    
    # 检查SKILL.md是否存在
    if [ -f "$skill_md" ]; then
        has_md="✅"
        
        # 检查是否包含关键部分
        has_trigger=$(grep -i "触发\|trigger\|when to use" "$skill_md" 2>/dev/null | head -1 | wc -l)
        has_action=$(grep -i "执行\|action\|how to use" "$skill_md" 2>/dev/null | head -1 | wc -l)
        has_verify=$(grep -i "验证\|verify\|check" "$skill_md" 2>/dev/null | head -1 | wc -l)
        
        trigger=$(if [ "$has_trigger" -gt 0 ]; then echo "✅"; else echo "❌"; fi)
        action=$(if [ "$has_action" -gt 0 ]; then echo "✅"; else echo "❌"; fi)
        verify=$(if [ "$has_verify" -gt 0 ]; then echo "✅"; else echo "❌"; fi)
        
        if [ "$has_trigger" -gt 0 ] && [ "$has_action" -gt 0 ] && [ "$has_verify" -gt 0 ]; then
            status="🟢 完整"
            COMPLETE=$((COMPLETE + 1))
        else
            status="🟡 部分"
            INCOMPLETE=$((INCOMPLETE + 1))
        fi
    else
        has_md="❌"
        trigger="-"
        action="-"
        verify="-"
        status="🔴 缺失"
        INCOMPLETE=$((INCOMPLETE + 1))
    fi
    
    echo "| $skill_name | $has_md | $trigger | $action | $verify | $status |" >> "$REPORT_FILE"
    
    if [ $((SKILL_INDEX % 10)) -eq 0 ]; then
        echo "  已验证 $SKILL_INDEX / $TOTAL_SKILLS ..."
    fi
done

cat >> "$REPORT_FILE" << EOF

---

## 统计结论

| 类别 | 数量 | 占比 |
|------|------|------|
| 文档完整 | $COMPLETE | $((COMPLETE * 100 / TOTAL_SKILLS))% |
| 文档部分/缺失 | $INCOMPLETE | $((INCOMPLETE * 100 / TOTAL_SKILLS))% |
| **总计** | **$TOTAL_SKILLS** | **100%** |

---

*报告生成: $(date)*
EOF

echo ""
echo "=== 第二项任务完成 ==="
echo "报告位置: $REPORT_FILE"
echo "文档完整: $COMPLETE / $TOTAL_SKILLS"
echo "文档部分/缺失: $INCOMPLETE / $TOTAL_SKILLS"
