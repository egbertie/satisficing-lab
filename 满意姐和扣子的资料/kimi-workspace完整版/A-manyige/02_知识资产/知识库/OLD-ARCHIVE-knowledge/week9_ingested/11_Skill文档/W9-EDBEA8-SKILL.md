---
# 知识元数据 (5标准化)
knowledge_id: W9-EDBEA8
title: Data Processor Suite
category: 11_Skill文档
source: skills/.archive_data-processor-suite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 7500
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Data Processor Suite

> **知识ID**: W9-EDBEA8  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_data-processor-suite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: data-processor-suite
description: Unified data processing suite - CSV/Excel conversion, data analysis, SQL queries, and automated Excel operations. Replaces csvtoexcel, automate-excel, and duckdb-cli-ai-skills with a single integrated interface. Use for: CSV to Excel conversion, Excel automation, data analysis with SQL, file format conversion, batch processing, data validation, aggregation, and reporting.
triggers: ["csv", "excel", "xlsx", "convert", "data analysis", "sql", "duckdb", "merge", "aggregate", "validate", "process data"]
---

# Data Processor Suite

**统一数据处理套件** - 整合CSV/Excel转换、数据分析、SQL查询和自动化Excel操作的完整解决方案。

> 🎯 替代: csvtoexcel + automate-excel + duckdb-cli-ai-skills

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **格式转换** | CSV ↔ Excel ↔ JSON ↔ Parquet |
| **Excel自动化** | 合并、拆分、筛选、去重、聚合、VLOOKUP |
| **SQL分析** | DuckDB驱动，支持CSV/Excel直接SQL查询 |
| **数据验证** | 格式检查、重复检测、完整性验证 |
| **批量处理** | 多文件自动化流水线 |

---

## 快速开始

### 1. 格式转换

```bash
# CSV 转 Excel (单文件)
dps convert input.csv output.xlsx

# CSV 转 Excel (多sheet)
dps convert file1.csv file2.csv file3.csv --output combined.xlsx --sheets "销售,库存,客户"

# Excel 转 CSV
dps convert data.xlsx output.csv --sheet 0

# 转 Parquet (高效存储)
dps convert large.csv data.parquet

# JSON 转 Excel
dps convert data.json output.xlsx
```

### 2. Excel自动化

```bash
# 合并多个Excel
dps excel merge *.xlsx --output merged.xlsx

# 按条件筛选
dps excel filter sales.xlsx --where "金额>1000" --output high_value.xlsx

# 按列拆分
dps excel split data.xlsx --by-column "地区" --output-dir ./split

# 去重
dps excel dedup orders.xlsx --keys "订单号" --keep first

# 聚合统计
dps excel aggregate sales.xlsx --group-by "地区" --agg "销售额:sum,订单数:count"

# VLOOKUP合并
dps excel vlookup main.xlsx --lookup "dict.xlsx:客户ID" --output result.xlsx
```

### 3. SQL分析

```bash
# 直接查询CSV
dps sql "SELECT * FROM 'data.csv' WHERE 金额 > 1000 LIMIT 10"

# 查询Excel指定sheet
dps sql "SELECT 地区, SUM(销售额) FROM 'sales.xlsx'.Sheet1 GROUP BY 地区"

# 多表JOIN
dps sql "SELECT a.*, b.客户名 FROM 'orders.csv' a JOIN 'customers.csv' b ON a.客户ID = b.ID"

# 保存查询结果
dps sql "SELECT * FROM 'data.csv' WHERE 日期 >= '2024-01-01'" --output result.xlsx
```

---

## 命令详解

### `dps convert` - 格式转换

| 参数 | 说明 | 示例 |
|------|------|------|
| `--sheet` | 指定Excel sheet索引或名称 | `--sheet 0` 或 `--sheet "销售数据"` |
| `--sheets` | 多CSV合并时的sheet名称 | `--sheets "Q1,Q2,Q3,Q4"` |
| `--encoding` | 指定编码 | `--encoding utf-8` |
| `--header` | 指定表头行 | `--header 1` |

**支持格式矩阵:**

| 从 \ 到 | CSV | Excel | Parquet | JSON |
|---------|-----|-------|---------|------|
| CSV | - | ✅ | ✅ | ✅ |
| Excel | ✅ | - | ✅ | ✅ |
| Parquet | ✅ | ✅ | - | ✅ |
| JSON | ✅ | ✅ | ✅ | - |

### `dps excel` - Excel操作

#### merge - 合并
```bash
dps excel merge file1.xlsx file2.xlsx --output merged.xlsx
dps excel merge ./data/*.xlsx --output all.xlsx --mode vertical  # vertical/horizontal
```

#### filter - 筛选
```bash
# 条件语法: 列名操作符值
# 操作符: =, !=, >, <, >=, <=, ~ (包含), !~ (不包含)
dps excel filter data.xlsx --where "状态=已完成" --output completed.xlsx
dps excel filter data.xlsx --where "金额>1000 AND 日期>=2024-01-01"
dps excel filter data.xlsx --where "客户名~北京"
```

#### split - 拆分
```bash
# 按行数拆分
dps excel split large.xlsx --by-rows 1000 --output-dir ./chunks

# 按列值拆分
dps excel split sales.xlsx --by-column "地区" --output-dir ./by_region
```

#### dedup - 去重
```bash
dps excel dedup orders.xlsx --keys "订单号" --keep first   # 保留第一个
dps excel dedup contacts.xlsx --keys "邮箱,电话" --keep last
```

#### aggregate - 聚合
```bash
# 聚合函数: sum, count, mean, min, max, std
dps excel aggregate sales.xlsx --group-by "地区,月份" --agg "销售额:sum,订单数:count,均价:mean"
```

#### vlookup - 表关联
```bash
# 单表lookup
dps excel vlookup main.xlsx --lookup "dict.xlsx:客户ID:客户名" --output result.xlsx

# 多表lookup
dps excel vlookup orders.xlsx --lookups "customers.xlsx:客户ID" "products.xlsx:产品ID" --output enriched.xlsx
```

#### template - 模板填充
```bash
dps excel template --template template.xlsx --data data.csv --output filled.xlsx
# 模板中使用 {{列名}} 作为占位符
```

### `dps sql` - SQL查询

```bash
# 交互式SQL shell
dps sql --shell

# 执行SQL文件
dps sql --file query.sql --output result.xlsx

# 创建临时视图
dps sql "CREATE VIEW vip AS SELECT * FROM 'customers.csv' WHERE 等级='VIP'"
dps sql "SELECT * FROM vip WHERE 消费金额 > 10000"
```

**SQL扩展函数:**

```sql
-- 读取各种格式
SELECT * FROM read_csv('file.csv')
SELECT * FROM read_excel('file.xlsx', sheet='Sheet1')
SELECT * FROM read_parquet('file.parquet')
SELECT * FROM read_json('file.json')

-- 写入各种格式
COPY (SELECT * FROM t) TO 'output.csv' (HEADER, DELIMITER ',')
COPY (SELECT * FROM t) TO 'output.xlsx' (FORMAT EXCEL)
COPY (SELECT * FROM t) TO 'output.parquet' (FORMAT PARQUET)
```

### `dps validate` - 数据验证

```bash
# 检查必填列
dps validate data.xlsx --required-columns "订单号,客户名,金额"

# 检查重复键
dps validate data.xlsx --unique-keys "订单号"

# 检查数据类型
dps validate data.xlsx --schema "金额:number,日期:date,邮箱:email"

# 完整验证报告
dps validate data.xlsx --full-report --output validation_report.json
```

---

## Python API

```python
from data_processor_suite import DataProcessor

dp = DataProcessor()

# 格式转换
dp.convert("input.csv", "output.xlsx", sheets=["Sheet1"])

# Excel操作
dp.excel.merge(["file1.xlsx", "file2.xlsx"], "merged.xlsx")
dp.excel.filter("data.xlsx", "金额 > 1000", "filtered.xlsx")
dp.excel.aggregate("sales.xlsx", group_by=["地区"], agg={"销售额": "sum"})

# SQL查询
result = dp.sql("SELECT * FROM 'data.csv' LIMIT 10")
print(result.to_df())

# 链式操作
dp.chain() \
  .load("raw_data.csv") \
  .filter("状态 = '有效'") \
  .aggregate(group_by=["类别"], agg={"金额": "sum"}) \
  .sort("金额 DESC") \
  .save("report.xlsx")
```

---

## 批量处理流水线

```yaml
# pipeline.yaml
pipeline:
  - name: load_data
    action: load
    files: "./raw/*.csv"
    
  - name: validate
    action: validate
    required_columns: ["订单号", "金额", "日期"]
    unique_keys: ["订单号"]
    
  - name: clean
    action: filter
    condition: "金额 > 0 AND 日期 IS NOT NULL"
    
  - name: enrich
    action: vlookup
    lookup_table: "customers.xlsx"
    key: "客户ID"
    
  - name: aggregate
    action: aggregate
    group_by: ["地区", "月份"]
    agg:
      销售额: sum
      订单数: count
      
  - name: export
    action: save
    format: xlsx
    output: "./output/report.xlsx"
    sheets: ["汇总", "明细"]
```

执行: `dps pipeline run pipeline.yaml`

---

## 性能优化

| 数据集大小 | 推荐格式 | 处理时间 |
|-----------|---------|---------|
| < 10MB | CSV/Excel | < 1s |
| 10MB - 100MB | Parquet | 1-5s |
| 100MB - 1GB | Parquet + 分区 | 5-30s |
| > 1GB | Parquet + 分块处理 | 30s+ |

**优化建议:**
- 大文件优先使用Parquet格式
- 使用 `--chunk-size` 参数分块处理
- SQL查询先过滤再聚合
- 内存不足时启用磁盘缓存: `--spill-to-disk`

---

## 与原有Skill的兼容

| 原Skill | 原命令 | 新命令 | 状态 |
|---------|--------|--------|------|
| csvtoexcel | `csv_to_excel.py a.csv b.xlsx` | `dps convert a.csv b.xlsx` | ✅ 替代 |
| automate-excel | `merge_sheets.py` | `dps excel merge` | ✅ 替代 |
| automate-excel | `filter_excel.py` | `dps excel filter` | ✅ 替代 |
| automate-excel | `split_excel.py` | `dps excel split` | ✅ 替代 |
| automate-excel | `deduplicate_excel.py` | `dps excel dedup` | ✅ 替代 |
| automate-excel | `aggregate_excel.py` | `dps excel aggregate` | ✅ 替代 |
| duckdb-cli | `duckdb -c "SELECT..."` | `dps sql "SELECT..."` | ✅ 替代 |

---

## 依赖安装

```bash
# 基础依赖
pip install pandas openpyxl duckdb

# 完整依赖 (含所有格式支持)
pip install -r requirements.txt
```

---

## 成本对比

| 方案 | 外部依赖 | 月度成本 |
|------|---------|---------|
| csvtoexcel + automate-excel + duckdb-cli | 3个独立Skill | 维护复杂 |
| **data-processor-suite** | **0个外部** | **完全免费** |

---

**状态**: ✅ 生产就绪
**自建替代计数**: +3 (csvtoexcel, automate-excel, duckdb-cli-ai-skills)
