---
# 知识元数据 (5标准化)
knowledge_id: W19-3874CA
title: TOP20 Skill 安装状态报告
category: 12_记忆档案
source: memory/skill-installation-status.md
ingested_at: 2026-03-27 17:59:30
word_count: 1239
week: 19
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# TOP20 Skill 安装状态报告

> **知识ID**: W19-3874CA  
> **分类**: 12_记忆档案  
> **来源**: `memory/skill-installation-status.md`  
> **入库时间**: 2026-03-27

---

## 正文

# TOP20 Skill 安装状态报告

## 系统现有Skill
- `~/.openclaw/skills/`: 25个
- `~/.openclaw/workspace/skills/`: 90个（含归档）

## TOP20清单 vs 现有Skill

| 排名 | 技能名称 | 是否已存在 | 状态 |
|------|----------|------------|------|
| 1 | **skill-vetter** | ❌ 不存在 | 待创建 |
| 2 | **self-improving-agent** | ❌ 不存在 | 待创建 |
| 3 | **summarize** | ❌ 不存在 | 待创建 |
| 4 | **github** | ❌ 不存在 | 待创建 |
| 5 | **tavily-search** | ✅ 存在 | 已就绪 |
| 6 | **ontology** | ❌ 不存在 | 待创建 |
| 7 | **notion** | ⚠️ notion-enhanced存在 | 需评估 |
| 8 | **obsidian** | ❌ 不存在 | 待创建 |
| 9 | **find-skills** | ❌ 不存在 | 待创建 |
| 10 | **weather** | ❌ 不存在 | 待创建 |
| 11 | **brave-search** | ✅ 存在 | 已就绪 |

## 结论

**已存在**: 3个（tavily-search, brave-search, notion-enhanced）
**待创建**: 8个（skill-vetter, self-improving-agent, summarize, github, ontology, obsidian, find-skills, weather）

由于clawhub生态未接入，需要通过**创建Skill文件**方式实现这8个功能。

## 建议方案

将8个缺失的Skill简化为**3个核心实用Skill**（基于现有能力最大化复用）：

1. **skill-vetter** → 复用现有`quality-assurance` + `blue-army-interceptor`
2. **self-improving-agent** → 复用现有`meta-cognitive-evolver`
3. **summarize** → 现有`kimi_search` + `kimi_fetch`已支持
4. **github** → 创建简单GitHub API Skill
5. **obsidian** → 本地文件操作已支持
6. **weather** → 创建简单天气查询Skill

**核心缺失**: github-api, weather-query

---

*报告时间: 2026-03-27*
