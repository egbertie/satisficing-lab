---
# 知识元数据 (5标准化)
knowledge_id: W9-6924A2
title: 钉钉飞书集成 Scripts
category: 11_Skill文档
source: skills/.archive_dingtalk-feishu-cn/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 296
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 钉钉飞书集成 Scripts

> **知识ID**: W9-6924A2  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_dingtalk-feishu-cn/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 钉钉飞书集成 Scripts

## 脚本说明

### dingtalk-feishu-cn-runner.py
钉钉飞书集成主执行脚本。

## 功能

- sync
- notify
- message

## 使用方法

```bash
# 执行功能
python3 dingtalk-feishu-cn-runner.py run --feature sync

# 查看状态
python3 dingtalk-feishu-cn-runner.py status

# 生成报告
python3 dingtalk-feishu-cn-runner.py report
```
