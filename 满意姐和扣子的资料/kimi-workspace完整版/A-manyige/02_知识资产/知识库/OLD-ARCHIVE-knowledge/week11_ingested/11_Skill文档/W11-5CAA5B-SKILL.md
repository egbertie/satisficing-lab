---
# 知识元数据 (5标准化)
knowledge_id: W11-5CAA5B
title: SKILL
category: 11_Skill文档
source: skills/.archive_kimi-cli-task-manager/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2248
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

> **知识ID**: W11-5CAA5B  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_kimi-cli-task-manager/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: kimi-cli-task-manager
version: 1.0.0
description: |
  Kimi CLI任务管理器 - PTY模式执行、速率限制处理、任务队列管理
  复杂代码任务的自动化执行与监控
author: Satisficing Institute
tags:
  - kimi
  - cli
  - task-management
  - automation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["kimi"]
  - cron: true
---

# 🤖 Kimi CLI Task Manager V1.0.0

## 🎯 功能概述

管理Kimi CLI复杂代码任务的执行，处理PTY模式、速率限制和任务队列。

### 核心功能
1. **任务队列管理** - 批量任务排队执行
2. **速率限制处理** - 429错误自动处理
3. **执行监控** - 实时跟踪任务状态
4. **结果收集** - 自动汇总执行结果

## 📋 标准1: 全局考虑

### 任务类型
| 类型 | 描述 | 超时 |
|------|------|------|
| quick | 快速任务 | 5分钟 |
| medium | 中等复杂度 | 10分钟 |
| complex | 复杂任务 | 30分钟 |
| interactive | 交互模式 | 无限制 |

### 429处理策略
1. 识别: 日志中包含`429`或`rate_limit_error`
2. 停止: 短时间重复调用只会继续失败
3. 等待: 60分钟后恢复
4. 记录: 标注任务为`blocked_by_rate_limit`
5. 补跑: 配额恢复后优先执行

## ⚙️ 标准2: 系统考虑

### 任务执行流程
```
接收任务 → 排队 → PTY执行 → 监控 → 完成 → 记录结果
```

### 错误处理
- 超时自动终止
- 429错误标记等待
- 失败任务重试(最多2次)
- 异常结果收集

## 🔄 标准3: 迭代机制

### 版本计划
```
V1.0: 基础任务队列管理
  ↓
V1.1: 智能超时调整
  ↓
V2.0: 多Kimi实例负载均衡
```

## 📦 标准4: Skill化

### 目录结构
```
skills/kimi-cli-task-manager/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── task_queue.py          # 任务队列管理
│   ├── execute_task.sh        # 任务执行
│   ├── monitor.py             # 执行监控
│   └── rate_limit_handler.py  # 429处理
├── tasks/
│   ├── pending/               # 待处理任务
│   ├── running/               # 运行中任务
│   ├── completed/             # 已完成任务
│   └── failed/                # 失败任务
└── cron/
    └── hourly_check.json      # 每小时检查
```

### 命令接口
```bash
# 添加任务到队列
./scripts/task_queue.py add [task-file]

# 执行任务
./scripts/execute_task.sh [task-id]

# 监控状态
./scripts/monitor.py status

# 处理429等待队列
./scripts/rate_limit_handler.py process
```

## 🤖 标准5: 流程自动化

### 定时任务
- **每小时**: 检查并恢复被阻塞的任务
- **每15分钟**: 清理超时任务

### 自动响应
- 429错误自动暂停队列
- 超时任务自动标记失败
- 配额恢复后自动补跑

## 🚀 使用方法

### 添加任务
```bash
# 创建任务文件
cat > tasks/pending/task_001.json << 'EOF'
{
  "id": "task_001",
  "type": "complex",
  "prompt": "创建一个React应用...",
  "workdir": "/tmp/project",
  "timeout": 600
}
EOF

./scripts/task_queue.py add tasks/pending/task_001.json
```

### 查看状态
```bash
./scripts/monitor.py status
```

## ⚠️ 前置要求

- 已安装: `pip install kimi-cli`
- 已登录: `kimi /login`
- PTY模式需要支持

---
*版本: v1.0.0 | 创建: 2026-03-20*
