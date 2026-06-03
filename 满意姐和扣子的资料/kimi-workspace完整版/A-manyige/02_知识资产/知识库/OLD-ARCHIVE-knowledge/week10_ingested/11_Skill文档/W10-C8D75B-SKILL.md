---
# 知识元数据 (5标准化)
knowledge_id: W10-C8D75B
title: SKILL
category: 11_Skill文档
source: skills/.archive_ffmpeg-batch-processor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 3066
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W10-C8D75B  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_ffmpeg-batch-processor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: ffmpeg-batch-processor
version: 1.0.0
description: |
  FFmpeg视频批处理器 - 视频剪切、格式转换、压缩、音频提取等15+操作
  支持批量处理和预设工作流
author: Satisficing Institute
tags:
  - ffmpeg
  - video
  - batch-processing
  - media
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["ffmpeg"]
  - cron: false
---

# 🎬 FFmpeg Batch Processor V1.0.0

## 🎯 功能概述

将自然语言视频编辑请求转换为FFmpeg命令，支持批量处理和预设工作流。

### 支持的操作
| 操作 | 描述 | 复杂度 |
|------|------|--------|
| cut/trim | 视频剪切 | ⭐ |
| convert | 格式转换 | ⭐ |
| compress | 视频压缩 | ⭐ |
| resize | 分辨率调整 | ⭐⭐ |
| aspect | 宽高比调整 | ⭐⭐ |
| extract-audio | 音频提取 | ⭐ |
| remove-audio | 移除音频 | ⭐ |
| speed | 变速 | ⭐⭐ |
| gif | 转GIF | ⭐⭐ |
| rotate | 旋转/翻转 | ⭐ |
| screenshot | 截图 | ⭐ |
| watermark | 添加水印 | ⭐⭐ |
| subtitle | 烧录字幕 | ⭐⭐ |
| concat | 视频合并 | ⭐⭐⭐ |

## 📋 标准1: 全局考虑

### 支持的格式
- **视频**: mp4, mkv, avi, webm, mov, flv, wmv
- **音频**: mp3, aac, wav, flac, ogg
- **图片**: jpg, png (截图输出)

### 预设配置
| 预设 | 分辨率 | 用途 |
|------|--------|------|
| youtube | 1920x1080 | YouTube上传 |
| tiktok | 1080x1920 | 抖音/竖屏 |
| instagram | 1080x1080 | Instagram方形 |
| web | 1280x720 | 网页视频 |
| mobile | 854x480 | 移动端 |

## ⚙️ 标准2: 系统考虑

### 批处理流程
```
扫描输入目录 → 识别文件类型 → 应用预设
  → 生成命令 → 执行转换 → 验证输出 → 记录日志
```

### 错误处理
- ✅ 自动跳过损坏文件
- ✅ 错误日志记录
- ✅ 部分失败继续处理
- ✅ 输出文件命名冲突解决

## 🔄 标准3: 迭代机制

### 版本计划
```
V1.0: 基础转换功能
  ↓
V1.1: 批量目录处理
  ↓
V2.0: 预设工作流 + 队列管理
```

## 📦 标准4: Skill化

### 目录结构
```
skills/ffmpeg-batch-processor/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── video_processor.sh      # 主处理脚本
│   ├── operations/
│   │   ├── cut.sh             # 剪切
│   │   ├── convert.sh         # 转换
│   │   ├── compress.sh        # 压缩
│   │   ├── resize.sh          # 调整大小
│   │   ├── extract_audio.sh   # 提取音频
│   │   └── make_gif.sh        # 生成GIF
│   └── batch_processor.py     # 批处理管理器
├── presets/
│   ├── youtube.yaml           # YouTube预设
│   ├── tiktok.yaml            # 抖音预设
│   └── web.yaml               # 网页预设
└── config/
    └── ffmpeg_options.json    # FFmpeg选项
```

### 命令接口
```bash
# 单文件处理
./scripts/video_processor.sh [operation] [input] [options]

# 批处理
./scripts/batch_processor.py --preset [preset] --input [dir]

# 示例
./scripts/video_processor.sh cut video.mp4 --start 00:01:21 --end 00:01:35
./scripts/batch_processor.py --preset youtube --input ./videos/
```

## 🤖 标准5: 流程自动化

### 批量工作流
```bash
# 目录监控模式（可选cron）
./scripts/batch_processor.py --watch --preset web --input ./incoming/
```

### 输出组织
```
output/
├── [date]/
│   ├── converted/       # 转换后的文件
│   ├── logs/           # 处理日志
│   └── failed/         # 失败文件
```

## 🚀 使用方法

### 视频剪切
```bash
./scripts/operations/cut.sh input.mp4 00:01:21 00:01:35 output.mp4
```

### 格式转换
```bash
./scripts/operations/convert.sh input.avi mp4
```

### 视频压缩
```bash
./scripts/operations/compress.sh input.mp4 --quality 23
# quality: 18(高质量) - 28(高压缩)
```

### 批量处理
```bash
./scripts/batch_processor.py --preset youtube --input ./my-videos/
```

## ⚠️ 注意事项

- 始终使用 `-y` 覆盖输出文件
- 使用 `-hide_banner` 清理输出
- 压缩时 CRF 值范围: 18(高质量) → 28(高压缩)
- 变速时音频 `atempo` 必须在 0.5-2.0 范围

---
*版本: v1.0.0 | 创建: 2026-03-20*
