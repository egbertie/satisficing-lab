---
# 知识元数据 (5标准化)
knowledge_id: W9-F23B11
title: 内容分发引擎 (Content Distribution Engine)
category: 11_Skill文档
source: skills/.archive_content-distribution-engine/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2087
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 内容分发引擎 (Content Distribution Engine)

> **知识ID**: W9-F23B11  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_content-distribution-engine/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: content-distribution-engine
description: |
  满意解研究所内容分发引擎 - 将百科全书核心内容转化为多平台适配版本。
  支持：商业伙伴版、渠道伙伴版、客户版、公众号版、小红书版。
  一键生成，多平台分发。
---

# 内容分发引擎 (Content Distribution Engine)

## 核心功能

将 V1.1 人格化整合版百科全书，按不同受众和平台特性，自动重组生成适配内容。

## 输入

- source: 百科全书核心内容路径
- target_audiences: ["business_partner", "channel_partner", "client", "wechat", "xiaohongshu"]
- output_dir: 输出目录

## 输出

| 受众 | 文件 | 特点 |
|------|------|------|
| 商业伙伴 | business-partner.md | 专业、数据、ROI导向 |
| 渠道伙伴 | channel-partner.md | 赋能、返佣、合作模式 |
| 客户 | client.md | 痛点、方案、信任背书 |
| 公众号 | wechat-official.md | 深度、故事、互动引导 |
| 小红书 | xiaohongshu.md | 视觉、金句、种草导向 |

## 内容重组规则

### 商业伙伴版 (Business Partner)

**核心诉求**: 专业可信度、投资回报、长期价值

**内容结构**:
1. 市场机会 (硬科技合伙人匹配的市场空白)
2. 独特优势 (11年银行风控 + 11年创业体感的组合门槛)
3. 商业模式 (OPC轻资产 → 系统化公司)
4. 合作价值 (为客户带来的ROI、降低的风险)
5. 成功案例 (潜在收益展示)

**语调**: 专业、数据驱动、可验证

### 渠道伙伴版 (Channel Partner)

**核心诉求**: 赋能价值、返佣机制、客户粘性

**内容结构**:
1. 痛点共鸣 (渠道客户常见的合伙人纠纷)
2. 解决方案 (如何帮渠道解决客户问题)
3. 赋能体系 (渠道可以获得什么)
4. 返佣机制 (具体合作模式)
5. 案例背书 (已有合作案例)

**语调**: 共赢、赋能、具体数字

### 客户版 (Client)

**核心诉求**: 理解痛点、信任、可落地的解决方案

**内容结构**:
1. 痛点诊断 (你遇到的合伙人选择困境)
2. 误解澄清 (不是猎头/不是法律/不是玄学)
3. 方法论介绍 (TRL-PFI模型)
4. 服务流程 (具体怎么做)
5. 信任背书 (专家网络、案例)

**语调**: 共情、专业、口语化

### 公众号版 (WeChat Official)

**核心诉求**: 阅读完成率、互动、关注转化

**内容结构**:
1. 钩子标题 (痛点/好奇/利益)
2. 故事开场 (个人经历引入)
3. 问题放大 (共鸣构建)
4. 解决方案 (方法论简述)
5. 互动引导 (评论/转发/关注)

**语调**: 亲切、有故事感、适度口语化
**长度**: 2000-3000字

### 小红书版 (Xiaohongshu)

**核心诉求**: 视觉吸引力、金句传播、收藏转化

**内容结构**:
1. 封面标题 (大字报风格)
2. 痛点金句 (3-5个)
3. 解决方案 (图示化)
4. 工具推荐 (TRL-PFI卡片)
5. CTA (私信/收藏/关注)

**语调**: 种草、实用、年轻化
**长度**: 500-800字

## 使用方式

```bash
# 生成全部版本
content-distribute --source encyclopedia_v1.1.md --all

# 生成指定版本
content-distribute --source encyclopedia_v1.1.md --target business_partner

# 生成公域内容
content-distribute --source encyclopedia_v1.1.md --target wechat xiaohongshu
```

## 模板文件

模板存储于 `templates/` 目录：
- `business-partner.md`
- `channel-partner.md`
- `client.md`
- `wechat-official.md`
- `xiaohongshu.md`

## 质量检查清单

- [ ] 每个版本都有明确的受众定位
- [ ] 核心信息一致，表达方式适配
- [ ] 有明确的行动召唤 (CTA)
- [ ] 符合平台调性
- [ ] Egbertie人格化特征保持一致
