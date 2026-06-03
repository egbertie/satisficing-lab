# 质量保证协议 Skill
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
>
> 版本: V1.0 | 创建: 2026-03-20 | 覆盖规则: 8-9

---

## 覆盖的隐性规则

| 规则编号 | 规则内容 | 触发条件 |
|----------|----------|----------|
| 规则8 | 所有AI输出必须标注置信度 | 每次输出时 |
| 规则9 | 重要决策建议需至少2个模型交叉验证 | 决策建议输出时 |

---

## 一、全局考虑（质量全链路）

### 1.1 质量保证链路

```
[内容生成] → [置信度评估] → [置信度标注] → [重要性判断] → [交叉验证] → [最终输出]
     ↑                                                                      ↓
     └───────────────────── [质量反馈循环] ←───────────────────────────────┘
```

### 1.2 三层覆盖

| 层级 | 覆盖内容 | 检查点 |
|------|----------|--------|
| L1: 基础质量 | 所有输出标注置信度 | 每次输出前 |
| L2: 决策质量 | 重要决策建议交叉验证 | 输出决策建议时 |
| L3: 持续改进 | 质量反馈与迭代 | 定期回顾 |

---

## 二、系统考虑（闭环设计）

### 2.1 质量保证闭环

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  内容生成   │ →  │ 置信度评估  │ →  │ 置信度标注  │ →  │ 重要性判断  │
│             │    │ (内部评估)  │    │ (输出标注)  │    │ (决策建议?) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                ↓
                        ┌───────────────────────────────────────┐
                        ↓                                       │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  质量反馈   │ ←  │  最终输出   │ ←  │  交叉验证   │←─────────┘
│  (迭代优化) │    │  (含标注)   │    │  (2+模型)   │ (重要决策)
└─────────────┘    └─────────────┘    └─────────────┘
```

### 2.2 质量检查矩阵

| 检查项 | 触发条件 | 阈值 | 自动动作 | 人工介入 |
|--------|----------|------|----------|----------|
| 置信度标注 | 所有AI输出 | - | 自动附加置信度标签 | 无需介入 |
| 重要性判断 | 输出决策建议 | - | 识别为重要决策 | 确认重要性 |
| 交叉验证触发 | 重要决策建议 | - | 启动多模型验证 | 等待验证结果 |
| 置信度不一致 | 多模型置信度差异 | >30% | 标记需人工复核 | 人工判断 |

---

## 三、迭代机制（PDCA）

### 3.1 每周质量分析

| 迭代维度 | 检查内容 | 优化动作 |
|----------|----------|----------|
| 置信度准确性 | 高置信度错误率 | 调整评估标准 |
| 低置信度处理 | 低置信度输出比例 | 改进信息收集 |
| 交叉验证效率 | 验证耗时与效果 | 优化验证流程 |
| 模型一致性 | 多模型一致性率 | 识别模型偏差 |
| 用户反馈 | 质量投诉/修正 | 针对性改进 |

### 3.2 置信度评估标准

| 置信度等级 | 定义 | 使用场景 | 建议动作 |
|------------|------|----------|----------|
| 🔴 低 (Low) | 信息不完整/不确定 | 推测、假设、不完整信息 | 建议验证/补充信息 |
| 🟡 中 (Medium) | 有一定依据但非绝对 | 一般性建议、常见场景 | 可接受但注意边界 |
| 🟢 高 (High) | 信息充分、逻辑严密 | 基于明确证据/标准答案 | 可信赖 |
| 🔵 已验证 (Verified) | 多模型交叉验证一致 | 重要决策、关键建议 | 高度可信 |

---

## 四、Skill化（可执行）

### 4.1 触发条件

**自动触发**:
- 每次AI输出时（自动附加置信度）
- 输出决策建议时（触发重要性判断）
- 识别为重要决策时（启动交叉验证）

**手动触发**:
```bash
# 手动进行交叉验证
./skills/quality-assurance/scripts/cross-validate.sh "决策内容"

# 查看质量报告
./skills/quality-assurance/scripts/quality-report.sh

# 检查置信度统计
./skills/quality-assurance/scripts/confidence-stats.sh
```

### 4.2 执行流程

```yaml
quality_assurance:
  confidence_labeling:
    trigger: "before_output"
    steps:
      - assess_information_completeness
      - assess_source_reliability
      - assess_logic_soundness
      - determine_confidence_level
      - format_confidence_label
      - prepend_to_output
    
  importance_assessment:
    trigger: "output_contains_recommendation"
    steps:
      - classify_output_type
      - if_decision_recommendation:
          - assess_importance_level
          - if_important:
              - trigger_cross_validation
          - else:
              - output_with_confidence_only
  
  cross_validation:
    trigger: "important_decision_detected"
    steps:
      - select_validation_models
      - send_to_secondary_model
      - collect_secondary_response
      - compare_responses
      - calculate_consistency_score
      - if_high_consistency:
          - label_as_verified
      - if_low_consistency:
          - flag_for_human_review
          - present_both_responses
      - generate_validation_report
  
  quality_review:
    trigger: "daily_scheduled"
    steps:
      - compile_confidence_distribution
      - identify_low_confidence_patterns
      - analyze_cross_validation_results
      - generate_improvement_suggestions
```

### 4.3 产出标准

| 产出物 | 格式 | 位置 | 质量要求 |
|--------|------|------|----------|
| 置信度标注 | 文本标签 | 输出内容 | 每个输出都有 |
| 交叉验证报告 | Markdown | `memory/quality/cross-validation/` | 验证结果+一致性评分 |
| 质量统计 | JSON | `memory/quality/stats.json` | 置信度分布+趋势 |
| 周质量报告 | Markdown | `memory/quality/weekly-reports/` | 分析+改进建议 |

---

## 五、流程自动化（Cron集成）

### 5.1 Cron配置

```json
{
  "jobs": [
    {
      "name": "quality-stats-update",
      "schedule": "0 */6 * * *",
      "enabled": true,
      "timeout": 60,
      "description": "更新质量统计数据"
    },
    {
      "name": "quality-weekly-report",
      "schedule": "0 20 * * 0",
      "enabled": true,
      "timeout": 120,
      "description": "生成每周质量报告"
    }
  ]
}
```

### 5.2 自动化脚本

**scripts/confidence-stats.sh**:
```bash
#!/bin/bash
# 置信度统计脚本

WORKSPACE="/root/.openclaw/workspace"
QUALITY_DIR="$WORKSPACE/memory/quality"
DATE=$(date +%Y%m%d)

mkdir -p "$QUALITY_DIR"

# 统计置信度分布
STATS_FILE="$QUALITY_DIR/stats.json"

# 如果存在历史统计文件，读取并更新
if [ -f "$QUALITY_DIR/quality-log.jsonl" ]; then
    TODAY_STATS=$(grep "\"date\":\"$DATE\"" "$QUALITY_DIR/quality-log.jsonl" 2>/dev/null | \
        python3 -c "
import sys, json
from collections import defaultdict
stats = defaultdict(int)
for line in sys.stdin:
    try:
        d = json.loads(line)
        stats[d['confidence']] += 1
    except: pass
total = sum(stats.values())
if total > 0:
    for level, count in sorted(stats.items()):
        pct = (count / total) * 100
        print(f'{level}: {count} ({pct:.1f}%)')
" 2>/dev/null)
fi

echo "=== 置信度统计 ==="
echo "日期: $DATE"
if [ -n "$TODAY_STATS" ]; then
    echo "$TODAY_STATS"
else
    echo "暂无今日数据"
fi
```

**scripts/cross-validate.sh**:
```bash
#!/bin/bash
# 交叉验证脚本
# 使用方式: ./cross-validate.sh "需要验证的决策内容"

CONTENT=$1
WORKSPACE="/root/.openclaw/workspace"
VALIDATION_DIR="$WORKSPACE/memory/quality/cross-validation"

if [ -z "$CONTENT" ]; then
    echo "使用方式: $0 '需要验证的决策内容'"
    exit 1
fi

mkdir -p "$VALIDATION_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VALIDATION_FILE="$VALIDATION_DIR/${TIMESTAMP}.md"

cat > "$VALIDATION_FILE" << EOF
# 交叉验证记录

## 验证时间
$(date '+%Y-%m-%d %H:%M:%S')

## 待验证内容
$CONTENT

## 模型A响应 (当前模型)
待记录...

## 模型B响应 (验证模型)
待记录...

## 一致性评估
- 一致性评分: 待评估
- 差异点: 待记录
- 建议: 待生成

## 验证结论
待生成...

---
*交叉验证进行中，请用另一模型运行相同问题后补充结果*
EOF

echo "✅ 交叉验证记录已创建: $VALIDATION_FILE"
echo ""
echo "请使用另一模型询问相同问题，然后将结果补充到该文件中"
