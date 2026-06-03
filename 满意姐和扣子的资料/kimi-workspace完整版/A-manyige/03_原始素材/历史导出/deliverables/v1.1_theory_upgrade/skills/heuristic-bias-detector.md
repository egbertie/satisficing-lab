# Skill: heuristic-bias-detector
## 启发式与偏差检测器

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **Skill ID** | `heuristic-bias-detector` |
| **名称** | 启发式与偏差检测器 |
| **理论来源** | Heuristics & Biases (Kahneman & Tversky) |
| **优先级** | P0 |
| **版本** | 1.0 |
| **创建日期** | 2026-03-15 |

---

## 功能概述

基于启发式与偏差理论，帮助创业者识别合伙人评估过程中的认知偏差，提供纠正策略，提升决策质量。

### 核心能力

1. **偏差扫描**: 识别决策过程中的12种常见认知偏差
2. **影响评估**: 评估偏差对当前决策的潜在影响
3. **纠正建议**: 提供针对性的偏差纠正策略
4. **预防清单**: 生成个性化的偏差预防检查清单

---

## 输入规范

### 输入参数

```typescript
interface BiasDetectionInput {
  // 决策情境
  context: {
    stage: 'search' | 'screening' | 'interview' | 'evaluation' | 'negotiation';
    candidateCount: number;
    timePressure: 'low' | 'medium' | 'high';
    informationCompleteness: 'low' | 'medium' | 'high';
  };
  
  // 决策者信息
  decisionMaker: {
    experience: 'first_time' | 'experienced' | 'serial';
    fatigue: 'low' | 'medium' | 'high';
    emotionalState: 'calm' | 'anxious' | 'excited' | 'stressed';
  };
  
  // 候选人信息（当前关注的）
  candidate?: {
    name: string;
    standoutFeatures: string[];     // 最突出的特征
    firstInteraction: string;       // 首次互动情况
    recentInteraction: string;      // 最近互动情况
  };
  
  // 决策过程描述
  decisionProcess: {
    howDidYouHear: string;          // 如何得知候选人
    firstImpression: string;        // 第一印象
    evaluationMethod: string;       // 评估方式
    comparisonBasis: string[];      // 比较基准
    recentChanges: string[];        // 近期信息变化
  };
}
```

### 输入示例

```json
{
  "context": {
    "stage": "evaluation",
    "candidateCount": 5,
    "timePressure": "medium",
    "informationCompleteness": "medium"
  },
  "decisionMaker": {
    "experience": "first_time",
    "fatigue": "medium",
    "emotionalState": "anxious"
  },
  "candidate": {
    "name": "张三",
    "standoutFeatures": ["大厂技术总监背景", "最近刚离职", "和我是校友"],
    "firstInteraction": "行业峰会上偶然认识",
    "recentInteraction": "昨天刚做了深度技术交流"
  },
  "decisionProcess": {
    "howDidYouHear": "行业峰会",
    "firstImpression": "非常专业，气场很强",
    "evaluationMethod": "技术交流+背景调查",
    "comparisonBasis": ["技术深度", "管理能力", "价值观"],
    "recentChanges": ["昨天交流后印象更好了"]
  }
}
```

---

## 检测偏差类型

### 12种核心偏差检测

| 偏差类型 | 检测信号 | 影响程度 |
|----------|----------|----------|
| **1. 可得性启发** | 最近/生动的信息权重过高 | 高 |
| **2. 代表性启发** | 以刻板印象代替深度分析 | 高 |
| **3. 锚定效应** | 过度依赖第一印象/首次报价 | 高 |
| **4. 确认偏误** | 只寻找支持已有判断的信息 | 高 |
| **5. 光环效应** | 某一优点泛化到整体评价 | 中 |
| **6. 近因效应** | 最近互动的权重过高 | 中 |
| **7. 损失厌恶** | 对损失的恐惧超过对收益的渴望 | 高 |
| **8. 禀赋效应** | 高估自己拥有的/已投入的 | 中 |
| **9. 现状偏见** | 倾向于维持现状 | 中 |
| **10. 过度自信** | 对自己判断的准确性过于自信 | 高 |
| **11. 幸存者偏差** | 只关注成功案例 | 中 |
| **12. 情感启发** | 当前情绪影响判断 | 中 |

### 检测逻辑示例

```typescript
// 可得性启发检测
function detectAvailabilityBias(input: BiasDetectionInput): BiasResult {
  const signals = [];
  
  if (input.candidate.recentInteraction.includes('昨天') ||
      input.candidate.recentInteraction.includes('最近')) {
    signals.push('最近互动印象深刻');
  }
  
  if (input.decisionProcess.recentChanges.length > 0) {
    signals.push('近期有新信息影响判断');
  }
  
  if (input.context.candidateCount > 3 && 
      input.decisionMaker.fatigue === 'high') {
    signals.push('候选人众多+疲劳，可能依赖最近记忆');
  }
  
  return {
    type: 'availability',
    detected: signals.length >= 2,
    confidence: signals.length * 25,
    signals,
    description: '可能过度重视最近获得的信息'
  };
}

// 代表性启发检测
function detectRepresentativenessBias(input: BiasDetectionInput): BiasResult {
  const signals = [];
  
  const stereotypes = ['大厂', '名校', '海归', '连续创业者'];
  const hasStereotype = input.candidate.standoutFeatures.some(f => 
    stereotypes.some(s => f.includes(s))
  );
  
  if (hasStereotype) {
    signals.push('候选人带有强烈的标签特征');
  }
  
  if (input.decisionProcess.firstImpression.includes('非常') ||
      input.decisionProcess.firstImpression.includes('一看就是')) {
    signals.push('第一印象过于绝对化');
  }
  
  return {
    type: 'representativeness',
    detected: signals.length >= 1,
    confidence: signals.length * 40 + (hasStereotype ? 30 : 0),
    signals,
    description: '可能以刻板印象代替深度分析'
  };
}

// 锚定效应检测
function detectAnchoringBias(input: BiasDetectionInput): BiasResult {
  const signals = [];
  
  if (input.decisionProcess.firstImpression.length > 20) {
    signals.push('对第一印象描述非常详细');
  }
  
  if (input.context.stage === 'negotiation') {
    signals.push('处于谈判阶段，可能受首次报价影响');
  }
  
  return {
    type: 'anchoring',
    detected: signals.length >= 1,
    confidence: signals.length * 45,
    signals,
    description: '可能过度依赖第一印象或初始信息'
  };
}
```

---

## 处理逻辑

### 检测流程

```
┌─────────────┐
│  接收输入    │
└──────┬──────┘
       ▼
┌─────────────────────────────┐
│      并行检测12种偏差         │
├─────────────────────────────┤
│ 可得性 → 代表性 → 锚定 → 确认 │
│ 光环   → 近因   → 损失 → 禀赋 │
│ 现状   → 过度自信→幸存者→情感 │
└─────────────────────────────┘
       ▼
┌─────────────┐
│  风险评级    │
└──────┬──────┘
       ▼
┌─────────────┐
│  生成纠正建议 │
└──────┬──────┘
       ▼
┌─────────────┐
│  输出报告    │
└─────────────┘
```

### 风险评级矩阵

| 检测到的偏差数 | 风险等级 | 建议行动 |
|----------------|----------|----------|
| 0-1个 | 低 | 正常推进，保持觉察 |
| 2-3个 | 中 | 使用纠正策略，增加验证 |
| 4-5个 | 高 | 暂停决策，全面重新审视 |
| 6个以上 | 极高 | 建议引入第三方评估 |

---

## 输出规范

### 输出结构

```typescript
interface BiasDetectionOutput {
  // 总体评估
  summary: {
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    detectedCount: number;
    topRiskBiases: string[];
    overallRecommendation: string;
  };
  
  // 详细检测结果
  detectedBiases: Array<{
    type: string;
    name: string;
    confidence: 1-100;
    signals: string[];
    description: string;
    impact: 'low' | 'medium' | 'high';
  }>;
  
  // 纠正建议
  correctionStrategies: Array<{
    biasType: string;
    strategies: string[];
    tools: string[];
  }>;
  
  // 预防清单
  preventionChecklist: string[];
  
  // 教育资源
  resources: Array<{
    title: string;
    type: 'article' | 'video' | 'tool';
    description: string;
  }>;
}
```

### 输出示例

```json
{
  "summary": {
    "riskLevel": "medium",
    "detectedCount": 3,
    "topRiskBiases": ["可得性启发", "代表性启发", "近因效应"],
    "overallRecommendation": "检测到中等程度认知偏差风险，建议使用纠正策略后再做决策"
  },
  "detectedBiases": [
    {
      "type": "availability",
      "name": "可得性启发",
      "confidence": 75,
      "signals": ["最近互动印象深刻", "近期有新信息影响判断"],
      "description": "过度重视昨天技术交流的积极印象，可能忽视之前的疑虑",
      "impact": "high"
    },
    {
      "type": "representativeness",
      "name": "代表性启发",
      "confidence": 60,
      "signals": ["候选人带有'大厂技术总监'标签"],
      "description": "可能因'大厂背景'标签高估其能力匹配度",
      "impact": "medium"
    },
    {
      "type": "recency",
      "name": "近因效应",
      "confidence": 70,
      "signals": ["昨天刚做完深度交流"],
      "description": "最近一次互动的积极体验可能 overshadow 之前的评估",
      "impact": "medium"
    }
  ],
  "correctionStrategies": [
    {
      "biasType": "可得性启发",
      "strategies": [
        "回顾之前记录的疑虑点",
        "与早期评估做对比",
        "咨询没有参与最近互动的人的意见"
      ],
      "tools": ["decision-journal", "360-evaluation"]
    },
    {
      "biasType": "代表性启发",
      "strategies": [
        "去标签化评估：不看背景，只看具体能力匹配",
        "寻找反例：大厂背景但失败的案例",
        "增加具体情境测试"
      ],
      "tools": ["structured-interview", "blind-evaluation"]
    }
  ],
  "preventionChecklist": [
    "□ 对所有候选人使用相同的评估标准",
    "□ 重要决策前24小时'冷静期'",
    "□ 咨询至少2位未参与评估的外部顾问",
    "□ 记录初始印象，避免被新信息过度影响",
    "□ 检查是否过度关注最近获得的信息"
  ],
  "resources": [
    {
      "title": "认知偏差速查表",
      "type": "tool",
      "description": "12种偏差的快速识别指南"
    }
  ]
}
```

---

## 纠正策略库

### 核心纠正策略

| 偏差类型 | 纠正策略 | 操作步骤 |
|----------|----------|----------|
| **可得性启发** | 信息平衡法 | 1.列出所有候选人 2.为每人列出3个优缺点 3.对比时只看清单不看记忆 |
| **代表性启发** | 去标签化 | 1.遮盖背景信息 2.只看具体能力描述 3.基于情境做判断 |
| **锚定效应** | 多重锚点 | 1.收集多个参考点 2.分别评估 3.综合判断 |
| **确认偏误** | 证伪思维 | 1.主动寻找反面证据 2.问自己"什么情况下他是错的" 3.寻求不同意见 |
| **光环效应** | 维度分离 | 1.将各维度分开评分 2.避免跨维度影响 3.使用结构化评估表 |
| **损失厌恶** | 框架转换 | 1.将"损失"重新表述为"机会成本" 2.计算不行动的成本 3.引入第三方视角 |
| **现状偏见** | 打破默认 | 1.强制考虑改变选项 2.设定决策截止日 3.引入外部视角 |

---

## 使用指南

### 触发条件

1. 决策前例行检查（推荐）
2. 感觉"太顺利"或"太纠结"时
3. 时间压力大、信息不完整时
4. 第一印象特别强时
5. 决策后复盘

### 使用流程

```
Step 1: 信息收集（5分钟）
  ├─ 记录决策情境
  ├─ 描述候选人特征
  └─ 回顾决策过程
  
Step 2: 偏差检测（自动）
  ├─ 系统并行检测12种偏差
  └─ 生成风险评级
  
Step 3: 结果解读（10分钟）
  ├─ 解释检测到的偏差
  ├─ 说明潜在影响
  └─ 讨论纠正策略
  
Step 4: 纠正实施（根据策略）
  ├─ 执行纠正行动
  └─ 更新评估结果
```

### 咨询师话术

**开场**:
> "人都有认知盲点，这不是能力问题，而是大脑的工作方式。让我们做个快速扫描，看看当前决策中可能有哪些'自动反应'在影响你。"

**解释偏差**:
> "我检测到可能有'可得性启发'在起作用——你最近和这位候选人的互动很积极，这可能会 overshadow 之前的疑虑。建议回顾一下之前的记录，看看整体画面是否一致。"

**给予信心**:
> "发现偏差是好事，说明我们有改进空间。这些纠正策略能帮你做出更清醒的选择。"

---

## 关联Skill

| Skill | 关系 | 说明 |
|-------|------|------|
| `dual-process-decision` | 上游 | 在感理协同分析后进一步检测偏差 |
| `decision-journal` | 配套 | 记录决策过程，便于偏差复盘 |
| `structured-interview` | 下游 | 使用结构化方法减少偏差 |

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-03-15 | 初始版本，12种核心偏差检测 |

---

## 参考资源

- Kahneman, D., & Tversky, A. (1974). Judgment under uncertainty
- Kahneman, D. (2011). Thinking, Fast and Slow
- 认知偏差在招聘决策中的应用研究
