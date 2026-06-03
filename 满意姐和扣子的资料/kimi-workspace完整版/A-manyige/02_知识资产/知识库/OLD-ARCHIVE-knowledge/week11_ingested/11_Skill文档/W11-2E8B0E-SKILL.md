---
# 知识元数据 (5标准化)
knowledge_id: W11-2E8B0E
title: SKILL.md - 信息闭环器
category: 11_Skill文档
source: skills/.archive_info-loop-closer/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1534
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL.md - 信息闭环器

> **知识ID**: W11-2E8B0E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_info-loop-closer/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# SKILL.md - 信息闭环器

> **Skill名称**: info-loop-closer  
> **版本**: V1.0  
> **创建时间**: 2026-03-20  
> **维护者**: 满意妞

---

## 描述

确保所有任务、承诺、安排都有明确的确认、执行汇报和验收闭环。防止"有安排无确认、有执行无汇报、有问题无升级"的信息黑洞。

---

## 触发条件

**自动触发**:
- 新任务被创建时
- 任务状态变更时
- 到达汇报节点时
- 任务逾期时

**手动触发**:
- 用户说"检查信息闭环"
- 用户说"任务汇报"
- 用户说"确认完成情况"

---

## 功能

### 1. 闭环检查 (check_loop)

检查指定任务的信息闭环状态。

**输入**: 任务ID或任务列表  
**输出**: 闭环状态报告

```json
{
  "task_id": "WIP-001",
  "status": "closed",
  "stages": {
    "confirm": {"status": "done", "time": "2026-03-20 10:00"},
    "execute": {"status": "done", "time": "2026-03-20 11:30"},
    "report": {"status": "done", "time": "2026-03-20 12:00"},
    "verify": {"status": "done", "time": "2026-03-20 12:30"}
  },
  "gap": null
}
```

### 2. 汇报生成 (generate_report)

根据任务状态生成标准汇报。

**汇报类型**:
- 启动汇报：目标+标准+时间+节点
- 进度汇报：已完成+进行中+阻塞
- 完成汇报：交付物+验证+质量

### 3. 闭环标记 (mark_closed)

标记任务已完成信息闭环。

### 4. 全局扫描 (global_scan)

扫描所有进行中任务，检查闭环状态。

**输出**: 未闭环任务清单

---

## 使用示例

```python
# 检查单个任务闭环
info-loop-closer check_loop --task WIP-001

# 生成完成汇报
info-loop-closer generate_report --task WIP-001 --type complete

# 标记闭环完成
info-loop-closer mark_closed --task WIP-001

# 全局扫描
info-loop-closer global_scan --status all
```

---

## 依赖

- `wecom_mcp` (企微API)
- `memory_search` (记忆检索)
- `sessions_list` (会话管理)

---

## 约束

- 未闭环任务必须汇报，不能静默
- 汇报必须包含"未完成部分"
- 虚报完成度触发惩罚机制

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-03-20 | 初始版本，四阶段闭环模型 |

---

## 参考

- `docs/INFO_LOOP_ISSUE_REVIEW.md` - 问题检讨与机制设计
- `MEMORY.md#信息闭环机制` - 全局配置