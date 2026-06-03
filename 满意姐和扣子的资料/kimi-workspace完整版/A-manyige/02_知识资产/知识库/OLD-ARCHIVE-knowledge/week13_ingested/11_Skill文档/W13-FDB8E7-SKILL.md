---
# 知识元数据 (5标准化)
knowledge_id: W13-FDB8E7
title: Task Coordinator Skill
category: 11_Skill文档
source: skills/.archive_task-coordinator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1827
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Task Coordinator Skill

> **知识ID**: W13-FDB8E7  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_task-coordinator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Task Coordinator Skill
> **任务协调管理Skill** - 确保正常计划和临时任务的统筹协调，永不掉链子

## 功能概述

本Skill负责任务的智能协调管理，核心能力：

1. **工作负载分析** - 实时分析当前任务状态（正常/临时/过期/阻塞）
2. **执行模式切换** - 自动切换顺序/并行/通知用户模式
3. **遗漏检测** - 自动检查日志，发现遗漏任务
4. **预警机制** - 任务到期前主动提醒

## 执行模式

### 模式1: Sequential（顺序执行）
**触发条件**: 有过期任务或高优先级临时任务
**行为**: 
- 暂停后台任务
- 全力处理过期/紧急任务
- 完成后恢复正常节奏

### 模式2: Parallel（并行执行）
**触发条件**: 无临时任务，无过期任务
**行为**:
- 正常计划任务并行推进
- 后台任务自主执行
- 效率最大化

### 模式3: Notify User（通知用户）
**触发条件**: 任务被用户阻塞
**行为**:
- 汇总所有阻塞项
- 一次性向用户确认
- 避免反复打扰

## 使用方式

### 自动运行（推荐）
```bash
# 每小时自动检查
python3 skills/task-coordinator/task_coordinator.py

# 或集成到心跳检查
```

### 手动触发
```bash
# 生成当前报告
cd skills/task-coordinator
python3 task_coordinator.py

# 查看详细状态
cat ../../memory/task-coordinator-status.json
```

## 输出示例

```
============================================================
任务协调管理报告
============================================================

📊 当前状态:
  - 过期任务: 2 项
  - 阻塞任务: 2 项
  - 待确认: 1 项

💡 执行建议:
  [P0] 立即补救过期任务
      模式: sequential
  [P1] 向用户确认阻塞项
      模式: notify_user

🎯 行动计划 (模式: sequential):
  1. 补救所有过期任务
     预计: 2小时
============================================================
```

## 集成建议

1. **心跳检查集成** - 每次心跳自动运行
2. **任务开始前** - 运行协调器确定执行模式
3. **每日晨报** - 包含协调报告

## 质量评估

### 测试结果 (2026-03-12)

| 指标 | 结果 | 等级 |
|------|------|------|
| 整体通过率 | 92% (23/25) | A- |
| 正例测试 | 90% (9/10) | B+ |
| 负例测试 | 90% (9/10) | B+ |
| 压力测试 | **100% (5/5)** | A+ |
| 平均响应时间 | 0.75ms | 优秀 |

**详细报告**: [QUALITY_ASSESSMENT_REPORT_FINAL.md](tests/QUALITY_ASSESSMENT_REPORT_FINAL.md)

## 文件结构

```
skills/task-coordinator/
├── SKILL.md              # 本文件
├── task_coordinator.py   # 核心引擎 V2.1
├── config/
│   └── rules.json        # 协调规则配置
└── tests/
    ├── test_plan.md      # 测试计划
    ├── test_quality.py   # 测试套件
    └── QUALITY_ASSESSMENT_REPORT_FINAL.md  # 质量评估报告
```
