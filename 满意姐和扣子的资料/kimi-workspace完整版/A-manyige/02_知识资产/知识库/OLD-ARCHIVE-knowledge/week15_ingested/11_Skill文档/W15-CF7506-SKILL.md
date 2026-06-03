---
# 知识元数据 (5标准化)
knowledge_id: W15-CF7506
title: duckdb-cli-ai-skills Skill V5标准版本
category: 11_Skill文档
source: skills/duckdb-cli-ai-skills/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 944
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# duckdb-cli-ai-skills Skill V5标准版本

> **知识ID**: W15-CF7506  
> **分类**: 11_Skill文档  
> **来源**: `skills/duckdb-cli-ai-skills/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# duckdb-cli-ai-skills Skill V5标准版本

## S1: 全局考虑

### 输入
- SQL查询语句
- 数据文件路径（CSV/JSON/Parquet）
- 分析需求描述

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 数据分析师、开发者 |
| **事** | SQL查询、数据分析、格式转换 |
| **物** | 数据文件、查询结果、数据库 |
| **环境** | 本地文件系统、内存限制 |
| **外部集成** | DuckDB引擎 |
| **边界情况** | 大文件、复杂查询、内存不足 |

---

## S2: 系统考虑

### 处理流程
```
加载数据 → 执行查询 → 返回结果 → 格式输出
```

### 故障处理
- **文件不存在**: 报错提示
- **SQL错误**: 返回错误信息
- **内存不足**: 建议分批处理
- **大文件**: 流式处理

---

## S3: 输出规范

### 查询结果格式
```json
{
  "query": "SELECT ...",
  "row_count": 100,
  "columns": ["col1", "col2"],
  "data": [[...], [...]],
  "execution_time_ms": 50
}
```

---

## S4: 自动化集成

### 支持格式
- CSV
- JSON
- Parquet
- Excel（通过转换）

---

## S5: 自我验证

### 质量指标
- 查询成功率: >95%
- 执行时间: 合理范围内
- 结果准确性: 100%

---

## S6: 认知谦逊

### 局限
- 依赖DuckDB引擎
- 超大文件可能内存不足
- 复杂查询需优化

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| 文件不存在 | 明确报错 |
| SQL语法错误 | 返回错误信息 |
| 内存不足 | 建议分批或优化 |
| 空结果 | 返回空数组 |
