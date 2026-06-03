---
# 知识元数据 (5标准化)
knowledge_id: W16-1E0A14
title: info-collection-quality Skill V5标准版本
category: 11_Skill文档
source: skills/info-collection-quality/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 994
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# info-collection-quality Skill V5标准版本

> **知识ID**: W16-1E0A14  
> **分类**: 11_Skill文档  
> **来源**: `skills/info-collection-quality/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# info-collection-quality Skill V5标准版本

## S1: 全局考虑

### 输入
- 信息采集任务
- 质量标准要求
- 采集来源列表

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 信息采集员、质量审核员 |
| **事** | 信息采集、质量检查、问题标记、改进反馈 |
| **物** | 原始数据、采集记录、质量报告 |
| **环境** | 网络环境、源站稳定性、时间窗口 |
| **外部集成** | 多个信息源、存储系统 |
| **边界情况** | 源站失效、数据缺失、格式混乱 |

---

## S2: 系统考虑

### 处理流程
```
任务分配 → 信息采集 → 实时质检 → 问题标记 → 修复/重采 → 质量报告
```

### 质量检查点
1. 完整性 - 字段是否齐全
2. 准确性 - 数据是否正确
3. 一致性 - 格式是否统一
4. 时效性 - 数据是否最新
5. 可追溯 - 来源是否记录

---

## S3: 输出规范

### 质量报告
```json
{
  "task_id": "...",
  "collected": 100,
  "passed": 95,
  "failed": 5,
  "quality_score": 95,
  "issues": [
    {"item": "...", "issue": "字段缺失", "severity": "medium"}
  ]
}
```

---

## S4: 自动化集成

### 自动检查
- 格式校验
- 必填项检查
- 范围检查
- 重复检测

---

## S5: 自我验证

### 质量指标
- 采集成功率: >95%
- 质检准确率: >90%
- 问题闭环率: >95%

---

## S6: 认知谦逊

### 局限
- 无法判断业务逻辑正确性
- 依赖规则配置完整性
- 新类型问题可能漏检

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| 源站全部失效 | 标记失败，尝试备用源 |
| 数据格式突变 | 记录异常，人工介入 |
| 大规模缺失 | 批量重采，告警 |
