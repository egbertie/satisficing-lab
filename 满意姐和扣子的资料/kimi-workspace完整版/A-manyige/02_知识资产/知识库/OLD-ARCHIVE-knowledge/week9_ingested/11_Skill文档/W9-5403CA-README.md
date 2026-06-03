---
# 知识元数据 (5标准化)
knowledge_id: W9-5403CA
title: 内容一致性治理 Scripts
category: 11_Skill文档
source: skills/.archive_content-consistency-governance/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 348
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 内容一致性治理 Scripts

> **知识ID**: W9-5403CA  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_content-consistency-governance/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 内容一致性治理 Scripts

## 脚本说明

### content-consistency-governance-runner.py
内容一致性治理主执行脚本。

## 功能

- check
- enforce
- report

## 使用方法

```bash
# 执行功能
python3 content-consistency-governance-runner.py run --feature check

# 查看状态
python3 content-consistency-governance-runner.py status

# 生成报告
python3 content-consistency-governance-runner.py report
```
