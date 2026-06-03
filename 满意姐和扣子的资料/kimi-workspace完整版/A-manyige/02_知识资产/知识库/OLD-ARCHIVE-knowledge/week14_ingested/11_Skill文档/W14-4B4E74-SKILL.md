---
# 知识元数据 (5标准化)
knowledge_id: W14-4B4E74
title: Unified Git Suite
category: 11_Skill文档
source: skills/.archive_unified-git-suite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1219
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Unified Git Suite

> **知识ID**: W14-4B4E74  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_unified-git-suite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: unified-git-suite
description: Unified Git and GitHub management suite. Replaces git, git-essentials, github with single integrated interface. Use for: repository management, code review automation, CI/CD integration, branch strategy, release management.
triggers: ["git", "github", "repository", "commit", "branch", "pull request", "代码"]
---

# Unified Git Suite

**统一Git/GitHub管理套件** - 整合代码版本控制和协作平台操作。

> 🎯 替代: git + git-essentials + github

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **仓库管理** | 克隆、初始化、配置、清理 |
| **工作流自动化** | PR模板、代码审查、合并策略 |
| **CI/CD集成** | GitHub Actions、自动化部署 |
| **团队协作** | 分支策略、代码审查清单 |
| **发布管理** | 版本标签、Release笔记、Changelog |

---

## 快速开始

```bash
# 仓库初始化
git-suite repo init --name "my-project" --template python

# 创建PR
git-suite pr create --title "Fix bug" --branch feature/fix --base main

# 代码审查
git-suite review --pr 123 --checklist security,performance

# 发布版本
git-suite release --version v1.0.0 --notes "Release notes..."

# 批量操作
git-suite batch --repos "org/*" --command "git pull"
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| git | `git-suite git` |
| git-essentials | `git-suite essentials` |
| github | `git-suite github` |

---

**自建替代计数**: +3
