---
# 知识元数据 (5标准化)
knowledge_id: W12-C49B33
title: Promise & System Guardian Skill
category: 11_Skill文档
source: skills/.archive_promise-system-guardian/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1914
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Promise & System Guardian Skill

> **知识ID**: W12-C49B33  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_promise-system-guardian/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Promise & System Guardian Skill
> **承诺与制度执行保障系统** - 确保所有承诺和制度有约束机制

## 核心功能

### 1. 承诺全生命周期管理
```
记录 → 监控 → 预警 → 补救 → 报告
```

### 2. 关键保障机制

| 机制 | 说明 | 触发条件 |
|------|------|----------|
| **自动记录** | 所有承诺写入数据库 | 承诺创建时自动 |
| **到期预警** | 24h/4h/1h前提醒 | 时间到达自动触发 |
| **超期补救** | 自动分析原因+调整+生成方案 | 超期自动触发 |
| **如实报告** | 未完成必须说明原因和调整 | 超期或主动报告 |
| **制度同步** | 规则更新自动同步到Skill | 规则变更时 |

## 使用方式

### 记录承诺
```python
from promise_guardian import PromiseAndSystemGuardian

guardian = PromiseAndSystemGuardian()

guardian.record_promise(
    promise_id="PROMISE-001",
    content="完成五路图腾信息图",
    deadline="2026-03-11 10:00",
    owner="DESIGN",
    priority="P0",
    consequences_if_fail="影响官宣进度"
)
```

### 报告完成
```python
guardian.report_completion(
    promise_id="PROMISE-001",
    completion_time="2026-03-11 09:30",
    result_summary="三风格全部完成",
    deliverables=["水墨风.png", "极简风.png", "国潮风.png"]
)
```

### 报告未完成
```python
guardian.report_failure(
    promise_id="PROMISE-001",
    reason="AI生成API限流，需要更多时间",
    adjusted_deadline="2026-03-11 14:00",
    mitigation_plan="1.启动备用API\n2.并行生成\n3.每2小时汇报"
)
```

### 更新制度规则
```python
guardian.update_system_rule(
    rule_id="RULE-001",
    rule_name="承诺记录规范",
    rule_content="所有承诺必须包含截止时间、负责人、后果说明",
    effective_date="2026-03-11"
)
```

## 数据结构

### 承诺数据库
- 位置: `memory/promise_database.json`
- 包含: 承诺ID、内容、截止、负责人、状态、报告等

### 制度规则数据库
- 位置: `memory/system_rule_database.json`
- 包含: 规则ID、名称、内容、版本、生效日期等

### 执行日志
- 位置: `memory/execution_log.json`
- 包含: 所有操作记录、变更历史

## 定时任务

**每日08:00自动生成报告**
- 检查所有承诺状态
- 发送预警提醒
- 触发超期补救
- 生成日报

## 文件清单

```
skills/promise-system-guardian/
├── SKILL.md                    # 本文件
├── promise_guardian.py         # 核心引擎
└── examples/                   # 使用示例
    └── demo.py
```

## 关键特性

1. **不掉链子保障**: 承诺必须兑现，否则自动补救
2. **制度约束**: 所有操作符合制度要求
3. **自动迭代**: 定时检查，自动优化
4. **透明报告**: 成功失败都如实记录
5. **版本管理**: 制度规则版本化，可追溯

---

**这是约束机制，不是口头承诺！**
