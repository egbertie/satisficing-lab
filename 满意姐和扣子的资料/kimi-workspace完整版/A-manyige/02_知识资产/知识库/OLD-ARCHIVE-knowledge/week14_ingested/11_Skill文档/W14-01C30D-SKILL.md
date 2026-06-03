---
# 知识元数据 (5标准化)
knowledge_id: W14-01C30D
title: automate-excel Skill V5标准版本
category: 11_Skill文档
source: skills/automate-excel/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1334
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# automate-excel Skill V5标准版本

> **知识ID**: W14-01C30D  
> **分类**: 11_Skill文档  
> **来源**: `skills/automate-excel/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# automate-excel Skill V5标准版本

## S1: 全局考虑

### 输入
- Excel文件路径
- 操作类型（读取/写入/转换/格式化）
- 数据处理规则

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 数据分析师、财务人员、运营人员 |
| **事** | Excel读取、写入、格式转换、数据清洗、批量处理 |
| **物** | Excel文件(.xlsx/.xls)、工作表、单元格、公式 |
| **环境** | 文件系统、内存限制、Excel版本兼容性 |
| **外部集成** | openpyxl/pandas库 |
| **边界情况** | 大文件、损坏文件、密码保护、宏病毒 |

---

## S2: 系统考虑

### 处理流程
```
文件验证 → 格式识别 → 数据读取 → 规则处理 → 结果输出 → 日志记录
```

### 故障处理
- **文件损坏**: 尝试修复，失败则报错
- **内存不足**: 分块读取，流式处理
- **密码保护**: 提示输入密码或跳过
- **格式不兼容**: 尝试转换，失败则报错

---

## S3: 输出规范

### 读取输出
```json
{
  "file": "path/to/file.xlsx",
  "sheets": ["Sheet1", "Sheet2"],
  "data": {
    "Sheet1": [
      {"col1": "value1", "col2": "value2"},
      {"col1": "value3", "col2": "value4"}
    ]
  },
  "metadata": {
    "rows": 100,
    "cols": 10,
    "formulas": 5
  }
}
```

---

## S4: 自动化集成

### 支持操作
| 操作 | 说明 |
|------|------|
| read | 读取Excel为JSON/CSV |
| write | 写入数据到Excel |
| convert | 格式转换(xlsx↔csv↔json) |
| format | 格式化(样式、公式) |
| merge | 合并多个Excel |
| split | 按sheet拆分 |

---

## S5: 自我验证

### 质量指标
- 读取成功率: >98%
- 数据准确性: 100%
- 格式保留率: >95%

---

## S6: 认知谦逊

### 局限
- 无法处理VBA宏
- 复杂公式可能解析错误
- 密码保护文件需密码
- 超大文件(>100MB)可能内存不足

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| 文件不存在 | 明确报错 |
| 文件损坏 | 尝试修复，失败报错 |
| 空文件 | 返回空数据 |
| 超大文件 | 分块处理或报错 |
| 密码保护 | 提示输入密码 |
