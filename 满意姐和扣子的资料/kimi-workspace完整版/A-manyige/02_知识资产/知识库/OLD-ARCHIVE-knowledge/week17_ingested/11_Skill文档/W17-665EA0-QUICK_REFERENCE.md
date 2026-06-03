---
# 知识元数据 (5标准化)
knowledge_id: W17-665EA0
title: Tiered Output System - Quick Reference
category: 11_Skill文档
source: skills/tiered-output/QUICK_REFERENCE.md
ingested_at: 2026-03-27 17:59:30
word_count: 1118
week: 17
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Tiered Output System - Quick Reference

> **知识ID**: W17-665EA0  
> **分类**: 11_Skill文档  
> **来源**: `skills/tiered-output/QUICK_REFERENCE.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Tiered Output System - Quick Reference

## 快速参考卡片

### 用户指令

| 指令 | 输出级别 | 说明 |
|------|----------|------|
| `/brief` 或 `/b` | L1 极简版 | 一句话，<50 tokens |
| `/normal` 或 `/n` | L2 标准版 | 一段话，200-500 tokens |
| `/detail` 或 `/d` | L3 详细版 | 深度分析，1000+ tokens |
| `/expand` | - | 展开上一条为详细版 |

### 三级输出对比

```
┌─────────────────────────────────────────────────────────────┐
│ L1 极简版                     │ L2 标准版      │ L3 详细版  │
├─────────────────────────────────────────────────────────────┤
│ ✅ 任务已完成。建议检查邮件。 │ 摘要+3发现+行动 │ 完整报告  │
│ ~30 tokens                    │ ~350 tokens    │ ~1500 tok │
│ <1秒响应                      │ <3秒响应       │ <10秒响应 │
└─────────────────────────────────────────────────────────────┘
```

### Token预算触发

| 预算状态 | 行为 |
|----------|------|
| >70% | 正常模式 |
| 30-70% | 默认L2 |
| <30% | 强制L1 |
| <10% | L1 + 警告 |

### 优先级映射

| 优先级 | 默认级别 |
|--------|----------|
| P0 | L2 (复杂分析用L3) |
| P1 | L2 |
| P2 | L2 |
| P3 | L1 |

### 文件位置

- 系统文档: `docs/TIERED_OUTPUT_SYSTEM.md`
- 配置文件: `skills/tiered-output/config.yaml`
- 测试脚本: `skills/tiered-output/tests/test_validation.py`

---
*分级输出系统 v1.0 | 2026-03-21*
