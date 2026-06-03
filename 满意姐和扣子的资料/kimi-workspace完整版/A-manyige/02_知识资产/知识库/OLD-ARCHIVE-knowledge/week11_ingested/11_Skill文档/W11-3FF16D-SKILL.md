---
# 知识元数据 (5标准化)
knowledge_id: W11-3FF16D
title: SKILL
category: 11_Skill文档
source: skills/.archive_growth-path-monitor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 774
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W11-3FF16D  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_growth-path-monitor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: growth-path-monitor
version: 1.0.0
description: |
  组织成长路径监控机制 - 追踪团队成员成长进度
  核心价值：自动进度追踪、升级提醒、能力评估
  适用：人才培养、晋升管理、团队建设
author: OpenClaw
tags:
  - growth
  - path
  - monitor
  - team
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "duckdb"]
  - cron: true
---

# 成长路径监控 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 5级成长路径全覆盖
2. **系统**: 追踪 → 评估 → 提醒闭环
3. **迭代**: PDCA优化成长模型
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 定时追踪 + 升级提醒

## 5级成长体系

| 级别 | 称号 | 时长 | 特权 |
|------|------|------|------|
| L1 | 初学者 | 1月 | 基础资源 |
| L2 | 进阶者 | 2月 | 导师指导 |
| L3 | 熟练者 | 3月 | 高级资源 |
| L4 | 大师 | 3月 | 研究方向 |
| L5 | 顶尖 | 3月 | 战略决策 |

## 定时任务

```bash
# 每日进度检查
0 9 * * * ./scripts/check_progress.py

# 每周成长报告
0 10 * * 1 ./scripts/weekly_report.py
```

---

*5标准全部满足*
