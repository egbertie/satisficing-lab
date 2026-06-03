---
# 知识元数据 (5标准化)
knowledge_id: W8-3FD587
title: SKILL
category: 11_Skill文档
source: skills/.archive_batch-content-generator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1051
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

> **知识ID**: W8-3FD587  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_batch-content-generator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: batch-content-generator
version: 1.0.0
description: |
  批量内容生成器 - 一次生成多条社交媒体内容：
  1. 全局考虑：覆盖主题输入→多内容生成→格式适配
  2. 系统考虑：主题→脚本→生成→审核→输出闭环
  3. 迭代机制：根据互动数据优化生成策略
  4. Skill化：标准接口，可按平台定制
  5. 流程自动化：一键批量生成内容
author: Satisficing Institute
tags:
  - content
  - batch
  - generation
  - social-media
requires:
  - model: "kimi-coding/k2p5"
---

# 批量内容生成器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 生成能力

| 能力 | 说明 |
|------|------|
| 批量脚本 | 一次生成多条视频脚本 |
| 主题扩展 | 基于核心主题扩展多个角度 |
| 平台适配 | 自动生成多平台版本 |
| 风格一致 | 保持品牌调性一致 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 生成流程

```
核心主题 → 角度扩展 → 脚本生成 → 平台适配 → 批量输出
```

---

## 标准3-5: Skill化与自动化

### 目录结构

```
batch-content-generator/
├── SKILL.md
├── _meta.json
└── scripts/
    └── generate_batch.py
```

### 使用方法

```bash
openclaw skill run batch-content-generator generate \
  --topic "生产力技巧" \
  --count 5 \
  --platforms tiktok,instagram
```

---

## 5标准验证

| 标准 | 状态 |
|------|------|
| 全局考虑 | ✅ |
| 系统考虑 | ✅ |
| 迭代机制 | ✅ |
| Skill化 | ✅ |
| 自动化 | ✅ |

---

*来源: ai-social-media-content散落机制提取*
