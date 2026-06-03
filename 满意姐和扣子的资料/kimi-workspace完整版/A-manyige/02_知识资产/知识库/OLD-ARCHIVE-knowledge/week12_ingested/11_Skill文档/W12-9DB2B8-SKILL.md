---
# 知识元数据 (5标准化)
knowledge_id: W12-9DB2B8
title: SKILL
category: 11_Skill文档
source: skills/.archive_partner-assessment/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 708
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

> **知识ID**: W12-9DB2B8  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_partner-assessment/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: partner-assessment
version: 1.0.0
description: |
  合伙人匹配评估机制 - 7维度标准化评估体系
  核心价值：标准化评估、风险预警、决策支持
  适用：合伙人选择、团队组建、尽职调查
author: OpenClaw
tags:
  - partner
  - assessment
  - decision
  - evaluation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "duckdb"]
  - cron: false
---

# 合伙人匹配评估 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 7维度全覆盖
2. **系统**: 评估 → 分析 → 建议闭环
3. **迭代**: PDCA持续优化评估模型
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 评估结果自动计算与归档

## 7维度评估体系

| 维度 | 权重 | 关键阈值 |
|------|------|----------|
| 价值观契合度 | 25% | <5 致命 |
| 能力互补性 | 20% | <7 需补强 |
| 沟通效率 | 15% | <5 中风险 |
| 承诺可信度 | 15% | <6 高风险 |
| 利益一致性 | 10% | 需机制 |
| 退出可接受性 | 10% | 需预设 |
| 成长匹配度 | 5% | 长期观察 |

---

*5标准全部满足*
