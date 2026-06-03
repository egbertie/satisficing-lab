---
knowledge_id: W1-3E4D48
title: SKL-SKILL-v1.0-FIN-260322-Scenario-Planner.md
category: 11_Skill文档
source: skills/scenario-planner/SKILL.md
ingested_at: 2026-03-27T17:44:51.289622
word_count: 1205
---

# SKL-SKILL-v1.0-FIN-260322-Scenario-Planner.md

**知识ID**: W1-3E4D48  
**分类**: 11_Skill文档  
**原始路径**: skills/scenario-planner/SKILL.md

---

# SKL-SKILL-v1.0-FIN-260322-Scenario-Planner.md

> **维度**: 3D预测式  
> **功能**: 情景规划(Base/Bull/Bear/Black Swan)  
> **状态**: WIP (S4/S7待完成)

---

## S1: 全局考虑

| 维度 | 覆盖 |
|------|------|
| 人 | 战略决策者 |
| 事 | 情景规划、风险预判 |
| 物 | 情景报告、概率评估 |
| 环境 | 市场/政策/技术变化 |
| 外部 | 行业数据、竞品动态 |
| 边界 | 黑天鹅不可预测 |

---

## S2: 系统闭环

```
输入(决策需求) → 生成4情景 → 概率评估 → 预警信号 → 输出报告
```

**4情景框架**:
| 情景 | 概率 | 特征 |
|------|------|------|
| Base | 60% | 最可能结果 |
| Bull | 20% | 乐观上限 |
| Bear | 15% | 悲观下限 |
| Black Swan | 5% | 极端未知 |

---

## S3: 输出规范

```json
{
  "decision": "决策主题",
  "scenarios": {
    "base": {"desc": "...", "probability": 0.6, "indicators": [...]},
    "bull": {"desc": "...", "probability": 0.2, "indicators": [...]},
    "bear": {"desc": "...", "probability": 0.15, "indicators": [...]},
    "black_swan": {"desc": "...", "probability": 0.05, "indicators": [...]}
  },
  "early_warnings": [...],
  "recommended_action": "..."
}
```

---

## S4: 自动化集成

- 每周一09:00自动生成关键决策情景
- 触发条件: 重大决策前/季度规划

---

## S5: 自我验证

- 情景准确率追踪
- 概率校准反馈

---

## S6: 认知谦逊

**局限**: 黑天鹅定义即为不可预测，5%概率为象征性标注

---

## S7: 对抗测试

| 场景 | 测试 |
|------|------|
| 过度乐观 | 强制生成Bear情景 |
| 过度悲观 | 强制生成Bull情景 |
| 忽视极端 | 强制Black Swan分析 |

**7标准达成度: 85%**
