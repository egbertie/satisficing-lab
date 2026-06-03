---
name: checkpoint-archivist
description: |
  断点存档技能 — 将灾备永生协议的7层状态栈简化为日常可执行的轻量存档流程。
  在每次会话结束、任务中断、系统休眠前，快速保存当前工作状态，确保重启后可恢复。
  当用户说"我去忙了""先这样""休眠""暂停"、当长任务需要中途保存、
  当系统即将进入静默模式时强制激活。
  触发词："存档" / "保存状态" / "休眠" / "暂停" / "断点" / "checkpoint" / 
  "我去忙了" / "先这样" / "重启恢复" / "恢复工作"
---

# Checkpoint Archivist — 断点存档工程师

> **来源**: 灾备永生协议（7层状态栈 / 3-2-1-1-0备份法则）
> **简化原则**: 从月度灾备级降到日常会话级，从7层全量降到3层核心

## 核心原则

**不是"等有空了再整理"，是"每次中断前30秒自动执行"。**

存档的目的不是完美归档，是**重启后能继续**。

---

## 轻量存档协议（3层核心，30秒完成）

### Layer A: 运行时上下文（10秒）

**保存内容**：
```json
{
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "session_id": "{current}",
  "active_task": "{当前正在做的任务}",
  "current_unit": "{执行到哪个单元}",
  "pending_units": ["U3", "U4", "U5"],
  "last_deliverable": "{最后交付物的路径}",
  "open_questions": ["{未解决的问题}"],
  "user_intent_queue": ["{用户排队待处理的需求}"]
}
```

**保存路径**：
```
A-manyige/对话/YYYY-MM-DD/checkpoint-{timestamp}.json
```

**工具**：`write` 工具写入JSON

---

### Layer B: 关键交付物快照（15秒）

**保存内容**：
1. 当前任务的所有交付物路径清单
2. 每个交付物的最后修改时间
3. 快速验证每个文件存在且非空

**保存路径**：
```
A-manyige/对话/YYYY-MM-DD/deliverables-snapshot-{timestamp}.md
```

**格式**：
```markdown
# 交付物快照 - YYYY-MM-DD HH:MM

| 序号 | 文件名 | 路径 | 大小 | 状态 |
|------|--------|------|------|------|
| 1 | 技能系列总纲 | skills/dual-economy-auditor/SKILL.md | 2.6KB | ✅ |
| 2 | FIN验证器 | skills/fin-honesty-validator/SKILL.md | 3.2KB | ✅ |

[未完成任务]
- 任务A: 进行到U3，剩余U4-U6
- 任务B: 等待用户确认
```

**工具**：`exec` 工具执行 `ls -la` + `wc -c` 验证

---

### Layer C: 记忆指针（5秒）

**保存内容**：
1. MEMORY.md 最后更新的关键条目
2. 今日memory文件是否已追加
3. 关键决策的编号和状态

**保存路径**：
```
memory/checkpoint-memory-pointer-{timestamp}.md
```

**格式**：
```markdown
# 记忆指针 - YYYY-MM-DD HH:MM

[MEMORY.md 最新指针]
- 最后关键条目: {内容摘要}
- 哈希锚点: {hash}

[今日Memory]
- 文件: memory/YYYY-MM-DD.md
- 状态: ✅ 已追加 / ❌ 待追加

[关键决策状态]
- DEC-XXX: {状态}

[下次恢复入口]
1. 读取 checkpoint-{timestamp}.json
2. 读取 deliverables-snapshot
3. 确认 memory 已同步
```

---

## 存档触发条件

**自动触发**（满足任一）：
- 用户说"我去忙了""先这样""休眠""暂停"
- 连续10分钟无交互且有待完成任务
- 系统进入L2/L3/L4休眠模式前
- 长任务完成一个单元后（已有task-resumption-guard覆盖）

**手动触发**：
- 用户明确说"存档""保存状态"

---

## 断点恢复协议

### 恢复时执行（重启后）

1. **读取最新checkpoint** — 找到最后存档的JSON
2. **验证交付物** — 确认snapshot中的文件存在且完整
3. **同步记忆** — 确认MEMORY.md指针已同步
4. **汇报状态** — 给用户清晰的恢复摘要

**恢复汇报格式**：
```
🔄 状态恢复完成
━━━━━━━━━━━━━━━━━━━━
断点时间: YYYY-MM-DD HH:MM
恢复时间: YYYY-MM-DD HH:MM

[中断前状态]
正在执行: {任务名}
当前位置: {单元编号}
已完成: {X}/{N} ({百分比}%)

[交付物验证]
✅ 文件1: {路径}
✅ 文件2: {路径}
🟡 文件3: {路径} — 最后修改时间异常

[待处理队列]
1. {未完成任务}
2. {用户排队需求}

[建议下一步]
→ 继续执行: {下一单元}
→ 或: {其他建议}
━━━━━━━━━━━━━━━━━━━━
```

---

## 快速存档命令（一键执行）

```bash
# 一键存档脚本（可由cron或手动触发）
python3 scripts/quick-checkpoint.py \
  --task "{任务名}" \
  --unit "{当前单元}" \
  --deliverables "{文件1,文件2,文件3}"
```

**输出**：
- checkpoint-{timestamp}.json
- deliverables-snapshot-{timestamp}.md
- memory-pointer-{timestamp}.md

---

## 反模式

❌ "等做完再一起存档" — 中断可能发生在"做完"之前
❌ 只存对话不存文件 — 文件才是交付物
❌ 存档路径随意 — 统一路径才能找到
❌ 恢复时不验证 — 直接继续可能导致基于不完整信息执行
❌ 存档后不做Git提交 — 文件系统级存档不等于版本控制

---

## 最佳实践

✅ **中断即存档**，不问"需不需要"
✅ **存档后立即Git提交**（哪怕是小提交）
✅ **恢复时先验证，后继续**
✅ **给用户一个明确的"已存档"确认**
✅ **定期检查存档文件的可读性**（防止格式损坏）

---

## 关联技能

- `task-resumption-guard` — 长任务的进度追踪与断点续作
- `memory-sync-protocol` — C1-C6静默前置条件的记忆同步
- `disaster-recovery` — 月度级的全量灾备（7层状态栈完整版）

---

*"存档的目的不是完美归档，是重启后能继续。"*
*"30秒的轻量存档 > 30分钟的完美归档（如果前者做了后者没做）。"*
