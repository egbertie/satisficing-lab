---
# 知识元数据 (5标准化)
knowledge_id: W7-11CB98
title: SKILL
category: 11_Skill文档
source: skills/.archive_ab-test-generator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1895
week: 7
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W7-11CB98  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_ab-test-generator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: ab-test-generator
version: 1.0.0
description: |
  A/B测试生成器 - 生成可测试的文案/设计变体：
  1. 全局考虑：覆盖标题、CTA、说服角度等测试维度
  2. 系统考虑：元素选择→变体生成→测试设计→结果分析闭环
  3. 迭代机制：根据测试结果优化变体生成策略
  4. Skill化：标准接口，可按维度独立生成
  5. 流程自动化：自动生成测试方案和变体
author: Satisficing Institute
tags:
  - ab-test
  - variant
  - optimization
  - marketing
requires:
  - model: "kimi-coding/k2p5"
---

# A/B测试生成器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 测试维度

| 维度 | 说明 | 示例变体 |
|------|------|----------|
| **标题角度** | 收益/痛点/好奇/权威 | 如何.../还在为...头疼？/揭秘... |
| **情感触发** | 恐惧/希望/社会认同/紧迫感 | 避免损失/实现目标/10万人选择/限时 |
| **CTA文案** | 动作+价值+紧迫感 | 立即领取/免费试用/本周优惠 |
| **证明位置** | 证明前置/后置 | 开头展示数据/结尾展示案例 |

### 1.2 测试原则

| 原则 | 说明 |
|------|------|
| 单一变量 | 每次只变一个维度 |
| 足够样本 | 统计显著性 |
| 明确指标 | 点击率/转化率/完成率 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 生成流程

```
原始文案 → 选择测试维度 → 生成变体 → 设计测试方案 → 输出测试计划
```

---

## 标准3: 迭代机制（Iterative）

根据测试结果优化变体生成策略。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
ab-test-generator/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── generate_variants.py    # 变体生成
│   ├── design_test.py          # 测试设计
│   └── analyze_results.py      # 结果分析
└── rules/
    └── test_principles.yaml
```

### 4.2 调用接口

```python
from ab_test_generator import ABTestGenerator

generator = ABTestGenerator()

# 生成测试变体
variants = generator.generate(
    original="立即领取你的方案",
    dimension="cta",
    count=3
)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 生成CTA变体
openclaw skill run ab-test-generator generate \
  --original "立即领取你的方案" \
  --dimension cta \
  --count 3
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 多测试维度覆盖 | ✅ |
| **2. 系统** | 生成→设计→分析闭环 | ✅ |
| **3. 迭代** | 策略优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动生成测试方案 | ✅ |

---

*版本: v1.0.0*  
*来源: copywriting-zh-pro散落机制提取*  
*创建: 2026-03-20*
