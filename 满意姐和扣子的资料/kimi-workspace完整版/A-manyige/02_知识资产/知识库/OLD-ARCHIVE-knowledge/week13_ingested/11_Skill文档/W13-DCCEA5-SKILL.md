---
# 知识元数据 (5标准化)
knowledge_id: W13-DCCEA5
title: SKILL
category: 11_Skill文档
source: skills/.archive_six-layer-research-model/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 3198
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W13-DCCEA5  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_six-layer-research-model/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: six-layer-research-model
version: 1.0.0
description: |
  六层研究模型标准Skill - 学术级深度研究的结构化框架：
  1. 全局考虑：L1-L6六层全覆盖（范式锚定→情报网格→证据链→多维分析→逻辑架构→迭代优化）
  2. 系统考虑：六层研究闭环，每层输出标准化
  3. 迭代机制：支持层间回溯和整体优化
  4. Skill化：标准接口，可独立调用任意一层
  5. 流程自动化：自动执行完整六层流程
author: Satisficing Institute
tags:
  - research
  - six-layer
  - academic
  - methodology
requires:
  - model: "kimi-coding/k2p5"
  - external: ["kimi-search", "kimi-fetch"]
---

# 六层研究模型标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 六层模型架构

| 层级 | 名称 | 核心功能 | 输出物 |
|------|------|----------|--------|
| **L1** | 范式锚定 | 明确研究范式、认识论、方法论 | 范式声明文档 |
| **L2** | 情报网格 | 多源信息收集与三角验证 | 情报汇总表 |
| **L3** | 证据链锻造 | 可追溯的证据分级与编码 | 证据链图谱 |
| **L4** | 多维分析 | 时间/空间/学科/利益/方法论五维 | 多维矩阵 |
| **L5** | 逻辑架构 | 钻石模型：Hook→Gap→Question→Significance | 逻辑框架图 |
| **L6** | 迭代优化 | 三轮自我修正循环 | 优化报告 |

### 1.2 研究类型适配

| 研究类型 | L1-L6侧重 | 特殊要求 |
|----------|-----------|----------|
| 学术理论 | 全六层 | 理论贡献声明 |
| 政策研究 | L1-L5 | 利益相关者分析 |
| 技术研究 | L1-L6 | TRL评估 |
| 市场研究 | L2-L4 | 数据真实性分级 |
| 竞品分析 | L2-L5 | 多维度比较框架 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 六层执行流程

```
主题输入 → L1范式锚定 → {检查通过?} → L2情报网格 → {≥3信源?}
  ↓
L3证据链 → {可追溯?} → L4多维分析 → L5逻辑架构 → L6迭代优化
  ↓
{三轮修正完成?} → 研究报告 → 质量门控 → {通过?} → 交付
```

### 2.2 质量检查点

| 检查点 | 检查内容 | 失败处理 |
|--------|----------|----------|
| G1 | 六层完整性 | 返回补充 |
| G2 | 引用溯源性 | 标记待验证 |
| G3 | 逻辑一致性 | 红队挑战 |
| G4 | 数据真实性 | 降级处理 |

---

## 标准3: 迭代机制（Iterative）

### 3.1 三轮自我修正

| 轮次 | 目标 | 检查点 |
|------|------|--------|
| 第一轮 | 信息饱和 | 覆盖度检查 |
| 第二轮 | 逻辑强化 | 因果检查 |
| 第三轮 | 表达精炼 | 可读性检查 |

### 3.2 版本进化

```
V1.0.0: 基础六层框架
  ↓
V1.1.0: 自动化质量门控
  ↓
V1.2.0: 领域自适应优化
```

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
six-layer-research-model/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── run_full_research.py    # 完整六层研究
│   ├── l1_paradigm.py          # L1范式锚定
│   ├── l2_intelligence.py      # L2情报网格
│   ├── l3_evidence.py          # L3证据链
│   ├── l4_multidimension.py    # L4多维分析
│   ├── l5_logic.py             # L5逻辑架构
│   └── l6_optimize.py          # L6迭代优化
└── rules/
    └── research_standards.yaml
```

### 4.2 调用接口

```python
from six_layer_research_model import ResearchEngine

engine = ResearchEngine()

# 完整研究
report = engine.conduct_research(topic="合伙人决策方法论")

# 单层执行
l1_result = engine.l1_paradigm(topic)
l2_result = engine.l2_intelligence(topic)

# 从指定层开始
report = engine.conduct_from_layer(topic, start_layer="L3")
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 自动执行流程

| 阶段 | 自动动作 | 输出 |
|------|----------|------|
| 主题输入 | 识别研究类型 | 类型标签 |
| L1-L6 | 自动执行六层分析 | 六层报告 |
| 质量检查 | 自动验证5个门控点 | 质量报告 |
| 迭代优化 | 自动执行三轮修正 | 优化报告 |

### 5.2 使用方法

```bash
# 完整六层研究
openclaw skill run six-layer-research-model conduct --topic "合伙人决策"

# 执行指定层
openclaw skill run six-layer-research-model l1 --topic "合伙人决策"
openclaw skill run six-layer-research-model l2 --topic "合伙人决策"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 六层全覆盖 + 研究类型适配 | ✅ |
| **2. 系统** | 六层闭环 + 质量门控 | ✅ |
| **3. 迭代** | 三轮修正 + 版本进化 | ✅ |
| **4. Skill化** | 标准目录 + 可调用接口 | ✅ |
| **5. 自动化** | 全自动执行 + 边界清晰 | ✅ |

---

*版本: v1.0.0*  
*来源: academic-deep-research散落机制提取*  
*创建: 2026-03-20*
