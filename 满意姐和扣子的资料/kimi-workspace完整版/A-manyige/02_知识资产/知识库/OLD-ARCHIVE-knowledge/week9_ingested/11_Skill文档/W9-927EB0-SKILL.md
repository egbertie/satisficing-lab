---
# 知识元数据 (5标准化)
knowledge_id: W9-927EB0
title: SKILL
category: 11_Skill文档
source: skills/.archive_customer-journey-mapper/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1934
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W9-927EB0  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_customer-journey-mapper/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: customer-journey-mapper
version: 1.0.0
description: |
  客户旅程映射器 - 分析客户当前状态并推荐下一步触点：
  1. 全局考虑：覆盖认知→考虑→决策→使用→忠诚全流程
  2. 系统考虑：客户输入→状态分析→旅程定位→推荐生成闭环
  3. 迭代机制：根据转化数据优化推荐策略
  4. Skill化：标准接口，可嵌入CRM系统
  5. 流程自动化：自动分析并推荐下一步行动
author: Satisficing Institute
tags:
  - customer-journey
  - mapping
  - recommendation
  - crm
requires:
  - model: "kimi-coding/k2p5"
---

# 客户旅程映射器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 旅程阶段

| 阶段 | 客户心理 | 推荐触点 |
|------|----------|----------|
| **认知** | 有问题但不知道解决方案 | 内容营销、社交分享 |
| **考虑** | 了解方案但比较中 | 免费工具、案例研究 |
| **决策** | 准备购买 | 咨询、演示、试用 |
| **使用** | 使用产品/服务 | 培训、支持、社区 |
| **忠诚** | 满意并推荐 | 推荐计划、增值服务 |

### 1.2 分析维度

| 维度 | 说明 |
|------|------|
| 当前阶段 | 客户处于旅程哪个阶段 |
| 痛点 | 当前主要痛点 |
| 需求 | 当前主要需求 |
| 推荐触点 | 下一步最佳触点 |
| 转化目标 | 本次互动目标 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 映射流程

```
客户信息 → 状态分析 → 旅程定位 → 痛点识别 → 推荐触点 → 行动清单
```

---

## 标准3: 迭代机制（Iterative）

根据转化率数据优化推荐策略。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
customer-journey-mapper/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── analyze_customer.py     # 客户分析
│   ├── map_journey.py          # 旅程映射
│   └── recommend_touchpoint.py # 触点推荐
└── rules/
    └── journey_stages.yaml
```

### 4.2 调用接口

```python
from customer_journey_mapper import JourneyMapper

mapper = JourneyMapper()

# 分析客户旅程
result = mapper.map(
    customer_id="C001",
    stage="awareness",
    pain_point="找合伙人困难"
)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 分析客户旅程
openclaw skill run customer-journey-mapper map \
  --customer-id C001 \
  --stage awareness \
  --pain "找合伙人困难"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 5阶段旅程覆盖 | ✅ |
| **2. 系统** | 分析→映射→推荐闭环 | ✅ |
| **3. 迭代** | 策略优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动分析+推荐 | ✅ |

---

*版本: v1.0.0*  
*来源: client-value-system散落机制提取*  
*创建: 2026-03-20*
