---
# 知识元数据 (5标准化)
knowledge_id: W10-BB6853
title: 涌现匹配算法标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_emergence-matching/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1642
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 涌现匹配算法标准Skill V2.0

> **知识ID**: W10-BB6853  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_emergence-matching/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 涌现匹配算法标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: 合伙人-项目智能匹配

---

## 一、全局考虑（六层+匹配维度）

### 匹配维度 × 六层矩阵

| 维度 | 权重 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|------|------|--------|--------|--------|--------|--------|--------|
| **能力匹配** | 30% | 能力评估 | 技能映射 | 算法匹配 | 外部验证 | 能力报告 | 能力库 |
| **愿景匹配** | 25% | 价值观 | 目标对齐 | 方向一致性 | 外部共识 | 对齐度报告 | 愿景档案 |
| **资源匹配** | 20% | 资源盘点 | 资源需求 | 资源优化 | 外部资源 | 资源方案 | 资源库 |
| **时机匹配** | 15% | 时机敏感度 | 时机判断 | 时机算法 | 外部时机 | 时机建议 | 时机档案 |
| **能量匹配** | 10% | 能量评估 | 能量管理 | 能量监测 | 外部互动 | 能量报告 | 能量档案 |

---

## 二、系统考虑（输入→计算→输出→反馈闭环）

### 2.1 匹配算法流程

```
合伙人画像 + 项目需求 → 五维评分 → 加权计算 → 匹配排序 → 推荐报告 → 反馈优化
```

---

## 三、迭代机制（每次匹配后）

---

## 四、Skill化（匹配计算）

```python
def calculate_match_score(partner, project):
    """计算匹配得分"""
    scores = {
        "capability": assess_capability_match(partner, project),
        "vision": assess_vision_match(partner, project),
        "resource": assess_resource_match(partner, project),
        "timing": assess_timing_match(partner, project),
        "energy": assess_energy_match(partner, project)
    }
    
    weights = {"capability": 0.3, "vision": 0.25, "resource": 0.2, 
               "timing": 0.15, "energy": 0.1}
    
    total_score = sum(scores[k] * weights[k] for k in scores)
    return total_score, scores
```

---

## 五、流程自动化

```json
{
  "job": {
    "name": "match-calculation",
    "schedule": "按需触发"
  }
}
```

---

## 六、质量门控

- [x] **全局**: 五维×六层
- [x] **系统**: 输入→计算→输出→反馈
- [x] **迭代**: 每次优化
- [x] **Skill化**: 匹配算法
- [x] **自动化**: 按需计算

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*