---
# 知识元数据 (5标准化)
knowledge_id: W11-C3854B
title: Maintenance Scheduler Skill
category: 11_Skill文档
source: skills/.archive_maintenance-scheduler/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 505
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Maintenance Scheduler Skill

> **知识ID**: W11-C3854B  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_maintenance-scheduler/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Maintenance Scheduler Skill

## Purpose
管理所有持续维护任务：案例库扩充、政策跟踪、问卷迭代、角色升级

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖所有MAINT-xxx持续维护任务 |
| 系统考虑 | 计划→执行→验证→报告→优化闭环 |
| 迭代机制 | 根据执行效果调整维护频率和策略 |
| Skill化 | 标准化接口：schedule/execute/verify/report |
| 自动化 | 按计划自动触发维护任务 |

## Maintenance Tasks
- MAINT-001: 案例库扩充（持续）
- MAINT-002: 政府补贴政策跟踪（每季度）
- MAINT-003: 问卷模板迭代（持续）
- MAINT-004: 角色档案升级（按需）

## Schedule
- 案例库: 每周检查
- 政策跟踪: 每季度更新
- 问卷迭代: 每次使用后
- 角色升级: 按需触发
