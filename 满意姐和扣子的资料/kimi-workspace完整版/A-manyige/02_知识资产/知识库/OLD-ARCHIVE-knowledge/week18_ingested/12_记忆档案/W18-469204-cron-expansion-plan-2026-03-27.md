---
# 知识元数据 (5标准化)
knowledge_id: W18-469204
title: Cron扩展计划 - 10→30任务
category: 12_记忆档案
source: memory/cron-expansion-plan-2026-03-27.md
ingested_at: 2026-03-27 17:59:30
word_count: 2903
week: 18
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Cron扩展计划 - 10→30任务

> **知识ID**: W18-469204  
> **分类**: 12_记忆档案  
> **来源**: `memory/cron-expansion-plan-2026-03-27.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Cron扩展计划 - 10→30任务

## 现状分析
- **当前Cron数**: 约10个（从HEARTBEAT.md提取）
- **目标Cron数**: 30个
- **缺口**: 20个新任务

---

## 现有Cron任务清单（10个）

| 序号 | 任务名称 | 频率 | 优先级 | 状态 |
|------|----------|------|--------|------|
| 1 | 晨间图腾仪式 | 每日09:00 | P0 | ✅ |
| 2 | 黄昏图腾归位 | 每日18:00 | P0 | ✅ |
| 3 | 信息防火墙检查 | 每次心跳 | P0 | ✅ |
| 4 | 自我评估校准 | 每次心跳 | P0 | ✅ |
| 5 | Token周度监控 | 每日12:00 | P0 | ✅ |
| 6 | 检查点健康验证 | 每4小时 | P0 | ✅ |
| 7 | 知识OS维护 | 每日1次 | P1 | ✅ |
| 8 | 日程检查 | 每次心跳 | P1 | ✅ |
| 9 | 提及通知 | 每次心跳 | P2 | ✅ |
| 10 | 基线检查 | 每次会话启动 | P0 | ✅ |

---

## 新增Cron任务规划（20个）

### 高频监控类（5个）

| 序号 | 任务名称 | 频率 | 用途 | 优先级 |
|------|----------|------|------|--------|
| 11 | Skill市场更新监控 | 每6小时 | 检测新Skill发布 | P1 |
| 12 | 知识库健康检查 | 每2小时 | 链接有效性验证 | P1 |
| 13 | 外部API可用性检测 | 每30分钟 | GitHub/飞书等 | P1 |
| 14 | Token实时预警 | 每15分钟 | <20%触发 | P0 |
| 15 | 会话状态归档 | 每小时 | 自动memory flush | P1 |

### 日报类（5个）

| 序号 | 任务名称 | 频率 | 用途 | 优先级 |
|------|----------|------|------|--------|
| 16 | 每日晨报生成 | 每日08:55 | AI资讯+日程+风险 | P0 |
| 17 | 每日晚报生成 | 每日18:30 | 今日完成+明日计划 | P1 |
| 18 | 任务逾期提醒 | 每日09:30 | 检查P0/P1逾期 | P0 |
| 19 | 信任积分日报 | 每日20:00 | 积分变动通知 | P2 |
| 20 | 知识入库进度 | 每日22:00 | Week 1进度追踪 | P1 |

### 周期性任务（5个）

| 序号 | 任务名称 | 频率 | 用途 | 优先级 |
|------|----------|------|------|--------|
| 21 | 周度系统复盘 | 每周日20:00 | 11系统健康检查 | P1 |
| 22 | 月度知识盘点 | 每月1日09:00 | 全库盘点 | P1 |
| 23 | 备份验证测试 | 每周三/六 02:00 | PHOENIX-BASELINE | P0 |
| 24 | Skill效果评估 | 每周五18:00 | TOP20使用效果 | P2 |
| 25 | 对抗测试执行 | 每周一04:00 | QA-S7自动化 | P1 |

### 事件驱动类（5个）

| 序号 | 任务名称 | 触发条件 | 用途 | 优先级 |
|------|----------|----------|------|--------|
| 26 | 飞书文档变更同步 | 文档更新 | 自动入库 | P1 |
| 27 | GitHub PR审查提醒 | 新PR提交 | 待审查通知 | P2 |
| 28 | 日程前准备提醒 | 事件前30分钟 | 准备事项推送 | P0 |
| 29 | Token耗尽预警 | Token<10% | 紧急通知用户 | P0 |
| 30 | 异常日志聚合 | 错误>5次/小时 | 异常汇总报告 | P1 |

---

## 实施步骤

### Phase 1（立即执行）- 5个P0任务
```bash
# 14. Token实时预警
cron schedule --name token-realtime-alert --schedule "*/15 * * * *" \
  --command "check-token-level.sh --threshold 20 --notify"

# 16. 每日晨报生成
cron schedule --name daily-morning-report --schedule "55 8 * * *" \
  --command "generate-morning-report.sh --source kimi-search --output feishu"

# 18. 任务逾期提醒
cron schedule --name task-overdue-alert --schedule "30 9 * * *" \
  --command "check-overdue-tasks.sh --priority P0,P1 --notify"

# 23. 备份验证测试（每周两次）
cron schedule --name backup-verification --schedule "0 2 * * 3,6" \
  --command "baseline-checker-runner.py check --category backup"

# 28. 日程前准备提醒
cron schedule --name calendar-prep-reminder --schedule "*/30 * * * *" \
  --command "check-upcoming-events.sh --window 30min --notify"
```

### Phase 2（本周内）- 10个P1任务
- 11,12,13,15,17,19,20,21,25,30

### Phase 3（下周）- 5个P2任务
- 22,24,26,27,29

---

## 依赖条件

| 任务 | 依赖 | 状态 |
|------|------|------|
| 每日晨报 | 飞书日历授权 | 🔄 外部协调中 |
| 飞书文档同步 | 飞书OAuth | 🔄 外部协调中 |
| GitHub PR提醒 | GitHub权限 | 🔄 外部协调中 |
| 知识入库进度 | 飞书多维表格 | ✅ 已配置 |

---

*计划生成时间: 2026-03-27*
*目标完成: 2026-04-03*
