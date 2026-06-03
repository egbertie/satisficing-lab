---
# 知识元数据 (5标准化)
knowledge_id: W9-79EC8A
title: Cron审计报告模板
category: 11_Skill文档
source: skills/.archive_cron-optimization-manager/templates/audit_template.md
ingested_at: 2026-03-27 17:59:30
word_count: 1324
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Cron审计报告模板

> **知识ID**: W9-79EC8A  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_cron-optimization-manager/templates/audit_template.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Cron审计报告模板

## 报告信息

- **报告类型**: Cron全面审计
- **生成时间**: {{timestamp}}
- **审计范围**: 全部Cron
- **审计标准**: 方案C+优化标准

## 审计概览

| 指标 | 数值 |
|------|------|
| 总计Cron数 | {{total_crons}} |
| 启用Cron数 | {{enabled_crons}} |
| 禁用Cron数 | {{disabled_crons}} |
| P0-保留 | {{p0_count}} |
| P1-优化 | {{p1_count}} |
| P2-延迟 | {{p2_count}} |
| P3-删除 | {{p3_count}} |

## 详细审计结果

{{#each crons}}
### {{name}} ({{id}})

- **层级**: Tier {{tier}}
- **状态**: {{status}}
- **综合得分**: {{score}}/10
- **分类**: {{classification}}

**详细评分**:
- 必要性: {{necessity_score}}/10
- 频率合理性: {{frequency_score}}/10
- Token效率: {{token_efficiency_score}}/10
- 可控性: {{controllability_score}}/10

**运行指标**:
- 执行次数: {{execution_count}}
- Token消耗: {{token_consumption}}
- 空转率: {{empty_rate}}%
- 最后执行: {{last_executed}}

**优化建议**:
{{#each suggestions}}
- {{this}}
{{/each}}

---
{{/each}}

## 优化建议汇总

### 立即执行（P0）
{{p0_suggestions}}

### 本周优化（P1）
{{p1_suggestions}}

### 延迟处理（P2）
{{p2_suggestions}}

### 建议删除（P3）
{{p3_suggestions}}

## 附录

### 评分标准

| 维度 | 权重 | 说明 |
|------|------|------|
| 必要性 | 40% | 是否必须，能否替代 |
| 频率合理性 | 30% | 频率是否过高 |
| Token效率 | 20% | 产出/消耗比 |
| 可控性 | 10% | 是否可审计调整 |

### 分类标准

| 等级 | 得分范围 | 处理策略 |
|------|----------|----------|
| P0-保留 | 8.0-10.0 | 保留，必要时微调 |
| P1-优化 | 6.0-7.9 | 合并、降频、改触发 |
| P2-延迟 | 4.0-5.9 | 非必要，延迟启动 |
| P3-删除 | 0-3.9 | 冗余无效，直接删除 |
