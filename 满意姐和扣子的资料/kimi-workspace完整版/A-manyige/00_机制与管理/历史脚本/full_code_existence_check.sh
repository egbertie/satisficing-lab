#!/bin/bash
# 全量代码存在性验证脚本 - 第一项任务
# 验证所有声称FIN的Skill是否真有代码

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/reports"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="$REPORT_DIR/code_existence_full_report_${TIMESTAMP}.md"

echo "=== 全量代码存在性验证开始 ==="
echo "时间: $(date)"
echo ""

mkdir -p "$REPORT_DIR"

# 统计总览
echo "正在统计..."
TOTAL_SKILLS=$(find "$WORKSPACE/skills" -name "SKILL.md" | wc -l)
TOTAL_PY=$(find "$WORKSPACE/skills" -name "*.py" | wc -l)
TOTAL_SH=$(find "$WORKSPACE/skills" -name "*.sh" | wc -l)
TOTAL_CODE=$((TOTAL_PY + TOTAL_SH))

# 开始生成报告
cat > "$REPORT_FILE" << EOF
# 全量代码存在性验证报告

**验证时间**: $(date)
**验证范围**: 所有Skill目录下的SKILL.md文件
**验证方法**: 检查每个SKILL.md对应目录下是否有可执行代码(.py/.sh)

---

## 统计总览

| 指标 | 数值 |
|------|------|
| SKILL.md 总数 | $TOTAL_SKILLS |
| Python代码文件 | $TOTAL_PY |
| Shell脚本文件 | $TOTAL_SH |
| **代码文件总数** | **$TOTAL_CODE** |
| 平均代码/Skill | $((TOTAL_CODE / (TOTAL_SKILLS > 0 ? TOTAL_SKILLS : 1))) |

---

## 详细验证结果

EOF

# 逐Skill验证
echo "正在逐个验证 $TOTAL_SKILLS 个Skill..."

echo "| Skill名称 | SKILL.md | Python | Shell | 代码行数 | 状态 |" >> "$REPORT_FILE"
echo "|-----------|----------|--------|-------|----------|------|" >> "$REPORT_FILE"

WITH_CODE=0
WITHOUT_CODE=0
SKILL_INDEX=0

find "$WORKSPACE/skills" -name "SKILL.md" | sort | while read skill_path; do
    SKILL_INDEX=$((SKILL_INDEX + 1))
    skill_dir=$(dirname "$skill_path")
    skill_name=$(basename "$skill_dir")
    
    # 统计该Skill下的代码
    py_count=$(find "$skill_dir" -name "*.py" 2>/dev/null | wc -l)
    sh_count=$(find "$skill_dir" -name "*.sh" 2>/dev/null | wc -l)
    total_lines=0
    
    # 计算代码行数
    if [ "$py_count" -gt 0 ]; then
        py_lines=$(find "$skill_dir" -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        total_lines=$((total_lines + ${py_lines:-0}))
    fi
    if [ "$sh_count" -gt 0 ]; then
        sh_lines=$(find "$skill_dir" -name "*.sh" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        total_lines=$((total_lines + ${sh_lines:-0}))
    fi
    
    # 判断状态
    if [ "$py_count" -gt 0 ] || [ "$sh_count" -gt 0 ]; then
        status="🟢 有代码"
        WITH_CODE=$((WITH_CODE + 1))
    else
        status="🔴 仅文档"
        WITHOUT_CODE=$((WITHOUT_CODE + 1))
    fi
    
    echo "| $skill_name | ✅ | $py_count | $sh_count | $total_lines | $status |" >> "$REPORT_FILE"
    
    # 每10个显示进度
    if [ $((SKILL_INDEX % 10)) -eq 0 ]; then
        echo "  已验证 $SKILL_INDEX / $TOTAL_SKILLS ..."
    fi
done

# 等待子进程完成
wait

# 重新计算最终结果（因为while在子shell中）
WITH_CODE=$(grep "🟢 有代码" "$REPORT_FILE" | wc -l)
WITHOUT_CODE=$(grep "🔴 仅文档" "$REPORT_FILE" | wc -l)

cat >> "$REPORT_FILE" << EOF

---

## 验证结论

| 类别 | 数量 | 占比 |
|------|------|------|
| 有代码的Skill | $WITH_CODE | $((WITH_CODE * 100 / (TOTAL_SKILLS > 0 ? TOTAL_SKILLS : 1)))% |
| 仅文档的Skill | $WITHOUT_CODE | $((WITHOUT_CODE * 100 / (TOTAL_SKILLS > 0 ? TOTAL_SKILLS : 1)))% |
| **总计** | **$TOTAL_SKILLS** | **100%** |

**诚实声明**: 
- 本次验证基于文件系统实际检查，非声称
- "有代码"定义为存在至少一个.py或.sh文件
- 代码行数统计包含注释和空行

---

*报告生成: $(date)*
*验证脚本: $0*
EOF

echo ""
echo "=== 验证完成 ==="
echo "报告位置: $REPORT_FILE"
echo "有代码Skill: $WITH_CODE / $TOTAL_SKILLS"
echo "仅文档Skill: $WITHOUT_CODE / $TOTAL_SKILLS"
