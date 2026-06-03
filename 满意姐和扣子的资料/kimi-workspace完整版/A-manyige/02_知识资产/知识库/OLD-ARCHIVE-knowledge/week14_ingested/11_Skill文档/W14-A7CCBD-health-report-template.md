---
# 知识元数据 (5标准化)
knowledge_id: W14-A7CCBD
title: 健康度报告模板
category: 11_Skill文档
source: skills/.archive_workspace-health-scanner/templates/health-report-template.md
ingested_at: 2026-03-27 17:59:30
word_count: 253
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 健康度报告模板

> **知识ID**: W14-A7CCBD  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_workspace-health-scanner/templates/health-report-template.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 健康度报告模板

## 总体评分: {{total_score}}分 {{grade_emoji}}

## 各维度评分

| 维度 | 得分 | 权重 | 状态 |
|------|------|------|------|
{{dimension_table}}

## 发现的问题

{{issues_list}}

## 优化建议

{{recommendations_list}}

## 历史趋势

{{trend_chart}}

---
*报告生成时间: {{timestamp}}*
