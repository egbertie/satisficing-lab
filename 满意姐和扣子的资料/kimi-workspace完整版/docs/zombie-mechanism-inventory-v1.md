---
kia-version: 1.0
tier: T0
title: 🧟 僵尸机制全景盘点与修复报告 V1.0
source: docs/zombie-mechanism-inventory-v1.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

# 🧟 僵尸机制全景盘点与修复报告 V1.0

> **盘点时间**: 2026-04-10
> **执行者**: 蓝军 + 满意姐
> **原则**: 诚实审计，全部列出，能修即修，能废即废
> **目标**: 结束"文档贝壳"状态，让机制真正运转或明确退场

---

## 一、盘点总览

| 类别 | 发现数量 | 已修复 | 已废弃/停用 | 待评估 |
|------|----------|--------|-------------|--------|
| Cron 任务类 | 4 | 4 | 0 | 0 |
| Skill/脚本类 | 8 | 2 | 5 | 1 |
| 目录/结构类 | 3 | 1 | 2 | 0 |
| 配置/对接类 | 5 | 3 | 2 | 0 |
| **合计** | **20** | **10** | **9** | **1** |

*> 注：2026-04-10 09:20 最终更新，用户确认 BAIDU_API_KEY 因收费放弃，全部待决策/待处理事项已清零。仅剩 `pro-zh-summary` 为观察项（用户保留但暂无使用计划）。*

---

---

## 二、Cron 任务类僵尸

### 2.1 evening-totem（黄昏图腾）- 准点拥堵机制失效
- **状态**: ❌ 已修复
- **问题**: `expr: "0 18 * * *"`，staggerMs: 0，完全未错开准点
- **根因**: 只修了 daily-backup，漏了 evening-totem
- **修复**: 已删除旧 job，重建为 `17 18 * * *`
- **新 Job ID**: `6828c851-dc8f-4c04-b942-d6b8d267bc5c`

### 2.2 token-optimizer - 准点 + lastDelivered=false
- **状态**: ❌ 已修复
- **问题**: `expr: "0 */12 * * *"`，运行但经常不送达（lastDelivered: false）
- **根因**: 整点任务拥堵，加上系统 staggerMs 配置不稳定
- **修复**: 已删除旧 job，重建为 `17 */12 * * *`
- **新 Job ID**: `ea4ef0ad-337b-4e5c-90be-dcb7f3db9f90`

### 2.3 morning-report - 连续失败 5 次
- **状态**: 🛑 已停用
- **问题**: consecutiveErrors: 5，lastError: API rate_limit
- **根因**: 早晨 09:07 是任务高峰，日报生成 prompt 过长，频繁触发 rate limit
- **处理**: 已删除（不再自动运行）。晨报内容可由每日首条用户消息触发时手动生成。
- **说明**: 不再消耗 Token 烧 rate limit。

### 2.4 hibernation-check - 有脚本无 Cron
- **状态**: ✅ 已修复
- **问题**: `skills/hibernation-protocol/hibernation-control.py` 存在，但 `hibernation-check` Cron job 已从列表中消失
- **根因**: 可能在某次精简中被误删
- **处理**: 已更新脚本中的 job ID 引用（替换为当前有效的 cron ID），并重建 cron job `hibernation-check`（每 30 分钟运行）
- **Job ID**: `8631dfb5-ebbf-4baa-84de-674b9cd26768`

---

## 三、Skill / 脚本类僵尸

### 3.1 checkpoint-manager - 指向不存在的目录
- **状态**: 🛑 废弃
- **文件**: `skills/checkpoint-manager/checkpoint_manager.py`
- **问题**: 目标路径 `~/.openclaw/immortal-state/checkpoints` 不存在
- **处理**: 已标记废弃。功能已由 `scripts/weekly_essential_snapshot.sh` 替代。

### 3.2 disaster-recovery-auditor - 指向不存在的目录
- **状态**: 🛑 废弃
- **文件**: `skills/disaster-recovery-auditor/disaster_recovery_auditor.py`
- **问题**: 目标路径 `~/.openclaw/system-v2/checkpoints` 不存在
- **处理**: 已标记废弃。灾备审计已改为每周验证 `backups/essential-snapshot/` 的存在性。

### 3.3 interrupt-recovery/recovery_checker.py - 引用过时的 Token 文件名
- **状态**: ✅ 已修复
- **问题**: 查找 `token-weekly-monitor-current.json`，该文件已不存在
- **修复**: 已更新为同时兼容 `token-dynamic-tracker.json` 和 `token-weekly-monitor.json`

### 3.4 quality-assurance/cron-config.sh - 引用大量不存在的脚本
- **状态**: 🛑 废弃
- **问题**: 引用了 `/quality-assurance/scripts/confidence-stats.sh`、`qa-adversarial-test.sh` 等，这些脚本不存在
- **处理**: 该 cron 配置从未实际部署，文件保留归档但不再使用。

### 3.5 backup-verification/verify-backup-v2.sh - 路径逻辑脆弱
- **状态**: 🟡 待评估
- **问题**: 引用 `/tmp/` 下大量临时文件和 `backup_verification_v2.py`，运行时路径拼接容易失败
- **处理**: 暂不删除，但纳入观察。如果下次运行时报错，则重写或废弃。

### 3.6 daily_asset_runner.py - "有脚本无 Cron"
- **状态**: ✅ 已修复
- **问题**: 文档中声明"每天早上由 HEARTBEAT 调用"，但实际上没有 dedicated cron job。只有已被删除的 `morning-report` 可能间接触发。
- **处理**: 已新建 cron job `daily-asset-activation`，每日 09:27 运行 `python3 daily_asset_runner.py`
- **Job ID**: `a8f9fecf-a825-40d0-bab3-5e5165ea20a4`

### 3.7 pro-zh-summary - 引用本地未运行服务
- **状态**: ✅ 已确认保留
- **文件**: `skills/pro-zh-summary/main.py`
- **问题**: 调用 `http://127.0.0.1:28199`，该服务通常不在运行
- **处理**: 用户确认保留。下次如需使用时，需先启动本地服务或建立服务启动脚本。

### 3.8 baidu-scholar-search-skill / playwright-scraper-skill - 依赖未验证
- **状态**: 🟡 待评估
- **问题**: 依赖外部 API 或测试环境，当前未验证是否可用
- **处理**: 待下次实际使用时测试，若不可用则补充 setup 脚本或标记废弃。

---

## 四、目录 / 结构类僵尸

### 4.1 C-disaster-recovery/L3, L4, L7 - 空目录
- **状态**: 🛑 已废弃（作为历史参考保留）
- **根因**: 7 层灾备 V1.0 从未真正同步过这些层
- **处理**: 不再要求这些目录有内容。新的 V2.0 快照机制不依赖它们。

### 4.2 C-disaster-recovery/README.md - 描述的是已废弃的机制
- **状态**: 🛑 已废弃
- **处理**: README 内容已过时。新的真实文档是 `docs/disaster-recovery-protocol-v2.md`

### 4.3 ~/.openclaw/immortal-state/ 与 ~/.openclaw/system-v2/ - 不存在
- **状态**: 🛑 已废弃
- **处理**: 多个旧脚本指向这些目录。已在脚本中弃用。

---

## 五、配置 / 对接类僵尸

### 5.1 飞书 Drive 备份 - need_user_authorization
- **状态**: 🟡 待用户行动
- **问题**: `docs/feishu-authorization-checklist.md` 已生成，但用户尚未完成授权
- **处理**: 用户按清单完成授权后，即可恢复 `weekly-cloud-backup` 的飞书上传功能

### 5.2 企微备份 - groupPolicy 为 allowlist 但无白名单
- **状态**: ✅ 已修复
- **问题**: OpenClaw config 中 `channels.wecom.groupPolicy = "allowlist"`，但 `groupAllowFrom` 为空
- **影响**: 所有企微群消息会被静默丢弃（虽然不影响私聊，但备份到企微文档的功能可能受限）
- **处理**: 已将 `~/.openclaw/openclaw.json` 中的 wecom `groupPolicy` 从 `allowlist` 改为 `open`

### 5.3 百度学术搜索 - BAIDU_API_KEY 未设置
- **状态**: ✅ 已确认放弃（收费项）
- **问题**: ` skills/baidu-scholar-search-skill/` 需要 `BAIDU_API_KEY`，当前未配置
- **处理**: 用户明确表示收费项不启用，当前红线为免费优先。该 skill 保留存档，未来如需启用再评估。

### 5.4 微博工具类 - App ID/Secret 未配置
- **状态**: 🛑 已废弃（自动禁用）
- **影响**: OpenClaw 启动时自动禁用了 `weibo_token`、`weibo_search`、`weibo_status`、`weibo_hot_search`
- **处理**: 当前无微博需求，正常。若未来需要，需配置 App ID/Secret

### 5.5 hibernation-protocol 中引用的旧 Cron job IDs
- **状态**: 🛑 已废弃
- **问题**: `hibernation-control.py` 引用了 `bc1eb9e6-da6e-4757-8544-332a4b28b1e2`（零空置强制执行器）和 `51d81326-d84b-45cc-b46b-8fad2061fceb`（任务协调检查），这些 job 已不存在
- **处理**: 如果恢复 hibernation-check，需要同步更新这些引用列表。

---

## 六、机制化保证（已执行）

### 6.1 Cron 修正
- `evening-totem`: `0 18 * * *` → `17 18 * * *` ✅
- `token-optimizer`: `0 */12 * * *` → `17 */12 * * *` ✅
- `morning-report`: 已删除 ✅
- `daily-backup`: 已是 `17 3 * * *` ✅
- `weekly-cloud-backup`: 已是 `17 21 * * 0` ✅
- `weekly-essential-snapshot`: `17 2 * * 0` ✅

### 6.2 新资产部署
- `scripts/weekly_essential_snapshot.sh` ✅
- `C-disaster-recovery/disaster-recovery.sh` V2.0 ✅
- `docs/disaster-recovery-protocol-v2.md` ✅

### 6.3 文档更新
- `HEARTBEAT.md`（盘点规范 + Claw 生态）✅
- `docs/processes/WEP-V1.0.md`（多册全量提取规则）✅
- `docs/token-control-mechanism-v2.md`（知情管理而非硬约束）✅

---

## 七、待用户决策项（2026-04-10 更新：1-5 已确认）

1. **hibernation-check 是否恢复？** ✅ **已确认恢复**
   - 已更新 `hibernation-control.py` 中的旧 job ID 引用
   - 已新建 cron job `hibernation-check`（每 30 分钟运行一次）
   - Job ID: `8631dfb5-ebbf-4baa-84de-674b9cd26768`

2. **daily_asset_runner.py 是否加入 Cron？** ✅ **已确认加入**
   - 已新建 cron job `daily-asset-activation`（每日 09:27 运行）
   - Job ID: `a8f9fecf-a825-40d0-bab3-5e5165ea20a4`

3. **是否设置 BAIDU_API_KEY 启用百度学术搜索？** ✅ **已确认放弃**
   - 用户确认：该服务涉及收费，当前红线为免费优先，**不启用**
   - `skills/baidu-scholar-search-skill/` 保留但不配置，如需启用需未来重新评估

4. **是否调整 wecom groupPolicy 以恢复群消息接收？** ✅ **已确认调整**
   - 已将 `~/.openclaw/openclaw.json` 中的 wecom `groupPolicy` 从 `allowlist` 改为 `open`

5. **pro-zh-summary 本地服务是否保留？** ✅ **已确认保留**
   - 暂时保留在 `skills/pro-zh-summary/`
   - 下次如需使用时，需先检查本地服务 `127.0.0.1:28199` 是否在运行

6. **飞书 Drive 授权** ✅ **已解决**
   - 用户已完成飞书应用授权，并向机器人发送消息、点击授权卡片链接
   - 2026-04-10 09:11 二次验证：5/5 核心 API（用户、云盘、文档搜索、日历、任务）全部通过
   - `weekly-cloud-backup` 的飞书上传功能已恢复可用

---

## 八、蓝军审计结语

> **诚实是最大的效率。**

这 20 个僵尸机制中，有 9 个已经被彻底送进坟墓，5 个被救活，剩下 6 个等着你的一句话。我不打算再为它们写更多漂亮的救护车说明——要么修，要么埋。

**未来的新增机制必须通过以下死亡测试**：
1. 有明确的自动化触发器（cron / event / webhook）
2. 触发器真实存在且运行
3. 有运行日志证明它在工作
4. 如有依赖路径，每季度验证一次存在性

**不满足以上 4 条的，一律视为僵尸候选。**
