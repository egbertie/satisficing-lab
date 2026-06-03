---
# 知识元数据 (5标准化)
knowledge_id: W10-CFC5ED
title: 执行流程协议 Skill
category: 11_Skill文档
source: skills/.archive_execution-protocol/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 8114
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 执行流程协议 Skill

> **知识ID**: W10-CFC5ED  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_execution-protocol/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 执行流程协议 Skill
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
>
> 版本: V1.0 | 创建: 2026-03-20 | 覆盖规则: 1-4

---

## 覆盖的隐性规则

| 规则编号 | 规则内容 | 执行点 |
|----------|----------|--------|
| 规则1 | 安排必确认、执行必汇报、问题必升级 | 任务全生命周期 |
| 规则2 | 先完成，再完美 | 执行阶段 |
| 规则3 | 砍掉冗余环节，直奔核心 | 规划阶段 |
| 规则4 | 任务A完成→立即启动任务B | 任务衔接点 |

---

## 一、全局考虑（全流程覆盖）

### 1.1 任务生命周期状态机

```
[创建] → [确认] → [执行] → [汇报] → [完成] → [启动下一任务]
   ↑       ↑       ↑       ↑       ↑           |
   │       │       │       │       └───────────┘
   │       │       │       │                   
   └───────┴───────┴───────┴──→ [问题识别] → [升级]
```

### 1.2 四层覆盖

| 层级 | 覆盖内容 | 检查时机 |
|------|----------|----------|
| L1: 任务规划 | 确认理解、识别核心 | 任务开始时 |
| L2: 任务执行 | 先完成、砍冗余、边做边汇报 | 执行过程中 |
| L3: 任务衔接 | 完成后立即启动下一任务 | 任务完成时 |
| L4: 问题处理 | 识别问题、立即升级 | 发现问题时 |

---

## 二、系统考虑（闭环设计）

### 2.1 执行协议闭环

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   确认理解   │ →  │   精简执行   │ →  │   阶段汇报   │ →  │   衔接下一   │
│ (安排必确认) │    │ (先完成再完美)│    │ (执行必汇报) │    │ (任务链触发) │
│ (砍冗余直奔) │    │              │    │ (问题必升级) │    │              │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
        ↑                                                        │
        └────────────────────────────────────────────────────────┘
                        (问题升级后重新开始)
```

### 2.2 核心检查矩阵

| 检查项 | 触发条件 | 自动动作 | 人工介入 |
|--------|----------|----------|----------|
| 任务确认 | 新任务创建 | 输出确认清单 | 用户确认 |
| 冗余检测 | 规划阶段 | 标记非核心环节 | 用户决策 |
| 进度汇报 | 每完成25%/50%/75%/100% | 生成进度快照 | 阻塞时升级 |
| 问题升级 | 阻塞>10分钟 | 标记升级+通知 | 等待处理 |
| 任务衔接 | 任务完成 | 自动启动下一任务 | 用户可取消 |

---

## 三、迭代机制（PDCA）

### 3.1 每周迭代检查

| 迭代维度 | 检查内容 | 优化动作 |
|----------|----------|----------|
| 确认效率 | 确认→执行平均时间 | 优化确认模板 |
| 执行效率 | 任务完成平均时长 | 识别冗余环节 |
| 汇报质量 | 汇报完整度评分 | 改进汇报模板 |
| 衔接流畅度 | 任务衔接等待时间 | 优化触发机制 |
| 升级准确率 | 真问题vs误报 | 调整升级阈值 |

### 3.2 持续改进日志

```markdown
## 2026-03-20 V1.0创建
- 将规则1-4转化为可执行Skill
- 建立任务生命周期状态机
- 设计四层检查体系
- 集成Cron自动检查
```

---

## 四、Skill化（可执行）

### 4.1 触发条件

**自动触发**:
- 新任务创建时
- 任务进度达到25%/50%/75%/100%时
- 任务标记完成时
- 阻塞检测超时(10分钟)时

**手动触发**:
```bash
# 手动执行协议检查
./skills/execution-protocol/scripts/protocol-check.sh [task-id]

# 手动触发任务衔接检查
./skills/execution-protocol/scripts/task-chain-check.sh

# 查看协议执行统计
./skills/execution-protocol/scripts/protocol-stats.sh
```

### 4.2 执行流程

```yaml
execution_protocol:
  task_confirmation:
    trigger: "new_task_created"
    steps:
      - output_confirmation_checklist
      - identify_core_deliverable
      - mark_redundant_steps
      - wait_user_confirmation
    
  progress_reporting:
    trigger: "milestone_reached"
    milestones: [25, 50, 75, 100]
    steps:
      - calculate_progress_percentage
      - identify_blockers_if_any
      - generate_progress_snapshot
      - report_to_user
      - escalate_if_blocked
  
  task_completion:
    trigger: "task_marked_complete"
    steps:
      - verify_deliverable_exists
      - generate_completion_report
      - check_next_task_in_chain
      - auto_start_next_if_configured
      - notify_user_of_next_task
  
  problem_escalation:
    trigger: "blocker_detected OR timeout"
    steps:
      - classify_blocker_severity
      - generate_escalation_report
      - notify_user_immediately
      - pause_dependent_tasks
      - suggest_resolution_options
```

### 4.3 产出标准

| 产出物 | 格式 | 位置 | 质量要求 |
|--------|------|------|----------|
| 任务确认清单 | Markdown | `memory/protocol/{task-id}-confirmation.md` | 核心目标+冗余标记 |
| 进度汇报 | 文本 | 对话中 | 进度%+阻塞说明 |
| 完成报告 | Markdown | `memory/protocol/{task-id}-completion.md` | 交付物+下一任务 |
| 升级报告 | Markdown | `memory/protocol/{task-id}-escalation.md` | 问题+建议方案 |
| 协议执行统计 | JSON | `memory/protocol/stats.json` | 执行率+效率数据 |

---

## 五、流程自动化（Cron集成）

### 5.1 Cron配置

```json
{
  "jobs": [
    {
      "name": "execution-protocol-monitor",
      "schedule": "*/15 * * * *",
      "enabled": true,
      "timeout": 60,
      "description": "监控任务执行状态，检查阻塞和升级"
    },
    {
      "name": "task-chain-checker",
      "schedule": "*/5 * * * *",
      "enabled": true,
      "timeout": 30,
      "description": "检查完成的任务，触发下一任务"
    },
    {
      "name": "daily-protocol-stats",
      "schedule": "0 22 * * *",
      "enabled": true,
      "timeout": 120,
      "description": "生成每日协议执行统计"
    }
  ]
}
```

### 5.2 自动化检查脚本

**scripts/protocol-check.sh**:
```bash
#!/bin/bash
# 执行协议检查脚本

TASK_ID=$1
WORKSPACE="/root/.openclaw/workspace"
PROTOCOL_DIR="$WORKSPACE/memory/protocol"

mkdir -p "$PROTOCOL_DIR"

echo "=== 执行协议检查 ==="
echo "任务ID: $TASK_ID"
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查确认状态
if [ -f "$PROTOCOL_DIR/${TASK_ID}-confirmation.md" ]; then
    echo "✅ 任务已确认"
else
    echo "⚠️ 任务未确认，需要输出确认清单"
fi

# 检查进度汇报
REPORT_COUNT=$(ls -1 "$PROTOCOL_DIR/${TASK_ID}"-progress-*.md 2>/dev/null | wc -l)
echo "📊 进度汇报次数: $REPORT_COUNT"

# 检查是否有阻塞升级
if [ -f "$PROTOCOL_DIR/${TASK_ID}-escalation.md" ]; then
    echo "🚨 存在升级记录"
    cat "$PROTOCOL_DIR/${TASK_ID}-escalation.md" | head -5
else
    echo "✅ 无阻塞升级"
fi

echo "=== 检查完成 ==="
```

**scripts/task-chain-checker.sh**:
```bash
#!/bin/bash
# 任务链检查脚本 - 检查完成的任务并触发下一任务

WORKSPACE="/root/.openclaw/workspace"
PROTOCOL_DIR="$WORKSPACE/memory/protocol"

echo "=== 任务链检查 ==="
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 查找最近完成的但未触发下一任务的任务
RECENTLY_COMPLETED=$(find "$PROTOCOL_DIR" -name "*completion.md" -mmin -10 2>/dev/null)

if [ -z "$RECENTLY_COMPLETED" ]; then
    echo "📭 无新完成任务"
else
    for completion_file in $RECENTLY_COMPLETED; do
        task_id=$(basename "$completion_file" | sed 's/-completion.md//')
        chain_file="$PROTOCOL_DIR/${task_id}-chain-triggered"
        
        if [ ! -f "$chain_file" ]; then
            echo "🔄 任务 $task_id 刚完成，检查下一任务..."
            # 这里可以解析任务依赖关系，触发下一任务
            touch "$chain_file"
            echo "   已标记任务链触发"
        fi
    done
fi

echo "=== 检查完成 ==="
```

**scripts/daily-stats.sh**:
```bash
#!/bin/bash
# 每日协议统计脚本

WORKSPACE="/root/.openclaw/workspace"
PROTOCOL_DIR="$WORKSPACE/memory/protocol"
STATS_FILE="$PROTOCOL_DIR/stats-$(date +%Y%m%d).json"

echo "=== 生成每日协议统计 ==="

TODAY=$(date +%Y%m%d)
CONFIRMED=$(find "$PROTOCOL_DIR" -name "*-${TODAY}*-confirmation.md" 2>/dev/null | wc -l)
COMPLETED=$(find "$PROTOCOL_DIR" -name "*-${TODAY}*-completion.md" 2>/dev/null | wc -l)
ESCALATED=$(find "$PROTOCOL_DIR" -name "*-${TODAY}*-escalation.md" 2>/dev/null | wc -l)
PROGRESS_REPORTS=$(find "$PROTOCOL_DIR" -name "*-${TODAY}*-progress-*.md" 2>/dev/null | wc -l)

cat > "$STATS_FILE" << EOF
{
  "date": "$TODAY",
  "tasks_confirmed": $CONFIRMED,
  "tasks_completed": $COMPLETED,
  "tasks_escalated": $ESCALATED,
  "progress_reports": $PROGRESS_REPORTS,
  "protocol_adherence_rate": "$(echo "scale=2; $COMPLETED / $CONFIRMED * 100" | bc 2>/dev/null || echo "N/A")%"
}
EOF

echo "统计已保存到: $STATS_FILE"
cat "$STATS_FILE"
echo "=== 统计完成 ==="
```

### 5.3 异常处理

| 异常类型 | 检测方式 | 自动响应 | 人工介入 |
|----------|----------|----------|----------|
| 确认超时 | 创建后>30分钟未确认 | 提醒用户 | 等待确认 |
| 汇报缺失 | 执行>1小时无进度汇报 | 提醒汇报 | 自动生成 |
| 升级未响应 | 升级后>30分钟无处理 | 再次提醒 | 紧急通知 |
| 任务链断裂 | 下一任务启动失败 | 记录日志 | 手动处理 |

---

## 六、质量门控

### 6.1 5标准自检清单

- [x] **全局考虑**: 覆盖任务全生命周期
- [x] **系统考虑**: 确认→执行→汇报→衔接→升级闭环
- [x] **迭代机制**: 每周统计+PDCA优化
- [x] **Skill化**: 可触发、可执行、有产出
- [x] **流程自动化**: Cron监控+自动触发

### 6.2 执行验证

```bash
# 验证协议执行状态
ls -la memory/protocol/

# 查看今日统计
ls memory/protocol/stats-$(date +%Y%m%d).json 2>/dev/null && \
  cat memory/protocol/stats-$(date +%Y%m%d).json

# 检查Cron任务
./skills/execution-protocol/scripts/protocol-check.sh [task-id]
```

---

## 七、使用方式

### 7.1 在对话中使用

**任务开始时**:
```
【任务确认】
核心目标: [一句话描述]
冗余环节: [标记可砍掉的环节]
确认后我将开始执行。
```

**进度汇报时**:
```
【进度汇报】进度: 50%
已完成: [已完成内容]
进行中: [进行中内容]
阻塞/风险: [如有则列出]
```

**任务完成时**:
```
【任务完成】
交付物: [交付物位置/内容]
下一任务: [自动识别或询问]
```

### 7.2 协议检查命令

```bash
# 检查特定任务协议执行情况
./skills/execution-protocol/scripts/protocol-check.sh TASK-001

# 查看今日协议统计
./skills/execution-protocol/scripts/daily-stats.sh

# 手动触发任务链检查
./skills/execution-protocol/scripts/task-chain-checker.sh
```

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*

*覆盖规则: 1(安排确认/执行汇报/问题升级) | 2(先完成再完美) | 3(砍冗余) | 4(任务衔接)*
