---
# 知识元数据 (5标准化)
knowledge_id: W9-B17B73
title: 成本控制协议 Skill
category: 11_Skill文档
source: skills/.archive_cost-control/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 11235
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 成本控制协议 Skill

> **知识ID**: W9-B17B73  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_cost-control/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 成本控制协议 Skill
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
>
> 版本: V1.0 | 创建: 2026-03-20 | 覆盖规则: 5-7

---

## 覆盖的隐性规则

| 规则编号 | 规则内容 | 触发条件 |
|----------|----------|----------|
| 规则5 | 使用Claude Opus需提前说明理由 | 选择模型时 |
| 规则6 | 单次成本超过¥20需记录用途 | 单次调用后 |
| 规则7 | 每日非Kimi模型总成本不超过¥50 | 每日累计检查 |

---

## 一、全局考虑（成本全链路）

### 1.1 成本链路覆盖

```
[模型选择] → [成本预估] → [理由确认] → [调用执行] → [成本记录] → [日限额检查]
     ↑                                                              ↓
     └─────────────────── [超标预警] ←──────────────────────────────┘
```

### 1.2 三层覆盖

| 层级 | 覆盖内容 | 检查点 |
|------|----------|--------|
| L1: 事前控制 | Opus使用理由、成本预估 | 模型选择前 |
| L2: 事中记录 | 单次成本记录、用途说明 | 调用完成后 |
| L3: 事后监控 | 日累计检查、限额预警 | 每次调用后+定时检查 |

---

## 二、系统考虑（闭环设计）

### 2.1 成本控制闭环

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  模型选择   │ →  │  成本预估   │ →  │  理由确认   │ →  │  调用执行   │
│ (Opus需理由)│    │ (预估成本)  │    │ (用户确认)  │    │ (执行调用)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                               ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  预警/干预  │ ←  │  日限额检查 │ ←  │  累计统计   │ ←  │  成本记录   │
│  (超标处理) │    │  (<¥50)    │    │  (非Kimi)   │    │  (>¥20记录) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 2.2 成本检查矩阵

| 检查项 | 触发条件 | 阈值 | 自动动作 | 人工介入 |
|--------|----------|------|----------|----------|
| Opus使用 | 选择Opus模型 | - | 要求理由说明 | 确认理由 |
| 高成本调用 | 单次调用完成 | >¥20 | 记录用途 | 补充说明 |
| 日限额检查 | 每次非Kimi调用后 | 累计>¥40 | 预警通知 | 确认/调整 |
| 日限额超限 | 每次非Kimi调用后 | 累计≥¥50 | 暂停非Kimi调用 | 紧急决策 |

---

## 三、迭代机制（PDCA）

### 3.1 每周成本分析

| 迭代维度 | 检查内容 | 优化动作 |
|----------|----------|----------|
| Opus使用频率 | Opus调用次数/占比 | 优化模型选择策略 |
| 高成本调用 | >¥20调用分析 | 识别可优化环节 |
| 日限额达标率 | 超限天数占比 | 调整限额或模型使用 |
| 成本效益 | 高成本→产出价值 | 优化投入产出比 |
| 记录完整性 | 超成本记录率 | 改进记录机制 |

### 3.2 成本趋势监控

```markdown
## 每周成本报告模板
- 非Kimi总成本: ¥XXX
- Opus使用次数: X次 (占比X%)
- >¥20调用次数: X次
- 日限额超限天数: X天
- 优化建议: [根据数据生成]
```

---

## 四、Skill化（可执行）

### 4.1 触发条件

**自动触发**:
- 每次模型选择时（检查Opus使用）
- 每次API调用完成后（记录成本）
- 每次非Kimi调用后（检查日限额）
- 每日定时（生成成本报告）

**手动触发**:
```bash
# 手动记录成本
./skills/cost-control/scripts/record-cost.sh <model> <cost> <usage>

# 查看今日成本
./skills/cost-control/scripts/daily-cost-check.sh

# 查看成本统计
./skills/cost-control/scripts/cost-stats.sh
```

### 4.2 执行流程

```yaml
cost_control:
  opus_usage_check:
    trigger: "model_selection"
    condition: "model == 'claude-opus'"
    steps:
      - check_opus_justification_exists
      - if_not_exists:
          - prompt_for_justification
          - require_user_confirmation
      - log_opus_usage_intent
    
  cost_recording:
    trigger: "api_call_completed"
    steps:
      - extract_call_cost
      - record_cost_to_log
      - if_cost > 20:
          - prompt_for_usage_description
          - record_usage_description
      - update_daily_total
  
  daily_limit_check:
    trigger: "non_kimi_call_completed OR scheduled"
    steps:
      - calculate_non_kimi_daily_total
      - if_total >= 50:
          - block_non_kimi_calls
          - notify_user_limit_reached
      - elif_total >= 40:
          - send_limit_warning
          - suggest_cost_saving_options
      - log_daily_cost_status
  
  daily_report:
    trigger: "daily_scheduled"
    steps:
      - compile_daily_cost_data
      - generate_cost_report
      - identify_anomalies
      - suggest_optimizations
      - archive_report
```

### 4.3 产出标准

| 产出物 | 格式 | 位置 | 质量要求 |
|--------|------|------|----------|
| 成本记录日志 | JSONL | `memory/cost/cost-log.jsonl` | 时间+模型+成本+用途 |
| 日限额状态 | JSON | `memory/cost/daily-status.json` | 当日累计+剩余额度 |
| Opus使用理由 | Markdown | `memory/cost/opus-justifications/` | 理由+批准状态 |
| 高成本记录 | Markdown | `memory/cost/high-cost-records/` | >¥20详细记录 |
| 周成本报告 | Markdown | `memory/cost/weekly-reports/` | 趋势+分析+建议 |

---

## 五、流程自动化（Cron集成）

### 5.1 Cron配置

```json
{
  "jobs": [
    {
      "name": "cost-daily-monitor",
      "schedule": "*/30 * * * *",
      "enabled": true,
      "timeout": 60,
      "description": "监控当日成本，检查日限额"
    },
    {
      "name": "cost-daily-report",
      "schedule": "0 23 * * *",
      "enabled": true,
      "timeout": 120,
      "description": "生成每日成本报告"
    },
    {
      "name": "cost-weekly-analysis",
      "schedule": "0 21 * * 0",
      "enabled": true,
      "timeout": 180,
      "description": "生成每周成本分析报告"
    }
  ]
}
```

### 5.2 自动化脚本

**scripts/record-cost.sh**:
```bash
#!/bin/bash
# 成本记录脚本

MODEL=$1
COST=$2
USAGE=$3
DATE=$(date +%Y%m%d)
TIME=$(date '+%Y-%m-%d %H:%M:%S')
WORKSPACE="/root/.openclaw/workspace"
COST_DIR="$WORKSPACE/memory/cost"

mkdir -p "$COST_DIR"

# 记录到JSONL日志
LOG_ENTRY="{\"time\":\"$TIME\",\"model\":\"$MODEL\",\"cost\":$COST,\"usage\":\"$USAGE\",\"date\":\"$DATE\"}"
echo "$LOG_ENTRY" >> "$COST_DIR/cost-log.jsonl"

echo "✅ 成本已记录: $MODEL = ¥$COST"

# 检查是否高成本(>¥20)
if (( $(echo "$COST > 20" | bc -l) )); then
    echo "⚠️ 高成本调用(≥¥20)，需要记录详细用途"
    HIGH_COST_FILE="$COST_DIR/high-cost-records/${DATE}-$(date +%H%M%S).md"
    mkdir -p "$(dirname "$HIGH_COST_FILE")"
    cat > "$HIGH_COST_FILE" << EOF
# 高成本调用记录

- 时间: $TIME
- 模型: $MODEL
- 成本: ¥$COST
- 用途: $USAGE

## 成本效益分析
待补充...
EOF
    echo "📄 高成本记录已保存: $HIGH_COST_FILE"
fi

# 更新当日累计
./skills/cost-control/scripts/daily-cost-check.sh --quiet
```

**scripts/daily-cost-check.sh**:
```bash
#!/bin/bash
# 每日成本检查脚本

QUIET=$1
WORKSPACE="/root/.openclaw/workspace"
COST_DIR="$WORKSPACE/memory/cost"
DATE=$(date +%Y%m%d)

mkdir -p "$COST_DIR"

# 计算当日非Kimi模型总成本
if [ -f "$COST_DIR/cost-log.jsonl" ]; then
    NON_KIMI_TOTAL=$(grep "\"date\":\"$DATE\"" "$COST_DIR/cost-log.jsonl" | \
        grep -v "kimi" | \
        python3 -c "import sys,json; print(sum(json.loads(l)['cost'] for l in sys.stdin))" 2>/dev/null || echo "0")
else
    NON_KIMI_TOTAL=0
fi

# 计算当日总成本
if [ -f "$COST_DIR/cost-log.jsonl" ]; then
    DAILY_TOTAL=$(grep "\"date\":\"$DATE\"" "$COST_DIR/cost-log.jsonl" | \
        python3 -c "import sys,json; print(sum(json.loads(l)['cost'] for l in sys.stdin))" 2>/dev/null || echo "0")
else
    DAILY_TOTAL=0
fi

# 检查限额
LIMIT=50
REMAINING=$(awk "BEGIN {printf \"%.2f\", $LIMIT - $NON_KIMI_TOTAL}")

# 更新状态文件
STATUS_FILE="$COST_DIR/daily-status.json"
cat > "$STATUS_FILE" << EOF
{
  "date": "$DATE",
  "non_kimi_total": $NON_KIMI_TOTAL,
  "daily_total": $DAILY_TOTAL,
  "limit": $LIMIT,
  "remaining": $REMAINING,
  "percentage_used": "$(awk "BEGIN {printf \"%.1f\", ($NON_KIMI_TOTAL / $LIMIT) * 100}")%",
  "updated_at": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

if [ "$QUIET" != "--quiet" ]; then
    echo "=== 今日成本状态 ==="
    cat "$STATUS_FILE" | python3 -m json.tool
    echo ""
    
    # 检查预警
    if (( $(echo "$NON_KIMI_TOTAL >= $LIMIT" | bc -l) )); then
        echo "🚨 警告：日限额已超限！"
        echo "   非Kimi模型成本: ¥$NON_KIMI_TOTAL / ¥$LIMIT"
        echo "   建议：暂停使用非Kimi模型，明日再恢复"
    elif (( $(echo "$NON_KIMI_TOTAL >= 40" | bc -l) )); then
        echo "⚠️ 预警：日限额即将用完"
        echo "   非Kimi模型成本: ¥$NON_KIMI_TOTAL / ¥$LIMIT"
        echo "   剩余额度: ¥$REMAINING"
    else
        echo "✅ 成本正常"
        echo "   非Kimi模型成本: ¥$NON_KIMI_TOTAL / ¥$LIMIT"
        echo "   剩余额度: ¥$REMAINING"
    fi
fi
```

**scripts/cost-stats.sh**:
```bash
#!/bin/bash
# 成本统计脚本

PERIOD=$1  # daily, weekly, monthly
WORKSPACE="/root/.openclaw/workspace"
COST_DIR="$WORKSPACE/memory/cost"

mkdir -p "$COST_DIR"

if [ "$PERIOD" == "daily" ]; then
    DATE=$(date +%Y%m%d)
    echo "=== 今日成本统计 ($DATE) ==="
    
    if [ -f "$COST_DIR/cost-log.jsonl" ]; then
        # 按模型统计
        echo ""
        echo "按模型统计:"
        grep "\"date\":\"$DATE\"" "$COST_DIR/cost-log.jsonl" | \
            python3 -c "
import sys, json
from collections import defaultdict
models = defaultdict(lambda: {'count': 0, 'cost': 0})
for line in sys.stdin:
    d = json.loads(line)
    models[d['model']]['count'] += 1
    models[d['model']]['cost'] += d['cost']
for model, data in sorted(models.items(), key=lambda x: -x[1]['cost']):
    print(f'  {model}: {data[\"count\"]}次, ¥{data[\"cost\"]:.2f}')
"
        
        # 高成本调用
        echo ""
        echo "高成本调用(≥¥20):"
        HIGH_COSTS=$(grep "\"date\":\"$DATE\"" "$COST_DIR/cost-log.jsonl" | \
            python3 -c "import sys,json; [print(json.dumps(l)) for l in sys.stdin if json.loads(l)['cost'] >= 20]" 2>/dev/null)
        if [ -z "$HIGH_COSTS" ]; then
            echo "  无"
        else
            echo "$HIGH_COSTS" | python3 -c "import sys,json; [print(f\"  {json.loads(l)['time']}: {json.loads(l)['model']} ¥{json.loads(l)['cost']}\") for l in sys.stdin]"
        fi
    else
        echo "暂无成本记录"
    fi
    
elif [ "$PERIOD" == "weekly" ]; then
    WEEK_START=$(date -d "$(date +%u) days ago" +%Y%m%d)
    echo "=== 本周成本统计 (自 $WEEK_START) ==="
    
    # 按天统计
    if [ -f "$COST_DIR/cost-log.jsonl" ]; then
        echo ""
        echo "每日成本:"
        python3 << EOF
import json
from collections import defaultdict
daily = defaultdict(lambda: {'total': 0, 'non_kimi': 0})
with open('$COST_DIR/cost-log.jsonl') as f:
    for line in f:
        d = json.loads(line)
        if d['date'] >= '$WEEK_START':
            daily[d['date']]['total'] += d['cost']
            if 'kimi' not in d['model'].lower():
                daily[d['date']]['non_kimi'] += d['cost']
for date in sorted(daily.keys()):
    data = daily[date]
    status = "🚨" if data['non_kimi'] > 50 else "⚠️" if data['non_kimi'] > 40 else "✅"
    print(f"  {date}: 总计¥{data['total']:.2f}, 非Kimi¥{data['non_kimi']:.2f} {status}")
EOF
    fi
else
    echo "使用方式: $0 [daily|weekly]"
fi
```

### 5.3 异常处理

| 异常类型 | 检测方式 | 自动响应 | 人工介入 |
|----------|----------|----------|----------|
| 日限额超限 | 累计≥¥50 | 阻止非Kimi调用 | 确认或临时调整 |
| 高成本未记录 | 成本>¥20无用途 | 提醒补充记录 | 补充说明 |
| Opus无理由 | 使用Opus无理由 | 要求补充理由 | 确认理由 |
| 成本数据异常 | 记录缺失 | 标记异常 | 检查日志 |

---

## 六、质量门控

### 6.1 5标准自检清单

- [x] **全局考虑**: 覆盖模型选择→调用→记录→监控全链路
- [x] **系统考虑**: 事前控制→事中记录→事后监控闭环
- [x] **迭代机制**: 每周成本分析+优化建议
- [x] **Skill化**: 可触发、可执行、有产出
- [x] **流程自动化**: Cron监控+自动预警+日报告

### 6.2 执行验证

```bash
# 查看成本日志
ls -la memory/cost/

# 检查今日成本状态
cat memory/cost/daily-status.json

# 查看今日统计
./skills/cost-control/scripts/cost-stats.sh daily

# 查看本周统计
./skills/cost-control/scripts/cost-stats.sh weekly
```

---

## 七、使用方式

### 7.1 在对话中使用

**选择Opus模型时**:
```
【模型选择】将使用 Claude Opus
理由: [详细说明为什么需要Opus]
预估成本: ¥XX
确认后执行。
```

**高成本调用后**:
```
【成本记录】本次调用成本: ¥XX (>¥20)
用途: [记录详细用途]
```

**日限额预警时**:
```
【成本预警】今日非Kimi模型成本: ¥XX/¥50
剩余额度: ¥XX
建议: [成本优化建议]
```

### 7.2 成本检查命令

```bash
# 手动记录成本
./skills/cost-control/scripts/record-cost.sh claude-opus 25 "复杂代码分析"

# 检查今日成本
./skills/cost-control/scripts/daily-cost-check.sh

# 查看成本统计
./skills/cost-control/scripts/cost-stats.sh daily
./skills/cost-control/scripts/cost-stats.sh weekly
```

---

## 八、成本控制最佳实践

### 8.1 模型选择建议

| 场景 | 推荐模型 | 预估成本 |
|------|----------|----------|
| 简单问答 | Kimi | ¥0-2 |
| 代码生成 | Kimi | ¥0-5 |
| 复杂分析 | Claude Sonnet | ¥3-10 |
| 深度研究 | Claude Opus | ¥10-30 |
| 创意写作 | Kimi/Claude | ¥0-5 |

### 8.2 成本优化策略

1. **先用Kimi，不够再升级**: 默认使用Kimi，输出不满意再考虑升级
2. **分段处理**: 长文本分段，避免单次大调用
3. **缓存复用**: 相似问题优先从历史记录找答案
4. **批量处理**: 多个小问题合并为一次调用
5. **定期回顾**: 每周分析高成本调用，优化模式

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*

*覆盖规则: 5(Opus需理由) | 6(≥¥20记录用途) | 7(日限额¥50)*
