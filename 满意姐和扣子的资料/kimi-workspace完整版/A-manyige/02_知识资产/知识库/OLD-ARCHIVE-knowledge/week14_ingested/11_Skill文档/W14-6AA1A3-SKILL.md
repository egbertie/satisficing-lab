---
# 知识元数据 (5标准化)
knowledge_id: W14-6AA1A3
title: Unified Expert Suite
category: 11_Skill文档
source: skills/.archive_unified-expert-suite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1307
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Unified Expert Suite

> **知识ID**: W14-6AA1A3  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_unified-expert-suite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: unified-expert-suite
description: Unified expert and knowledge worker suite. Replaces expert-council, expert-profile-manager, expert-digital-twin-trainer with single integrated interface. Use for: expert consultation, profile management, digital twin training, knowledge sharing.
triggers: ["expert", "consultant", "profile", "digital twin", "knowledge", "专家", "顾问"]
---

# Unified Expert Suite

**统一专家与知识工作者套件** - 整合理事会咨询、专家档案、数字孪生。

> 🎯 替代: expert-council + expert-profile-manager + expert-digital-twin-trainer

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **专家咨询** | 多专家会诊、意见综合、决策支持 |
| **档案管理** | 专家画像、能力评估、匹配推荐 |
| **数字孪生** | 知识训练、行为模拟、持续学习 |
| **知识共享** | 经验萃取、最佳实践、传承机制 |
| **专家网络** | 关系图谱、协作分析、影响力评估 |

---

## 快速开始

```bash
# 专家咨询
expert-suite consult --topic "战略规划" --experts "strategy,finance,market" --synthesis

# 档案管理
expert-suite profile create --name "张三" --expertise "AI,数据分析" --level senior

# 数字孪生训练
expert-suite twin train --expert-id expert-001 --data conversations.json

# 知识萃取
expert-suite extract --source case-studies --format playbook
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| expert-council | `expert-suite consult` |
| expert-profile-manager | `expert-suite profile` |
| expert-digital-twin-trainer | `expert-suite twin` |

---

**自建替代计数**: +3
