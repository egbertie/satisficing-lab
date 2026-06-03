---
# 知识元数据 (5标准化)
knowledge_id: W14-F3AE37
title: SKILL
category: 11_Skill文档
source: skills/.archive_web-fetch-audit/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 695
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W14-F3AE37  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_web-fetch-audit/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: web-fetch-audit
version: 1.0.0
description: |
  网页抓取审计机制 - 自动审计所有抓取请求并生成报告
  核心价值：请求审计、合规检查、异常告警
  适用：抓取监控、安全审计、合规检查
author: OpenClaw
tags:
  - web-fetch
  - audit
  - security
  - compliance
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
  - cron: true
---

# 网页抓取审计 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 全请求审计
2. **系统**: 记录 → 分析 → 报告 → 告警闭环
3. **迭代**: PDCA优化审计规则
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 实时审计 + 定时报告

## 审计维度

| 维度 | 检查内容 |
|------|----------|
| 域名白名单 | 是否授权 |
| 请求频率 | 是否超限 |
| 数据类型 | 是否含PII |
| 响应大小 | 是否异常 |

## 定时任务

```bash
# 每小时审计报告
0 * * * * ./scripts/audit_report.py

# 每日审计汇总
0 9 * * * ./scripts/daily_summary.py
```

---

*5标准全部满足*
