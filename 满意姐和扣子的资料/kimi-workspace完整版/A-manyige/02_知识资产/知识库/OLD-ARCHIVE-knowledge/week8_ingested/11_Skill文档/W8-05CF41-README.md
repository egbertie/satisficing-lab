---
# 知识元数据 (5标准化)
knowledge_id: W8-05CF41
title: 客户画像模拟器 Scripts
category: 11_Skill文档
source: skills/.archive_client-persona-simulator/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 331
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 客户画像模拟器 Scripts

> **知识ID**: W8-05CF41  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_client-persona-simulator/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 客户画像模拟器 Scripts

## 脚本说明

### client-persona-simulator-runner.py
客户画像模拟器主执行脚本。

## 功能

- simulate
- analyze
- predict

## 使用方法

```bash
# 执行功能
python3 client-persona-simulator-runner.py run --feature simulate

# 查看状态
python3 client-persona-simulator-runner.py status

# 生成报告
python3 client-persona-simulator-runner.py report
```
