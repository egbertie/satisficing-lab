---
# 知识元数据 (5标准化)
knowledge_id: W9-49E27D
title: Cron优化管理器 Scripts
category: 11_Skill文档
source: skills/.archive_cron-optimization-manager/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 334
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Cron优化管理器 Scripts

> **知识ID**: W9-49E27D  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_cron-optimization-manager/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Cron优化管理器 Scripts

## 脚本说明

### cron-optimization-manager-runner.py
Cron优化管理器主执行脚本。

## 功能

- merge
- analyze
- optimize

## 使用方法

```bash
# 执行功能
python3 cron-optimization-manager-runner.py run --feature merge

# 查看状态
python3 cron-optimization-manager-runner.py status

# 生成报告
python3 cron-optimization-manager-runner.py report
```
