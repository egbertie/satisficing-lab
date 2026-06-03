---
# 知识元数据 (5标准化)
knowledge_id: W14-6FF7E1
title: Unified Workflow Suite
category: 11_Skill文档
source: skills/.archive_unified-workflow-suite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1236
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Unified Workflow Suite

> **知识ID**: W14-6FF7E1  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_unified-workflow-suite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: unified-workflow-suite
description: Unified workflow and process management suite. Replaces workflow-engine, rule-execution-engine, sop-standard-operations with single integrated interface. Use for: workflow design, rule engine, SOP management, process automation.
triggers: ["workflow", "process", "rule", "sop", "engine", "工作流", "流程"]
---

# Unified Workflow Suite

**统一工作流与流程管理套件** - 整合工作流引擎、规则执行、SOP管理。

> 🎯 替代: workflow-engine + rule-execution-engine + sop-standard-operations

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **工作流设计** | 可视化设计、节点配置、流转规则 |
| **规则引擎** | 条件判断、规则集管理、动态更新 |
| **SOP管理** | 标准流程、检查清单、版本控制 |
| **流程自动化** | 触发器、自动执行、异常处理 |
| **流程分析** | 瓶颈识别、效率优化、合规检查 |

---

## 快速开始

```bash
# 创建工作流
workflow-suite create --name "审批流程" --steps "提交,审核,批准,执行"

# 规则执行
workflow-suite rule execute --ruleset approval --data request.json

# SOP管理
workflow-suite sop create --name "上线流程" --template release --checklist 10

# 流程监控
workflow-suite monitor --workflow approval --alert delay
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| workflow-engine | `workflow-suite create` |
| rule-execution-engine | `workflow-suite rule` |
| sop-standard-operations | `workflow-suite sop` |

---

**自建替代计数**: +3
