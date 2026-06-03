---
# 知识元数据 (5标准化)
knowledge_id: W12-111CB5
title: Overdue Task Rescuer Skill
category: 11_Skill文档
source: skills/.archive_overdue-task-rescuer/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 411
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Overdue Task Rescuer Skill

> **知识ID**: W12-111CB5  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_overdue-task-rescuer/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Overdue Task Rescuer Skill

## Purpose
自动检测逾期任务并执行补救

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖所有任务的逾期检测与补救 |
| 系统考虑 | 扫描→评估→补救→验证→根因分析闭环 |
| 迭代机制 | 补救后分析根因，优化预防机制 |
| Skill化 | 标准化接口：scan/assess/rescue/verify/analyze |
| 自动化 | 每日扫描逾期任务，自动触发补救 |

## Commands
- `scan` - 扫描逾期任务
- `assess` - 评估补救方案
- `rescue` - 执行补救
- `verify` - 验证补救结果
- `analyze` - 根因分析
