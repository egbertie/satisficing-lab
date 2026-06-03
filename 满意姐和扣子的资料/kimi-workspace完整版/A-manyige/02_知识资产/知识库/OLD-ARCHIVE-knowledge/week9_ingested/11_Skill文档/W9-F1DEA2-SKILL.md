---
# 知识元数据 (5标准化)
knowledge_id: W9-F1DEA2
title: 信息闭环三原则标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_closed-loop-enforcer/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2999
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 信息闭环三原则标准Skill V2.0

> **知识ID**: W9-F1DEA2  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_closed-loop-enforcer/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 信息闭环三原则标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: 发出→确认→落实

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

---

## 四、Skill化（可执行）

### 4.1 闭环检查代码

```python
def information_closed_loop_enforcer(message):
    """
    信息闭环强制执行
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
```

---

## 五、流程自动化

### 5.1 定时检查

```json
{
  "job": {
    "name": "closed-loop-check",
    "schedule": "0 * * * *",
    "enabled": true
  }
}
```

---

## 六、质量门控

- [x] **全局**: 三原则×六层全覆盖
- [x] **系统**: 发出→确认→落实→反馈闭环
- [x] **迭代**: 每次交互检查+定时扫描
- [x] **Skill化**: 自动追踪+提醒+升级
- [x] **自动化**: 定时检查+自动提醒

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*