> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 刘禹锡 Skill - 根基与信任评估器

## 基本信息

| 属性 | 值 |
|------|-----|
| **名称** | 刘禹锡 |
| **五行** | 土 |
| **工整对仗** | 聚贤才为伍，引智士同行 |
| **象征** | 根基与信任——如同山之稳固，是长期合作的基石 |
| **版本** | v1.0 |
| **状态** | FIN |

---

## 核心功能

评估合伙人的**根基与信任worthiness**，提供数据驱动的合伙人筛选建议。

### 评估维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 价值观一致性 | 30% | 与团队核心价值观匹配度 |
| 历史诚信 | 25% | 过往合作中的诚信记录 |
| 长期承诺 | 20% | 对长期合作的意愿和能力 |
| 文化契合 | 15% | 与团队文化的适应度 |
| 人品口碑 | 10% | 第三方评价和推荐 |

### 信任等级

| 等级 | 分数区间 | 含义 |
|------|----------|------|
| L5 | 85-100 | 完全信任 |
| L4 | 70-84 | 可信任 |
| L3 | 55-69 | 中立 |
| L2 | 40-54 | 需谨慎 |
| L1 | 0-39 | 不信任 |

---

## 使用方法

### 快速评估

```python
from liu_skill import evaluate_partner

report = evaluate_partner(
    name="候选人姓名",
    values_alignment=8.0,      # 价值观一致性 (0-10)
    integrity_history=7.5,     # 历史诚信 (0-10)
    long_term_commitment=8.0,  # 长期承诺 (0-10)
    cultural_fit=7.0,          # 文化契合 (0-10)
    reputation_score=8.5,      # 人品口碑 (0-10)
    red_flags=[]               # 风险标记列表
)

print(report)
```

### 高级用法

```python
from liu_skill import 刘禹锡Skill, CandidateData

liu = 刘禹锡Skill()

candidate = CandidateData(
    name="张三",
    values_alignment=9.0,
    integrity_history=8.5,
    long_term_commitment=8.0,
    cultural_fit=8.5,
    reputation_score=9.0,
    red_flags=["历史合同纠纷"]  # 如有风险标记
)

result = liu.evaluate_partner(candidate)

print(f"总分: {result.total_score}")
print(f"信任等级: {result.trust_level.value}")
print(f"建议: {result.recommendation.value}")

# 生成完整报告
report = liu.format_report(result)
```

---

## 文件结构

```
liu-skill/
├── SKILL.md              # 本文件
├── DESIGN.md             # 设计文档
├── liu_skill.py          # 核心实现 (290行)
└── test_liu_skill.py     # 测试文件 (80行)
```

---

## 测试

```bash
cd /root/.openclaw/workspace/skills/liu-skill
python3 test_liu_skill.py
```

**测试结果**: 4/4 PASS

---

## 五路图腾集成

刘禹锡是五路图腾的第一位（土），为其他四路提供基础：

```
        刘禹锡（土）- 根基
         /    \
   司马贺（金）  孔子（木）
   理性决策      伦理治理
         \    /
     观自在（水）- 洞察应变
           |
      六祖慧能（火）- 行动转化
```

---

## 实际应用案例

### 案例1：优秀合伙人
```python
result = evaluate_partner(
    name="优秀候选人",
    values_alignment=9.0,
    integrity_history=8.5,
    long_term_commitment=8.0,
    cultural_fit=8.5,
    reputation_score=9.0
)
# 输出: 总分86.0，信任等级L5，建议: 推荐
```

### 案例2：高风险候选人
```python
result = evaluate_partner(
    name="风险候选人",
    values_alignment=4.0,
    integrity_history=3.5,
    long_term_commitment=4.0,
    red_flags=["失信记录", "合同纠纷"]
)
# 输出: 总分<50，信任等级L1/L2，建议: 不推荐
```

---

## 设计原则

1. **根基优先**: 合伙人的人品和价值观比能力更重要
2. **数据驱动**: 基于多维度加权评分，避免主观偏见
3. **风险预警**: 主动识别red flags，提供决策依据
4. **五路集成**: 作为五路图腾基础，与其他四路协同

---

**实现日期**: 2026-03-29  
**代码行数**: 370行 (含测试)  
**测试通过率**: 100% (4/4)

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
