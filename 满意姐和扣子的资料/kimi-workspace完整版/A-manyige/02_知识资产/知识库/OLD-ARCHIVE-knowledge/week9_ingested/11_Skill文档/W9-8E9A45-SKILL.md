---
# 知识元数据 (5标准化)
knowledge_id: W9-8E9A45
title: 闭环率追踪器标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_closure-rate-tracker/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1276
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 闭环率追踪器标准Skill V2.0

> **知识ID**: W9-8E9A45  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_closure-rate-tracker/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 闭环率追踪器标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: 信息闭环率统计

---

## 一、全局考虑（六层+闭环维度）

| 闭环维度 | 目标 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|----------|------|--------|--------|--------|--------|--------|--------|
| **闭环率** | ≥95% | 承诺闭环 | 任务闭环 | 系统闭环 | 外部闭环 | 交付闭环 | 归档闭环 |
| **闭环时间** | ≤24h | 即时响应 | 按时完成 | 自动处理 | 及时反馈 | 准时交付 | 及时归档 |

---

## 二、系统考虑（采集→统计→分析→改进闭环）

### 2.1 统计指标

```yaml
closure_metrics:
  closure_rate:
    target: "≥95%"
    current: "待计算"
    
  avg_closure_time:
    target: "≤24h"
    current: "待计算"
    
  overdue_items:
    threshold: "<5%"
    current: "待统计"
```

---

## 三、迭代机制（每日统计+每周分析）

---

## 四、Skill化（自动统计）

```python
def track_closure_rate():
    """闭环率追踪"""
    items = collect_all_items()
    
    total = len(items)
    closed = len([i for i in items if i.status == "closed"])
    avg_time = calculate_avg_closure_time(items)
    
    return {
        "closure_rate": closed / total * 100,
        "avg_time": avg_time,
        "overdue_count": len([i for i in items if i.is_overdue])
    }
```

---

## 五、流程自动化（每日23:00统计）

```json
{
  "job": {
    "name": "closure-rate-tracker",
    "schedule": "0 23 * * *"
  }
}
```

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*