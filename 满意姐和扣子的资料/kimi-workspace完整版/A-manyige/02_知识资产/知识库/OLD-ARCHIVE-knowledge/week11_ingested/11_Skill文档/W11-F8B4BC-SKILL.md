---
# 知识元数据 (5标准化)
knowledge_id: W11-F8B4BC
title: SKILL
category: 11_Skill文档
source: skills/.archive_iterative-research-optimizer/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 3087
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W11-F8B4BC  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_iterative-research-optimizer/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: iterative-research-optimizer
version: 1.0.0
description: |
  迭代研究优化器 - 自动执行研究内容的三轮自我修正：
  1. 全局考虑：覆盖信息饱和、逻辑强化、表达精炼三个维度
  2. 系统考虑：输入→修正→验证→输出完整闭环
  3. 迭代机制：三轮递进式优化，每轮有明确检查点
  4. Skill化：标准接口，可对接任何研究输出
  5. 流程自动化：全自动三轮迭代，无需人工介入
author: Satisficing Institute
tags:
  - iteration
  - optimization
  - research
  - refinement
requires:
  - model: "kimi-coding/k2p5"
---

# 迭代研究优化器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 三轮优化维度

| 轮次 | 目标 | 检查点 | 优化动作 |
|------|------|--------|----------|
| **第一轮** | 信息饱和 | 覆盖度检查 | 补充缺失信源 |
| **第二轮** | 逻辑强化 | 因果检查 | 修正逻辑漏洞 |
| **第三轮** | 表达精炼 | 可读性检查 | 优化结构表达 |

### 1.2 质量指标

| 指标 | 第一轮 | 第二轮 | 第三轮 |
|------|--------|--------|--------|
| 信息覆盖率 | ≥90% | - | - |
| 逻辑一致性 | - | ≥95% | - |
| 可读性评分 | - | - | ≥85分 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 迭代优化流程

```
初稿输入 → 第一轮（信息饱和）→ {通过?} → 第二轮（逻辑强化）→ {通过?}
  ↓
第三轮（表达精炼）→ {通过?} → 终稿输出
```

### 2.2 失败处理

| 失败轮次 | 处理动作 | 输出 |
|----------|----------|------|
| 第一轮 | 返回信息收集阶段 | 缺失清单 |
| 第二轮 | 启动红队挑战 | 逻辑问题清单 |
| 第三轮 | 提供改写建议 | 表达优化建议 |

---

## 标准3: 迭代机制（Iterative）

### 3.1 自适应迭代

```python
if round1_score < 80:
    extend_search_depth()
    retry_round1()
    
if round2_score < 85:
    activate_red_team()
    enhance_logic_check()
    
if round3_score < 80:
    apply_style_guide()
    restructure_content()
```

### 3.2 历史学习

| 优化类型 | 学习来源 | 应用方式 |
|----------|----------|----------|
| 信息补充模式 | 历史缺失清单 | 预判补充 |
| 逻辑修正模式 | 历史漏洞类型 | 前置检查 |
| 表达优化模式 | 历史改写建议 | 模板应用 |

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
iterative-research-optimizer/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── optimize.py             # 主优化脚本
│   ├── round1_information.py   # 第一轮：信息饱和
│   ├── round2_logic.py         # 第二轮：逻辑强化
│   ├── round3_expression.py    # 第三轮：表达精炼
│   └── compare_versions.py     # 版本对比
└── rules/
    └── optimization_criteria.yaml
```

### 4.2 调用接口

```python
from iterative_research_optimizer import IterativeOptimizer

optimizer = IterativeOptimizer()

# 执行完整三轮优化
final = optimizer.optimize(draft, rounds=3)

# 执行指定轮次
round1_result = optimizer.round1_information(draft)
round2_result = optimizer.round2_logic(round1_result)

# 对比版本
comparison = optimizer.compare_versions(original, optimized)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 自动优化流程

| 阶段 | 自动动作 | 输出 |
|------|----------|------|
| 初稿输入 | 评估当前质量 | 质量基线 |
| 第一轮 | 检查信息覆盖度 | 补充建议 |
| 第二轮 | 检查逻辑一致性 | 修正建议 |
| 第三轮 | 检查可读性 | 优化建议 |
| 完成 | 生成优化报告 | 对比文档 |

### 5.2 使用方法

```bash
# 执行三轮优化
openclaw skill run iterative-research-optimizer optimize --file draft.md --rounds 3

# 执行单轮优化
openclaw skill run iterative-research-optimizer round1 --file draft.md

# 对比版本
openclaw skill run iterative-research-optimizer compare --original draft.md --optimized final.md
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 三轮维度全覆盖 | ✅ |
| **2. 系统** | 输入→修正→输出闭环 | ✅ |
| **3. 迭代** | 自适应迭代 + 历史学习 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 全自动三轮优化 | ✅ |

---

*版本: v1.0.0*  
*来源: academic-deep-research散落机制提取*  
*创建: 2026-03-20*
