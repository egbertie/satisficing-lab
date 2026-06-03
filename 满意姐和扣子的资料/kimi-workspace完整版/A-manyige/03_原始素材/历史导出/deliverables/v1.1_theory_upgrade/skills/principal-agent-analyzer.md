# Skill: principal-agent-analyzer
## 委托代理分析器

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **Skill ID** | `principal-agent-analyzer` |
| **名称** | 委托代理分析器 |
| **理论来源** | Principal-Agent Theory (Jensen & Meckling, 1976) |
| **优先级** | P0 |
| **版本** | 1.0 |
| **创建日期** | 2026-03-15 |

---

## 功能概述

基于委托代理理论，帮助创业者分析和设计创始人（委托人）与合伙人（代理人）之间的关系机制，解决信息不对称和利益不一致问题，构建激励相容的合伙体系。

### 核心能力

1. **关系诊断**: 识别委托代理关系中的核心问题
2. **风险分析**: 评估道德风险和逆向选择风险
3. **机制设计**: 设计激励相容的合伙机制
4. **契约优化**: 优化股权、vesting、考核等契约条款

---

## 输入规范

### 输入参数

```typescript
interface PrincipalAgentInput {
  // 委托人（创始人）信息
  principal: {
    name: string;
    role: string;
    ownership: number;              // 当前股权比例
    keyInterests: string[];         // 核心利益点
    informationAdvantages: string[]; // 信息优势领域
    riskTolerance: 'low' | 'medium' | 'high';
  };
  
  // 代理人（合伙人）信息
  agent: {
    name: string;
    role: string;
    proposedOwnership: number;      // 提议股权比例
    keyMotivations: string[];       // 核心动机
    informationAsymmetries: string[]; // 信息不对称领域
    riskTolerance: 'low' | 'medium' | 'high';
  };
  
  // 关系特征
  relationship: {
    stage: 'pre_deal' | 'new_partnership' | 'established' | 'troubled';
    duration: number;               // 合作月数（如已合作）
    trustLevel: 1-10;
    communicationFrequency: 'daily' | 'weekly' | 'monthly';
    pastConflicts: string[];
  };
  
  // 业务情境
  business: {
    stage: 'seed' | 'series_a' | 'growth' | 'mature';
    keyMetrics: string[];           // 关键业务指标
    uncertaintyLevel: 'low' | 'medium' | 'high';
    industry: string;
  };
  
  // 现有/拟议契约
  contract: {
    equitySplit: {
      principal: number;
      agent: number;
    };
    vestingSchedule: {
      years: number;
      cliff: number;
      acceleration: string[];
    };
    performanceTerms: string[];
    exitProvisions: string[];
  };
}
```

### 输入示例

```json
{
  "principal": {
    "name": "创始人A",
    "role": "CEO",
    "ownership": 80,
    "keyInterests": ["保持战略控制权", "公司长期价值", "融资节奏"],
    "informationAdvantages": ["投资人关系", "战略方向", "财务状况"],
    "riskTolerance": "medium"
  },
  "agent": {
    "name": "合伙人B",
    "role": "CTO",
    "proposedOwnership": 20,
    "keyMotivations": ["技术实现", "股权价值", "决策参与权"],
    "informationAsymmetries": ["真实技术能力", "工作投入度", "长期承诺"],
    "riskTolerance": "medium"
  },
  "relationship": {
    "stage": "pre_deal",
    "duration": 0,
    "trustLevel": 5,
    "communicationFrequency": "weekly",
    "pastConflicts": []
  },
  "business": {
    "stage": "seed",
    "keyMetrics": ["产品开发进度", "技术验证", "团队建设"],
    "uncertaintyLevel": "high",
    "industry": "AI芯片"
  },
  "contract": {
    "equitySplit": {
      "principal": 80,
      "agent": 20
    },
    "vestingSchedule": {
      "years": 4,
      "cliff": 1,
      "acceleration": ["公司出售", "里程碑达成"]
    },
    "performanceTerms": ["完成MVP开发", "组建3人技术团队"],
    "exitProvisions": ["离职回购", "竞业禁止"]
  }
}
```

---

## 核心问题分析

### 委托代理问题的三维模型

```
                    ┌─────────────────────────────────────┐
                    │         委托代理核心问题              │
                    └─────────────────┬───────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│   利益不一致          │   │    信息不对称        │   │    契约不完全        │
│  Divergent Interests  │   │  Information        │   │  Incomplete         │
│                       │   │  Asymmetry          │   │  Contracts          │
├─────────────────────┤   ├─────────────────────┤   ├─────────────────────┤
• 创始人要长期价值      │   │ • 真实能力难观察      │   │ • 未来情境难预测      │
• 合伙人要短期收益      │   │ • 努力程度难验证      │   │ • 所有条款难穷尽      │
• 风险偏好不同         │   │ • 私人信息难获取      │   │ • 执行标准难量化      │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      ▼
                    ┌─────────────────────────────────────┐
                    │    风险表现：道德风险 + 逆向选择       │
                    └─────────────────────────────────────┘
```

### 道德风险（Moral Hazard）检测

**定义**: 签约后，代理人可能采取损害委托人利益的行为

**检测指标**:

| 风险信号 | 权重 | 检测方法 |
|----------|------|----------|
| 努力不可观察 | 高 | 是否有明确的交付物和里程碑 |
| 多任务冲突 | 中 | 合伙人是否承担多个可能有冲突的角色 |
| 短期主义 | 高 | 激励机制是否过度强调短期指标 |
| 搭便车 | 中 | 团队产出是否难以归因到个人 |
| 资产挪用 | 高 | 是否有财务管控机制 |

### 逆向选择（Adverse Selection）检测

**定义**: 签约前，低质量候选人更积极争取机会，委托人难以识别

**检测指标**:

| 风险信号 | 权重 | 检测方法 |
|----------|------|----------|
| 能力难验证 | 高 | 是否有试用期或验证期 |
| 信号虚假 | 中 | 背景信息是否经过核实 |
| 隐藏动机 | 中 | 是否有深入的动机访谈 |
| 过度承诺 | 高 | 承诺是否与历史表现一致 |

---

## 处理逻辑

### 分析流程

```
┌─────────────┐
│  识别问题类型 │
│ 道德风险？   │
│ 逆向选择？   │
└──────┬──────┘
       ▼
┌─────────────┐
│  评估风险等级 │
│ 高/中/低    │
└──────┬──────┘
       ▼
┌─────────────┐
│  设计机制   │
│ 激励相容    │
└──────┬──────┘
       ▼
┌─────────────┐
│  优化契约   │
│ 条款建议    │
└──────┬──────┘
       ▼
┌─────────────┐
│  输出方案   │
└─────────────┘
```

### 机制设计原则

```typescript
interface MechanismDesign {
  // 激励相容约束（IC）
  incentiveCompatibility: {
    description: string;
    implementation: string[];
  };
  
  // 参与约束（IR）
  participationConstraint: {
    description: string;
    minimumOffer: string;
  };
  
  // 信息揭示机制
  informationRevelation: {
    mechanisms: string[];
    verification: string[];
  };
}

// 激励相容设计
function designIncentiveContract(
  principal: Principal,
  agent: Agent,
  business: Business
): MechanismDesign {
  return {
    incentiveCompatibility: {
      description: "让合伙人的最优选择与创始人的目标一致",
      implementation: [
        "股权vesting与里程碑绑定",
        "业绩股权与关键指标挂钩",
        "长期激励超过短期收益"
      ]
    },
    participationConstraint: {
      description: "确保合伙人愿意参与",
      minimumOffer: "达到合伙人的机会成本 + 风险溢价"
    },
    informationRevelation: {
      mechanisms: [
        "试用期验证真实能力",
        "阶段性里程碑检验承诺",
        "第三方背调核实信息"
      ],
      verification: [
        "定期绩效评估",
        "关键交付物审查",
        "360度反馈"
      ]
    }
  };
}
```

---

## 输出规范

### 输出结构

```typescript
interface PrincipalAgentOutput {
  // 问题诊断
  diagnosis: {
    primaryIssues: string[];
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    keyConcerns: string[];
  };
  
  // 风险分析
  riskAnalysis: {
    moralHazard: {
      level: 'low' | 'medium' | 'high';
      scenarios: string[];
      indicators: string[];
    };
    adverseSelection: {
      level: 'low' | 'medium' | 'high';
      scenarios: string[];
      indicators: string[];
    };
  };
  
  // 机制设计建议
  mechanismDesign: {
    incentiveAlignment: string[];
    monitoringMechanisms: string[];
    informationRevelation: string[];
  };
  
  // 契约条款优化
  contractOptimization: {
    equityStructure: {
      recommendation: string;
      rationale: string;
    };
    vestingOptimization: {
      recommendation: string;
      rationale: string;
    };
    performanceTerms: string[];
    protectionClauses: string[];
  };
  
  // 实施建议
  implementation: {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
  };
  
  // 风险提示
  riskWarnings: string[];
}
```

### 输出示例

```json
{
  "diagnosis": {
    "primaryIssues": [
      "信息不对称：合伙人的真实技术能力和长期承诺难以验证",
      "利益校准：合伙人的短期收益诉求与创始人的长期价值创造目标需要校准",
      "契约不完全：未来技术发展路径不确定，难以预设所有情境"
    ],
    "riskLevel": "medium",
    "keyConcerns": [
      "签约后技术投入不足",
      "关键节点前离职",
      "技术与商业目标冲突"
    ]
  },
  "riskAnalysis": {
    "moralHazard": {
      "level": "medium",
      "scenarios": [
        "合伙人获得股权后工作投入下降",
        "技术路线选择偏向个人兴趣而非公司需要",
        "关键产品节点前离职"
      ],
      "indicators": [
        "当前vesting方案缺乏里程碑绑定",
        "绩效考核标准不够具体",
        "缺乏关键节点留存机制"
      ]
    },
    "adverseSelection": {
      "level": "medium",
      "scenarios": [
        "实际技术能力低于面试表现",
        "对创业承诺不如口头表达的坚定"
      ],
      "indicators": [
        "缺乏技术验证期",
        "背景调查不够深入"
      ]
    }
  },
  "mechanismDesign": {
    "incentiveAlignment": [
      "将vesting与技术里程碑绑定（MVP完成、产品上线、技术团队搭建）",
      "设置业绩股权，与公司估值增长挂钩",
      "引入竞业禁止和离职回购条款"
    ],
    "monitoringMechanisms": [
      "双周技术进展评审",
      "月度OKR对齐会议",
      "季度360度反馈"
    ],
    "informationRevelation": [
      "3个月试用期，重点验证技术能力和工作投入",
      "技术能力第三方评估",
      "参考前同事/下属反馈"
    ]
  },
  "contractOptimization": {
    "equityStructure": {
      "recommendation": "20%总股权 = 15%基础股权 + 5%业绩股权",
      "rationale": "基础股权保障合伙人基本激励，业绩股权与公司成功绑定，实现激励相容"
    },
    "vestingOptimization": {
      "recommendation": "4年vesting，1年cliff，里程碑加速条款",
      "rationale": "长期绑定+关键节点激励，既防短期离职，又奖重大贡献"
    },
    "performanceTerms": [
      "试用期：完成技术架构设计 + 组建2人核心团队",
      "第一年：MVP开发完成并通过技术验证",
      "第二年：产品上线并实现技术迭代"
    ],
    "protectionClauses": [
      "离职回购：按已服务时间比例回购未归属股权",
      "竞业禁止：离职后2年内不得加入竞品公司",
      "知识产权：在职期间所有技术成果归公司所有",
      "道德条款：严重失职可无偿收回股权"
    ]
  },
  "implementation": {
    "immediate": [
      "完善vesting条款，增加里程碑绑定",
      "设计3个月试用期考核标准"
    ],
    "shortTerm": [
      "建立双周技术评审机制",
      "完成背景调查"
    ],
    "longTerm": [
      "建立季度合伙人OKR对齐机制",
      "设计长期股权激励池"
    ]
  },
  "riskWarnings": [
    "警告：当前方案缺乏里程碑绑定，存在技术节点前离职风险",
    "建议：务必设置试用期，验证真实能力后再全面授权",
    "注意：竞业禁止条款需要合理补偿，否则可能无效"
  ]
}
```

---

## 机制设计工具箱

### 激励相容机制

| 机制 | 适用情境 | 设计要点 | 注意事项 |
|------|----------|----------|----------|
| **里程碑vesting** | 长期项目 | 将股权释放与关键节点绑定 | 里程碑需可验证、不可操控 |
| **业绩股权** | 目标明确 | 与关键指标（用户、收入、估值）挂钩 | 指标需双方认可、不可操纵 |
| **对赌条款** | 估值分歧 | 根据未来业绩调整股权比例 | 需考虑极端情况的处理 |
| **期权池** | 团队扩张 | 预留股权用于未来激励 | 明确期权池的管理机制 |

### 监督与信息揭示机制

| 机制 | 功能 | 实施方式 |
|------|------|----------|
| **试用期** | 能力验证 | 3-6个月，明确考核标准 |
| **阶段性评审** | 进度监控 | 双周/月度里程碑检查 |
| **360度反馈** | 全面评估 | 上级、同事、下属反馈 |
| **第三方审计** | 财务监督 | 季度财务审查 |
| **信息公开** | 减少信息不对称 | 定期分享关键业务数据 |

### 保护机制

| 机制 | 保护对象 | 设计要点 |
|------|----------|----------|
| **离职回购** | 公司 | 按服务时间比例回购 |
| **竞业禁止** | 公司 | 合理期限+合理补偿 |
| **知识产权** | 公司 | 明确归属，离职交接 |
| **道德条款** | 公司 | 严重失职的处理机制 |
| **拖售权** | 小股东 | 大股东出售时需带小股东 |
| **反稀释** | 股东 | 后续融资时的保护 |

---

## 使用指南

### 触发条件

1. 设计合伙协议时
2. 评估现有合伙关系健康度时
3. 合伙关系出现问题时
4. 引入新合伙人前

### 使用流程

```
Step 1: 信息收集
  ├─ 明确双方角色和利益点
  ├─ 识别信息不对称领域
  └─ 了解现有契约条款
  
Step 2: 风险诊断
  ├─ 评估道德风险等级
  ├─ 评估逆向选择风险
  └─ 确定关键问题
  
Step 3: 机制设计
  ├─ 设计激励相容机制
  ├─ 设计监督机制
  └─ 设计信息揭示机制
  
Step 4: 契约优化
  ├─ 优化股权结构
  ├─ 优化vesting条款
  └─ 增加保护条款
```

### 咨询师话术

**开场**:
> "创始人（委托人）和合伙人（代理人）天然有信息不对称——你不可能完全知道他的真实能力和动机。让我们用委托代理理论的框架，设计一套机制，让双方的利益自动对齐。"

**解释问题**:
> "当前方案有两个风险点：一是道德风险——签约后他可能没有面试时那么努力；二是信息不对称——他的真实能力还需要验证。我们需要在契约中设计应对机制。"

**建议机制**:
> "我建议采用'里程碑vesting'机制：不是简单地4年vesting，而是将股权释放与关键节点绑定——MVP完成、产品上线、技术团队组建。这样，他的利益就与公司的发展真正绑定了。"

---

## 关联Skill

| Skill | 关系 | 说明 |
|-------|------|------|
| `game-theory-negotiation` | 上游 | 谈判后的机制固化 |
| `heuristic-bias-detector` | 并行 | 防止机制设计中的认知偏差 |
| `contract-drafter` | 下游 | 将机制转化为法律条款 |

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-03-15 | 初始版本，核心机制设计框架 |

---

## 参考资源

- Jensen, M. C., & Meckling, W. H. (1976). Theory of the firm
- Holmström, B. (1979). Moral hazard and observability
- 激励机制设计最佳实践
