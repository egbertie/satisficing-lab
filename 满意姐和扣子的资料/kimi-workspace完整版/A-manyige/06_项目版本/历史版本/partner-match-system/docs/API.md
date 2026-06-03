# API 文档

## 核心类

### `EntanglementMatchingSystem`

主系统类，整合所有6层评估引擎。

```python
system = EntanglementMatchingSystem()
result = system.comprehensive_match(partner_a, partner_b)
```

#### 方法

##### `comprehensive_match(partner_a: PartnerProfile, partner_b: PartnerProfile) -> Dict`

执行完整的六层匹配评估。

**参数:**
- `partner_a`: 第一位合伙人档案
- `partner_b`: 第二位合伙人档案

**返回:**
```python
{
    'overall_compatibility': float,  # 0-1 综合兼容度
    'layer_results': {
        'quantum_perception': Dict,     # Layer 1 结果
        'emergent_matching': Dict,      # Layer 2 结果
        'embodied_cognition': Dict,     # Layer 3 结果
        'narrative_identity': Dict,     # Layer 4 结果
        'cognitive_diversity': Dict,    # Layer 5 结果
        'ethical_alignment': Dict       # Layer 6 结果
    },
    'predictions': {
        '6_months': {'success_probability': float, 'key_challenge': str},
        '1_year': {...},
        '3_years': {...}
    },
    'recommendations': List[Dict]  # 优化建议
}
```

---

### `PartnerProfile`

合伙人档案数据结构。

```python
profile = PartnerProfile(
    name="李明",
    id="p001",
    cognitive_profile={
        'analytical': 0.7,       # 分析倾向 0-1
        'detail_oriented': 0.8,   # 细节导向 0-1
        'risk_tolerance': 0.6,    # 风险容忍 0-1
        'independent': 0.7        # 独立性 0-1
    },
    narrative_profile={
        'interview': '生命故事访谈文本',
        'sense_test': '共享意义建构测试结果'
    },
    ethical_profile={
        'responses': [...],       # 道德基础问卷回答
        'scenarios': [...]        # 义利情境测试选择
    }
)
```

---

### `WaveFunction`

量子波函数，表示认知状态的叠加。

```python
wf = WaveFunction()
wf.amplitudes = {
    'high': 0.5 + 0.1j,
    'medium': 0.4 + 0.2j,
    'low': 0.3 - 0.1j
}
wf.normalize()
collapsed_state = wf.measure(context)
```

#### 方法

##### `normalize()`

归一化波函数，使概率总和为1。

##### `measure(context: Dict = None) -> str`

测量波函数，导致坍缩到一个确定态。

**返回:** 坍缩后的状态名称

##### `entangle_with(other: WaveFunction, strength: float = 0.5) -> WaveFunction`

与另一个波函数纠缠，创建联合波函数。

---

### `CognitiveAgent`

认知代理，模拟个体在决策场景中的行为。

```python
agent = CognitiveAgent(
    name="创始人A",
    cognitive_profile={
        'analytical': 0.7,
        'intuitive': 0.3,
        'risk_tolerance': 0.6,
        'detail_focus': 0.8,
        'decision_speed': 0.5
    }
)
```

#### 方法

##### `make_decision(scenario: Dict, partner: CognitiveAgent = None) -> Dict`

在场景中做出决策。

**参数:**
- `scenario`: 决策场景 `{'type': str, 'complexity': float}`
- `partner`: 可选的合作伙伴

**返回:**
```python
{
    'decision': float,      # 决策值 0-1
    'mode': str,            # 协作模式
    'timestamp': str
}
```

---

### `EmergentMatcher`

涌现式匹配算法，模拟两人合作系统。

```python
matcher = EmergentMatcher()
result = matcher.simulate_partnership(agent_a, agent_b, n_scenarios=100)
```

#### 方法

##### `simulate_partnership(agent_a: CognitiveAgent, agent_b: CognitiveAgent, n_scenarios: int = 100) -> Dict`

模拟两人合作系统。

**返回:**
```python
{
    'collaboration_pattern': Dict,  # 协作模式分布
    'dominant_mode': str,           # 主导协作模式
    'creativity_index': float,      # 创造性能量
    'attractors': List[Dict],       # 稳定吸引子
    'stability_score': float,       # 系统稳定性
    'emergence_score': float        # 涌现性指数
}
```

---

### `DiversityOptimizer`

认知多样性优化器，找到最优差异区。

```python
optimizer = DiversityOptimizer()
result = optimizer.evaluate_diversity_sweet_spot(style_a, style_b)
```

#### 方法

##### `evaluate_diversity_sweet_spot(style_a: CognitiveStyle, style_b: CognitiveStyle) -> Dict`

评估两人是否在最优差异区。

**返回:**
```python
{
    'cognitive_distance': float,    # 认知距离
    'sweet_spot_score': float,      # 最优区评分
    'in_danger_zone': bool,         # 是否在危险区
    'diversity_benefit': float,     # 多样性收益
    'conflict_risk': float          # 冲突风险
}
```

---

### `EmbodiedAnalyzer`

身体化认知分析器。

```python
analyzer = EmbodiedAnalyzer()
analyzer.add_data('A', BiomarkerData(...))
analyzer.add_data('B', BiomarkerData(...))
report = analyzer.generate_embodied_report()
```

#### 方法

##### `add_data(partner: str, data: BiomarkerData)`

添加生物标记数据。

##### `calculate_hrv_synchronization() -> float`

计算心率变异性同步性。

##### `generate_embodied_report() -> Dict`

生成身体共鸣图谱。

---

## 数据类

### `BiomarkerData`

生物标记数据。

```python
BiomarkerData(
    timestamp=float,        # 时间戳
    hr=float,              # 心率
    hrv=float,             # 心率变异性
    voice_pitch=float,     # 语音基频
    voice_tremor=float,    # 语音颤抖
    micro_expression=str   # 微表情（可选）
)
```

### `CognitiveStyle`

认知风格档案。

```python
CognitiveStyle(
    analytical=float,       # 分析型 0-1
    detail_oriented=float,  # 细节导向 0-1
    risk_tolerance=float,   # 风险容忍 0-1
    independent=float       # 独立性 0-1
)
```

---

## 可视化API

### `AttractorLandscapeVisualizer`

吸引子景观可视化。

```python
viz = AttractorLandscapeVisualizer()
fig = viz.visualize(collaboration_data, save_path='landscape.png')
```

### `CognitiveDiversityMap`

认知多样性图谱。

```python
map_viz = CognitiveDiversityMap()
fig = map_viz.create_radial_chart(style_a, style_b)
fig = map_viz.create_dance_visualization(style_a, style_b)
```

### `FutureEvolutionSimulator`

未来演化模拟。

```python
sim = FutureEvolutionSimulator()
fig = sim.create_evolution_timeline(predictions)
```

---

## 示例代码

### 完整匹配流程

```python
from core.entanglement_system import *

# 初始化
system = EntanglementMatchingSystem()

# 创建档案
partner_a = PartnerProfile(
    name="技术创始人",
    id="tech_001",
    cognitive_profile={
        'analytical': 0.8,
        'detail_oriented': 0.9,
        'risk_tolerance': 0.4,
        'independent': 0.7
    }
)

partner_b = PartnerProfile(
    name="市场创始人",
    id="biz_001",
    cognitive_profile={
        'analytical': 0.4,
        'detail_oriented': 0.3,
        'risk_tolerance': 0.8,
        'independent': 0.6
    }
)

# 执行匹配
result = system.comprehensive_match(partner_a, partner_b)

# 输出结果
print(f"兼容度: {result['overall_compatibility']:.1%}")

# 各层详细结果
for layer, data in result['layer_results'].items():
    print(f"\n{layer}:")
    print(json.dumps(data, indent=2, default=str))

# 未来预测
for timeframe, pred in result['predictions'].items():
    print(f"{timeframe}: {pred['success_probability']:.1%} - {pred['key_challenge']}")

# 建议
for rec in result['recommendations']:
    print(f"[{rec['priority']}] {rec['category']}: {rec['suggestion']}")
```

### 可视化示例

```python
from core.visualization import *

# 生成可视化报告
visualizations = generate_full_report_visualization(
    match_result,
    save_dir='./outputs'
)

print(f"生成文件: {visualizations}")
```

---

## 错误处理

所有方法在输入无效时会抛出 `ValueError` 或 `TypeError`。

```python
try:
    result = system.comprehensive_match(partner_a, partner_b)
except ValueError as e:
    print(f"输入错误: {e}")
except Exception as e:
    print(f"系统错误: {e}")
```
