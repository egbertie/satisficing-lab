---
# 知识元数据 (5标准化)
knowledge_id: W9-699E96
title: SKILL
category: 11_Skill文档
source: skills/.archive_copywriting-framework-engine/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2278
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

> **知识ID**: W9-699E96  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_copywriting-framework-engine/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: copywriting-framework-engine
version: 1.0.0
description: |
  文案框架引擎 - 多种说服框架的文案生成工具：
  1. 全局考虑：覆盖AIDA、PAS、FAB、BAB、4P等主流框架
  2. 系统考虑：目标输入→框架选择→文案生成→优化闭环
  3. 迭代机制：根据点击率/转化率优化框架应用
  4. Skill化：标准接口，可扩展新框架
  5. 流程自动化：自动生成多框架文案
author: Satisficing Institute
tags:
  - copywriting
  - framework
  - persuasion
  - marketing
requires:
  - model: "kimi-coding/k2p5"
---

# 文案框架引擎标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 支持框架

| 框架 | 适用场景 | 结构 |
|------|----------|------|
| **AIDA** | 落地页/销售页 | Attention→Interest→Desire→Action |
| **PAS** | 痛点明确的受众 | Problem→Agitate→Solution |
| **FAB** | 产品描述 | Feature→Advantage→Benefit |
| **BAB** | 简单转化文案 | Before→After→Bridge |
| **4P** | 简洁促销 | Picture→Promise→Proof→Push |

### 1.2 输出格式

| 格式 | 说明 |
|------|------|
| 主推荐 | 最佳框架生成的文案 |
| 备选版本 | 其他框架生成的文案 |
| 标题选项 | 多个标题供测试 |
| CTA选项 | 多个CTA供测试 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 生成流程

```
目标输入 → 受众分析 → 框架选择 → 文案生成 → 多版本输出 → 优化建议
```

---

## 标准3: 迭代机制（Iterative）

根据A/B测试结果优化框架选择和文案生成。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
copywriting-framework-engine/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── generate_copy.py        # 文案生成
│   ├── aida_framework.py       # AIDA框架
│   ├── pas_framework.py        # PAS框架
│   ├── fab_framework.py        # FAB框架
│   └── optimize_copy.py        # 文案优化
└── templates/
    └── framework_templates.yaml
```

### 4.2 调用接口

```python
from copywriting_framework_engine import CopyEngine

engine = CopyEngine()

# 生成文案
copy = engine.generate(
    goal="转化",
    audience="硬科技创始人",
    offer="合伙人决策服务",
    framework="PAS"
)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 使用指定框架生成文案
openclaw skill run copywriting-framework-engine generate \
  --goal "转化" \
  --audience "硬科技创始人" \
  --offer "合伙人决策服务" \
  --framework PAS

# 生成多框架版本
openclaw skill run copywriting-framework-engine generate-all \
  --goal "转化" \
  --audience "硬科技创始人" \
  --offer "合伙人决策服务"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 5大框架覆盖 | ✅ |
| **2. 系统** | 输入→框架→生成闭环 | ✅ |
| **3. 迭代** | 效果优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动生成多框架文案 | ✅ |

---

*版本: v1.0.0*  
*来源: copywriting-zh-pro散落机制提取*  
*创建: 2026-03-20*
