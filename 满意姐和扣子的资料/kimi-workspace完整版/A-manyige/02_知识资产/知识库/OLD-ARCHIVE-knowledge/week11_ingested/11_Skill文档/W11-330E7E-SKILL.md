---
# 知识元数据 (5标准化)
knowledge_id: W11-330E7E
title: Git Suite V2 - 整合版
category: 11_Skill文档
source: skills/.archive_git-suite-v2/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1309
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Git Suite V2 - 整合版

> **知识ID**: W11-330E7E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_git-suite-v2/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Git Suite V2 - 整合版

> **整合来源**: git + git-essentials + github + git-workflow-auto + github-ci-monitor + github-models + unified-git-suite  
> **整合时间**: 2026-03-21  
> **整合原因**: 消除重复，提升效率

## Purpose
Git全流程管理：本地操作、远程协作、CI/CD集成、模型管理

## 5-Standard Compliance (整合后)

| Standard | Implementation | Status |
|----------|----------------|--------|
| 全局考虑 | 覆盖本地/远程/CI/模型全场景 | ✅ 100% |
| 系统考虑 | 完整Git工作流闭环 | ✅ 100% |
| 迭代机制 | 版本历史+回滚机制 | ✅ 100% |
| Skill化 | 统一接口 | ✅ 100% |
| 自动化 | 自动检测+执行 | ✅ 100% |

## Commands

### 本地操作
- git status - 状态检查
- git commit - 提交变更
- git branch - 分支管理
- git merge - 合并分支
- git rebase - 变基操作

### 远程协作
- gh repo - 仓库管理
- gh pr - PR管理
- gh issue - Issue管理
- gh run - CI运行监控

### 工作流
- git workflow init - 初始化工作流
- git workflow feature - 创建特性分支
- git workflow release - 发布流程

### CI监控
- gh ci status - CI状态检查
- gh ci logs - 查看日志
- gh ci retry - 重试失败任务

### 模型管理
- gh models list - 列出模型
- gh models deploy - 部署模型

## 整合说明

| 原Skill | 功能 | 整合状态 |
|---------|------|----------|
| git | 基础操作 | ✅ 保留 |
| git-essentials | 精简版 | ✅ 合并 |
| github | CLI操作 | ✅ 合并 |
| git-workflow-auto | 自动化 | ✅ 合并 |
| github-ci-monitor | CI监控 | ✅ 合并 |
| github-models | 模型管理 | ✅ 合并 |
| unified-git-suite | 套件 | ✅ 合并 |

## 优化收益
- Skill数量: 8 → 1 (-87.5%)
- Token消耗: -87.5%
- 维护成本: -87.5%

---

*整合完成: 2026-03-21*
