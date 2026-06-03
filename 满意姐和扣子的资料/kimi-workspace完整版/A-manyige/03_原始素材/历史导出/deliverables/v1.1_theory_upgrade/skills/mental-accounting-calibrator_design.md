# Skill: mental-accounting-calibrator
## 心理账户校准 - P1级Skill设计文档

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **Skill ID** | `mental-accounting-calibrator` |
| **名称** | 心理账户校准 |
| **理论来源** | Mental Accounting (Thaler, 1985) |
| **优先级** | P1 |
| **版本** | 0.1 (设计阶段) |
| **计划引入** | V1.2 (3个月内) |

---

## 设计目标

基于心理账户理论，帮助创业者识别和调整对股权、现金、期权等不同"账户"的非理性分类，优化谈判中的价值感知和分配决策。

---

## 架构设计

### 功能模块

```
┌─────────────────────────────────────────────────────────────┐
│                  心理账户校准 Skill 架构                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐      ┌───────────────┐                  │
│  │   账户识别     │  →   │   偏差检测     │                  │
│  │  Identification│      │   Detection   │                  │
│  └───────┬───────┘      └───────┬───────┘                  │
│          │                       │                          │
│          └───────────┬───────────┘                          │
│                      ▼                                      │
│              ┌───────────────┐                             │
│              │   价值重构     │                             │
│              │  Revaluation  │                             │
│              └───────┬───────┘                             │
│                      │                                      │
│                      ▼                                      │
│              ┌───────────────┐                             │
│              │   校准建议     │                             │
│              │ Calibration   │                             │
│              └───────────────┘                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 心理账户类型

| 账户类型 | 典型偏差 | 合伙人场景 |
|----------|----------|------------|
| **当前收入账户** | 过度重视现金 | 现金vs股权的权衡 |
| **资产账户** | 禀赋效应 | 对自己股权的过度估值 |
| **未来收入账户** | 过度折现 | 对期权价值的低估 |
| **沉没成本账户** | 沉没成本谬误 | 对过往投入的执念 |
| ** windfall 账户** | 轻松消费心理 | 对意外股权的不珍惜 |

---

## 接口定义

### 输入接口

```typescript
interface MentalAccountingInput {
  // 决策者信息
  decisionMaker: {
    role: 'founder' | 'candidate';
    financialSituation: {
      liquidityNeeds: 'low' | 'medium' | 'high';
      riskTolerance: 'low' | 'medium' | 'high';
      opportunityCost: number;  // 机会成本估算
    };
    currentMentalAccounts: Array<{
      category: string;
      perceivedValue: number;  // 主观价值（1-10）
      actualValue: number;     // 客观价值（1-10）
    }>;
  };
  
  // 决策情境
  decisionContext: {
    type: 'equity_negotiation' | 'compensation_design' | 'investment_decision';
    options: Array<{
      name: string;
      cashComponent: number;
      equityComponent: number;
      vestingYears: number;
      riskLevel: 'low' | 'medium' | 'high';
    }>;
  };
  
  // 认知偏差信号
  biasSignals: {
    anchoringToFirstOffer: boolean;
    lossAversionManifested: boolean;
    endowmentEffectPresent: boolean;
    sunkCostConsideration: boolean;
  };
}
```

### 输出接口

```typescript
interface MentalAccountingOutput {
  // 账户分析
  accountAnalysis: {
    identifiedAccounts: Array<{
      account: string;
      currentPerception: string;
      rationalValue: string;
      gap: 'undervalued' | 'overvalued' | 'aligned';
      gapMagnitude: 'small' | 'medium' | 'large';
    }>;
    primaryBias: string;
    biasImpact: string;
  };
  
  // 价值重构
  valueReframing: {
    originalFrame: string;
    reframedPerspective: string;
    newValuation: number;
    reframingTechniques: string[];
  };
  
  // 校准建议
  calibration: {
    cognitiveAdjustments: string[];
    negotiationTactics: string[];
    decisionAids: string[];
  };
  
  // 工具
  suggestedTools: string[];
}
```

---

## 校准技术

### 框架转换技术

| 原始框架 | 问题 | 转换框架 | 效果 |
|----------|------|----------|------|
| "给股权" | 损失框架 | "共同创造价值" | 收益框架 |
| "现金 vs 股权" | 独立账户 | "总报酬包" | 整合评估 |
| "我的股权" | 禀赋效应 | "公司未来价值的一部分" | 客观估值 |
| "已经投入的时间" | 沉没成本 | "未来的机会成本" | 前瞻视角 |

### 参考点调整

```typescript
interface ReferencePointAdjustment {
  // 锚定调整
  anchoringCalibration: {
    currentAnchor: string;
    alternativeAnchors: string[];
    recommendedAnchor: string;
    rationale: string;
  };
  
  // 损失/收益框架
  lossGainReframing: {
    currentFrame: 'loss' | 'gain';
    suggestedFrame: 'loss' | 'gain';
    reframingScript: string;
  };
}

// 示例：股权谈判中的框架转换
const equityNegotiationReframing: ReferencePointAdjustment = {
  anchoringCalibration: {
    currentAnchor: "行业惯例是CTO拿20%",
    alternativeAnchors: [
      "公司未来估值增长潜力",
      "全职机会成本折现",
      "风险调整后的期望收益"
    ],
    recommendedAnchor: "基于公司5年后的估值预期，计算风险调整后的期望收益",
    rationale: "将谈判从'分蛋糕'转向'一起把蛋糕做大'"
  },
  lossGainReframing: {
    currentFrame: 'loss',
    suggestedFrame: 'gain',
    reframingScript: "不是'我给你20%'，而是'如果你加入，我们一起创造的价值中，你占20%'"
  }
};
```

---

## 典型场景应用

### 场景1：创始人过度珍惜股权

**症状**: 创始人只愿给10%股权，候选人要求25%

**分析**:
- 心理账户：将股权视为"我的"（禀赋效应）
- 框架：损失框架（给出去就是失去）

**校准**:
1. 重新框架：从"给股权"到"共同创造"
2. 计算机会成本：不给够股权，找不到合适人的代价
3. 锚定调整：从固定比例到业绩对赌

### 场景2：候选人过度重视现金

**症状**: 候选人坚持高现金低股权

**分析**:
- 心理账户：现金账户vs股权账户分离
- 偏差：过度折现未来收益

**校准**:
1. 展示股权长期价值
2. 总报酬包视角
3. 风险调整后的比较

---

## 与五路图腾的关联

| 心理账户概念 | 五路图腾对应 | 整合应用 |
|--------------|--------------|----------|
| 框架转换 | 司马贺（方法） | 理性重新评估 |
| 价值重构 | 刘禹锡（价值） | 本质价值识别 |
| 损失厌恶 | 六祖慧能（直觉） | 情绪反应觉察 |

---

## 开发计划

| 阶段 | 时间 | 任务 |
|------|------|------|
| **设计** | 第1-2周 | 完善校准技术、设计交互 |
| **开发** | 第3-6周 | 实现核心校准逻辑 |
| **测试** | 第7-10周 | 案例测试、效果验证 |
| **试点** | 第11-12周 | 2-3个客户试点 |

---

**设计文档版本**: 0.1  
**下次更新**: 开发启动前完善校准技术细节
