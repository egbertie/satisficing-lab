---
# 知识元数据 (5标准化)
knowledge_id: W12-4CE470
title: SKILL
category: 11_Skill文档
source: skills/.archive_multi-platform-content-adapter/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2649
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

> **知识ID**: W12-4CE470  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_multi-platform-content-adapter/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: multi-platform-content-adapter
version: 1.0.0
description: |
  多平台内容适配器 - 将核心内容自动适配为多平台版本：
  1. 全局考虑：覆盖公众号、小红书、B站、知乎等多平台特性
  2. 系统考虑：输入→分析→适配→输出→验证闭环
  3. 迭代机制：根据平台反馈优化适配规则
  4. Skill化：标准接口，可扩展新平台
  5. 流程自动化：一键生成多平台版本
author: Satisficing Institute
tags:
  - content
  - multi-platform
  - adaptation
  - social-media
requires:
  - model: "kimi-coding/k2p5"
---

# 多平台内容适配器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 平台特性覆盖

| 平台 | 格式特点 | 长度限制 | 风格 |
|------|----------|----------|------|
| **公众号** | 长图文 | 2000-3000字 | 深度、故事化 |
| **小红书** | 短图文 | 500-800字 | 种草、视觉化 |
| **B站** | 视频脚本 | 3-10分钟 | 口语化、梗 |
| **知乎** | 问答 | 1000-2000字 | 专业、理性 |
| **朋友圈** | 短文案 | 100-200字 | 自然、信任 |
| **抖音** | 短视频 | 15-60秒 | 快节奏、钩子 |

### 1.2 适配维度

| 维度 | 适配内容 |
|------|----------|
| **结构** | 标题→开头→正文→结尾→CTA |
| **语调** | 专业/口语化/种草/故事化 |
| **长度** | 压缩/扩展 |
| **格式** | 图文/纯文/脚本 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 适配流程

```
核心内容 → 平台选择 → 内容分析 → 结构重排 → 语调转换 → 长度调整 → 输出生成
```

### 2.2 质量验证

| 检查项 | 验证方式 |
|--------|----------|
| 平台调性匹配 | 风格检查 |
| 长度合规 | 字数统计 |
| CTA完整性 | 结构检查 |
| 品牌一致性 | 关键词检查 |

---

## 标准3: 迭代机制（Iterative）

### 3.1 规则优化

| 反馈来源 | 优化动作 |
|----------|----------|
| 阅读完成率 | 调整开头钩子 |
| 互动率 | 优化CTA |
| 转发率 | 增强金句 |

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
multi-platform-content-adapter/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── adapt.py                # 主适配脚本
│   ├── analyze_content.py      # 内容分析
│   ├── adapt_wechat.py         # 公众号适配
│   ├── adapt_xiaohongshu.py    # 小红书适配
│   ├── adapt_bilibili.py       # B站适配
│   └── validate.py             # 质量验证
└── rules/
    └── platform_styles.yaml
```

### 4.2 调用接口

```python
from multi_platform_content_adapter import ContentAdapter

adapter = ContentAdapter()

# 适配到指定平台
wechat_version = adapter.adapt(content, platform="wechat")
xiaohongshu_version = adapter.adapt(content, platform="xiaohongshu")

# 批量适配
all_versions = adapter.adapt_all(content, platforms=["wechat", "xiaohongshu", "bilibili"])
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 适配到指定平台
openclaw skill run multi-platform-content-adapter adapt \
  --source article.md \
  --platform wechat

# 批量适配
openclaw skill run multi-platform-content-adapter adapt-all \
  --source article.md \
  --platforms wechat,xiaohongshu,bilibili
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 多平台特性覆盖 | ✅ |
| **2. 系统** | 分析→适配→验证闭环 | ✅ |
| **3. 迭代** | 根据反馈优化 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 一键生成多平台版本 | ✅ |

---

*版本: v1.0.0*  
*来源: content-distribution-engine散落机制提取*  
*创建: 2026-03-20*
