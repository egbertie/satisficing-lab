# Skill: game-theory-negotiation
## 博弈论谈判助手

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **Skill ID** | `game-theory-negotiation` |
| **名称** | 博弈论谈判助手 |
| **理论来源** | Game Theory (von Neumann, Morgenstern, Nash) |
| **优先级** | P0 |
| **版本** | 1.0 |
| **创建日期** | 2026-03-15 |

---

## 功能概述

基于博弈论理论，帮助创业者在合伙人谈判中设计策略、预测对方行为、寻找共赢均衡，将对抗性谈判转化为合作性共创。

### 核心能力

1. **博弈建模**: 将谈判情境转化为博弈模型
2. **均衡分析**: 识别纳什均衡和最优策略
3. **策略设计**: 设计谈判策略和让步方案
4. **冲突化解**: 将零和博弈转化为正和博弈

---

## 输入规范

### 输入参数

```typescript
interface GameTheoryInput {
  // 谈判基础信息
  negotiation: {
    stage: 'preparation' | 'opening' | 'bargaining' | 'closing';
    topic: 'equity' | 'role' | 'compensation' | 'vesting' | 'multi';
    powerBalance: 'favorable' | 'balanced' | 'unfavorable';
    timePressure: 'none' | 'mild' | 'high';
  };
  
  // 己方信息
  self: {
    reservationPoint: number;       // 底线（最低可接受）
    targetPoint: number;            // 目标（最理想）
    alternatives: string[];         // BATNA（最佳替代方案）
    constraints: string[];          // 硬性约束
    priorities: Array<{            // 优先级排序
      item: string;
      weight: 1-10;
    }>;
  };
  
  // 对方信息（预估）
  opponent: {
    estimatedReservation: number;
    estimatedTarget: number;
    knownConstraints: string[];
    estimatedPriorities: string[];
    relationshipImportance: 'one_time' | 'long_term';
  };
  
  // 历史互动
  history: {
    previousRounds: number;
    offersExchanged: Array<{
      round: number;
      by: 'self' | 'opponent';
      offer: string;
      response: 'accepted' | 'rejected' | 'countered';
    }>;
    trustLevel: 1-10;
    conflictPoints: string[];
  };
}
```

### 输入示例

```json
{
  "negotiation": {
    "stage": "bargaining",
    "topic": "equity",
    "powerBalance": "balanced",
    "timePressure": "mild"
  },
  "self": {
    "reservationPoint": 15,
    "targetPoint": 25,
    "alternatives": ["继续寻找其他候选人", "先不引入合伙人"],
    "constraints": ["必须保留控制权", "技术合伙人不能低于15%"],
    "priorities": [
      {"item": "控制权", "weight": 10},
      {"item": "股权比例", "weight": 8},
      {"item": "vesting期限", "weight": 6}
    ]
  },
  "opponent": {
    "estimatedReservation": 20,
    "estimatedTarget": 35,
    "knownConstraints": ["需要足够激励", "希望有决策权"],
    "estimatedPriorities": ["股权比例", "决策权", "短期收益"],
    "relationshipImportance": "long_term"
  },
  "history": {
    "previousRounds": 2,
    "offersExchanged": [
      {
        "round": 1,
        "by": "self",
        "offer": "15%股权，4年vesting",
        "response": "rejected"
      },
      {
        "round": 2,
        "by": "opponent",
        "offer": "30%股权，3年vesting",
        "response": "countered"
      }
    ],
    "trustLevel": 6,
    "conflictPoints": ["股权比例差距大", "vesting期限不一致"]
  }
}
```

---

## 博弈模型

### 核心博弈类型

#### 1. 股权分配博弈（Chicken Game变体）

```
                    对方
              强硬        妥协
           ┌─────────┬─────────┐
    强硬   │ (0,0)   │ (3,1)   │
己         │ 双输     │ 己方大胜 │
方         ├─────────┼─────────┤
    妥协   │ (1,3)   │ (2,2)   │
           │ 对方大胜 │ 双赢     │
           └─────────┴─────────┘
```

**分析**: 双方都不希望双输（谈判破裂），因此有动力走向双赢。

#### 2. 信任建立博弈（重复囚徒困境）

```
                    对方
              合作        背叛
           ┌─────────┬─────────┐
    合作   │ (3,3)   │ (0,5)   │
己         │ 双赢     │ 被利用   │
方         ├─────────┼─────────┤
    背叛   │ (5,0)   │ (1,1)   │
           │ 利用对方 │ 双输     │
           └─────────┴─────────┘
```

**分析**: 合伙是长期关系（重复博弈），合作是最优策略。

#### 3. 不完全信息博弈（信号传递）

- 对方真实能力未知
- 通过谈判行为推断对方类型
- 设计机制筛选真实信息

---

## 处理逻辑

### 分析流程

```
┌─────────────┐
│  识别博弈类型 │
└──────┬──────┘
       ▼
┌─────────────┐
│  构建收益矩阵 │
└──────┬──────┘
       ▼
┌─────────────┐
│  计算均衡点  │
└──────┬──────┘
       ▼
┌─────────────┐
│  设计策略   │
└──────┬──────┘
       ▼
┌─────────────┐
│  生成方案   │
└─────────────┘
```

### 均衡计算

```typescript
interface NashEquilibrium {
  selfStrategy: string;
  opponentStrategy: string;
  selfPayoff: number;
  opponentPayoff: number;
  stability: 'stable' | 'unstable';
}

function findNashEquilibrium(game: GameMatrix): NashEquilibrium[] {
  // 寻找双方都没有动力单方面偏离的策略组合
  const equilibria = [];
  
  for (const selfStrategy of game.selfStrategies) {
    for (const opponentStrategy of game.opponentStrategies) {
      const payoff = game.payoffMatrix[selfStrategy][opponentStrategy];
      
      // 检查是否为均衡：双方都无法通过单方面改变获得更好结果
      const selfCanImprove = game.selfStrategies.some(s => 
        game.payoffMatrix[s][opponentStrategy].self > payoff.self
      );
      const opponentCanImprove = game.opponentStrategies.some(s => 
        game.payoffMatrix[selfStrategy][s].opponent > payoff.opponent
      );
      
      if (!selfCanImprove && !opponentCanImprove) {
        equilibria.push({
          selfStrategy,
          opponentStrategy,
          selfPayoff: payoff.self,
          opponentPayoff: payoff.opponent,
          stability: 'stable'
        });
      }
    }
  }
  
  return equilibria;
}
```

---

## 输出规范

### 输出结构

```typescript
interface GameTheoryOutput {
  // 博弈分析
  gameAnalysis: {
    gameType: string;
    description: string;
    keyInsights: string[];
  };
  
  // 均衡分析
  equilibria: Array<{
    name: string;
    description: string;
    selfOutcome: string;
    opponentOutcome: string;
    feasibility: 'high' | 'medium' | 'low';
  }>;
  
  // 策略建议
  strategies: {
    recommended: string;
    rationale: string;
    fallback: string;
    contingency: string;
  };
  
  // 具体方案
  proposals: Array<{
    name: string;
    details: string;
    selfBenefit: string;
    opponentBenefit: string;
    winWinScore: 1-10;
  }>;
  
  // 谈判话术
  scripts: {
    opening: string;
    responseToRejection: string;
    concession: string;
    closing: string;
  };
  
  // 风险提示
  risks: Array<{
    scenario: string;
    probability: 'low' | 'medium' | 'high';
    mitigation: string;
  }>;
}
```

### 输出示例

```json
{
  "gameAnalysis": {
    "gameType": "股权分配博弈（Chicken Game）",
    "description": "双方都希望达成协议，但在股权比例上有分歧。这是一个非零和博弈，存在双赢空间。",
    "keyInsights": [
      "双方的最佳替代方案（BATNA）都不理想",
      "长期合作关系增加了合作激励",
      "存在多个可接受的均衡点"
    ]
  },
  "equilibria": [
    {
      "name": "平等分配均衡",
      "description": "双方各退一步，达成20-22%区间",
      "selfOutcome": "略低于目标，但可接受",
      "opponentOutcome": "接近目标，感到满意",
      "feasibility": "high"
    },
    {
      "name": "条件交换均衡",
      "description": "股权让步换取其他条件",
      "selfOutcome": "股权略高，但有其他付出",
      "opponentOutcome": "股权理想，接受其他条件",
      "feasibility": "medium"
    }
  ],
  "strategies": {
    "recommended": "条件交换策略：在股权上适当让步，换取vesting期限和决策权的优势",
    "rationale": "对方最在意股权比例，而你更在意控制权。这是一个天然的交易空间。",
    "fallback": "如果股权无法低于22%，坚持4年vesting",
    "contingency": "如果对方坚持30%，考虑引入业绩对赌条款"
  },
  "proposals": [
    {
      "name": "方案A：平衡方案",
      "details": "20%股权，4年vesting， CTO职位，技术决策权",
      "selfBenefit": "保留足够股权和战略决策权",
      "opponentBenefit": "获得技术决策权和合理股权",
      "winWinScore": 8
    },
    {
      "name": "方案B：绩效方案",
      "details": "18%基础股权 + 5%业绩股权，4年vesting",
      "selfBenefit": "降低前期股权支出",
      "opponentBenefit": "有潜力获得更高股权",
      "winWinScore": 7
    }
  ],
  "scripts": {
    "opening": "我理解股权对你很重要，这是对你价值的认可。让我们找一个既能体现你价值，又能保证公司长期发展的方案。",
    "responseToRejection": "我理解这个方案对你还不够理想。能否告诉我，你最在意的是股权比例，还是其他方面？",
    "concession": "如果在股权上我可以让一步，你是否可以在vesting期限上配合？",
    "closing": "这个方案让我们在各自最在意的地方都得到满足。我相信这是一个能让双方都全力以赴的合作基础。"
  },
  "risks": [
    {
      "scenario": "对方坚持30%不妥协",
      "probability": "medium",
      "mitigation": "引入里程碑条款，根据业绩逐步释放股权"
    },
    {
      "scenario": "谈判陷入僵局",
      "probability": "low",
      "mitigation": "建议暂停48小时，各自重新评估BATNA"
    }
  ]
}
```

---

## 策略库

### 常用谈判策略

| 策略名称 | 适用情境 | 核心逻辑 | 话术示例 |
|----------|----------|----------|----------|
| **扩大蛋糕** | 零和僵局 | 引入新变量，创造增量价值 | "除了股权，我们还可以讨论..." |
| **条件交换** | 优先级不同 | 在你轻对方重的维度让步 | "如果在X上我配合，Y上你是否可以..." |
| **分步推进** | 分歧较大 | 将大问题分解为小问题 | "我们先确定大原则，细节后面再谈" |
| **锚定调整** | 开局阶段 | 先提出极端但合理的锚点 | "基于市场惯例，这个范围是..." |
| **BATNA强化** | 处于弱势 | 改善替代方案，增加谈判力 | "同时我也在和其他候选人接触" |
| **长期框架** | 关系重要 | 强调长期价值超过短期利益 | "我们要一起走过5-10年..." |

### 孙子兵法融合策略

| 兵法原则 | 谈判应用 |
|----------|----------|
| **知己知彼** | 充分了解对方的真实需求和底线 |
| **上兵伐谋** | 通过策略设计让对方"自愿"接受 |
| **全胜** | 不以击败对方为目标，而以共赢为目标 |
| **先胜后战** | 充分准备后再进入谈判 |
| **以正合，以奇胜** | 有标准方案，也准备意外之招 |

---

## 使用指南

### 触发条件

1. 股权谈判僵局时
2. 需要设计谈判策略时
3. 预测对方可能行为时
4. 评估谈判方案时

### 使用流程

```
Step 1: 信息收集
  ├─ 明确己方底线和目标
  ├─ 评估对方可能的底线
  └─ 列出BATNA
  
Step 2: 博弈建模
  ├─ 识别博弈类型
  ├─ 构建收益矩阵
  └─ 分析均衡点
  
Step 3: 策略设计
  ├─ 选择核心策略
  ├─ 设计让步方案
  └─ 准备应急预案
  
Step 4: 方案优化
  ├─ 评估各方案的双赢度
  ├─ 准备谈判话术
  └─ 制定风险预案
```

### 咨询师话术

**开场**:
> "谈判不是零和博弈。让我们用博弈论的视角分析一下：双方的底线在哪里？有没有双赢的空间？怎么设计一个让双方都不愿意偏离的方案？"

**解释均衡**:
> "根据分析，如果你们都坚持目前的立场，最可能的结果是谈判破裂——这是双输。但如果双方都适当让步，可以达成一个纳什均衡：你得到控制权，他得到合理的股权，双方都不愿再改变。"

**策略建议**:
> "我建议采用'条件交换'策略。你最在意控制权，他最在意股权比例。这是一个天然的交易空间——在股权上适当让步，换取决策权和vesting期限。"

---

## 关联Skill

| Skill | 关系 | 说明 |
|-------|------|------|
| `principal-agent-analyzer` | 下游 | 谈判后的机制设计 |
| `heuristic-bias-detector` | 并行 | 防止谈判中的认知偏差 |
| `dual-process-decision` | 上游 | 在感理协同基础上进行策略设计 |

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-03-15 | 初始版本，核心博弈模型 |

---

## 参考资源

- Nash, J. (1950). Equilibrium points in n-person games
- Dixit, A. K., & Nalebuff, B. J. (1991). Thinking Strategically
- 孙子兵法（战略思维）
