# Skill: dual-process-decision
## 双系统决策分析器

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **Skill ID** | `dual-process-decision` |
| **名称** | 双系统决策分析器 |
| **理论来源** | Dual Process Theory (Kahneman, 2011) |
| **优先级** | P0 |
| **版本** | 1.0 |
| **创建日期** | 2026-03-15 |

---

## 功能概述

基于卡尼曼双系统理论，帮助创业者分析和协调系统1（直觉/快速）与系统2（理性/慢速）在合伙人决策中的输入，识别两者冲突，提供协同建议。

### 核心能力

1. **系统识别**: 区分决策中的直觉信号与理性分析
2. **冲突检测**: 识别系统1与系统2的矛盾
3. **协同建议**: 提供感理协同的具体策略
4. **校准训练**: 帮助提升系统1准确性和系统2效率

---

## 输入规范

### 输入参数

```typescript
interface DualProcessInput {
  // 基础信息
  decisionContext: {
    stage: 'search' | 'evaluation' | 'negotiation' | 'decision';
    urgency: 'low' | 'medium' | 'high';
    complexity: 'simple' | 'moderate' | 'complex';
  };
  
  // 系统1输入（直觉）
  system1: {
    firstImpression: string;        // 第一印象描述
    gutFeeling: 'positive' | 'neutral' | 'negative' | 'mixed';
    bodilySignals: string[];        // 身体信号（紧绷/舒展/心跳等）
    intuitionConfidence: 1-10;      // 直觉自信度
  };
  
  // 系统2输入（理性）
  system2: {
    pfiScore: number;               // PFI分数（如有）
    logicAnalysis: string;          // 逻辑分析摘要
    prosCons: {
      pros: string[];
      cons: string[];
    };
    logicConfidence: 1-10;          // 逻辑自信度
  };
  
  // 候选人信息（如适用）
  candidate?: {
    name: string;
    role: string;
    interactionCount: number;
  };
}
```

### 输入示例

```json
{
  "decisionContext": {
    "stage": "evaluation",
    "urgency": "medium",
    "complexity": "complex"
  },
  "system1": {
    "firstImpression": "第一次见面感觉很舒服，像认识很久的朋友",
    "gutFeeling": "positive",
    "bodilySignals": ["肩膀放松", "交流时面带微笑", "没有防御姿态"],
    "intuitionConfidence": 8
  },
  "system2": {
    "pfiScore": 72,
    "logicAnalysis": "技术能力匹配，但过往创业经历有一次失败",
    "prosCons": {
      "pros": ["技术深度好", "沟通能力佳", "价值观一致"],
      "cons": ["创业经验不足", "过往有失败记录"]
    },
    "logicConfidence": 6
  }
}
```

---

## 处理逻辑

### 流程图

```
┌─────────────┐
│  接收输入    │
└──────┬──────┘
       ▼
┌─────────────┐
│  系统1分析   │ ──→ 直觉可信度评估
└──────┬──────┘
       ▼
┌─────────────┐
│  系统2分析   │ ──→ 逻辑完整度评估
└──────┬──────┘
       ▼
┌─────────────┐
│  冲突检测    │ ──→ 类型A/B/无冲突
└──────┬──────┘
       ▼
┌─────────────┐
│  协同建议    │ ──→ 具体行动建议
└──────┬──────┘
       ▼
┌─────────────┐
│  生成报告    │
└─────────────┘
```

### 冲突检测逻辑

```typescript
type ConflictType = 'A' | 'B' | 'none';

function detectConflict(s1: System1, s2: System2): {
  type: ConflictType;
  severity: 'low' | 'medium' | 'high';
  description: string;
} {
  // 类型A: 直觉绿灯 + 逻辑红灯
  if (s1.gutFeeling === 'positive' && s2.logicConfidence < 5) {
    return {
      type: 'A',
      severity: 'high',
      description: '直觉喜欢但理性有顾虑'
    };
  }
  
  // 类型B: 直觉红灯 + 逻辑绿灯
  if (s1.gutFeeling === 'negative' && s2.logicConfidence > 7) {
    return {
      type: 'B',
      severity: 'medium',
      description: '理性认可但直觉有保留'
    };
  }
  
  // 无冲突
  return {
    type: 'none',
    severity: 'low',
    description: '感理基本协同'
  };
}
```

### 协同建议矩阵

| 冲突类型 | 建议策略 | 具体行动 |
|----------|----------|----------|
| **类型A** | 深度调查 | 增加背景调查、延长试用期、引入第三方评估 |
| **类型B** | 直觉解码 | 分析直觉来源、检查可得性/代表性偏差、增加互动 |
| **无冲突** | 推进确认 | 综合评估、设定满意标准、准备决策 |

---

## 输出规范

### 输出结构

```typescript
interface DualProcessOutput {
  // 分析摘要
  summary: {
    overallAlignment: 'high' | 'medium' | 'low';
    recommendation: 'proceed' | 'investigate' | 'pause';
    confidence: 1-10;
  };
  
  // 系统1分析
  system1Analysis: {
    credibility: 1-10;
    potentialBiases: string[];
    strengths: string[];
    concerns: string[];
  };
  
  // 系统2分析
  system2Analysis: {
    completeness: 1-10;
    gaps: string[];
    strengths: string[];
  };
  
  // 冲突分析
  conflictAnalysis: {
    type: 'A' | 'B' | 'none';
    description: string;
    rootCause: string;
  };
  
  // 协同建议
  recommendations: {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
  };
  
  // 工具建议
  suggestedTools: string[];
}
```

### 输出示例

```json
{
  "summary": {
    "overallAlignment": "medium",
    "recommendation": "investigate",
    "confidence": 6
  },
  "system1Analysis": {
    "credibility": 7,
    "potentialBiases": ["可得性启发（最近见面印象深刻）"],
    "strengths": ["身体信号积极", "直觉自信度高"],
    "concerns": ["互动次数少，直觉可能基于有限信息"]
  },
  "system2Analysis": {
    "completeness": 6,
    "gaps": ["未进行深度背景调查", "技术能力需进一步验证"],
    "strengths": ["PFI分数达标", "价值观维度匹配"]
  },
  "conflictAnalysis": {
    "type": "A",
    "description": "直觉喜欢但理性有顾虑",
    "rootCause": "系统1捕捉到良好的人际化学反应，但系统2识别出经验不足的客观风险"
  },
  "recommendations": {
    "immediate": ["增加一次技术深度交流", "验证过往创业失败的具体原因"],
    "shortTerm": ["进行结构化背景调查", "设计3个月试用期方案"],
    "longTerm": ["建立系统1直觉日志，追踪准确率"]
  },
  "suggestedTools": ["heuristic-bias-detector", "background-check-guide"]
}
```

---

## 使用指南

### 触发条件

1. 客户报告直觉与理性冲突时
2. 决策陷入僵局时
3. 需要验证感理协同时
4. 定期校准训练时

### 使用流程

```
Step 1: 收集系统1输入
  ├─ 询问第一印象
  ├─ 记录身体信号
  └─ 评估直觉自信度
  
Step 2: 收集系统2输入
  ├─ 获取PFI分数（如有）
  ├─ 整理逻辑分析
  └─ 列出优缺点
  
Step 3: 运行分析
  ├─ 系统识别
  ├─ 冲突检测
  └─ 建议生成
  
Step 4: 解读结果
  ├─ 解释冲突类型
  ├─ 说明建议理由
  └─ 讨论下一步行动
```

### 咨询师话术

**开场**:
> "选合伙人时，我们常常遇到'脑子说可以，但心里不踏实'，或者反过来。这很正常——我们的大脑有两个系统在工作。让我们分析一下你的系统1（直觉）和系统2（理性）分别在说什么。"

**解释类型A冲突**:
> "你的直觉给了绿灯，但理性有顾虑。这通常意味着你捕捉到了一些非语言的积极信号，但客观数据有缺口。建议增加调查，给直觉一个更坚实的基础。"

**解释类型B冲突**:
> "理性分析不错，但直觉有保留。这可能是因为：1）某些偏差影响了直觉；2）直觉捕捉到了理性分析遗漏的信息。建议深入探索直觉的来源。"

---

## 关联Skill

| Skill | 关系 | 触发条件 |
|-------|------|----------|
| `heuristic-bias-detector` | 下游 | 检测到潜在偏差时调用 |
| `decision-quality-assessor` | 上游 | 作为整体决策质量评估的一部分 |
| `intuition-training` | 并行 | 长期提升系统1准确性 |

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-03-15 | 初始版本，P0级核心Skill |

---

## 参考资源

- Kahneman, D. (2011). Thinking, Fast and Slow
- 双系统理论在决策科学中的应用综述
- 满意解研究所感理协同框架V1.1
