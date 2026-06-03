---
# 知识元数据 (5标准化)
knowledge_id: W8-A0775D
title: Skill: Behavioral Design
category: 11_Skill文档
source: skills/.archive_behavioral-design/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 3032
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Skill: Behavioral Design

> **知识ID**: W8-A0775D  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_behavioral-design/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Skill: Behavioral Design

## 简介

行为设计体系Skill - 基于第一性原理的客户触点行为设计与话术管理工具。

> **核心原理**：信任建立 = 可验证的专业 + 可感知的风险意识 + 可追溯的成功案例

## 能力

- 触点行为设计（首次/深度/长期接触）
- 话术管理（电梯演讲/异议处理/场景话术）
- 仪式感设计
- 视觉体验规范
- 行为效果分析

## 使用方式

### 触点设计

```bash
# 设计首次接触体验
behavioral-design first-contact --channel [web/phone/event]

# 设计深度接触流程
behavioral-design deep-contact --service [diagnosis/evaluation]

# 设计长期接触节奏
behavioral-design long-term --customer <customer-id>
```

### 话术获取

```bash
# 获取电梯演讲
behavioral-design pitch --duration [30s/2min/5min]

# 获取异议处理话术
behavioral-design objection --type [price/need/think/self]

# 获取场景话术
behavioral-design script --scene [intro/consult/close/followup]
```

### 仪式感生成

```bash
# 生成服务启动仪式
behavioral-design ritual --type kickoff --customer <id>

# 生成报告交付仪式
behavioral-design ritual --type delivery --customer <id>
```

### 效果分析

```bash
# 分析触点转化效果
behavioral-design analyze --funnel [awareness/consideration/decision]

# 生成行为优化建议
behavioral-design optimize --touchpoint <point>
```

## 输入

- 触点类型（first/deep/long-term）
- 场景描述
- 客户信息
- 转化目标

## 输出

- 触点设计方案
- 标准话术
- 仪式感文案
- 视觉规范
- 优化建议

## 示例

### 示例1：获取30秒电梯演讲

```
启动：behavioral-design pitch --duration 30s

输出：
我们帮助硬科技企业家避开合伙人选择的坑。
11年银行风控+11年创业经验，
用科学方法+实战直觉，
让你选对合伙人、分好股权、走稳第一步。
```

### 示例2：获取异议处理话术

```
启动：behavioral-design objection --type price

输出：
【场景】客户说"太贵了"

【应对话术】
理解您的顾虑。让我帮您算笔账：

我们的深度诊断服务是3万元，
但如果选错合伙人，代价是什么？

• 股权纠纷律师费：10-50万
• 团队分裂重建成本：6-12个月时间
• 公司估值损失：可能腰斩
• 个人精力消耗：无法估量

花3万避免潜在千万级损失，这个投资回报率如何？
```

### 示例3：设计首次接触体验

```
启动：behavioral-design first-contact --channel web

输出：
【网站首页触点设计】

3秒价值传递区（首屏）：
┌─────────────────────────────────────┐
│ 主标题：选对合伙人，避开创业第一大坑    │
│ 副标题：11年银行风控+11年创业经验      │
│         专为硬科技创始人服务           │
│ CTA按钮：免费获取合伙人风险评估        │
└─────────────────────────────────────┘

15秒信任建立区（首屏下方）：
├─ ✓ 11年银行风控经验
├─ ✓ 11年创业实战经验
├─ ✓ 服务50+硬科技企业
└─ ✓ 帮助客户避免数亿元潜在损失

60秒兴趣激发区（第二屏）：
├─ 痛点共鸣视频/案例
├─ QPMS方法简介
└─ 免费工具入口
```

### 示例4：生成服务启动仪式

```
启动：behavioral-design ritual --type kickoff --customer "XX公司"

输出：
【诊断启动仪式文案】

尊敬的客户：

恭喜您正式启动QPMS合伙人深度诊断项目！

这不仅是一次评估，
更是您为创业成功所做的重要投资。

我们承诺：
✓ 以专业态度对待每一个数据
✓ 以客观立场呈现每一个发现
✓ 以实战经验提供每一条建议

让我们一起，
为您的合伙人决策保驾护航。

【附：诊断旅程地图】
【附：资料清单】
【附：首次访谈预约链接】
```

## 话术库

### 电梯演讲系列
- 30秒版本
- 2分钟版本
- 5分钟版本（详细版）

### 异议处理系列
- "太贵了" → 价值对比法
- "不需要" → 痛点唤醒法
- "再考虑" → 紧迫感营造
- "自己能解决" → 专业分工引导

### 场景话术系列
- 初次咨询开场
- 诊断报告汇报
- 签约确认
- 跟进邮件

## 触点设计原则

### 首次接触原则
1. **3秒原则**：第一句话回答"你能为我解决什么问题"
2. **15秒原则**：提供可验证的专业证据
3. **60秒原则**：激发进一步了解的兴趣

### 深度接触原则
1. **可视化**：让客户"看见"专业过程
2. **故事化**：用故事包装数据
3. **可执行化**：给出明天就能开始的行动清单

### 长期接触原则
1. **定期价值**：即使无项目也要保持连接
2. **关键时刻**：在最需要时出现
3. **社交货币**：让客户愿意主动分享

## 自动化配置

### Cron任务

```bash
# 每周行为效果分析（周五17:17）
0 17 * * 5 openclaw agent --skill behavioral-design --task analyze

# 每月话术优化建议（月末）
0 9 28-31 * * openclaw agent --skill behavioral-design --task optimize
```

## 相关文档

- [行为设计手册_V1.1.md](/root/.openclaw/workspace/行为设计手册_V1.1.md)
- [客户价值体系_V1.1.md](/root/.openclaw/workspace/客户价值体系_V1.1.md)

## 元数据

- 版本：V1.1
- 作者：满意解研究所
- 更新日期：2026-03-15
- 适用范围：硬科技创业服务
