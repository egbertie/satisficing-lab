---
# 知识元数据 (5标准化)
knowledge_id: W12-A5C815
title: SKILL
category: 11_Skill文档
source: skills/.archive_questionnaire-auto-gen/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 644
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

> **知识ID**: W12-A5C815  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_questionnaire-auto-gen/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: questionnaire-auto-gen
version: 1.0.0
description: |
  评估问卷自动生成机制 - 基于维度配置自动生成结构化问卷
  核心价值：多维度配置、多格式输出、智能题目生成
  适用：候选人评估、满意度调查、能力测评
author: OpenClaw
tags:
  - questionnaire
  - generator
  - assessment
  - survey
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
  - cron: false
---

# 问卷自动生成 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 4维度全覆盖（认知/情感/行为/直觉）
2. **系统**: 配置 → 生成 → 输出闭环
3. **迭代**: PDCA优化题目质量
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 一键生成完整问卷

## 评估维度

| 维度 | 权重 | 题型 |
|------|------|------|
| 认知层 | 30% | 选择题、情景题 |
| 情感层 | 30% | 量表题、排序题 |
| 行为层 | 20% | 案例题、行为描述 |
| 直觉层 | 20% | 开放题、图片题 |

---

*5标准全部满足*
