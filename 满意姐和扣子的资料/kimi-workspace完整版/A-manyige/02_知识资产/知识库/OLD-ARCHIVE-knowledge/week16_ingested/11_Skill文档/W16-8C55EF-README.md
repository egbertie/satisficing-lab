---
# 知识元数据 (5标准化)
knowledge_id: W16-8C55EF
title: Sentinel Guard - 快速使用手册
category: 11_Skill文档
source: skills/sentinel-guard/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 1155
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Sentinel Guard - 快速使用手册

> **知识ID**: W16-8C55EF  
> **分类**: 11_Skill文档  
> **来源**: `skills/sentinel-guard/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Sentinel Guard - 快速使用手册

> 你的OpenClaw系统保镖 - 5标准完整安全防护

---

## 一句话说明

Sentinel Guard 是一套**全自动**的系统安全防护系统，每5分钟检查一次你的OpenClaw系统，发现问题**自动修复**，不需要你操心。

---

## 防护范围

| 风险 | 防护方式 | 频率 |
|------|----------|------|
| 🔴 循环备份 | 自动检测+移动回收站 | 每小时 |
| 🔴 磁盘满 | 自动清理临时文件 | 每5分钟 |
| 🔴 日志膨胀 | 自动轮转+压缩 | 每日 |
| 🟡 僵尸进程 | 自动清理 | 每15分钟 |
| 🟡 CPU滥用 | 自动降优先级 | 每5分钟 |
| 🟡 内存泄漏 | 监控告警 | 每5分钟 |

---

## 查看系统状态

```bash
# 查看最新监控日志（实时）
tail -f /var/log/sentinel/sentinel.log

# 查看当前系统状态
/root/.openclaw/workspace/scripts/sentinel-guard.sh
```

---

## 收到告警时

### 🔴 CRIT 级别（严重）
- 系统已**自动处理**
- 检查处理结果：`tail /var/log/sentinel/sentinel.log`
- 如持续告警，人工介入

### 🟡 ALERT/WARN 级别（警告）
- 系统正在监控
- 可能自动处理（如磁盘清理）
- 观察趋势，如持续恶化则处理

### ✅ OK 级别（正常）
- 一切正常，无需操作

---

## 历史事件

| 时间 | 事件 | 处理 | 结果 |
|------|------|------|------|
| 2026-03-27 | 循环备份20+层 | 自动检测+清理 | ✅ 8.9GB已回收 |
| 2026-03-27 | 日志系统故障 | 手动修复 | ✅ 已恢复 |

---

## 文档索引

| 文档 | 路径 | 用途 |
|------|------|------|
| 完整Skill | `skills/sentinel-guard/SKILL.md` | 技术规范 |
| 5标准验收 | `docs/SENTINEL-GUARD-V1.0-5STANDARD-ACCEPTANCE.md` | 验收报告 |
| 存储安全 | `memory/archive/storage-safety-redline-v1.0.md` | 存储红线 |

---

*Sentinel Guard - 守护你的系统*
