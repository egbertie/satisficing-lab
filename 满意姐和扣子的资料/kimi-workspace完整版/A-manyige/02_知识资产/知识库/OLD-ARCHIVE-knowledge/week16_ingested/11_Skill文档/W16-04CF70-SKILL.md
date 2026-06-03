---
# 知识元数据 (5标准化)
knowledge_id: W16-04CF70
title: sync-manager Skill V5标准版本
category: 11_Skill文档
source: skills/sync-manager/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1128
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# sync-manager Skill V5标准版本

> **知识ID**: W16-04CF70  
> **分类**: 11_Skill文档  
> **来源**: `skills/sync-manager/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# sync-manager Skill V5标准版本

## S1: 全局考虑

### 输入
- 同步源和目标配置
- 同步模式（全量/增量）
- 冲突解决策略

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 数据管理员、开发者 |
| **事** | 数据同步、冲突处理、一致性维护 |
| **物** | 数据源、目标端、同步日志 |
| **环境** | 网络环境、时区差异 |
| **外部集成** | Notion、飞书、本地文件等 |
| **边界情况** | 网络中断、数据冲突、权限不足 |

---

## S2: 系统考虑

### 处理流程
```
扫描变更 → 对比差异 → 冲突检测 → 策略处理 → 执行同步 → 记录日志
```

### 故障处理
- **网络中断**: 记录断点，恢复后继续
- **数据冲突**: 按策略处理（最新优先/人工裁决）
- **权限不足**: 记录错误，跳过并告警

---

## S3: 输出规范

### 同步报告
```json
{
  "sync_id": "sync_xxx",
  "timestamp": "2026-03-22T09:00:00+08:00",
  "source": "notion",
  "target": "local",
  "mode": "incremental",
  "changes": {
    "added": 10,
    "updated": 5,
    "deleted": 2,
    "conflicts": 1
  },
  "status": "success|partial|failed"
}
```

---

## S4: 自动化集成

### 同步模式
| 模式 | 说明 |
|------|------|
| 全量 | 完整重新同步 |
| 增量 | 仅同步变更 |
| 定时 | 按计划执行 |
| 实时 | 监听变更立即同步 |

---

## S5: 自我验证

### 质量指标
- 同步成功率: >95%
- 数据一致性: 100%
- 冲突解决率: >90%

---

## S6: 认知谦逊

### 局限
- 依赖外部服务可用性
- 复杂冲突需人工介入
- 实时同步有延迟

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| 网络中断 | 断点续传 |
| 大量变更 | 分批处理 |
| 循环依赖 | 检测并中断 |
| 目标不可写 | 记录并重试 |
