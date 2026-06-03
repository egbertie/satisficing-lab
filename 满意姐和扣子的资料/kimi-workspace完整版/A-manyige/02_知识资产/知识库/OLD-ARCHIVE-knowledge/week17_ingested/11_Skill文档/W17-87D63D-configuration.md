---
# 知识元数据 (5标准化)
knowledge_id: W17-87D63D
title: Zero-Vacancy Executor - 配置详解
category: 11_Skill文档
source: skills/zero-vacancy-executor/references/configuration.md
ingested_at: 2026-03-27 17:59:30
word_count: 2467
week: 17
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Zero-Vacancy Executor - 配置详解

> **知识ID**: W17-87D63D  
> **分类**: 11_Skill文档  
> **来源**: `skills/zero-vacancy-executor/references/configuration.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Zero-Vacancy Executor - 配置详解

## 配置结构说明

### slot_management - 槽位管理

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `total_slots` | int | 4 | 系统总槽位数 |
| `reserved_slots.user_dialogue` | int | 1 | 预留给用户对话的槽位数 |
| `reserved_slots.emergency` | int | 0 | 预留紧急槽位 |
| `dynamic_allocation` | bool | true | 是否允许动态分配 |
| `preemption_enabled` | bool | true | 是否允许抢占低优先级任务 |
| `grace_period_ms` | int | 1000 | 抢占前的宽限期 |

### detection - 空闲检测

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `idle_check_interval_sec` | int | 5 | 空闲检测间隔（秒） |
| `user_intent_detection` | bool | true | 是否检测用户意图 |
| `intent_triggers` | list | [...] | 触发预留的用户行为 |

### response - 响应配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `max_response_time_ms` | int | 500 | 最大响应时间目标 |
| `priority_boost` | string | "high" | 用户对话优先级提升 |
| `queue_enabled` | bool | true | 是否启用等待队列 |
| `max_queue_length` | int | 10 | 最大队列长度 |

### release - 释放配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `session_timeout_sec` | int | 300 | 会话超时时间（秒） |
| `auto_release_on_complete` | bool | true | 任务完成后自动释放 |
| `cleanup_interval_sec` | int | 30 | 清理检查间隔 |

### monitoring - 监控配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enabled` | bool | true | 是否启用监控 |
| `metrics_endpoint` | string | "/metrics" | 指标端点路径 |
| `status_endpoint` | string | "/status" | 状态端点路径 |
| `health_check_interval_sec` | int | 10 | 健康检查间隔 |
| `alerts_enabled` | bool | true | 是否启用告警 |

### alerts - 告警阈值

| 指标 | warning | critical | 说明 |
|------|---------|----------|------|
| `slot_availability_ratio` | 0.8 | 0.5 | 槽位可用率 |
| `user_response_latency_ms` | 1000 | 3000 | 用户响应延迟 |
| `slot_preemption_count_per_min` | 10 | 30 | 抢占次数/分钟 |
| `user_wait_queue_length` | 5 | 10 | 用户等待队列长度 |

## 配置示例

### 高响应场景（推荐）

```json
{
  "slot_management": {
    "total_slots": 4,
    "reserved_slots": {
      "user_dialogue": 1
    },
    "preemption_enabled": true
  },
  "response": {
    "max_response_time_ms": 300,
    "queue_enabled": true
  }
}
```

### 高吞吐场景

```json
{
  "slot_management": {
    "total_slots": 8,
    "reserved_slots": {
      "user_dialogue": 1
    },
    "preemption_enabled": false
  },
  "response": {
    "max_response_time_ms": 1000,
    "queue_enabled": false
  }
}
```

### 开发测试场景

```json
{
  "slot_management": {
    "total_slots": 2,
    "reserved_slots": {
      "user_dialogue": 1
    }
  },
  "adversarial_test": {
    "enabled": true
  }
}
```
