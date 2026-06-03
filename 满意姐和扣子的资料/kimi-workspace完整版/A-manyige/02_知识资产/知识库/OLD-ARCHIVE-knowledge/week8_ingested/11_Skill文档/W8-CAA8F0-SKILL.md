---
# 知识元数据 (5标准化)
knowledge_id: W8-CAA8F0
title: Claude Code Skill
category: 11_Skill文档
source: skills/.archive_claude-code/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 832
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Claude Code Skill

> **知识ID**: W8-CAA8F0  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_claude-code/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: claude-code
description: 调用Claude API进行代码生成、调试和深度分析。免费额度内使用，需要时再付费。
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["CLAUDE_API_KEY"] },
        "emoji": "🧠",
      },
  }

# Claude Code Skill

利用Claude 3.5 Sonnet API进行编程和深度分析。

## 使用前提

需要设置环境变量：
```bash
export CLAUDE_API_KEY=sk-ant-apixx-xxxxxxxx
```

## 使用策略（免费优先）

### 阶段1：免费额度内使用（当前）
- 新用户通常有$5-10免费额度
- 完成联调测试
- 评估实际需求量

### 阶段2：按需付费（轻量使用）
- 如果每月 < $10，直接API按量付费
- 无需$20订阅

### 阶段3：订阅模式（重度使用）
- 如果每月 > $15，订阅Claude Code $20/月

## 功能

### 1. 代码生成
复杂算法、架构设计、完整项目

### 2. 代码调试
错误分析、性能优化、重构建议

### 3. 深度分析
长文本理解、多文档对比、趋势分析

## 与Kimi对比使用

| 场景 | 首选 | 原因 |
|------|------|------|
| 中文场景 | Kimi | 中文理解更强 |
| 复杂编程 | Claude | 代码能力更强 |
| 紧急调试 | 看额度 | 哪个有额度用哪个 |
| 长文本分析 | Claude | 逻辑推理更强 |

## 成本控制

- 每次调用前评估必要性
- 批量处理，减少调用次数
- 结果保存复用
- 监控用量，接近限额时切换Kimi
