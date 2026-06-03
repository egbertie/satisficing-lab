---
# 知识元数据 (5标准化)
knowledge_id: W14-152ACA
title: Video Frames (ffmpeg)
category: 11_Skill文档
source: skills/.archive_video-frames/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 767
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Video Frames (ffmpeg)

> **知识ID**: W14-152ACA  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_video-frames/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: video-frames
description: Extract frames or short clips from videos using ffmpeg.
homepage: https://ffmpeg.org
metadata: {"clawdbot":{"emoji":"🎞️","requires":{"bins":["ffmpeg"]},"install":[{"id":"brew","kind":"brew","formula":"ffmpeg","bins":["ffmpeg"],"label":"Install ffmpeg (brew)"}]}}
---

# Video Frames (ffmpeg)

Extract a single frame from a video, or create quick thumbnails for inspection.

## Quick start

First frame:

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
```

At a timestamp:

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

## Notes

- Prefer `--time` for “what is happening around here?”.
- Use a `.jpg` for quick share; use `.png` for crisp UI frames.
