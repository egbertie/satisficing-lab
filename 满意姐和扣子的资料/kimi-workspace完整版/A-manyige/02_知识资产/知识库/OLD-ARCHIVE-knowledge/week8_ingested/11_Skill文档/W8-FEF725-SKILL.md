---
# 知识元数据 (5标准化)
knowledge_id: W8-FEF725
title: SKILL
category: 11_Skill文档
source: skills/.archive_bmc-consistency-checker/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2185
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W8-FEF725  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_bmc-consistency-checker/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: bmc-consistency-checker
version: 1.0.0
description: |
  商业模式画布一致性检查器 - 验证商业模式各模块的交叉一致性：
  1. 全局考虑：覆盖BMC 9(+1)个模块的交叉验证
  2. 系统考虑：输入→交叉检查→问题识别→建议生成闭环
  3. 迭代机制：根据实际运营反馈优化检查规则
  4. Skill化：标准接口，可嵌入任何商业模式设计流程
  5. 流程自动化：自动检查并生成一致性报告
author: Satisficing Institute
tags:
  - business-model
  - bmc
  - validation
  - consistency
requires:
  - model: "kimi-coding/k2p5"
---

# 商业模式画布一致性检查器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 检查维度

| 检查点 | 验证内容 |
|--------|----------|
| Value ↔ Segments | 价值主张是否直接解决细分客户痛点 |
| Revenue ↔ Value | 客户是否愿意为价值支付设定价格 |
| Channels ↔ Segments | 是否能通过渠道触达目标客户 |
| Activities ↔ Time | 关键活动是否适配可用时间 |
| Costs ↔ Revenue | 收入是否覆盖成本(单位经济学) |
| Resources ↔ Activities | 是否有资源执行所有活动 |
| Partnerships ↔ Risks | 关键依赖是否识别并有缓解措施 |

### 1.2 附加检查（Solopreneur专用）

| 检查点 | 说明 |
|--------|------|
| Time Budget | 时间预算是否平衡 |
| Burnout Risk | 是否存在过劳风险 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 检查流程

```
BMC输入 → 逐对检查 → 问题识别 → 严重程度评估 → 改进建议 → 报告生成
```

### 2.2 问题分级

| 级别 | 说明 | 处理 |
|------|------|------|
| 🔴 Critical | 商业模式根本性矛盾 | 必须修复 |
| 🟡 Warning | 存在风险需关注 | 建议修复 |
| 🟢 OK | 一致性良好 | 保持 |

---

## 标准3: 迭代机制（Iterative）

根据实际运营数据优化检查规则和阈值。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
bmc-consistency-checker/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── check_consistency.py    # 一致性检查
│   ├── identify_issues.py      # 问题识别
│   └── generate_suggestions.py # 建议生成
└── rules/
    └── consistency_rules.yaml
```

### 4.2 调用接口

```python
from bmc_consistency_checker import BMCChecker

checker = BMCChecker()

# 检查BMC一致性
result = checker.check(bmc_data)

# 生成报告
checker.generate_report(result)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 检查BMC一致性
openclaw skill run bmc-consistency-checker check --file bmc.md

# 生成报告
openclaw skill run bmc-consistency-checker report --file bmc.md
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 7个交叉检查点全覆盖 | ✅ |
| **2. 系统** | 检查→识别→建议闭环 | ✅ |
| **3. 迭代** | 规则优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动检查+报告 | ✅ |

---

*版本: v1.0.0*  
*来源: business-model-canvas散落机制提取*  
*创建: 2026-03-20*
