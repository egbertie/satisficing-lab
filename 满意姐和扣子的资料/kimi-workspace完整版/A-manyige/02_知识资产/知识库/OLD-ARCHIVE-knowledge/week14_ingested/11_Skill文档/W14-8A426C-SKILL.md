---
# 知识元数据 (5标准化)
knowledge_id: W14-8A426C
title: Unified Knowledge Suite
category: 11_Skill文档
source: skills/.archive_unified-knowledge-suite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1421
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Unified Knowledge Suite

> **知识ID**: W14-8A426C  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_unified-knowledge-suite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: unified-knowledge-suite
description: Unified knowledge management and extraction suite. Replaces knowledge-extractor, knowledge-distiller, multi-format-output-evolution, multi-format-delivery with single integrated interface. Use for: knowledge extraction, summarization, format conversion, multi-channel delivery.
triggers: ["knowledge", "extract", "summarize", "distill", "format", "知识", "提取"]
---

# Unified Knowledge Suite

**统一知识管理与提取套件** - 整合知识提取、蒸馏、多格式输出。

> 🎯 替代: knowledge-extractor + knowledge-distiller + multi-format-output-evolution + multi-format-delivery

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **知识提取** | 实体识别、关系抽取、知识图谱 |
| **内容蒸馏** | 摘要生成、关键点提取、结构化 |
| **格式转换** | 多格式输入输出、模板渲染 |
| **多渠道发布** | PDF、网页、邮件、消息推送 |
| **知识库构建** | 自动分类、标签体系、检索优化 |

---

## 快速开始

```bash
# 知识提取
knowledge-suite extract --input document.pdf --entities person,org,tech

# 内容蒸馏
knowledge-suite distill --input article.txt --length short --format bullet

# 格式转换
knowledge-suite convert --input report.md --formats pdf,html,docx

# 多渠道发布
knowledge-suite publish --content summary.md --channels email,slack,web
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| knowledge-extractor | `knowledge-suite extract` |
| knowledge-distiller | `knowledge-suite distill` |
| multi-format-output-evolution | `knowledge-suite convert` |
| multi-format-delivery | `knowledge-suite publish` |

---

**自建替代计数**: +4
