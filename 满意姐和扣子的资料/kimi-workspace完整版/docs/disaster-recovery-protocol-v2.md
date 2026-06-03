---
kia-version: 1.0
tier: T0
title: 🛡️ 灾备复刻机制 V2.0（简化版）
source: docs/disaster-recovery-protocol-v2.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchC-docs-03]
---

# 🛡️ 灾备复刻机制 V2.0（简化版）

> **最后更新**: 2026-04-10
> **维护者**: 蓝军 + 满意姐
> **原则**: 双经济要求——实用够用，拒绝过度工程化

---

## 一、诚实审计：旧机制的真实状态

### V1.0 的现状（2026-04-02 建立后未再更新）
- `C-disaster-recovery/L1-L7` 是一组**静态快照**，内容停留在 4 月初
- `disaster-recovery.sh` 只能"从旧快照恢复到工作区"，没有自动更新快照的管道
- `skills/checkpoint-manager/` 指向 `~/.openclaw/immortal-state/checkpoints`，但**该目录不存在**
- `skills/disaster-recovery-auditor/` 指向 `~/.openclaw/system-v2/checkpoints`，**该目录也不存在**
- `skills/interrupt-recovery/recovery_checker.py` 查找的文件名 `token-weekly-monitor-current.json` 已过时
- **L3、L4、L7 目录为空**
- **结论**：7 层架构是一个漂亮的文件夹结构，但已停止运转，处于**文档贝壳状态**

---

## 二、V2.0 核心思路：Git 是主备份，快照补缺口

### 为什么可以简化？
- **Git 已经跟踪了 95% 的恢复资产**：所有代码、文档、协议、SKILL 都是 Git tracked
- 真正可能丢失的，只有 `memory/` 目录下的**每日记录**（部分没进 Git）和**本地环境配置**
- 重建一个平行 7 层目录，等于每改一个文件就要复制一份，**空间 + Token 双浪费**

### 新架构：1+1+1

| 层级 | 机制 | 覆盖内容 | 恢复方式 |
|------|------|----------|----------|
| **主备份** | Git 仓库 | 代码、文档、SKILL、协议 | `git clone` / `git pull` |
| **状态快照** | `backups/essential-snapshot/` | memory/ 每日记录、任务追踪、元协议文件 | 从最新快照 `cp` |
| **云备份** | GitHub + 每周企微摘要 | Git push + Markdown 摘要 | 远程 clone |

---

## 三、已部署资产

### 3.1 每周精简快照脚本
- **路径**: `scripts/weekly_essential_snapshot.sh`
- **频率**: 每周日 02:17（错开准点）
- **保留数量**: 最近 2 个快照
- **内容**:
  - 元协议文件（SOUL.md, AGENTS.md, USER.md, TOOLS.md, HEARTBEAT.md, MEMORY.md, BOOTSTRAP.md）
  - memory/ 目录下的所有 `.md` 和 `.json` 记录
  - 环境配置文件的存在性元数据（不含密钥）
  - TASK_MASTER.md, token_economic_ledger.json
- **体积控制**: 预计 < 20MB

### 3.2 简化恢复脚本
- **路径**: `C-disaster-recovery/disaster-recovery.sh`（已重写为 V2.0）
- **流程**:
  1. `git reset --hard HEAD` + `git pull`
  2. 从 `backups/essential-snapshot/` 复制最新状态文件
  3. 快速验证关键文件存在性

### 3.3 废弃/待归档的旧资产
- `C-disaster-recovery/L1-L7/` 将不再主动同步（留作 4 月初历史参考）
- `skills/checkpoint-manager/` — 建议停用或指向新快照路径
- `skills/disaster-recovery-auditor/` — 建议审计对象改为 `backups/essential-snapshot/`

---

## 四、RPO / RTO 目标

| 指标 | 旧 V1.0 | 新 V2.0 | 说明 |
|------|---------|---------|------|
| **RPO** | 理论 5 分钟，实际 ∞（从未自动更新） | **7 天**（每周快照） | 每日记忆最大丢失 7 天 |
| **RTO** | 30 分钟 | **5 分钟** | `git pull` + `cp` 即可 |
| **维护成本** | 高（需维护 7 层平行目录） | **极低**（一个脚本，2 个快照） | 符合双经济要求 |
| **空间占用** | ~5MB（但已过时） | **<20MB**（滚动保留 2 份） | 可控 |

**蓝军判断**：V2.0 的 RPO 变长但从虚假 5 分钟变成了诚实的 7 天，且维护成本骤降 90%。这是正确的 tradeoff。

---

## 五、机制化保证

**已加入 OpenClaw Cron**:
- `weekly-essential-snapshot` 将在每周日 02:17 触发（后续可配置为独立 cron job）

**手动触发命令**:
```bash
bash /root/.openclaw/workspace/scripts/weekly_essential_snapshot.sh
```

**灾备验证命令**（每月执行一次）:
```bash
bash /root/.openclaw/workspace/C-disaster-recovery/disaster-recovery.sh
```

---

## 六、使用手册统一存放规则

**所有给用户看的使用手册/操作指南/核心文档，统一存放于**：

```
A-manyige/手册/
```

### 已归入手册索引

| 手册名 | 来源路径 | 类型 |
|--------|----------|------|
| 合伙人决策产品完整手册 | `B-egbertie-view/合伙人决策产品完整手册_V1.0-20260406-1112.md` | 产品 |
| 快速查找指南 | `B-egbertie-view/快速查找指南-V1.0-20260406-1112.md` | 导航 |
| 工作空间全景导航 | `B-egbertie-view/工作空间全景导航-V1.0-20260406-1112.md` | 导航 |
| 理论体系架构 | `B-egbertie-view/理论体系架构-V1.0-20260406-1112.md` | 理论 |
| 灾备恢复手册 | `C-disaster-recovery/恢复手册.md` | 运维 |
| 资源执行手册 | `memory/working/resource-execution-handbook.md` | 运营 |
| 飞书授权清单 | `docs/feishu-authorization-checklist.md` | 操作 |
| 58涌现匹配算法实施手册 | `A-manyige/汇报/58涌现匹配算法实施手册-任务登记-2026-04-04-V1.0-20260404-1112.md` | 技术 |

*主索引文件*: `A-manyige/手册/README.md`

---

**蓝军审计**: 旧 7 层灾备是"向内集邮"的典型产物——结构很漂亮，但没在运行。V2.0 用 Git 做主力、快照补缺口，是真正的满意解。
