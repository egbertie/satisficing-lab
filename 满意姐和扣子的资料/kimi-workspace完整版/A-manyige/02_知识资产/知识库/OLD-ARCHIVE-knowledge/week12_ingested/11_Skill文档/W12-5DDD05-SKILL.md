---
# 知识元数据 (5标准化)
knowledge_id: W12-5DDD05
title: SKILL
category: 11_Skill文档
source: skills/.archive_reversibility-checker/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1995
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

> **知识ID**: W12-5DDD05  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_reversibility-checker/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: reversibility-checker
version: 1.0.0
description: |
  可逆性检查器 - 决策分类与风险评估工具：
  1. 全局考虑：覆盖单向门/双向门分类、评估标准、风险缓解
  2. 系统考虑：决策输入→分类→评估→建议→缓解措施闭环
  3. 迭代机制：根据决策结果优化分类准确度
  4. Skill化：标准接口，可嵌入任何决策流程
  5. 流程自动化：自动分类并提供处理建议
author: Satisficing Institute
tags:
  - decision
  - reversibility
  - risk-assessment
  - framework
requires:
  - model: "kimi-coding/k2p5"
---

# 可逆性检查器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 决策类型

| 类型 | 定义 | 示例 |
|------|------|------|
| **单向门(Type 1)** | 不可逆或撤销成本极高 | 数据库迁移、公共API |
| **双向门(Type 2)** | 可轻松撤销 | UI框架、功能开关实验 |

### 1.2 评估标准

| 标准 | 单向门 | 双向门 |
|------|--------|--------|
| 撤销成本 | >1个sprint | 配置变更即可 |
| 数据迁移 | 需要 | 不需要 |
| 用户通知 | 需要 | 不需要 |
| 决策时间 | 天-周 | 小时 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 检查流程

```
决策描述 → 可逆性评估 → 类型分类 → 生成建议 → 缓解措施
```

### 2.2 缓解策略

| 策略 | 说明 |
|------|------|
| 接口抽象 | 将风险隐藏在接口后 |
| 功能开关 | 可随时关闭 |
| 渐进发布 | 灰度验证 |
| 回滚计划 | 预定义回滚步骤 |

---

## 标准3: 迭代机制（Iterative）

根据实际决策结果调整分类规则。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
reversibility-checker/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── check_reversibility.py  # 可逆性检查
│   ├── classify_decision.py    # 决策分类
│   └── suggest_mitigation.py   # 缓解建议
└── rules/
    └── reversibility_criteria.yaml
```

### 4.2 调用接口

```python
from reversibility_checker import ReversibilityChecker

checker = ReversibilityChecker()

# 检查决策可逆性
result = checker.check(
    decision="从MySQL迁移到PostgreSQL",
    rollback_cost="2周",
    data_migration=True
)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 检查决策可逆性
openclaw skill run reversibility-checker check \
  --decision "数据库迁移" \
  --rollback-cost "2周"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 决策类型全覆盖 | ✅ |
| **2. 系统** | 检查→分类→建议闭环 | ✅ |
| **3. 迭代** | 规则优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动分类+建议 | ✅ |

---

*版本: v1.0.0*  
*来源: decision-frameworks散落机制提取*  
*创建: 2026-03-20*
