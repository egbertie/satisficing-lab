---
# 知识元数据 (5标准化)
knowledge_id: W14-D5EBBC
title: SKILL: 会议管理
category: 11_Skill文档
source: skills/.archive_weekly-meeting/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 872
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL: 会议管理

> **知识ID**: W14-D5EBBC  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_weekly-meeting/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# SKILL: 会议管理

> 技能包：内部会议机制建立与执行
> 路径: skills/weekly-meeting/

---

## 功能概述

本技能负责满意解研究所内部会议机制的创建、管理和执行，包括：
- 晨会/周会/月度复盘的组织与记录
- 会议议程和纪要的生成
- 行动项跟踪与提醒

---

## 使用方法

### 发起晨会
```
请发起今日晨会
```
→ 自动生成晨会记录模板，收集各角色昨日完成/今日计划

### 组织周会
```
请准备本周周会
```
→ 生成周会议程，汇总本周数据，准备讨论要点

### 月度复盘
```
启动月度复盘
```
→ 生成月度复盘模板，整理KPT分析框架

### 会议记录
```
记录周会纪要：[粘贴会议内容]
```
→ 整理结构化纪要，提取行动项

---

## 依赖文件

| 文件 | 用途 |
|------|------|
| `MEETING_PROTOCOL.md` | 会议机制主文档 |
| `templates/weekly-meeting.md` | 周会模板 |
| `templates/monthly-retro.md` | 月度复盘模板 |
| `templates/adhoc-meeting.md` | 专题会模板 |
| `templates/notion-meeting-template.md` | Notion数据库模板 |

---

## 输出规范

- 晨会记录 → `memory/YYYY-MM-DD.md`
- 周会记录 → `memory/YYYY-MM-DD-weekly.md`
- 月度复盘 → `memory/YYYY-MM-monthly.md`
- 专题会记录 → `memory/YYYY-MM-DD-adhoc-[topic].md`

---

## 维护者

- 主维护：满意妞
- 审批：Egbertie

---

*技能版本: v1.0*  
*创建时间: 2026-03-13*
