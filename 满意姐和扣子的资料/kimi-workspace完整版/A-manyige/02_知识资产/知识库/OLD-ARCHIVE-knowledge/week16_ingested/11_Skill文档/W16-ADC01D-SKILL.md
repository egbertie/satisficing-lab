---
# 知识元数据 (5标准化)
knowledge_id: W16-ADC01D
title: quality-assessment Skill V5标准版本
category: 11_Skill文档
source: skills/quality-assessment/SKILL.md
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

# quality-assessment Skill V5标准版本

> **知识ID**: W16-ADC01D  
> **分类**: 11_Skill文档  
> **来源**: `skills/quality-assessment/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# quality-assessment Skill V5标准版本

## S1: 全局考虑

### 输入
- 待评估产出物
- 评估标准
- 评估维度

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 质量审核员、项目负责人 |
| **事** | 质量评估、缺陷识别、改进建议 |
| **物** | 产出物、评估报告、评分记录 |
| **环境** | 项目阶段、交付要求 |
| **外部集成** | 检查工具、测试系统 |
| **边界情况** | 标准不适用、主观判断、时间压力 |

---

## S2: 系统考虑

### 评估维度
| 维度 | 权重 | 检查项 |
|------|------|--------|
| 完整性 | 25% | 需求覆盖、文档齐全 |
| 正确性 | 30% | 功能正确、无缺陷 |
| 规范性 | 20% | 符合标准、风格一致 |
| 可维护性 | 15% | 结构清晰、文档完善 |
| 性能 | 10% | 满足性能要求 |

### 处理流程
```
标准加载 → 自动检查 → 人工评审 → 分数计算 → 报告生成 → 改进建议
```

---

## S3: 输出规范

### 评估报告
```json
{
  "item": "产出物名称",
  "overall_score": 85,
  "grade": "B",
  "dimensions": {
    "completeness": 90,
    "correctness": 80,
    "compliance": 85,
    "maintainability": 88,
    "performance": 82
  },
  "issues": [...],
  "suggestions": [...]
}
```

---

## S4: 自动化集成

### 自动检查项
- 格式规范
- 必填项检查
- 基础测试
- 代码规范

---

## S5: 自我验证

### 质量指标
- 评估一致性: >90%
- 问题发现率: >80%
- 建议采纳率: >70%

---

## S6: 认知谦逊

### 局限
- 部分维度需人工判断
- 标准可能不完全适用
- 无法保证发现所有问题

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| 标准不适用 | 标记N/A，人工介入 |
| 争议评分 | 记录分歧，多方复核 |
| 时间紧急 | 快速评估，标记风险 |
