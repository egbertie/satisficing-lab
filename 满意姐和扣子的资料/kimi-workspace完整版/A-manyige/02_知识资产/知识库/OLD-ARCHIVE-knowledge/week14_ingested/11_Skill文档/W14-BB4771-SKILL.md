---
# 知识元数据 (5标准化)
knowledge_id: W14-BB4771
title: User Conversation Reservation Skill
category: 11_Skill文档
source: skills/.archive_user-conversation-reservation/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 492
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# User Conversation Reservation Skill

> **知识ID**: W14-BB4771  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_user-conversation-reservation/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# User Conversation Reservation Skill

## Purpose
永远预留一个子代理槽位保持与用户对话的能力

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 监控所有子代理使用，确保用户对话优先级 |
| 系统考虑 | 检测→预留→分配→释放→恢复闭环 |
| 迭代机制 | 根据用户活跃度调整预留策略 |
| Skill化 | 标准化接口：monitor/reserve/release/report |
| 自动化 | 实时监控，自动预留和释放 |

## Commands
- `monitor` - 监控用户活跃度
- `reserve` - 预留子代理槽位
- `release` - 释放预留槽位
- `report` - 生成预留状态报告

## Rules
- 用户活跃时：自动预留1个槽位，暂停后台子代理启动
- 用户空闲时：释放预留，恢复后台任务
- 最大并发从8降至7，确保用户通道
