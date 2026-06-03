---
# 知识元数据 (5标准化)
knowledge_id: W14-F1B0D6
title: Unified Mermaid Suite
category: 11_Skill文档
source: skills/.archive_unified-mermaid-suite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1365
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Unified Mermaid Suite

> **知识ID**: W14-F1B0D6  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_unified-mermaid-suite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: unified-mermaid-suite
description: Unified diagram and visualization suite. Replaces mermaid-diagrams, swotpal-swot-analysis, business-model-canvas, presentation-helper with single integrated interface. Use for: diagram creation, chart generation, presentation slides, visual analysis.
triggers: ["diagram", "mermaid", "chart", "visualization", "presentation", "图表", "可视化"]
---

# Unified Mermaid Suite

**统一图表与可视化套件** - 整合图表创建、演示文稿、可视化分析。

> 🎯 替代: mermaid-diagrams + swotpal-swot-analysis + business-model-canvas + presentation-helper

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **图表创建** | 流程图、时序图、类图、甘特图 |
| **分析框架** | SWOT、商业模式画布、价值链 |
| **演示文稿** | PPT生成、演讲备注、动画效果 |
| **可视化模板** | 预设模板、自定义主题、批量生成 |
| **导出格式** | PNG、SVG、PDF、PPT、HTML |

---

## 快速开始

```bash
# 创建图表
mermaid-suite create --type flowchart --input process.txt --output diagram.png

# SWOT分析
mermaid-suite swot --subject "新产品" --output swot.png

# 商业模式画布
mermaid-suite canvas --business "SaaS平台" --output canvas.pdf

# 演示文稿
mermaid-suite ppt --content slides.md --template business --output presentation.pptx
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| mermaid-diagrams | `mermaid-suite create` |
| swotpal-swot-analysis | `mermaid-suite swot` |
| business-model-canvas | `mermaid-suite canvas` |
| presentation-helper | `mermaid-suite ppt` |

---

**自建替代计数**: +4
