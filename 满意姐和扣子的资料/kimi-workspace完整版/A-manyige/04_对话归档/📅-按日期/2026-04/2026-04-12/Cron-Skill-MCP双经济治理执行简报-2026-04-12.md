# Cron+Skill+MCP 双经济治理执行简报（4-12 即时动作）

> **时间**: 2026-04-12 12:30  
> **状态**: 根因排查后，已启动 P0 即时治理动作  
> **Token**: 84%

---

## 一、已完成的即时治理动作

### 1.1 Disabled Cron 物理清理（P0-AC-01）

**动作**: 将 `~/.openclaw/cron/jobs.json` 中 61 个已禁用的 cron 任务物理移除，仅保留 7 个启用任务。

- **清理前**: 68 个任务（7 启用，61 禁用）
- **清理后**: 7 个任务（全部启用）
- **备份**: `jobs.json.bak-2026-04-12` + `removed_crons_2026-04-12.json`

**效果**: Gateway 解析 cron 调度器时的内存负担立即降低。特别是移除了"每小时任务协调检查"（disabled 但 lastDurationMs=382秒）等高风险 agentTurn 僵尸任务。

### 1.2 Skills 大体积目录归档（P0-AC-03 第一步）

**动作**: 将 12 个大型、非核心的 skill 目录移动到 `skills-archive/`。

已移动目录:
- `testing-framework` (3.8MB)
- `tencent-news` (8.1MB)
- `lb-nextjs16-skill` (3.5MB)
- `api-gateway` (1.7MB)
- `ui-ux-pro-max` (1.2MB)
- `universal-task-executor-v3` (1.1MB)
- `tencent-channel-community` (1.1MB)
- `kubernetes` (788KB)
- `swarm` (572KB)
- `evolver` (860KB)
- `scry` (788KB)
- `super-knowledge-ingest` (916KB)

- **移动前**: skills 目录总大小 ~78MB，453 个子目录
- **移动后**: skills 目录总大小 ~54MB，441 个子目录

**注意**: 从 441 进一步收敛到 <150 个需要更深度的小体积 skill 清理，将在明日低峰期继续。

---

## 二、尚未执行但已排期的治理项

| 编号 | 任务 | 状态 | 计划时间 |
|:----:|:-----|:----:|:--------:|
| AC-03 续 | Skills 小体积目录深度清理（441 → <150） | 待执行 | 4-13 |
| AC-02 | 建立 `capability-registry.json` | 待执行 | 4-14 |
| AC-04 | 为 Tier 1/2 cron 启用 `--stagger` | 待执行 | 4-13 |
| AC-05 | agentTurn cron 绑定低消耗模型 | 待执行 | 4-14 |
| AC-06 | MCP 健康监控脚本 | 待执行 | 4-16 |
| M-02 | AGENTS.md 压缩（根治内存泄漏 P0） | 待执行 | 4-13 |

---

## 三、当前系统状态（治理后）

| 指标 | 治理前 | 治理后 | 备注 |
|------|--------|--------|------|
| Cron 总数 | 68 | **7** | 僵尸任务已清除 |
| Skills 目录数 | 453 | **441** | 第一批大地 skill 已归档 |
| Skills 总大小 | ~78MB | **54MB** | 释放 24MB |
| Gateway RSS | 1155 MB | 待重启后观测 | 需配合 AGENTS 压缩 + 重启验证 |

---

## 四、下一步动作

1. **4-13 上午**: 完成 skills 小目录深度清理（441 → <150）+ AGENTS.md 压缩
2. **4-13 下午**: 重启 Gateway，观测 24 小时内存曲线
3. **4-14**: 提交《内存泄漏根治效果验证报告》

---

*蓝军签章：即时治理动作已完成，僵尸 cron 已清除，大地 skill 已归档。剩余工作排入明日执行队列。*
