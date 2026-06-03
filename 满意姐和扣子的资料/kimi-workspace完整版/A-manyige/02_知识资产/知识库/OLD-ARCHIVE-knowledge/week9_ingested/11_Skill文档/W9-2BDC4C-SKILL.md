---
# 知识元数据 (5标准化)
knowledge_id: W9-2BDC4C
title: 闭环三原则标准Skill V1.0
category: 11_Skill文档
source: skills/.archive_closed-loop-principles/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 6098
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 闭环三原则标准Skill V1.0

> **知识ID**: W9-2BDC4C  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_closed-loop-principles/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 闭环三原则标准Skill V1.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V1.0 | 更新: 2026-03-20 | 核心: 发出→确认→落实→反馈

---

## 一、全局考虑（六层+三原则）

### 三原则 × 六层矩阵

| 原则 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|------|--------|--------|--------|--------|--------|--------|
| **发出必有确认** | 身份确认 | 任务确认 | 配置确认 | 外部确认 | 交付确认 | 归档确认 |
| **确认必有落实** | 能力落实 | 任务落实 | 系统落实 | 外部落实 | 交付落实 | 归档落实 |
| **落实必有反馈** | 状态反馈 | 进度反馈 | 状态反馈 | 结果反馈 | 质量反馈 | 完整反馈 |

---

## 二、系统考虑（发出→确认→落实→反馈闭环）

### 2.1 三原则详解

```
发出(信息/任务/要求) → 确认(收到/理解/接受) → 落实(执行/完成) → 反馈(结果/状态)
        ↑                                                                    │
        └──────────────────── 闭环完成 ←─────────────────────────────────────┘
```

#### 原则1: 发出必有确认

| 发出类型 | 确认方式 | 确认时限 | 未确认处理 |
|----------|----------|----------|------------|
| 任务分配 | 明确接受 | 1小时内 | 二次提醒 |
| 信息同步 | 已读确认 | 2小时内 | 升级通知 |
| 会议要求 | 出席确认 | 24小时前 | 单独沟通 |
| 变更通知 | 理解确认 | 立即 | 电话确认 |

#### 原则2: 确认必有落实

| 确认类型 | 落实标准 | 落实时限 | 监督方式 |
|----------|----------|----------|----------|
| 任务接受 | 开始执行 | 立即 | 状态跟踪 |
| 信息理解 | 正确执行 | 依任务 | 结果验证 |
| 承诺出席 | 准时到场 | 会议时 | 签到确认 |
| 变更接受 | 按新方案 | 立即 | 检查执行 |

#### 原则3: 落实必有反馈

| 落实类型 | 反馈内容 | 反馈时限 | 反馈方式 |
|----------|----------|----------|----------|
| 任务完成 | 结果+产出 | 完成时 | 状态更新 |
| 信息处理 | 处理结果 | 处理后 | 简要回复 |
| 会议参与 | 会议纪要 | 24小时内 | 文档共享 |
| 变更执行 | 执行结果 | 完成后 | 状态报告 |

---

## 三、迭代机制（每次交互检查）

### 3.1 闭环状态追踪

```yaml
closed_loop_tracking:
  message_id: "msg_001"
  content: "请完成XX任务"
  sent_at: "2026-03-20T09:00:00Z"
  
  confirmation:
    status: "confirmed"
    confirmed_at: "2026-03-20T09:15:00Z"
    confirmed_by: "receiver"
    
  implementation:
    status: "in_progress"
    started_at: "2026-03-20T09:20:00Z"
    
  feedback:
    status: "pending"
    expected_by: "2026-03-20T18:00:00Z"
```

### 3.2 闭环质量评估

| 评估维度 | 指标 | 目标值 | 评估频率 |
|----------|------|--------|----------|
| 确认率 | 确认数/发出数 | ≥95% | 每日 |
| 落实率 | 落实数/确认数 | ≥90% | 每日 |
| 反馈率 | 反馈数/落实数 | ≥95% | 每日 |
| 闭环时长 | 发出到反馈平均时间 | ≤24h | 每周 |

---

## 四、Skill化（可执行）

### 4.1 触发条件

**自动触发**:
- 信息发出后1小时未收到确认
- 确认后2小时未开始落实
- 任务完成后未提供反馈
- 每日定时扫描所有待闭环事项

**手动触发**:
- 用户指令: "检查闭环状态"
- 用户指令: "强制闭环检查"

### 4.2 闭环检查代码

```python
def closed_loop_principles_enforcer(message):
    """
    闭环三原则强制执行
    """
    # 原则1: 发出必有确认
    if not has_confirmation(message):
        send_confirmation_request(message)
        return "等待确认"
    
    # 原则2: 确认必有落实
    if not is_being_implemented(message):
        send_implementation_reminder(message)
        return "提醒落实"
    
    # 原则3: 落实必有反馈
    if is_completed(message) and not has_feedback(message):
        send_feedback_request(message)
        return "等待反馈"
    
    return "闭环完成"

def check_all_pending_loops():
    """检查所有待闭环"""
    pending = get_pending_confirmations()
    pending.extend(get_pending_implementations())
    pending.extend(get_pending_feedbacks())
    
    for item in pending:
        if is_overdue(item):
            escalate(item)
        else:
            send_reminder(item)
    
    return pending

def generate_loop_report():
    """生成闭环执行报告"""
    stats = {
        "total_sent": count_sent_messages(),
        "confirmed": count_confirmed(),
        "implemented": count_implemented(),
        "feedback_received": count_feedback(),
        "confirmation_rate": calculate_confirmation_rate(),
        "implementation_rate": calculate_implementation_rate(),
        "feedback_rate": calculate_feedback_rate()
    }
    return stats
```

### 4.3 标准响应模板

**确认请求**:
```
📋 **请确认收到**

内容: [消息内容]
发送时间: [时间]

请在1小时内回复"确认收到"，超时将升级提醒。
```

**落实提醒**:
```
⏰ **请开始落实**

您已确认: [任务内容]
确认时间: [时间]

请立即开始执行，并在完成后提供反馈。
```

**反馈请求**:
```
🔄 **请提供反馈**

任务: [任务内容]
已完成，请提供执行结果反馈。

反馈格式:
- 执行结果: [成功/部分成功/失败]
- 关键产出: [描述]
- 遇到问题: [如有]
```

---

## 五、流程自动化

### 5.1 定时检查

```json
{
  "jobs": [
    {
      "name": "closed-loop-check",
      "schedule": "0 * * * *",
      "enabled": true,
      "description": "每小时检查待闭环事项"
    },
    {
      "name": "closed-loop-daily-report",
      "schedule": "0 9 * * *",
      "enabled": true,
      "description": "每日生成闭环执行报告"
    }
  ]
}
```

### 5.2 自动化脚本

```bash
#!/bin/bash
# scripts/closed-loop-check.sh

echo "=== 闭环三原则检查 ==="
echo "检查时间: $(date)"
echo ""

# 检查待确认事项
echo "1. 待确认事项..."
python3 -c "from closed_loop_enforcer import check_pending_confirmations; check_pending_confirmations()"

# 检查待落实事项
echo "2. 待落实事项..."
python3 -c "from closed_loop_enforcer import check_pending_implementations; check_pending_implementations()"

# 检查待反馈事项
echo "3. 待反馈事项..."
python3 -c "from closed_loop_enforcer import check_pending_feedbacks; check_pending_feedbacks()"

# 处理逾期事项
echo "4. 处理逾期事项..."
python3 -c "from closed_loop_enforcer import escalate_overdue_items; escalate_overdue_items()"

echo ""
echo "=== 检查完成 ==="
```

```bash
#!/bin/bash
# scripts/closed-loop-daily-report.sh

echo "=== 闭环三原则日报 ==="
echo "报告日期: $(date +%Y-%m-%d)"
echo ""

# 生成统计报告
python3 << 'EOF'
from closed_loop_enforcer import generate_loop_report
report = generate_loop_report()

print("## 闭环执行统计")
print(f"- 总发出: {report['total_sent']}")
print(f"- 已确认: {report['confirmed']} ({report['confirmation_rate']:.1f}%)")
print(f"- 已落实: {report['implemented']} ({report['implementation_rate']:.1f}%)")
print(f"- 已反馈: {report['feedback_received']} ({report['feedback_rate']:.1f}%)")

# 质量评估
if report['confirmation_rate'] >= 0.95 and report['implementation_rate'] >= 0.90 and report['feedback_rate'] >= 0.95:
    print("\n✅ **闭环质量: 优秀**")
elif report['confirmation_rate'] >= 0.85 and report['implementation_rate'] >= 0.80 and report['feedback_rate'] >= 0.85:
    print("\n⚠️ **闭环质量: 良好，有提升空间**")
else:
    print("\n🔴 **闭环质量: 需改进**")
EOF

echo ""
echo "=== 报告结束 ==="
```

---

## 六、质量门控

- [x] **全局**: 三原则×六层全覆盖
- [x] **系统**: 发出→确认→落实→反馈闭环
- [x] **迭代**: 每次交互检查+定时扫描
- [x] **Skill化**: 自动追踪+提醒+升级
- [x] **自动化**: 定时检查+自动提醒

---

## 七、使用方式

### 7.1 人工检查

```bash
# 检查当前闭环状态
./scripts/closed-loop-check.sh

# 查看日报
./scripts/closed-loop-daily-report.sh

# 查看待闭环清单
cat logs/pending-closures.log
```

### 7.2 集成到工作流

所有发出的消息自动经过闭环追踪，系统会自动检查确认、落实、反馈状态。

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*
