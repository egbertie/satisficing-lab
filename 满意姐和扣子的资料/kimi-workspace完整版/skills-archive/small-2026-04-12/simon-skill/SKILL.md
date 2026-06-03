> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 司马贺 Skill - 理性决策与满意解计算器

## 基本信息

| 属性 | 值 |
|------|-----|
| **名称** | 司马贺 |
| **五行** | 金 |
| **工整对仗** | 不求最优，但求最适；结果为本，满意为尺 |
| **象征** | 理性决策——基于Simon满意解理论，在有限信息下追求足够好的方案 |
| **版本** | v1.0 |
| **状态** | FIN |

---

## 核心功能

基于Herbert Simon的满意解理论，为合伙人决策提供**理性分析**和**满意解计算**。

### 满意解 vs 最优解

| 维度 | 最优解 | 满意解 |
|------|--------|--------|
| 目标 | 全局最优 | 足够好即可 |
| 信息需求 | 完全信息 | 有限信息 |
| 搜索范围 | 全部方案 | 可行方案 |
| 决策时间 | 可能无限 | 有限时间内 |
| 适用场景 | 简单问题 | 复杂、不确定问题 |

### 决策维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 能力匹配度 | 25% | 技能vs需求匹配 |
| 成本效益 | 25% | ROI分析 |
| 风险可控性 | 20% | 风险矩阵评估 |
| 利益平衡 | 20% | 多方满意度 |
| 时间可行性 | 10% | 实施周期评估 |

### 决策状态

| 状态 | 分数区间 | 含义 |
|------|----------|------|
| 推荐 | ≥期望阈值+10 | 达到满意标准，可立即合作 |
| 可接受 | ≥期望阈值 | 达到期望，可以接受 |
| 边缘 | 期望阈值-15 | 接近但未达，需谨慎 |
| 不推荐 | <期望阈值-15 | 未达标准，不建议 |

---

## 使用方法

### 快速决策

```python
from simon_skill import satisficing_decision

report = satisficing_decision(
    name="候选人姓名",
    liu_score=80,              # 刘禹锡根基评分 (0-100)
    capability_match=8.0,      # 能力匹配度 (0-10)
    cost_benefit=7.5,          # 成本效益 (0-10)
    risk_controllability=8.0,  # 风险可控性 (0-10)
    stakeholder_satisfaction=7.0,  # 利益平衡 (0-10)
    time_feasibility=8.0,      # 时间可行性 (0-10)
    aspiration_level=70.0      # 期望阈值 (默认70)
)

print(report)
```

### 高级用法

```python
from simon_skill import 司马贺Skill, CandidateProfile

simon = 司马贺Skill(aspiration_level=75)  # 设置严格阈值

candidate = CandidateProfile(
    name="张三",
    liu_score=85,
    capability_match=8.5,
    cost_benefit=7.0,
    risk_controllability=8.0,
    stakeholder_satisfaction=7.5,
    time_feasibility=8.0
)

result = simon.make_decision(candidate)

print(f"满意解得分: {result.satisficing_score}")
print(f"决策状态: {result.decision_status.value}")
print(f"权衡分析: {result.trade_offs}")

# 生成完整报告
report = simon.format_report(result)
```

### 批量评估

```python
candidates = [
    CandidateProfile("候选人A", 80, 8.0, 7.5, 8.0, 7.5, 8.0),
    CandidateProfile("候选人B", 75, 7.5, 8.0, 7.5, 8.0, 7.5),
    CandidateProfile("候选人C", 70, 7.0, 7.0, 7.0, 7.0, 7.0),
]

results = simon.batch_evaluate(candidates)
# 自动按满意解得分排序
```

---

## 文件结构

```
simon-skill/
├── SKILL.md              # 本文件
├── DESIGN.md             # 设计文档
├── simon_skill.py        # 核心实现 (320行)
└── test_simon_skill.py   # 测试文件 (100行)
```

---

## 测试

```bash
cd /root/.openclaw/workspace/skills/simon-skill
python3 test_simon_skill.py
```

**测试结果**: 4/4 PASS

---

## 五路图腾集成

司马贺承接刘禹锡的根基评估，为理性决策提供方法论：

```
刘禹锡（土）根基评估 → 司马贺（金）理性决策 → 观自在（水）洞察应变 → 孔子（木）伦理治理 → 六祖慧能（火）行动转化
```

**刘禹锡与司马贺的关系**:
- 刘禹锡回答"这人可信吗？"
- 司马贺回答"这人合适吗？"
- 刘禹锡是前提（根基差直接否决）
- 司马贺是方法（满意解而非最优解）

---

## 实际应用案例

### 案例1: 优秀合伙人
```python
result = satisficing_decision(
    name="优秀合伙人",
    liu_score=85,
    capability_match=9.0,
    cost_benefit=8.0,
    risk_controllability=8.5,
    stakeholder_satisfaction=8.0,
    time_feasibility=8.0
)
# 输出: 满意解得分83.5，决策状态: 推荐
```

### 案例2: 根基好但能力一般
```python
result = satisficing_decision(
    name="根基好能力一般",
    liu_score=80,
    capability_match=6.0,  # 短板
    cost_benefit=7.0,
    risk_controllability=7.5,
    stakeholder_satisfaction=7.0,
    time_feasibility=6.5
)
# 输出: 满意解得分68.0，决策状态: 边缘
# 权衡: 根基好但能力一般，需加强短板
```

### 案例3: 根基差（直接否决）
```python
result = satisficing_decision(
    name="根基差候选人",
    liu_score=35,  # 根基差
    capability_match=9.0,
    cost_benefit=8.0,
    risk_controllability=7.0,
    stakeholder_satisfaction=8.0,
    time_feasibility=8.0
)
# 输出: 满意解得分44.3，决策状态: 不推荐
# 原因: 刘禹锡根基评分过低，直接否决
```

---

## 设计原则

1. **满意解理论**: 不求最优，但求最适
2. **有限理性**: 接受信息不完备，在约束下决策
3. **根基优先**: 刘禹锡根基评分低直接否决（修正因子）
4. **动态阈值**: 可根据场景调整期望阈值
5. **权衡分析**: 显式列出决策中的利弊权衡

---

**实现日期**: 2026-03-29  
**代码行数**: 420行 (含测试)  
**测试通过率**: 100% (4/4)

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
