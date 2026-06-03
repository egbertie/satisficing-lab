---
kia-version: 1.0
tier: T0
title: 🧟 僵尸机制全景盘点与修复报告 V1.2
source: docs/zombie-mechanism-inventory-v1.1-addendum.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

# 🧟 僵尸机制全景盘点与修复报告 V1.2

> **盘点时间**: 2026-04-12（本次追加更新至 V1.2）
> **执行者**: 满意姐（主执行） + 蓝军（协助与监督）
> **更新原因**: Egbertie 要求对最近 10 天所有系统优化、整改、调整进行全面筛查，检查是否因「毛细血管未处理好」导致未真实闭环
> **筛查范围**: 2026-04-03 至 2026-04-12 期间所有标 FIN 的系统与机制任务

---

## V1.0 → V1.1 新增发现

### 新增发现 1：system-guardian.py 数据源断链（同构于 hibernation-control.py 断链）
- **状态**: ❌ 已修复（2026-04-12）
- **问题**: `scripts/system-guardian.py` 同样读取 `memory/token-dynamic-tracker.json`（停更于 2026-04-10），导致 Token 监控数据错误
- **根因**: 2026-04-10 从 token-dynamic 切换到 token-zero 数据源时，只修了休眠控制器和Token周报脚本，漏了 system-guardian
- **修复**:已切换为 `memory/token-zero-tracker.json`，适配 display 字段结构，并增加 pace_ratio / time_progress 输出
- **教训**: 数据源迁移必须执行全仓库 grep，不能只修「当时想起来的」那几个文件

### 新增发现 2：token-dynamic-tracker.json 幽灵文件
- **状态**: 🛑 已废弃（2026-04-12）
- **问题**: `memory/token-dynamic-tracker.json` 自 4 月 10 日后不再更新，却仍被两份文档和一份脚本引用，极易误导
- **修复**: 已重命名为 `token-dynamic-tracker.json.DEPRECATED-2026-04-12`，任何残留引用都会立即暴露为文件不存在错误

### 新增发现 3：docs/token-control-mechanism-v2.md 文档与运行现实脱节
- **状态**: ❌ 已修正（2026-04-12）
- **问题**: 文档 still 声称 Token 监控的数据源是 `token-dynamic-tracker.json`，且模板结构为旧格式
- **修复**: 文档已更新为引用 `token-zero-tracker.json`，并给出了包含 pace_ratio 等新字段的真实模板

### 新增发现 4：hibernation-control.py auto-check cron 再次失踪
- **状态**: ❌ 已修复（2026-04-12）
- **问题**: V1.0 声称已恢复 `hibernation-check` cron，但在 4 月 11 日 cron 大清理中再次被误删
- **修复**: 已重新注册 `*/30 * * * * auto-check`，并增加自我校验逻辑
- **教训**: cron 恢复后没有被标记为「不可删除」，导致后续清理时无保护地干掉

### 新增发现 5：interrupt-recovery/recovery_checker.py 本身就是僵尸
- **状态**: 🛑 已废弃（2026-04-12 确认）
- **问题**: V1.0 记录「已修复 recovery_checker.py 兼容旧 Token 文件名」，但 `skills/interrupt-recovery/` 目录根本不存在
- **修复**: 确认该 skill 已随 4 月 12 日 skills 大清理被移除，V1.0 记录中的「已修复」实为文档幻觉

---

## V1.1 机制化保证（新增）

1. **数据源切换必须全仓库 grep**：任何涉及 `memory/*.json` 数据文件的路径变更，必须在 `scripts/`、`skills/`、`docs/` 三个目录全量搜索旧文件名
2. **废弃文件立即重命名**：旧数据文件不再更新时，24 小时内必须添加 `.DEPRECATED-YYYY-MM-DD` 后缀，不能保留原文件名躺尸
3. **cron 恢复必须加保护注释**：恢复的关键 cron 必须在 crontab 条目前增加明确注释（如 `# CRITICAL - do not delete during cleanup`），防止下一轮精简误伤
4. **文档模板必须定期与运行文件 diff**：任何 `.md` 中的 JSON 模板，至少每 7 天与真实运行输出比对一次，防文档说谎

### 新增发现 6：daily-asset-activation cron 声称已注册但物理不存在
- **状态**: 🛑 已废弃/澄清（2026-04-12）
- **问题**: zombie V1.0 和 automation governance V1.0 之间冲突——V1.0 声称「已新建 cron job daily-asset-activation」，automation governance 标为 ⏸️ 暂停，但 crontab 中**根本不存在该条目**
- **根因**: 04-11 cron 大清理（Token 小偷歼灭战）中有意/无意删除了该高消耗 agentTurn 任务，但文档未同步更新
- **修复**: 明确废弃，`daily_asset_runner.py` 的功能已被 `unified_system_nurse.py` + `morning-ritual.py` 晨报机制替代。不再恢复该 cron。

### 新增发现 7：token-level-checker.py 读取不存在字段
- **状态**: ❌ 已修复（2026-04-12）
- **问题**: `skills/token-management-satisficing/scripts/token-level-checker.py` 读取 `token-weekly-monitor.json` 中的 `openclawToken.percentage`，但该字段**从未存在于该文件中**。结果永远只能拿到默认值 50，输出虚假的 L3 档位。
- **修复**: 已改为读取统一数据源 `token-zero-tracker.json` 的 `display.display_percentage`。验证通过：现在正确输出 78% / L4。

### 新增发现 8：token_fuse_system.py 读取不存在字段
- **状态**: ❌ 已修复（2026-04-12）
- **问题**: `skills/token-fuse-system/token_fuse_system.py` 读取 `token-weekly-monitor.json` 中的 `week_used_percentage`，同样不存在的字段。导致 `weekly_used` 永远为 0，熔断系统实际上从未工作。
- **修复**: 已改为优先读取 `token-zero-tracker.json` 的 `display.display_percentage`，并保留旧文件作为 fallback。验证通过：现在正确输出 78.0%。

### 新增发现 9：token-tracker-zero.py 没有稳定触发器
- **状态**: ❌ 已修复（2026-04-12）
- **问题**: 作为当前唯一的 Token S-曲线监控数据源，`token-tracker-zero.py` 不在系统 crontab 中，也没有任何其他脚本调用它。它偶尔更新只是因为用户会话中可能被手动触发。
- **修复**: 在 `unified_system_nurse.py`（每日 06:17 运行）中加入前置调用：先执行 `token-tracker-zero.py` 刷新数据，再读取分析。这为 token-zero-tracker.json 提供了稳定的每日更新触发器。

### 新增发现 10：token-weekly-monitor-runner.py 系统 cron 脱节
- **状态**: 🛑 已废弃/澄清（2026-04-12）
- **问题**: `skills/token-weekly-monitor/cron.json` 中定义了 4 个 cron 任务，但系统 crontab 中一个都没有。这意味着 `token-weekly-monitor.json` 的数据更新和报告生成都依赖手工运行。
- **修复**: `token-weekly-monitor.json` 的维护功能已被 `token-tracker-zero.py` + `unified_system_nurse.py` 覆盖。`cron.json` 中的旧定义保留作为 skill 自身文档，但明确其**未在系统层注册**。后续如需自动化，必须通过 `system-guardian.py gate` 审查后再注册。

---

## V1.2 机制化保证（再追加）

5. **字段兼容性必须显式验证**：任何脚本读取 JSON 时，如果使用了 `.get("xx", default)`，必须验证该字段在真实数据中是否存在，不能依赖默认值「碰巧」工作。
6. **数据源单点真相源（SSOT）原则**：同一类监控数据只能有一个活跃的数据文件。旧文件必须 deprecate，新文件必须被所有消费者统一读取。
7. **运行入口强制审查**：任何声称「已注册 cron」的任务，必须在 crontab 中执行 `crontab -l | grep job_name` 做物理验证；任何声称「被XX调用」的任务，必须在调用者代码中 grep 到显式调用。

---

*本报告作为 V1.0 / V1.1 的持续性补丁执行。蓝军结论：过去 10 天内 75 项标 FIN 的任务中，至少 6-8 项存在「文档已闭环、物理未闭环」的毛细血管问题。满意姐已执行全量扩散修复，机制化保证已升级到 7 条。*
