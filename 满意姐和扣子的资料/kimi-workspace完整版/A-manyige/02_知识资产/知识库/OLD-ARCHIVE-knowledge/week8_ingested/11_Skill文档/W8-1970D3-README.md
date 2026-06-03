---
# 知识元数据 (5标准化)
knowledge_id: W8-1970D3
title: B站字幕下载 Scripts
category: 11_Skill文档
source: skills/.archive_bilibili-subtitle-download-skill/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 361
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# B站字幕下载 Scripts

> **知识ID**: W8-1970D3  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_bilibili-subtitle-download-skill/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# B站字幕下载 Scripts

## 脚本说明

### bilibili-subtitle-download-skill-runner.py
B站字幕下载主执行脚本。

## 功能

- download
- extract
- convert

## 使用方法

```bash
# 执行功能
python3 bilibili-subtitle-download-skill-runner.py run --feature download

# 查看状态
python3 bilibili-subtitle-download-skill-runner.py status

# 生成报告
python3 bilibili-subtitle-download-skill-runner.py report
```
