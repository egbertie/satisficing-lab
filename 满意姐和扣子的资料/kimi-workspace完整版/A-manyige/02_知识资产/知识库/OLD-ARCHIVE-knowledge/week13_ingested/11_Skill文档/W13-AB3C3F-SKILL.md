---
# 知识元数据 (5标准化)
knowledge_id: W13-AB3C3F
title: SKILL
category: 11_Skill文档
source: skills/.archive_subagent-dual-review/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 751
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W13-AB3C3F  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_subagent-dual-review/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: subagent-dual-review
version: 1.0.0
description: |
  子代理双审机制 - 规格审查 + 代码质量审查双阶段审查
  核心价值：自动化双审、问题分级、修复追踪
  适用：子代理输出审查、代码审查、质量保证
author: OpenClaw
tags:
  - subagent
  - dual-review
  - quality
  - audit
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "git"]
  - cron: false
---

# 子代理双审 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 双阶段全覆盖
2. **系统**: 审查 → 分级 → 修复 → 验证闭环
3. **迭代**: PDCA优化审查标准
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 自动触发双审流程

## 双审阶段

| 阶段 | 审查内容 | 严重度 |
|------|----------|--------|
| 规格审查 | 是否符合规格要求 | Critical/Important/Minor |
| 质量审查 | DRY/YAGNI/命名/错误处理 | Critical/Important/Minor |

## 严重度处理

| 严重度 | 行动 |
|--------|------|
| Critical | 阻塞下一任务 |
| Important | 修复后继续 |
| Minor | 记录稍后处理 |

---

*5标准全部满足*
