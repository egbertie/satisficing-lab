---
# 知识元数据 (5标准化)
knowledge_id: W12-375D0A
title: SKILL
category: 11_Skill文档
source: skills/.archive_n8n-idempotency-checker/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 698
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W12-375D0A  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_n8n-idempotency-checker/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: n8n-idempotency-checker
version: 1.0.0
description: |
  n8n工作流幂等性检查机制 - 确保工作流重复执行不会重复数据
  核心价值：自动检查幂等性、生成修复建议、监控重复执行
  适用：n8n工作流审计、数据一致性保障
author: OpenClaw
tags:
  - n8n
  - idempotency
  - workflow
  - audit
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "curl"]
  - cron: true
---

# n8n幂等性检查 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 全工作流节点检查
2. **系统**: 检查 → 报告 → 修复闭环
3. **迭代**: PDCA持续优化检查规则
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 定时检查 + 告警

## 检查维度

| 检查项 | 说明 | 风险等级 |
|--------|------|----------|
| 去重键 | 是否有唯一标识 | 高 |
| 状态存储 | 是否存储执行状态 | 高 |
| 重复检测 | 是否检测重复数据 | 中 |

## 定时任务

```bash
# 每日检查所有工作流
0 9 * * * ./scripts/check_idempotency.py
```

---

*5标准全部满足*
