---
# 知识元数据 (5标准化)
knowledge_id: W11-2E83BF
title: SKILL
category: 11_Skill文档
source: skills/.archive_github-ci-monitor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2169
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

> **知识ID**: W11-2E83BF  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_github-ci-monitor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: github-ci-monitor
version: 1.0.0
description: |
  GitHub CI监控器 - PR状态检查、工作流监控、API查询
  持续集成状态实时监控与告警
author: Satisficing Institute
tags:
  - github
  - ci-cd
  - monitoring
  - automation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["gh"]
  - cron: true
---

# 🔍 GitHub CI Monitor V1.0.0

## 🎯 功能概述

监控GitHub仓库的持续集成状态，包括PR检查、工作流运行状态和高级API查询。

### 核心功能
1. **PR状态监控** - 检查CI状态、审查状态
2. **工作流监控** - 列出一览、查看失败步骤
3. **API查询** - 高级数据获取和JSON处理
4. **告警通知** - 失败时自动报告

## 📋 标准1: 全局考虑

### 监控范围
| 检查项 | 描述 | 优先级 |
|--------|------|--------|
| PR CI状态 | 检查通过/失败 | P0 |
| 工作流运行 | 最近执行状态 | P0 |
| 失败日志 | 提取失败步骤日志 | P1 |
| API字段查询 | 自定义数据提取 | P2 |

### 支持的监控对象
- Pull Requests
- GitHub Actions工作流
- Issues状态
- 仓库API端点

## ⚙️ 标准2: 系统考虑

### 监控流程
```
定时触发 → 获取CI状态 → 分析结果
  → 发现问题 → 生成报告 → 通知相关人员
```

### 告警规则
- CI失败立即告警
- 工作流连续失败2次告警
- PR审查超期提醒

## 🔄 标准3: 迭代机制

### 版本计划
```
V1.0: 基础CI状态检查
  ↓
V1.1: 智能告警（减少误报）
  ↓
V2.0: 自动重试失败工作流
```

## 📦 标准4: Skill化

### 目录结构
```
skills/github-ci-monitor/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── ci_check.sh            # CI状态检查
│   ├── workflow_monitor.sh    # 工作流监控
│   ├── pr_status.sh           # PR状态查询
│   └── api_query.sh           # API查询工具
├── config/
│   └── repos.yaml             # 仓库配置
└── cron/
    └── ci_check.json          # 定时检查配置
```

### 命令接口
```bash
# 检查PR的CI状态
./scripts/pr_status.sh [owner/repo] [pr-number]

# 监控工作流
./scripts/workflow_monitor.sh [owner/repo] [--failed-only]

# 查询API
./scripts/api_query.sh [owner/repo] [endpoint] [jq-filter]

# 完整CI检查
./scripts/ci_check.sh [owner/repo]
```

## 🤖 标准5: 流程自动化

### 定时配置
- **频率**: 每15分钟
- **监控时间**: 工作日 09:00-21:00
- **告警方式**: 控制台输出 + 可选消息通知

### 自动响应
- 检测到CI失败时立即报告
- 收集失败日志便于排查

## 🚀 使用方法

### 检查PR状态
```bash
./scripts/pr_status.sh owner/repo 55
```

### 监控工作流
```bash
./scripts/workflow_monitor.sh owner/repo --failed-only
```

### API查询示例
```bash
# 获取PR标题和状态
./scripts/api_query.sh owner/repo pulls/55 '.title, .state, .user.login'

# 获取最近issues
./scripts/api_query.sh owner/repo issues --jq '.[] | "\(.number): \(.title)"'
```

## ⚠️ 前置要求

- 安装 GitHub CLI: `gh`
- 已登录: `gh auth login`
- 有仓库访问权限

---
*版本: v1.0.0 | 创建: 2026-03-20*
