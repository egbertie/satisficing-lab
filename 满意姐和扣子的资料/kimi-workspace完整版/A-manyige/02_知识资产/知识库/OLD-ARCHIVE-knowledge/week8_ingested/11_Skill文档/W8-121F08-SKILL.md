---
# 知识元数据 (5标准化)
knowledge_id: W8-121F08
title: Skill: Client Value System
category: 11_Skill文档
source: skills/.archive_client-value-system/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1340
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Skill: Client Value System

> **知识ID**: W8-121F08  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_client-value-system/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Skill: Client Value System

## 简介

客户价值体系Skill - 基于第一性原理的客户导向服务体系管理工具。

> **核心原理**：客户购买的不是产品，而是状态的改变。

## 能力

- 客户旅程管理
- 价值主张设计
- 产品服务分层
- 客户细分策略
- 关键指标监测

## 使用方式

### 启动客户旅程分析

```bash
# 分析特定客户的旅程状态
client-value journey --customer <customer-id>

# 查看旅程地图
client-value journey-map
```

### 价值主张设计

```bash
# 为特定细分客户设计价值主张
client-value value-prop --segment <segment>

# 更新价值主张画布
client-value vpc-update
```

### 产品服务管理

```bash
# 查看产品服务分层
client-value offerings

# 为客户推荐服务包
client-value recommend --customer <id> --stage <stage>
```

### 指标监测

```bash
# 查看客户价值指标仪表盘
client-value dashboard

# 生成周报
client-value weekly-report
```

## 输入

- 客户ID或客户画像
- 当前旅程阶段
- 业务场景描述

## 输出

- 客户旅程状态分析
- 推荐服务方案
- 价值主张建议
- 行动建议清单

## 示例

### 示例1：新客户旅程规划

```
> 客户背景：AI芯片公司创始人，技术背景，正在寻找商业合伙人
> 当前阶段：认知阶段

启动：client-value journey --customer "AI芯片-创始人A"

输出：
- 旅程阶段：认知 → 考虑
- 推荐触点：免费诊断咨询 + QPMS自评工具
- 交付物：初步分析报告
- 转化目标：预约深度诊断
- 关键行动：
  1. 发送合伙人避坑指南
  2. 邀请参加行业沙龙
  3. 提供TRL自评工具
```

### 示例2：价值主张优化

```
> 目标客户：连续创业者，经历过合伙人失败

启动：client-value value-prop --segment "连续创业者"

输出：
- 核心痛点：决策后悔、信任危机
- 价值主张：用科学方法帮你避开那些坑
- 关键信息：85%失败率、案例背书、方法论
- 差异化：不是泛泛咨询，是针对性的避坑指南
```

## 相关文档

- [客户价值体系_V1.1.md](/root/.openclaw/workspace/客户价值体系_V1.1.md)
- [行为设计手册_V1.1.md](/root/.openclaw/workspace/行为设计手册_V1.1.md)

## 元数据

- 版本：V1.1
- 作者：满意解研究所
- 更新日期：2026-03-15
- 适用范围：硬科技创业服务
