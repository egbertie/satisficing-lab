> 生成时间: 2026-04-01 14:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 观自在 Skill - 洞察与应变决策器

## 基本信息

| 属性 | 值 |
|------|-----|
| **名称** | 观自在 |
| **五行** | 水 |
| **工整对仗** | 居方寸之地，以价值致远 |
| **象征** | 洞察与应变——敏锐感知环境变化，灵活调整执行策略 |
| **版本** | v1.0 |
| **状态** | FIN |

---

## 核心功能

基于环境数据生成**洞察分析**和**应变策略**，提供轻资产运营建议。

### 环境感知维度

| 维度 | 范围 | 说明 |
|------|------|------|
| 市场趋势 | 0-10 | 5=中性，>7=上行，<3=下行 |
| 团队士气 | 0-10 | 团队状态和凝聚力 |
| 风险等级 | 0-10 | 当前风险水平 |
| 机会评分 | 0-10 | 机会质量 |
| 资源可用性 | 0-10 | 资源充足程度 |

### 应变策略

| 策略 | 触发条件 | 说明 |
|------|----------|------|
| 加速推进 | 机会高+风险低+资源足 | 加大投入，抓住机会 |
| 策略转向 | 市场/机会恶化 | 调整方向，寻找新模式 |
| 保持定力 | 形势中性+风险可控 | 维持现状，优化效率 |
| 适应调整 | 环境变化但不极端 | 微调策略，保持灵活 |
| 策略收缩 | 风险高或资源紧张 | 减少投入，保存实力 |

### 轻资产建议

根据资源和风险状况，提供轻资产运营建议：
- 资源紧张时：合作、外包、共享
- 高机会时：资源整合、战略联盟
- 高风险时：减少固定投入、现金储备

---

## 使用方法

### 快速洞察

```python
from guanyin_skill import guanyin_insight

report = guanyin_insight(
    market_trend=8.0,          # 市场趋势 (0-10)
    team_morale=7.5,           # 团队士气 (0-10)
    risk_level=3.0,            # 风险等级 (0-10)
    opportunity_score=8.5,     # 机会评分 (0-10)
    resource_availability=6.0  # 资源可用性 (0-10)
)

print(report)
```

### 高级用法

```python
from guanyin_skill import GuanyinSkill, EnvironmentData, EnvironmentSignal

guanyin = GuanyinSkill()

# 带显式信号的环境数据
data = EnvironmentData(
    market_trend=7.0,
    team_morale=6.0,
    risk_level=8.0,  # 高风险
    opportunity_score=5.0,
    resource_availability=4.0,  # 资源紧张
    signals=[
        (EnvironmentSignal.RISK_ALERT, "供应商问题", 8),
        (EnvironmentSignal.TEAM_DYNAMIC, "关键人员变动", 6)
    ]
)

insight = guanyin.sense_environment(data)

print(f"形势判断: {insight.overall_situation}")
print(f"推荐策略: {insight.recommended_strategy.value}")
print(f"行动计划: {insight.action_plan}")
print(f"轻资产建议: {insight.light_asset_advice}")
```

---

## 文件结构

```
guanyin-skill/
├── SKILL.md              # 本文件
├── DESIGN.md             # 设计文档
├── guanyin_skill.py      # 核心实现 (360行)
└── test_guanyin_skill.py # 测试文件 (80行)
```

---

## 测试

```bash
cd /root/.openclaw/workspace/skills/guanyin-skill
python3 test_guanyin_skill.py
```

**测试结果**: 4/4 PASS

---

## 五路图腾集成

观自在承接刘禹锡和司马贺，提供**动态执行**能力：

```
刘禹锡（土）根基 → 司马贺（金）决策 → 观自在（水）应变 → 孔子（木）治理 → 六祖慧能（火）行动
```

**水的特性**:
- 随形就势（灵活应变）
- 润物无声（持续影响）
- 以柔克刚（柔性策略）
- 居低不争（轻资产姿态）

---

## 实际应用案例

### 案例1: 形势大好，加速推进
```python
insight = guanyin_insight(
    market_trend=8.5,
    team_morale=8.0,
    risk_level=3.0,
    opportunity_score=9.0,
    resource_availability=7.0
)
# 输出: 策略=加速推进，建议加大资源投入
```

### 案例2: 形势严峻，策略收缩
```python
insight = guanyin_insight(
    market_trend=3.5,
    team_morale=4.0,
    risk_level=8.0,
    opportunity_score=3.0,
    resource_availability=4.0
)
# 输出: 策略=策略收缩，建议轻资产运营
```

---

## 设计原则

1. **水性智慧**: 随形就势，不硬碰硬
2. **感知优先**: 先感知环境，再生成策略
3. **轻资产思维**: 以最小投入获取最大价值
4. **动态应变**: 根据环境变化持续调整
5. **柔性执行**: 保持灵活性，快速响应

---

**实现日期**: 2026-03-29  
**代码行数**: 440行 (含测试)  
**测试通过率**: 100% (4/4)

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
