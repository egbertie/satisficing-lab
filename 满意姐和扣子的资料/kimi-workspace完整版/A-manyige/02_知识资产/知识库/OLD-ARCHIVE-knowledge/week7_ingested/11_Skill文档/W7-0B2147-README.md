---
# 知识元数据 (5标准化)
knowledge_id: W7-0B2147
title: ActiveCampaign CRM集成 Scripts
category: 11_Skill文档
source: skills/.archive_activecampaign/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 326
week: 7
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# ActiveCampaign CRM集成 Scripts

> **知识ID**: W7-0B2147  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_activecampaign/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# ActiveCampaign CRM集成 Scripts

## 脚本说明

### activecampaign-runner.py
ActiveCampaign CRM集成主执行脚本。

## 功能

- contacts
- deals
- tags
- automations

## 使用方法

```bash
# 执行功能
python3 activecampaign-runner.py run --feature contacts

# 查看状态
python3 activecampaign-runner.py status

# 生成报告
python3 activecampaign-runner.py report
```
