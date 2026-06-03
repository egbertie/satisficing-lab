> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 六祖慧能 Skill - 顿悟与行动转化器

## 基本信息

| 属性 | 值 |
|------|-----|
| **名称** | 六祖慧能 |
| **五行** | 火 |
| **工整对仗** | 顿悟 |
| **象征** | 直觉与创新突破——在理性分析基础上，借助直觉把握关键决策节点，实现从量变到质变的顿悟 |
| **版本** | v1.0 |
| **状态** | FIN |

---

## 核心功能

将刘禹锡、司马贺、观自在、孔子四路洞察**综合顿悟**，转化为**可执行的行动计划**。

### 输入

| 来源 | 洞察类型 |
|------|----------|
| 刘禹锡（土） | 根基与信任评估 |
| 司马贺（金） | 满意解决策建议 |
| 观自在（水） | 环境应变策略 |
| 孔子（木） | 伦理治理方案 |

### 输出

- 综合顿悟洞察
- 关键突破点识别
- 优先级行动序列
- 风险缓解措施
- 成功概率评估

### 行动优先级

| 优先级 | 触发条件 | 投入估算 |
|--------|----------|----------|
| 关键 | 置信×紧迫≥70 | 4-6小时 |
| 高 | 置信×紧迫≥50 | 3-5小时 |
| 中 | 置信×紧迫≥30 | 3-4小时 |
| 低 | 置信×紧迫≥15 | 2-3小时 |
| 延后 | 置信×紧迫<15 | 1-2小时 |

---

## 使用方法

### 快速转化

```python
from huineng_skill import huineng_transform

report = huineng_transform(
    liu_insight="根基优秀，可信任",
    simon_insight="满意解得分85，建议合作",
    guanyin_insight="市场机会良好，加速推进",
    confucius_insight="五常得分高，伦理优秀"
)

print(report)
```

### 高级用法

```python
from huineng_skill import HuinengSkill, InsightItem

huineng = HuinengSkill()

insights = [
    InsightItem("刘禹锡", "根基优秀", 80, 7),
    InsightItem("司马贺", "决策可行", 75, 6),
    InsightItem("观自在", "机会良好", 70, 8),
    InsightItem("孔子", "伦理优秀", 85, 5)
]

plan = huineng.generate_action_plan(insights)

print(f"综合顿悟: {plan.overall_insight}")
print(f"关键突破: {plan.critical_breakthrough}")
print(f"总投入: {plan.total_effort}小时")
print(f"成功概率: {plan.success_probability}%")

for action in plan.action_sequence:
    print(f"[{action.priority.value}] {action.name}: {action.description}")
```

---

## 文件结构

```
huineng-skill/
├── SKILL.md              # 本文件
├── huineng_skill.py      # 核心实现 (320行)
└── test_huineng_skill.py # 测试文件 (85行)
```

---

## 测试

```bash
cd /root/.openclaw/workspace/skills/huineng-skill
python3 test_huineng_skill.py
```

**测试结果**: 4/4 PASS

---

## 五路图腾集成

六祖慧能是五路图腾的最后一环，将前四路洞察**转化行动**：

```
刘禹锡（土）根基 → 司马贺（金）决策 → 观自在（水）应变 → 孔子（木）治理 → 六祖慧能（火）行动
```

**火的特性**:
- 点燃（激发行动）
- 转化（从知到行）
- 照亮（明确路径）
- 释放能量（执行动力）

---

## 实际应用案例

```python
report = huineng_transform(
    liu_insight="候选人根基优秀，价值观一致",
    simon_insight="满意解得分85，建议立即合作",
    guanyin_insight="市场趋势强劲，机会良好",
    confucius_insight="五常得分优秀，伦理治理良好"
)

# 输出:
# - 综合顿悟：四路共识，建议合作
# - 关键突破：市场机会窗口
# - 行动序列：4个优先级行动
# - 总投入：约16小时
# - 成功概率：70%
```

---

## 设计原则

1. **顿悟综合**: 整合多路洞察，形成统一认知
2. **突破识别**: 识别关键转折点，把握时机
3. **行动转化**: 从洞察到行动的直接映射
4. **优先级排序**: 资源有限时先做最重要的事
5. **风险可控**: 每步行动都有风险缓解措施

---

**实现日期**: 2026-03-29  
**代码行数**: 405行 (含测试)  
**测试通过率**: 100% (4/4)

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
