---
# 知识元数据 (5标准化)
knowledge_id: W12-5C4DDD
title: SKILL
category: 11_Skill文档
source: skills/.archive_obsidian-archiver/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 628
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W12-5C4DDD  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_obsidian-archiver/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: obsidian-archiver
version: 1.0.0
description: |
  Obsidian笔记自动归档机制 - 自动整理和归档旧笔记
  核心价值：自动分类、过期清理、链接维护
  适用：知识库整理、笔记归档、空间优化
author: OpenClaw
tags:
  - obsidian
  - archive
  - notes
  - automation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "obsidian-cli"]
  - cron: true
---

# Obsidian笔记自动归档 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 全Vault扫描 + 多维度归档策略
2. **系统**: 完整归档流程 + 安全备份
3. **迭代**: PDCA持续优化归档规则
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 定时归档 + 链接修复

## 定时任务

```bash
# 每日凌晨归档
0 2 * * * ./scripts/archive_old_notes.py

# 每周链接检查
0 3 * * 0 ./scripts/fix_broken_links.py
```

---

*5标准全部满足*
