---
# 知识元数据 (5标准化)
knowledge_id: W14-C0455C
title: SKILL
category: 11_Skill文档
source: skills/.archive_video-content-processor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2053
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W14-C0455C  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_video-content-processor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: video-content-processor
version: 1.0.0
description: |
  视频内容处理器 - B站等视频字幕提取与内容总结：
  1. 全局考虑：覆盖字幕下载、分块处理、内容总结全流程
  2. 系统考虑：URL→下载→分块→总结→输出闭环
  3. 迭代机制：根据总结质量优化分块策略
  4. Skill化：标准接口，支持多种视频平台
  5. 流程自动化：全自动提取和总结
author: Satisficing Institute
tags:
  - video
  - subtitle
  - summary
  - bilibili
requires:
  - model: "kimi-coding/k2p5"
  - external: ["bilibili-api"]
---

# 视频内容处理器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 处理流程

| 阶段 | 动作 | 输出 |
|------|------|------|
| **解析URL** | 识别BV号/EP号/SS号 | ID |
| **下载字幕** | 调用API获取字幕 | 原始字幕 |
| **分块处理** | 按Token安全分块 | 分块文件 |
| **内容总结** | LLM总结各块内容 | 分块摘要 |
| **整合输出** | 合并为完整总结 | 最终报告 |

### 1.2 支持格式

| 格式 | 说明 |
|------|------|
| BV号 | 普通视频 |
| EP号 | 课程剧集 |
| SS号 | 课程系列 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 文件管理

```
bili_temp/
├── {BV_ID}/
│   ├── {BV_ID}_chunk_0.txt
│   ├── {BV_ID}_chunk_1.txt
│   └── summary.md
└── {EP_ID}/
    ├── chunk_0.txt
    └── summary.md
```

---

## 标准3: 迭代机制（Iterative）

根据总结质量优化分块大小和重叠策略。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
video-content-processor/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── download_subtitle.py    # 字幕下载
│   ├── chunk_content.py        # 内容分块
│   └── generate_summary.py     # 总结生成
└── rules/
    └── chunking_rules.yaml
```

### 4.2 调用接口

```python
from video_content_processor import VideoProcessor

processor = VideoProcessor()

# 处理视频
result = processor.process("BV1xx411c7mD")

# 获取总结
summary = processor.get_summary("BV1xx411c7mD")
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 处理视频
openclaw skill run video-content-processor process --url "BV1xx411c7mD"

# 获取总结
openclaw skill run video-content-processor summary --id "BV1xx411c7mD"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 全流程覆盖 | ✅ |
| **2. 系统** | 下载→分块→总结闭环 | ✅ |
| **3. 迭代** | 分块策略优化 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 全自动处理 | ✅ |

---

*版本: v1.0.0*  
*来源: bilibili-subtitle-download-skill散落机制提取*  
*创建: 2026-03-20*
