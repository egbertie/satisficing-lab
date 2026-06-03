---
# 知识元数据 (5标准化)
knowledge_id: W15-5EE741
title: csvtoexcel Skill V5标准版本
category: 11_Skill文档
source: skills/csvtoexcel/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1009
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# csvtoexcel Skill V5标准版本

> **知识ID**: W15-5EE741  
> **分类**: 11_Skill文档  
> **来源**: `skills/csvtoexcel/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# csvtoexcel Skill V5标准版本

## S1: 全局考虑

### 输入
- CSV/Excel文件路径
- 编码格式(UTF-8/GBK等)
- 分隔符配置

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 数据分析师、开发人员 |
| **事** | CSV↔Excel格式互转、编码处理、分隔符识别 |
| **物** | CSV文件、Excel文件、编码格式 |
| **环境** | 文件系统、编码环境 |
| **外部集成** | pandas/openpyxl |
| **边界情况** | 编码错误、格式混乱、大文件 |

---

## S2: 系统考虑

### 处理流程
```
格式检测 → 编码识别 → 数据解析 → 格式转换 → 结果输出
```

### 故障处理
- **编码错误**: 尝试多种编码，失败则提示
- **格式混乱**: 记录错误行，跳过继续
- **大文件**: 分块处理

---

## S3: 输出规范

### 转换输出
```json
{
  "input": "data.csv",
  "output": "data.xlsx",
  "input_format": "csv",
  "output_format": "xlsx",
  "rows": 1000,
  "encoding": "utf-8",
  "delimiter": ","
}
```

---

## S4: 自动化集成

### 使用方式
```bash
# CSV转Excel
csvtoexcel input.csv output.xlsx

# Excel转CSV
csvtoexcel input.xlsx output.csv
```

---

## S5: 自我验证

### 质量指标
- 转换成功率: >99%
- 数据准确性: 100%

---

## S6: 认知谦逊

### 局限
- 复杂Excel特性(图表/宏)会丢失
- 编码自动识别可能不准确

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| 编码错误 | 尝试GBK/UTF-8 |
| 空文件 | 返回空结果 |
| 大文件 | 流式处理 |
