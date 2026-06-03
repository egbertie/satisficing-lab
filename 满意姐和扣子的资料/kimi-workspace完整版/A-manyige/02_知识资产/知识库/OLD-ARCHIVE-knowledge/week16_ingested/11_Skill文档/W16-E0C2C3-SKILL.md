---
# 知识元数据 (5标准化)
knowledge_id: W16-E0C2C3
title: RPO/RTO Monitor Skill
category: 11_Skill文档
source: skills/rpo-rto-monitor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 5272
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# RPO/RTO Monitor Skill

> **知识ID**: W16-E0C2C3  
> **分类**: 11_Skill文档  
> **来源**: `skills/rpo-rto-monitor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# RPO/RTO Monitor Skill

## Overview
RPO/RTO实时监控系统——量化数据保护能力，确保业务连续性可测量、可改进。

## S1: Global Consideration (全局考虑)

### 1.1 人 (People)
| 角色 | 关注点 | 决策依赖 |
|------|--------|----------|
| 业务负责人 | 最大可接受数据丢失 | RPO目标设定 |
| 运维人员 | 恢复速度 | RTO优化方向 |
| 管理层 | 合规与风险 | 投资回报率 |

### 1.2 事 (Tasks)
- RPO实时计算（未提交变更时间窗口）
- RTO能力测试（恢复演练）
- 趋势分析与预测
- 告警与升级
- 容量规划建议

### 1.3 物 (Resources)
- Git提交历史
- 备份时间戳
- 恢复测试记录
- 监控数据存储

### 1.4 环境 (Environment)
- 工作时间（高变更频率）
- 非工作时间（低变更频率）
- 发布窗口（高变更风险）
- 灾难场景（恢复执行）

### 1.5 外部集成 (External)
- Git系统
- 备份系统
- 告警系统（飞书/企微）
- 仪表板（可视化）

### 1.6 边界情况 (Edge Cases)
- 长时间无提交（RPO失真）
- 恢复测试失败（RTO无限大）
- 备份中断（RPO持续增长）
- 并发灾难（多系统同时故障）

## S2: System Closed Loop (系统闭环)

### 2.1 RPO计算流程
```
当前时间 - 最后一次成功备份时间 = RPO（数据丢失窗口）
  ↓
与目标RPO比较
  ↓
超标 → 告警 → 触发紧急备份
正常 → 记录 → 趋势分析
```

### 2.2 RTO测试流程
```
定期演练 → 记录恢复时间 → 分析瓶颈 → 优化流程 → 重新测试
```

### 2.3 反馈机制
```
RPO趋势恶化 → 建议增加备份频率
RTO超出目标 → 建议优化恢复流程
备份失败率上升 → 建议改进备份策略
```

### 2.4 分级响应
| RPO状态 | 阈值 | 响应 |
|---------|------|------|
| 正常 | <50%目标 | 记录 |
| 警告 | 50-80%目标 | 提示 |
| 危险 | 80-100%目标 | 告警 |
| 超标 | >100%目标 | 紧急+升级 |

## S3: Observable Outputs (可观测输出)

### 3.1 核心指标
| 指标 | 定义 | 目标 |
|------|------|------|
| RPO | 可丢失数据时间窗口 | <2小时 |
| RTO | 恢复服务所需时间 | <10分钟 |
| MTBF | 平均故障间隔 | >30天 |
| MTTR | 平均恢复时间 | <15分钟 |

### 3.2 实时状态
```json
{
  "timestamp": "2026-03-25T20:35:00+08:00",
  "rpo": {
    "current_minutes": 0,
    "target_minutes": 120,
    "status": "normal",
    "last_backup": "2026-03-25T20:35:00+08:00"
  },
  "rto": {
    "tested_minutes": 5,
    "target_minutes": 10,
    "status": "normal",
    "last_test": "2026-03-25T18:00:00+08:00"
  },
  "trend": {
    "rpo_7d_avg": 45,
    "rto_improvement": "-20%",
    "prediction": "on_track"
  }
}
```

### 3.3 可视化仪表板
```
📊 RPO/RTO 监控仪表板 (2026-03-25 20:35)
━━━━━━━━━━━━━━━━━━━━━━━━━━

RPO (恢复点目标)
当前: 0分钟 ████░░░░░░░░░░░░░░░░ 目标: 120分钟
状态: 🟢 正常

RTO (恢复时间目标)  
实测: 5分钟 ██████░░░░░░░░░░░░░░ 目标: 10分钟
状态: 🟢 正常

趋势 (7天)
RPO平均: 45分钟 ↓ 改善中
RTO平均: 6分钟 ↓ 改善中
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## S4: Automated Integration (自动化集成)

### 4.1 Cron配置
```yaml
jobs:
  - name: rpo-monitor
    schedule: "*/10 * * * *"  # 每10分钟
    script: disaster-recovery/rpo_monitor.py --check
    
  - name: rto-test
    schedule: "0 2 * * 0"     # 每周日凌晨2点
    script: disaster-recovery/rpo_monitor.py --test-rto
    
  - name: rpo-report
    schedule: "0 9,18 * * *"  # 早晚报告
    script: disaster-recovery/rpo_monitor.py --report
```

### 4.2 脚本清单
| 脚本 | 功能 | 调用 |
|------|------|------|
| rpo_monitor.py | RPO计算与监控 | Cron/手动 |
| dashboard.py | 仪表板生成 | 手动 |
| trend_analyzer.py | 趋势分析 | 定时 |

### 4.3 告警规则
```python
ALERT_RULES = {
    "rpo_warning": {"threshold": 0.5, "action": "log"},      # 50%目标
    "rpo_critical": {"threshold": 0.8, "action": "notify"},   # 80%目标
    "rpo_breach": {"threshold": 1.0, "action": "escalate"},   # 100%目标
    "rto_fail": {"threshold": None, "action": "escalate"}     # 测试失败
}
```

## S5: Self-Validation (自我验证)

### 5.1 自动检查
- [ ] Git提交时间戳可获取
- [ ] 备份时间戳可获取
- [ ] 恢复测试可执行
- [ ] 告警通道可用
- [ ] 数据存储可写

### 5.2 测试用例
```bash
# 测试RPO计算
python3 disaster-recovery/rpo_monitor.py --check
# 期望: 返回当前RPO分钟数

# 测试RTO演练
python3 disaster-recovery/rpo_monitor.py --test-rto
# 期望: 执行恢复测试，返回实际RTO

# 测试告警
python3 disaster-recovery/rpo_monitor.py --simulate-breach
# 期望: 触发RPO超标告警
```

### 5.3 健康检查
```bash
# 检查监控状态
python3 disaster-recovery/rpo_monitor.py --status
# 应显示: 最后检查时间、当前RPO/RTO、告警状态

# 检查趋势数据
cat /tmp/rpo_trend.json | jq '.last_7_days'
```

## S6: Cognitive Humility (认知谦逊)

### 6.1 能力边界
1. **RPO基于备份时间点**：如果备份已损坏，实际RPO更大
2. **RTO基于测试环境**：生产环境可能更慢
3. **无法预测未知故障类型**：基于历史模式
4. **单点监控**：不覆盖所有可能的丢失场景

### 6.2 不确定性标注
- RPO标注[基于Git提交时间]
- RTO标注[基于上次演练]
- 预测标注[趋势外推，非保证]

### 6.3 已知局限
- 依赖Git/备份系统的时间戳准确性
- 演练环境与真实灾难有差异
- 多系统故障的复合RPO/RTO未计算

## S7: Adversarial Testing (对抗测试)

### 7.1 测试场景

#### 场景1: 长时间无提交
```
场景: 节假日无工作
状态: 3天无Git提交
RPO计算: 3天
预期: 标注异常，提示"无活动"，不触发告警
```

#### 场景2: 备份中断
```
场景: 飞书备份失败3天
检测: 每次检查RPO增长
预期: 第2天告警，第3天紧急升级
```

#### 场景3: 恢复测试失败
```
场景: RTO演练时Git仓库损坏
测试: 执行恢复
预期: 记录RTO=失败，立即告警，启动修复
```

#### 场景4: 时间戳异常
```
场景: 系统时间被修改
输入: 错误的提交时间
预期: 检测时间异常，标记数据不可靠
```

#### 场景5: 并发灾难
```
场景: Git和飞书同时故障
状态: 无可用恢复源
预期: RPO/RTO标记为未知，触发最高级告警
```

#### 场景6: 目标不合理
```
场景: RPO目标设为1分钟
实际: 备份频率无法达到
预期: 标注目标不可达，建议调整
```

#### 场景7: 监控自身故障
```
场景: rpo_monitor.py无法运行
检测: 外部健康检查
预期: 监控静默失败，需独立 watchdog 检测
```

## Usage

### 查看当前状态
```bash
# 检查RPO/RTO
python3 disaster-recovery/rpo_monitor.py --check

# 查看仪表板
python3 disaster-recovery/dashboard.py

# 生成报告
python3 disaster-recovery/rpo_monitor.py --report
```

### 执行RTO演练
```bash
# 手动触发恢复测试
python3 disaster-recovery/rpo_monitor.py --test-rto

# 查看演练历史
python3 disaster-recovery/rpo_monitor.py --history
```

### 配置目标
```json
{
  "rpo_target_minutes": 120,
  "rto_target_minutes": 10,
  "alert_channels": ["feishu", "wecom"],
  "test_schedule": "0 2 * * 0"
}
```

## Files

| 文件 | 路径 | 说明 |
|------|------|------|
| RPO监控 | disaster-recovery/rpo_monitor.py | 核心脚本 |
| 仪表板 | disaster-recovery/dashboard.py | 可视化 |
| 配置 | config/rpo_rto_config.json | 目标设置 |
| 数据 | /tmp/rpo_metrics.jsonl | 时序数据 |

## Version
- **Version**: V1.0
- **Status**: FIN (7-standard complete)
- **Created**: 2026-03-25
- **Principle**: "If you can't measure it, you can't improve it"
- **Standard**: S1-S7 full compliance
