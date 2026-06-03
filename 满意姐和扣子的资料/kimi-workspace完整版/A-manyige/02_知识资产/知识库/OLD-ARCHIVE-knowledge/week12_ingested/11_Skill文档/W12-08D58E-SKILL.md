---
# 知识元数据 (5标准化)
knowledge_id: W12-08D58E
title: SKILL
category: 11_Skill文档
source: skills/.archive_promise-management-system/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 3922
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W12-08D58E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_promise-management-system/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: promise-management-system
version: 1.0.0
description: |
  承诺管理标准Skill - 满足5个标准：
  1. 全局考虑：覆盖全部承诺类型（任务/会议/交付/沟通）
  2. 系统考虑：承诺创建→执行→监控→闭环完整系统
  3. 迭代机制：PDCA闭环，每周优化承诺流程
  4. Skill化：标准SKILL.md格式，可安装可调用
  5. 流程自动化：承诺到期前自动预警，逾期自动补救
author: Satisficing Institute
tags:
  - promise
  - commitment
  - tracking
  - automation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3", "grep", "date"]
  - cron: true
  - external: ["github", "wecom"]
---

# 承诺管理标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 承诺类型全覆盖

| 类型 | 示例 | 追踪方式 |
|------|------|----------|
| **任务承诺** | "今日完成XX" | TASK_MASTER.md + 截止日 |
| **会议承诺** | "明日10点开会" | 日历集成 + 提醒 |
| **交付承诺** | "周五交付文档" | 交付清单 + 验收标准 |
| **沟通承诺** | "今晚回复邮件" | 待回复清单 + 截止时 |
| **改进承诺** | "下次不再犯" | 错误日志 + 预防机制 |

### 1.2 承诺生命周期全覆盖

```
承诺创建 → 承诺确认 → 执行监控 → 到期预警 → 完成闭环 → 复盘归档
   ↑___________________________________________↓
              （逾期则触发补救循环）
```

---

## 标准2: 系统考虑（Systematic）

### 2.1 承诺创建系统

| 字段 | 必填 | 验证规则 |
|------|------|----------|
| 承诺内容 | ✅ | 清晰可执行 |
| 截止日期 | ✅ | 必须为具体日期时间 |
| 提醒时间 | ✅ | 截止前24小时 |
| 验收标准 | ✅ | 可验证的完成标准 |
| 关联任务 | ⚠️ | 如有关联需标记 |

### 2.2 承诺执行系统

| 阶段 | 系统动作 | 人工干预 |
|------|----------|----------|
| 创建时 | 自动记录到TASK_MASTER.md | 零干预 |
| T-24h | 自动发送到期预警 | 零干预 |
| T-2h | 自动发送紧急提醒 | 零干预 |
| 到期时 | 自动检查完成状态 | 零干预 |
| 逾期时 | 自动触发补救流程 | P1需确认 |
| 完成时 | 自动归档+复盘 | 零干预 |

### 2.3 系统间联动

| 触发条件 | 联动动作 |
|----------|----------|
| 承诺创建 | 更新任务看板 + 设置提醒 |
| 承诺到期 | 检查执行状态 + 生成报告 |
| 承诺逾期 | 触发补救 + 记录错误日志 |
| 承诺完成 | 更新仪表盘 + 释放资源 |

---

## 标准3: 迭代机制（Iterative）

### 3.1 PDCA闭环

| 阶段 | 动作 | 频率 |
|------|------|------|
| **Plan** | 每周生成承诺计划 | 每周日 |
| **Do** | 自动执行承诺监控 | 每日 |
| **Check** | 分析承诺准时率 | 每周六 |
| **Act** | 优化承诺流程 | 每周日 |

### 3.2 承诺质量迭代

```
V1.0.0: 基础承诺追踪
  ↓
V1.1.0: 智能到期预测
  ↓
V1.2.0: 承诺依赖管理
  ↓
V2.0.0: 承诺网络分析
```

---

## 标准4: Skill化（Skill-ified）

### 4.1 标准Skill结构

```
skills/promise-management-system/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── promise_master.py       # 主控脚本
│   ├── promise_creator.py      # 创建承诺
│   ├── promise_monitor.py      # 监控执行
│   ├── promise_reminder.py     # 发送提醒
│   └── promise_closer.py       # 闭环归档
├── rules/
│   ├── promise_format.yaml     # 承诺格式规范
│   └── reminder_rules.yaml     # 提醒规则
├── templates/
│   ├── promise_template.md
│   └── reminder_template.md
└── validators/
    └── promise_validator.py
```

### 4.2 可调用接口

```python
# 创建承诺
promise_manager.create(
    content="完成XX文档",
    deadline="2026-03-25 18:00",
    reminder="2026-03-24 18:00",
    criteria="文档通过审核"
)

# 检查承诺状态
promise_manager.check_status(promise_id="P-001")

# 触发补救
promise_manager.trigger_remediation(promise_id="P-001")
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 全自动承诺生命周期

| 时间点 | 自动动作 | 输出 |
|--------|----------|------|
| 承诺创建 | 记录+设置提醒 | TASK_MASTER更新 |
| T-24h | 发送预警通知 | 提醒消息 |
| T-2h | 发送紧急提醒 | 紧急提醒 |
| 到期时 | 检查完成状态 | 状态报告 |
| 逾期时 | 触发补救+记录 | 补救任务+错误日志 |
| 完成时 | 归档+复盘 | 归档记录 |

### 5.2 定时任务

```bash
# 每日承诺监控
0 8 * * * promise_manager daily_check

# 到期前24小时预警
0 10 * * * promise_manager send_reminders

# 到期检查
0 18 * * * promise_manager check_deadlines

# 周承诺复盘
0 10 * * 6 promise_manager weekly_review
```

---

## 使用方法

### 创建承诺（自动模式）
```
用户: "我承诺周五完成V1.0文档"
AI: 自动创建承诺
   - 内容: 完成V1.0文档
   - 截止: 2026-03-25 18:00
   - 提醒: 2026-03-24 18:00
   - 标准: 文档通过审核
   
   已记录到TASK_MASTER.md
   将在周四18:00提醒您
```

### 监控承诺（自动）
```
每日08:00自动扫描所有承诺
- 到期前24小时: 发送预警
- 到期前2小时: 发送紧急提醒
- 到期时: 检查完成状态
- 逾期时: 触发补救
```

### 承诺复盘（每周六）
```
本周承诺统计:
- 总承诺: 10个
- 准时完成: 7个 (70%)
- 延期完成: 2个 (20%)
- 未完成: 1个 (10%)

改进建议:
- 减少同时进行的承诺数量
- 增加缓冲时间
```

---

## 5个标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 4种承诺类型 + 完整生命周期 | ✅ |
| **2. 系统** | 创建→执行→监控→闭环 + 系统联动 | ✅ |
| **3. 迭代** | PDCA闭环 + 版本升级 | ✅ |
| **4. Skill化** | 标准SKILL.md + 可调用接口 | ✅ |
| **5. 自动化** | 全自动生命周期 + 零干预 | ✅ |

---

*版本: v1.0.0*  
*创建: 2026-03-20*  
*标准: 5个标准全部满足*