---
# 知识元数据 (5标准化)
knowledge_id: W11-EA1B39
title: GitHub Models Skill
category: 11_Skill文档
source: skills/.archive_github-models/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 924
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# GitHub Models Skill

> **知识ID**: W11-EA1B39  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_github-models/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: github-models
description: 使用GitHub Models免费调用GPT-4o等主流AI模型。完全免费，替代Claude Code。
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["GITHUB_TOKEN"] },
        "emoji": "🐙",
      },
  }

# GitHub Models Skill

利用GitHub Token免费使用GPT-4o等模型。

## 使用前提

需要设置环境变量：
```bash
export GITHUB_TOKEN=ghp_xxxxxxxx
```

## 模型列表

| 模型 | 能力 | 用途 |
|------|------|------|
| **gpt-4o** | 最强通用 | 复杂编程、深度分析 |
| **gpt-4o-mini** | 快速轻量 | 简单任务、快速响应 |
| **Meta-Llama-3.1-405B** | 开源大模型 | 长文本处理 |
| **Mistral-large** | 欧洲模型 | 多语言任务 |

## 免费额度

-  generous免费额度（具体数量GitHub管理）
- 日常使用足够
- 超出后需等待或付费

## 与Claude对比

| 场景 | 首选 | 原因 |
|------|------|------|
| 复杂编程 | GitHub Models (GPT-4o) | 代码能力强 |
| 中文场景 | Kimi | 中文理解更强 |
| 快速响应 | GPT-4o-mini | 速度快 |
| 长文本 | Llama 3.1 | 上下文长 |

## 使用策略

1. **优先使用**：GPT-4o（综合能力最强）
2. **快速任务**：GPT-4o-mini（省额度）
3. **中文任务**：Kimi（中文更强）
4. **混合使用**：根据任务选择最优模型

## 成本控制

- 完全免费（在额度内）
- 无需订阅
- 无需额外付费
