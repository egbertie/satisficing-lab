---
# 知识元数据 (5标准化)
knowledge_id: W11-552BA3
title: SKILL
category: 11_Skill文档
source: skills/.archive_git-workflow-auto/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2374
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W11-552BA3  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_git-workflow-auto/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: git-workflow-auto
version: 1.0.0
description: |
  Git工作流自动化 - 分支管理、提交自动化、清理工作流
  规范Git操作，减少重复工作
author: Satisficing Institute
tags:
  - git
  - workflow
  - automation
  - version-control
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["git"]
  - cron: true
---

# 🌳 Git Workflow Automation V1.0.0

## 🎯 功能概述

自动化Git工作流程，包括分支管理、提交规范、定期清理等操作。

### 核心功能
1. **特性分支工作流** - 创建→开发→PR→合并→清理
2. **提交规范化** - 自动格式化提交信息
3. **定期清理** - 删除已合并分支、清理旧stash
4. **同步检查** - 检测落后/领先的提交

## 📋 标准1: 全局考虑

### 支持的工作流
| 工作流 | 描述 | 触发条件 |
|--------|------|----------|
| feature-branch | 特性分支标准流程 | 手动/脚本 |
| hotfix | 热修复快速流程 | 紧急触发 |
| sync-fork | 同步上游仓库 | 定时检查 |
| cleanup | 清理已合并分支 | 每日定时 |

### 分支命名规范
- 特性分支: `feature/description`
- 修复分支: `fix/issue-description`
- 热修复: `hotfix/critical-fix`
- 发布分支: `release/v1.x.x`

## ⚙️ 标准2: 系统考虑

### 特性分支流程
```
创建分支 → 开发 → 提交 → 推送 → PR → 合并 → 清理
```

### 安全检查
- ✅ 禁止直接在main分支修改
- ✅ 强制pull前检查
- ✅ 合并前状态验证
- ✅ 删除分支前确认已合并

## 🔄 标准3: 迭代机制

### 版本计划
```
V1.0: 基础工作流脚本
  ↓
V1.1: 提交信息模板
  ↓
V2.0: 智能分支管理 + 冲突预警
```

## 📦 标准4: Skill化

### 目录结构
```
skills/git-workflow-auto/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── feature_workflow.sh     # 特性分支工作流
│   ├── hotfix_workflow.sh      # 热修复工作流
│   ├── sync_upstream.sh        # 同步上游
│   ├── cleanup.sh              # 清理脚本
│   └── commit_helper.sh        # 提交助手
├── templates/
│   └── commit_template.txt     # 提交信息模板
└── cron/
    └── daily_cleanup.json      # 每日清理定时任务
```

### 命令接口
```bash
# 特性分支工作流
./scripts/feature_workflow.sh start [feature-name]
./scripts/feature_workflow.sh finish

# 清理工作
./scripts/cleanup.sh [--dry-run]

# 提交助手
./scripts/commit_helper.sh [type] [message]
# type: feat|fix|docs|style|refactor|test|chore
```

## 🤖 标准5: 流程自动化

### 定时任务
- **每日清理**: 每天 02:00 执行分支清理
- **每周同步**: 每周一 09:00 检查上游更新

### 自动操作
- 自动检测并删除已合并的本地/远程分支
- 自动清理超过30天的stash
- 自动同步fork仓库

## 🚀 使用方法

### 启动特性开发
```bash
./scripts/feature_workflow.sh start user-authentication
# 自动执行: git checkout -b feature/user-authentication
```

### 完成特性开发
```bash
./scripts/feature_workflow.sh finish
# 自动执行: push → PR提示 → 合并后清理
```

### 规范提交
```bash
./scripts/commit_helper.sh feat "add user login"
# 生成: feat: add user login
```

### 定期清理
```bash
./scripts/cleanup.sh
# 清理已合并分支、旧stash、无效远程引用
```

## ⚠️ 安全提示

- 执行前会自动检查当前分支状态
- 清理操作有 `--dry-run` 预览模式
- 强制推送需要显式确认

---
*版本: v1.0.0 | 创建: 2026-03-20*
