---
# 知识元数据 (5标准化)
knowledge_id: W12-A5BC13
title: SKILL
category: 11_Skill文档
source: skills/.archive_persona-debate-simulator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2141
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

> **知识ID**: W12-A5BC13  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_persona-debate-simulator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: persona-debate-simulator
version: 1.0.0
description: |
  客户替身辩论模拟器 - 在多智能体辩论中模拟客户视角：
  1. 全局考虑：覆盖反应模拟、辩论参与、方案评估
  2. 系统考虑：替身加载→刺激输入→反应生成→辩论参与闭环
  3. 迭代机制：根据真实客户反馈优化替身模型
  4. Skill化：标准接口，可扩展新替身
  5. 流程自动化：自动加载替身并参与辩论
author: Satisficing Institute
tags:
  - persona
  - debate
  - simulation
  - customer
requires:
  - model: "kimi-coding/k2p5"
---

# 客户替身辩论模拟器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 替身类型

| ID | 姓名 | 类型 | 特点 |
|----|------|------|------|
| chenmingyuan | 陈明远 | 科学家型 | 学术背景 |
| zhangjianguo | 张建国 | 连续创业者 | 经验丰富 |
| lixiaowen | 李晓雯 | 跨界转型者 | 转型期 |

### 1.2 能力

| 能力 | 说明 |
|------|------|
| 反应模拟 | 对刺激(如提案)生成情感+认知+行为反应 |
| 辩论参与 | 在多智能体辩论中提供客户视角论点 |
| 方案评估 | 评估方案可接受度并给出理由 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 模拟流程

```
加载替身 → 设置情境 → 输入刺激 → 生成反应 → 参与辩论 → 评估方案
```

---

## 标准3: 迭代机制（Iterative）

根据真实客户反馈持续优化替身行为模型。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
persona-debate-simulator/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── load_persona.py         # 替身加载
│   ├── generate_reaction.py    # 反应生成
│   ├── participate_debate.py   # 辩论参与
│   └── evaluate_proposal.py    # 方案评估
└── personas/
    ├── zhangjianguo.yaml
    ├── chenmingyuan.yaml
    └── lixiaowen.yaml
```

### 4.2 调用接口

```python
from persona_debate_simulator import PersonaSimulator

simulator = PersonaSimulator()

# 加载替身
persona = simulator.load("zhangjianguo")

# 获取反应
reaction = persona.react("股权分配方案", context={"stage": "A轮"})

# 参与辩论
response = persona.debate("股权分配", position="客户视角")
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 加载替身并获取反应
openclaw skill run persona-debate-simulator react \
  --persona zhangjianguo \
  --stimulus "股权分配方案"

# 参与辩论
openclaw skill run persona-debate-simulator debate \
  --persona zhangjianguo \
  --topic "股权分配"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 多替身+多能力覆盖 | ✅ |
| **2. 系统** | 加载→反应→辩论闭环 | ✅ |
| **3. 迭代** | 模型优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动加载和参与 | ✅ |

---

*版本: v1.0.0*  
*来源: client-persona-simulator散落机制提取*  
*创建: 2026-03-20*
