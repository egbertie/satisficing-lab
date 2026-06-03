---
# 知识元数据 (5标准化)
knowledge_id: W8-1DDAC7
title: 自主执行系统 Scripts
category: 11_Skill文档
source: skills/.archive_autonomous-execution-system/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 338
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 自主执行系统 Scripts

> **知识ID**: W8-1DDAC7  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_autonomous-execution-system/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 自主执行系统 Scripts

## 脚本说明

### autonomous-execution-system-runner.py
自主执行系统主执行脚本。

## 功能

- execute
- monitor
- report

## 使用方法

```bash
# 执行功能
python3 autonomous-execution-system-runner.py run --feature execute

# 查看状态
python3 autonomous-execution-system-runner.py status

# 生成报告
python3 autonomous-execution-system-runner.py report
```
