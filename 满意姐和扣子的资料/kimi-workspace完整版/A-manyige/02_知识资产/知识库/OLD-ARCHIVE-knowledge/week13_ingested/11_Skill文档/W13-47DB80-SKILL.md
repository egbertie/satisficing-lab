---
# 知识元数据 (5标准化)
knowledge_id: W13-47DB80
title: SKILL
category: 11_Skill文档
source: skills/.archive_tdd-compliance-checker/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 682
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

> **知识ID**: W13-47DB80  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_tdd-compliance-checker/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: tdd-compliance-checker
version: 1.0.0
description: |
  TDD合规性检查机制 - 验证开发流程是否遵循测试驱动开发
  核心价值：自动检查TDD流程、生成合规报告、违规预警
  适用：代码审查、流程审计、质量保证
author: OpenClaw
tags:
  - tdd
  - compliance
  - checker
  - quality
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "git"]
  - cron: true
---

# TDD合规检查 Skill V1.0.0

## 标准1-5: 5标准满足

1. **全局**: 全提交历史检查
2. **系统**: 检查 → 报告 → 改进闭环
3. **迭代**: PDCA优化检查规则
4. **Skill化**: 标准结构 + CLI接口
5. **自动化**: 定时检查 + 提交前钩子

## 检查维度

| 检查项 | 说明 | 风险等级 |
|--------|------|----------|
| 先测后码 | 测试提交早于实现 | 高 |
| 测试覆盖 | 新功能必有测试 | 高 |
| 小步提交 | 每次绿测试后提交 | 中 |

## 定时任务

```bash
# 每日合规检查
0 18 * * * ./scripts/check_tdd.py
```

---

*5标准全部满足*
