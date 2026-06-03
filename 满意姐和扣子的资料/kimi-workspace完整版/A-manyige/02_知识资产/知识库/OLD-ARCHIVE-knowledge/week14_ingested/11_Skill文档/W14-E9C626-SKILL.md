---
# 知识元数据 (5标准化)
knowledge_id: W14-E9C626
title: Unified Scheduler Suite
category: 11_Skill文档
source: skills/.archive_unified-scheduler-suite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1294
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Unified Scheduler Suite

> **知识ID**: W14-E9C626  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_unified-scheduler-suite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: unified-scheduler-suite
description: Unified scheduling and planning suite. Replaces first-principle-scheduler, cron-scheduling, daily-reminder-auditor with single integrated interface. Use for: task scheduling, reminder management, calendar optimization, priority planning.
triggers: ["schedule", "plan", "reminder", "calendar", "cron", "调度", "提醒"]
---

# Unified Scheduler Suite

**统一调度与规划套件** - 整合任务调度、提醒管理、日历优化。

> 🎯 替代: first-principle-scheduler + cron-scheduling + daily-reminder-auditor

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **智能调度** | 优先级排序、时间分配、冲突检测 |
| **提醒管理** | 多级提醒、智能时机、免打扰 |
| **日历优化** | 会议压缩、专注时间、能量管理 |
| **定时任务** | Cron表达式、任务链、失败重试 |
| **规划建议** | 工作量评估、截止日期优化 |

---

## 快速开始

```bash
# 任务调度
scheduler-suite schedule --tasks tasks.json --optimize energy

# 设置提醒
scheduler-suite reminder add --what "会议" --when "2024-04-01 14:00" --advance 15min

# 日历优化
scheduler-suite calendar optimize --focus-blocks 2h --meeting-limit 4

# 定时任务
scheduler-suite cron add --name "备份" --schedule "0 2 * * *" --command backup.sh
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| first-principle-scheduler | `scheduler-suite schedule` |
| cron-scheduling | `scheduler-suite cron` |
| daily-reminder-auditor | `scheduler-suite reminder` |

---

**自建替代计数**: +3
