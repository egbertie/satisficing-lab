---
# 知识元数据 (5标准化)
knowledge_id: W12-1786FE
title: 合伙人评估问卷生成器
category: 11_Skill文档
source: skills/.archive_questionnaire-generator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 995
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 合伙人评估问卷生成器

> **知识ID**: W12-1786FE  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_questionnaire-generator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: questionnaire-generator
description: 合伙人评估问卷生成器 - 满意解研究所专用工具。基于五路图腾感知力决策方法论，生成结构化合伙人评估问卷。
---

# 合伙人评估问卷生成器

满意解研究所核心工具 - 基于感知力决策方法论。

## 核心功能

### 1. 问卷模板管理
- V1.0 基础版：认知、情感、行为三维度
- V2.0 感知力版：加入直觉判断维度
- 定制版：针对特定行业/阶段定制

### 2. 评估维度

| 维度 | 权重 | 评估内容 |
|------|------|----------|
| 认知层 | 30% | 经验、能力、资源匹配度 |
| 情感层 | 30% | 价值观、信任度、默契度 |
| 行为层 | 20% | 行动习惯、承诺兑现 |
| 直觉层 | 20% | 感知力判断、气场匹配 |

### 3. 输出格式
- Markdown（飞书文档友好）
- Excel（数据分析友好）
- PDF（正式交付物）

## 问卷类型

### 类型A：初筛问卷（5分钟）
快速过滤明显不匹配的候选人

### 类型B：深度评估（30分钟）
针对通过初筛的候选人，全面评估

### 类型C：72小时压力测试
《极限72小时》实战测试配套问卷

## 使用方法

```bash
# 生成初筛问卷
./qgen.sh screening

# 生成深度评估问卷
./qgen.sh deep

# 生成压力测试问卷
./qgen.sh stress

# 导出为Excel
./qgen.sh deep --format excel

# 定制问卷（指定维度权重）
./qgen.sh custom --cognitive 25 --emotional 35 --behavior 20 --intuition 20
```

## 集成

- 飞书多维表格：自动同步评估结果
- Notion：问卷结果存档
- DuckDB：数据分析、候选人对比

## 输出示例

生成的问卷包含：
1. 指导语（说明评估目的和填写方式）
2. 基本信息（姓名、背景、联系方式）
3. 评估题目（按维度分组，含评分标准）
4. 感知力判断（直觉维度的特殊题目）
5. 总结建议（基于得分的初步判断）
