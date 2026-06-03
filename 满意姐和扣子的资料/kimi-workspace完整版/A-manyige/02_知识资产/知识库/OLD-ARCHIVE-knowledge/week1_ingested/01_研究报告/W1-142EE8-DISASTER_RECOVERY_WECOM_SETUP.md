---
knowledge_id: W1-142EE8
title: 灾备企微通道配置指南
category: 01_研究报告
source: docs/DISASTER_RECOVERY_WECOM_SETUP.md
ingested_at: 2026-03-27T17:44:51.277365
word_count: 8374
---

# 灾备企微通道配置指南

**知识ID**: W1-142EE8  
**分类**: 01_研究报告  
**原始路径**: docs/DISASTER_RECOVERY_WECOM_SETUP.md

---

# 灾备企微通道配置指南

> **文档版本**: 1.0  
> **创建时间**: 2026-03-21  
> **维护责任人**: 满意妞 (AI助手)

---

## 📋 目录

1. [概述](#1-概述)
2. [快速开始](#2-快速开始)
3. [配置文件详解](#3-配置文件详解)
4. [使用方法](#4-使用方法)
5. [通知模板](#5-通知模板)
6. [与灾备系统整合](#6-与灾备系统整合)
7. [7层备份流程集成](#7-7层备份流程集成)
8. [常见问题](#8-常见问题)
9. [待配置项](#9-待配置项)

---

## 1. 概述

灾备企微通道是在现有7层灾备体系基础上，增加的企业微信实时告警通知系统。当系统发生异常时，能够第一时间通过企微群聊通知相关人员。

### 1.1 功能特性

| 特性 | 说明 |
|------|------|
| 多级告警 | P0/P1/P2/P3 四级告警级别 |
| 模板通知 | 预设10种通知模板 |
| Webhook 分组 | 系统/灾备/安全/任务 四组通知 |
| 灵活调用 | 支持命令行和脚本集成 |
| 限流保护 | 防止通知轰炸 |

### 1.2 告警级别

| 级别 | 名称 | 响应时间 | 颜色 | @所有人 |
|------|------|---------|------|---------|
| P0 | 紧急 | 立即 | 🔴 红色 | 是 |
| P1 | 高优先级 | 1小时内 | 🟠 橙色 | 否 |
| P2 | 中等优先级 | 4小时内 | 🟡 黄色 | 否 |
| P3 | 低优先级 | 24小时内 | 🔵 蓝色 | 否 |

---

## 2. 快速开始

### 2.1 创建企微机器人

1. 在企微群聊中，点击右上角「...」→「添加群机器人」
2. 选择「新建机器人」，输入机器人名称（如：系统告警机器人）
3. 复制 Webhook URL，提取 key 参数

示例 Webhook URL：
```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 2.2 配置 Webhook

编辑配置文件 `skills/disaster-recovery-wecom/config.yaml`：

```yaml
webhooks:
  system_alerts:
    name: "系统告警通知群"
    url: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_ACTUAL_KEY"
    enabled: true
```

将 `YOUR_ACTUAL_KEY` 替换为实际的 key 值。

### 2.3 测试配置

```bash
# 发送测试消息
./scripts/emergency-wecom-alert.sh test "这是一条测试消息"
```

---

## 3. 配置文件详解

### 3.1 文件位置

```
skills/disaster-recovery-wecom/
├── config.yaml          # 主配置文件
├── templates/           # 通知模板目录
│   ├── system_failure.md
│   ├── token_warning.md
│   └── ...
└── logs/               # 日志目录
```

### 3.2 配置结构

```yaml
# 告警级别配置
settings:
  severity_levels:
    P0:
      name: "紧急"
      color: "FF0000"
      at_all: true

# Webhook 配置
webhooks:
  system_alerts:
    name: "系统告警通知群"
    url: "..."
    enabled: true
    default_level: P1

# 通知规则
rules:
  token_alerts:
    - condition: "token_usage > 80%"
      level: P1
      webhook: system_alerts

# 限流配置
rate_limiting:
  min_interval:
    P0: 60      # 1分钟
    P1: 300     # 5分钟

# 重试配置
retry:
  max_attempts: 3
```

---

## 4. 使用方法

### 4.1 命令行使用

```bash
# 基本用法
./scripts/emergency-wecom-alert.sh <level> <message> [options]

# 发送 P0 紧急告警
./scripts/emergency-wecom-alert.sh P0 "系统核心服务异常"

# 指定 Webhook
./scripts/emergency-wecom-alert.sh P1 "Token使用率超过80%" -w system_alerts

# 使用模板
./scripts/emergency-wecom-alert.sh P1 -t token_warning \
    USAGE_PERCENT=85 \
    TOKENS_REMAINING=1500

# @所有人
./scripts/emergency-wecom-alert.sh P0 "严重故障" -a

# 发送测试消息
./scripts/emergency-wecom-alert.sh test

# 附加文件内容
./scripts/emergency-wecom-alert.sh P1 "任务失败" -f /var/log/error.log

# 干运行模式（测试但不发送）
./scripts/emergency-wecom-alert.sh P1 "测试消息" --dry-run
```

### 4.2 脚本中调用

```bash
ALERT_SCRIPT="/root/.openclaw/workspace/scripts/emergency-wecom-alert.sh"

# 简单调用
"$ALERT_SCRIPT" P1 "备份任务开始"

# 使用模板
"$ALERT_SCRIPT" P0 -t backup_failure \
    BACKUP_TYPE="全量备份" \
    ERROR_MESSAGE="磁盘空间不足"

# 检查结果
if "$ALERT_SCRIPT" P3 "任务完成"; then
    echo "通知发送成功"
else
    echo "通知发送失败"
fi
```

### 4.3 在其他脚本中集成

```bash
#!/bin/bash

WORKSPACE="/root/.openclaw/workspace"
ALERT_SCRIPT="$WORKSPACE/scripts/emergency-wecom-alert.sh"

# 发送告警的函数
send_alert() {
    local level="$1"
    local message="$2"
    
    if [[ -x "$ALERT_SCRIPT" ]]; then
        "$ALERT_SCRIPT" "$level" "$message" 2>/dev/null || true
    fi
}

# 使用示例
send_alert P2 "开始执行数据同步..."

# 执行任务...
if some_task; then
    send_alert P3 "任务执行成功"
else
    send_alert P0 "任务执行失败！"
fi
```

---

## 5. 通知模板

### 5.1 可用模板

| 模板名称 | 用途 | 默认级别 |
|----------|------|---------|
| system_failure | 系统故障 | P0 |
| token_warning | Token预警 | P1 |
| token_critical | Token紧急 | P0 |
| backup_failure | 备份失败 | P0 |
| backup_success | 备份成功 | P3 |
| memory_failure | 记忆异常 | P0 |
| security_breach | 安全入侵 | P0 |
| security_warning | 安全预警 | P1 |
| task_failure | 任务失败 | P0 |
| task_success | 任务成功 | P3 |

### 5.2 模板变量

模板支持使用 `{{VARIABLE}}` 语法插入变量：

| 变量名 | 说明 | 自动填充 |
|--------|------|---------|
| {{LEVEL}} | 告警级别 | 是 |
| {{TIMESTAMP}} | 时间戳 | 是 |
| {{HOSTNAME}} | 主机名 | 是 |
| {{COLOR}} | 颜色代码 | 是 |
| 其他 | 根据模板自定义 | 否 |

### 5.3 自定义模板

创建新模板文件 `skills/disaster-recovery-wecom/templates/custom_alert.md`：

```markdown
<font color="#{{COLOR}}">**[{{LEVEL}}]**</font>

**自定义告警标题**

{{CUSTOM_MESSAGE}}

---
<font color="gray">{{TIMESTAMP}}</font>
```

使用模板：
```bash
./scripts/emergency-wecom-alert.sh P1 -t custom_alert CUSTOM_MESSAGE="我的消息"
```

---

## 6. 与灾备系统整合

### 6.1 现有整合点

已修改 `scripts/disaster-recovery-sync-v2.sh`，在以下节点发送通知：

| 节点 | 级别 | 说明 |
|------|------|------|
| 备份开始 | P2 | 任务启动通知 |
| 备份成功 | P3 | 备份完成统计 |
| 备份失败 | P0 | 关键文件缺失告警 |

### 6.2 整合方式

在灾备脚本中添加以下代码：

```bash
ALERT_SCRIPT="/root/.openclaw/workspace/scripts/emergency-wecom-alert.sh"

send_wecom_alert() {
    local level="$1"
    local template="$2"
    shift 2
    
    if [[ -x "$ALERT_SCRIPT" ]]; then
        "$ALERT_SCRIPT" "$level" -t "$template" "$@" 2>/dev/null || true
    fi
}

# 在关键节点调用
send_wecom_alert P1 backup_success BACKUP_TYPE="增量备份" BACKUP_SIZE="1.2GB"
```

---

## 7. 7层备份流程集成

### 7.1 L1 - 元协议层

**集成点**: 元协议更新时
```bash
# 当 DISASTER_RECOVERY_V1.1.md 更新时
send_wecom_alert P3 task_success \
    TASK_NAME="灾备手册更新" \
    OUTPUT_SUMMARY="已更新至 V1.1"
```

### 7.2 L4 - 核心身份层

**集成点**: 核心身份文件变更
```bash
# 当 SOUL.md, USER.md 等文件更新时
send_wecom_alert P2 task_success \
    TASK_NAME="核心身份备份" \
    DATA_PROCESSED="身份文件同步完成"
```

### 7.3 L7 - 运行时状态层

**集成点**: 会话检查点创建
```bash
# 创建会话检查点后
send_wecom_alert P3 task_success \
    TASK_NAME="会话检查点" \
    OUTPUT_SUMMARY="检查点 ID: $(date +%s)"
```

### 7.4 各层告警建议

| 层级 | 告警场景 | 建议级别 | 模板 |
|------|---------|---------|------|
| L7 | 会话异常中断 | P1 | system_failure |
| L6 | MEMORY.md 损坏 | P0 | memory_failure |
| L5 | 知识图谱损坏 | P1 | system_failure |
| L4 | 身份文件缺失 | P0 | system_failure |
| L3 | 数字孪生配置错误 | P2 | system_failure |
| L2 | Cron 任务失败 | P1 | task_failure |
| L1 | 灾备手册缺失 | P0 | system_failure |

---

## 8. 常见问题

### Q1: 测试时提示 "Webhook URL 未配置"

**原因**: 配置文件中的 Webhook URL 仍是默认值

**解决**: 编辑 `skills/disaster-recovery-wecom/config.yaml`，将 `YOUR_*_KEY` 替换为实际的 key

### Q2: 通知发送成功但企微没收到

**排查步骤**:
1. 检查企微群聊中是否添加了机器人
2. 检查 Webhook URL 是否完整
3. 检查 key 是否正确（不要有额外空格）
4. 检查企微是否有网络限制

### Q3: 如何在其他脚本中使用？

**参考**:
```bash
ALERT_SCRIPT="/root/.openclaw/workspace/scripts/emergency-wecom-alert.sh"

# 发送告警（失败不中断主流程）
"$ALERT_SCRIPT" P1 "消息内容" 2>/dev/null || true
```

### Q4: 通知太频繁怎么办？

**解决**: 配置文件中有 rate_limiting 设置，默认：
- P0: 1分钟间隔
- P1: 5分钟间隔
- P2: 30分钟间隔
- P3: 1小时间隔

### Q5: 如何禁用某个 Webhook？

**解决**: 在配置文件中设置 `enabled: false`

```yaml
webhooks:
  task_notifications:
    enabled: false
```

---

## 9. 待配置项

### 9.1 必需配置（P0）

| 配置项 | 文件路径 | 说明 |
|--------|---------|------|
| system_alerts Webhook | config.yaml | 系统告警通知群 |
| disaster_recovery Webhook | config.yaml | 灾备通知群 |

### 9.2 可选配置（P1）

| 配置项 | 文件路径 | 说明 |
|--------|---------|------|
| security_alerts Webhook | config.yaml | 安全告警群 |
| task_notifications Webhook | config.yaml | 任务通知群 |
| rate_limiting | config.yaml | 调整通知频率 |
| 自定义模板 | templates/ | 添加业务相关模板 |

### 9.3 配置检查清单

```bash
# 1. 检查配置文件
ls -la skills/disaster-recovery-wecom/config.yaml

# 2. 检查脚本可执行
ls -la scripts/emergency-wecom-alert.sh

# 3. 检查模板存在
ls -la skills/disaster-recovery-wecom/templates/

# 4. 发送测试消息
./scripts/emergency-wecom-alert.sh test

# 5. 检查日志目录
ls -la skills/disaster-recovery-wecom/logs/
```

---

## 10. 附录

### 10.1 文件清单

```
.
├── skills/disaster-recovery-wecom/
│   ├── config.yaml                    # 主配置（需用户配置）
│   ├── templates/
│   │   ├── system_failure.md          # 系统故障模板
│   │   ├── token_warning.md           # Token预警模板
│   │   ├── token_critical.md          # Token紧急模板
│   │   ├── backup_failure.md          # 备份失败模板
│   │   ├── backup_success.md          # 备份成功模板
│   │   ├── memory_failure.md          # 记忆异常模板
│   │   ├── security_breach.md         # 安全入侵模板
│   │   ├── security_warning.md        # 安全预警模板
│   │   ├── task_failure.md            # 任务失败模板
│   │   └── task_success.md            # 任务成功模板
│   └── logs/                          # 日志目录
├── scripts/
│   └── emergency-wecom-alert.sh       # 告警脚本
├── scripts/disaster-recovery-sync-v2.sh  # 已整合的灾备脚本
└── docs/
    └── DISASTER_RECOVERY_WECOM_SETUP.md  # 本文档
```

### 10.2 更新记录

| 版本 | 日期 | 修订内容 | 修订人 |
|-----|------|---------|--------|
| 1.0 | 2026-03-21 | 初始版本 | 满意妞 |

---

**文档状态**: ✅ 配置完成，等待用户填写 Webhook  
**配置完成度**: 90% (仅缺 Webhook key)  
**维护责任人**: 满意妞
