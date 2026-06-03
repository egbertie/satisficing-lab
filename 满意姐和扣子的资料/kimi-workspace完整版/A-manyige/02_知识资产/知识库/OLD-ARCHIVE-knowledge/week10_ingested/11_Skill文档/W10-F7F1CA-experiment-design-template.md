---
# 知识元数据 (5标准化)
knowledge_id: W10-F7F1CA
title: 实验设计模板
category: 11_Skill文档
source: skills/.archive_evolution-experiment-lab/templates/experiment-design-template.md
ingested_at: 2026-03-27 17:59:30
word_count: 564
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 实验设计模板

> **知识ID**: W10-F7F1CA  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_evolution-experiment-lab/templates/experiment-design-template.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 实验设计模板

## 基本信息
- 实验ID: {{exp_id}}
- 实验名称: {{name}}
- 创建时间: {{created_at}}

## 实验目标
### 要验证的假设
{{hypothesis}}

### 预期收益
{{expected_benefits}}

## 成功指标
| 指标 | 当前值 | 目标值 | 测量方式 |
|------|--------|--------|----------|
{{metrics_table}}

## 实验方案
### 具体实施步骤
{{steps}}

### 影响范围
{{impact_scope}}

### 风险评估
| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
{{risks_table}}

## 实验计划
| 阶段 | 时间 | 产出 |
|------|------|------|
{{schedule_table}}

## 回滚计划
- 回滚触发条件: {{rollback_trigger}}
- 回滚步骤: {{rollback_steps}}
- 预计回滚时间: {{rollback_time}}

---
*状态: {{status}}*
