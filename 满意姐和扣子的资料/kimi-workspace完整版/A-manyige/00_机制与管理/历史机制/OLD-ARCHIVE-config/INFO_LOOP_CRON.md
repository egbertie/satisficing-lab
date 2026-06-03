# 信息闭环自动化Cron配置
> **配置版本**: V1.0  
> **创建时间**: 2026-03-20  
> **维护者**: 满意妞

---

## 定时任务

| 任务 | 频率 | 时间 | 动作 | 产出 |
|------|------|------|------|------|
| 信息闭环检查 | 每小时 | :00 | 扫描未闭环任务 | 提醒报告 |
| 日报生成 | 每日 | 18:00 | 汇总当日闭环状态 | 闭环日报 |
| 周报生成 | 每周 | 周日 20:00 | 统计周闭环率 | 闭环周报 |
| 月度优化 | 每月 | 最后一天 22:00 | 分析闭环效率 | 优化建议 |

---

## Cron表达式

```bash
# 每小时检查未闭环任务
0 * * * * cd /root/.openclaw/workspace && python3 scripts/info-loop-automation.py hourly >> logs/info-loop-hourly.log 2>&1

# 每日18:00生成闭环日报
0 18 * * * cd /root/.openclaw/workspace && python3 scripts/info-loop-automation.py daily-report >> logs/info-loop-daily.log 2>&1

# 每周日20:00生成闭环周报
0 20 * * 0 cd /root/.openclaw/workspace && python3 scripts/info-loop-automation.py weekly-report >> logs/info-loop-weekly.log 2>&1

# 每月最后一天22:00分析闭环效率
0 22 28-31 * * [ $(date +\%d -d "tomorrow") -eq 1 ] && cd /root/.openclaw/workspace && python3 scripts/info-loop-automation.py monthly-analysis >> logs/info-loop-monthly.log 2>&1
```

---

## 触发条件

### 自动触发

| 事件 | 触发动作 | 输出 |
|------|----------|------|
| 新任务创建 | 检查启动确认 | 确认请求 |
| 任务状态变更 | 检查阶段闭环 | 阶段汇报 |
| 任务逾期 | 紧急升级 | 逾期告警 |
| 到达汇报节点 | 生成进度汇报 | 进度报告 |

### 手动触发

```bash
# 检查特定任务
python3 scripts/info-loop-automation.py check WIP-001

# 全局扫描
python3 scripts/info-loop-automation.py scan

# 生成启动汇报
python3 scripts/info-loop-automation.py report WIP-001 start

# 生成进度汇报
python3 scripts/info-loop-automation.py report WIP-001 progress

# 生成完成汇报
python3 scripts/info-loop-automation.py report WIP-001 complete
```

---

## 输出位置

| 输出类型 | 文件路径 |
|----------|----------|
| 每小时检查日志 | `memory/info-loop-log.jsonl` |
| 每日闭环日报 | `reports/INFO_LOOP_DAILY_YYYYMMDD.md` |
| 每周闭环周报 | `reports/INFO_LOOP_WEEKLY_YYYYMMDD.md` |
| 月度优化建议 | `reports/INFO_LOOP_OPTIMIZATION_YYYYMMDD.md` |

---

## 验收标准

| 指标 | 目标 | 当前 |
|------|------|------|
| 任务闭环率 | ≥95% | 待统计 |
| 平均闭环时间 | ≤24小时 | 待统计 |
| 逾期未汇报率 | ≤5% | 待统计 |
| 信息遗漏次数 | 0次/月 | 待统计 |

---

## 迭代计划

| 版本 | 时间 | 功能 |
|------|------|------|
| V1.0 | 2026-03-20 | 基础闭环检查 + 定时扫描 |
| V1.1 | 2026-03-27 | 自动汇报生成 + 多渠道推送 |
| V1.2 | 2026-04-03 | 闭环率统计 + 趋势分析 |
| V2.0 | 2026-04-10 | 预测性提醒 + 智能优化建议 |

---

## 与其他系统的集成

| 系统 | 集成方式 | 数据流向 |
|------|----------|----------|
| 任务看板 | 读取TASK_BOARD | 任务状态 → 闭环检查 |
| 企微智能表 | API读写 | 闭环状态 → 表格更新 |
| 记忆系统 | 写入memory | 闭环记录 → 长期存储 |
| 报告系统 | 生成报告 | 闭环数据 → 日报/周报 |

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
