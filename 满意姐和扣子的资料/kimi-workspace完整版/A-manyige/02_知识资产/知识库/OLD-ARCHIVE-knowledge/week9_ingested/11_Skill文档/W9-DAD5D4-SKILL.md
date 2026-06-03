---
# 知识元数据 (5标准化)
knowledge_id: W9-DAD5D4
title: SKILL
category: 11_Skill文档
source: skills/.archive_decision-matrix-calculator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2498
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

> **知识ID**: W9-DAD5D4  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_decision-matrix-calculator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: decision-matrix-calculator
version: 1.0.0
description: |
  决策矩阵计算器 - 结构化决策的加权评分工具：
  1. 全局考虑：支持多选项、多标准、权重自定义
  2. 系统考虑：输入→权重→评分→计算→决策建议闭环
  3. 迭代机制：根据决策结果反馈优化权重
  4. Skill化：标准接口，可复用决策模板
  5. 流程自动化：自动计算总分并排序推荐
author: Satisficing Institute
tags:
  - decision
  - matrix
  - weighted-scoring
  - framework
requires:
  - model: "kimi-coding/k2p5"
---

# 决策矩阵计算器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 决策要素

| 要素 | 说明 | 必含 |
|------|------|------|
| **选项** | 待比较的备选方案 | ✅ |
| **标准** | 评估维度 | ✅ |
| **权重** | 各标准重要性(1-5) | ✅ |
| **评分** | 各选项在各标准上的得分(1-5) | ✅ |
| **计算** | 加权总分 | ✅ |

### 1.2 输出内容

| 输出 | 说明 |
|------|------|
| 评分矩阵 | 选项×标准的完整矩阵 |
| 加权得分 | 各选项总分 |
| 排名 | 按总分排序 |
| 建议 | 最优选项+理由 |
| 敏感性分析 | 权重变化对结果的影响 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 决策流程

```
定义选项 → 定义标准 → 分配权重 → 逐项评分 → 计算总分 → 生成建议
```

### 2.2 矩阵模板

```
| 标准 | 权重 | 选项A | 选项B | 选项C |
|------|------|-------|-------|-------|
| 性能 | 5 | 4(20) | 3(15) | 5(25) |
| 成本 | 3 | 5(15) | 4(12) | 2(6)  |
| 总分 |      | 35    | 27    | 31    |
```

---

## 标准3: 迭代机制（Iterative）

### 3.1 权重优化

| 反馈 | 优化 |
|------|------|
| 决策结果不满意 | 调整权重 |
| 某标准区分度低 | 降低权重或细化 |
| 新因素出现 | 添加标准 |

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
decision-matrix-calculator/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── calculate_matrix.py     # 矩阵计算
│   ├── sensitivity_analysis.py # 敏感性分析
│   └── generate_report.py      # 报告生成
└── templates/
    └── decision_templates.yaml
```

### 4.2 调用接口

```python
from decision_matrix_calculator import DecisionMatrix

matrix = DecisionMatrix()

# 定义决策
result = matrix.calculate(
    options=["选项A", "选项B", "选项C"],
    criteria=["性能", "成本", "易用性"],
    weights=[5, 3, 4],
    scores={
        "选项A": [4, 5, 3],
        "选项B": [3, 4, 4],
        "选项C": [5, 2, 5]
    }
)

# 生成报告
matrix.generate_report(result)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 计算决策矩阵
openclaw skill run decision-matrix-calculator calculate \
  --options "选项A,选项B,选项C" \
  --criteria "性能,成本,易用性" \
  --weights "5,3,4"

# 使用模板
openclaw skill run decision-matrix-calculator use-template \
  --template tech-stack \
  --options "React,Vue,Angular"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 决策要素全覆盖 | ✅ |
| **2. 系统** | 输入→计算→建议闭环 | ✅ |
| **3. 迭代** | 权重优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动计算+排序+建议 | ✅ |

---

*版本: v1.0.0*  
*来源: decision-frameworks散落机制提取*  
*创建: 2026-03-20*
