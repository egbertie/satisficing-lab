# Skill: emotional-intelligence-assessment
## 情商评估 - P1级Skill设计文档

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **Skill ID** | `emotional-intelligence-assessment` |
| **名称** | 情商评估 |
| **理论来源** | Emotional Intelligence (Goleman, 1995) |
| **优先级** | P1 |
| **版本** | 0.1 (设计阶段) |
| **计划引入** | V1.2 (3个月内) |

---

## 设计目标

基于戈尔曼情商理论，帮助创业者评估合伙人的情绪智力，包括自我觉察、自我管理、社会觉察、关系管理四个维度，预测合伙关系中的情绪冲突风险。

---

## 架构设计

### 功能模块

```
┌─────────────────────────────────────────────────────────────┐
│                   情商评估 Skill 架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  自我觉察评估  │  │  自我管理评估  │  │  社会觉察评估  │      │
│  │ Self-Aware   │  │ Self-Manage  │  │ Social-Aware │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│                           ▼                                │
│                  ┌──────────────┐                         │
│                  │  关系管理评估  │                         │
│                  │ Relationship │                         │
│                  └──────┬───────┘                         │
│                           │                                │
│                           ▼                                │
│                  ┌──────────────┐                         │
│                  │   综合报告    │                         │
│                  │   Report     │                         │
│                  └──────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 理论映射

| 情商维度 | 理论定义 | 合伙人场景映射 |
|----------|----------|----------------|
| **自我觉察** | 识别自身情绪 | 能否在压力下保持清醒自我认知 |
| **自我管理** | 调节自身情绪 | 面对挫折和冲突时的情绪控制 |
| **社会觉察** | 感知他人情绪 | 理解团队成员和创始人的情绪状态 |
| **关系管理** | 管理人际关系 | 处理冲突、建立信任、影响他人 |

---

## 接口定义

### 输入接口

```typescript
interface EQAssessmentInput {
  // 评估方式
  method: 'self_report' | 'interview' | '360_feedback' | 'mixed';
  
  // 自评问卷结果（如使用）
  selfReport?: {
    questionnaireId: string;
    responses: Array<{
      questionId: string;
      score: 1-5;
    }>;
  };
  
  // 访谈记录（如使用）
  interviewData?: {
    notes: string;
    observedBehaviors: string[];
    stressResponseExamples: string[];
    conflictHandlingExamples: string[];
  };
  
  // 360度反馈（如使用）
  feedback360?: {
    raters: Array<{
      relationship: 'supervisor' | 'peer' | 'subordinate';
      ratings: {
        selfAwareness: 1-5;
        selfManagement: 1-5;
        socialAwareness: 1-5;
        relationshipManagement: 1-5;
      };
      comments: string;
    }>;
  };
  
  // 候选人信息
  candidate: {
    name: string;
    role: string;
    experience: string;
  };
}
```

### 输出接口

```typescript
interface EQAssessmentOutput {
  // 综合评分
  overall: {
    eqScore: 1-100;
    percentile: string;  // "高于85%的职场人士"
    interpretation: string;
  };
  
  // 四维度评分
  dimensions: {
    selfAwareness: {
      score: 1-25;
      level: 'low' | 'medium' | 'high';
      strengths: string[];
      developmentAreas: string[];
    };
    selfManagement: {
      score: 1-25;
      level: 'low' | 'medium' | 'high';
      strengths: string[];
      developmentAreas: string[];
    };
    socialAwareness: {
      score: 1-25;
      level: 'low' | 'medium' | 'high';
      strengths: string[];
      developmentAreas: string[];
    };
    relationshipManagement: {
      score: 1-25;
      level: 'low' | 'medium' | 'high';
      strengths: string[];
      developmentAreas: string[];
    };
  };
  
  // 合伙关系风险预测
  partnershipRisks: Array<{
    scenario: string;
    probability: 'low' | 'medium' | 'high';
    mitigation: string;
  }>;
  
  // 建议
  recommendations: {
    forFounder: string[];      // 创始人如何与此人合作
    forCandidate: string[];    // 此人如何提升
    teamFit: string;           // 与现有团队的匹配建议
  };
}
```

---

## 问卷设计（草案）

### 自我觉察维度（示例题目）

| 题目 | 选项 | 计分 |
|------|------|------|
| 我能准确识别自己当下的情绪状态 | 1-5分 | 直接计分 |
| 我知道什么情况下自己会情绪失控 | 1-5分 | 直接计分 |
| 我能理解自己情绪的来源 | 1-5分 | 直接计分 |

### 自我管理维度（示例题目）

| 题目 | 选项 | 计分 |
|------|------|------|
| 压力下我能保持冷静 | 1-5分 | 直接计分 |
| 挫折后我能快速恢复 | 1-5分 | 直接计分 |
| 我不会让负面情绪影响决策 | 1-5分 | 直接计分 |

### 社会觉察维度（示例题目）

| 题目 | 选项 | 计分 |
|------|------|------|
| 我能感知他人的情绪状态 | 1-5分 | 直接计分 |
| 我能理解他人的观点 | 1-5分 | 直接计分 |
| 我能在团队中感知氛围变化 | 1-5分 | 直接计分 |

### 关系管理维度（示例题目）

| 题目 | 选项 | 计分 |
|------|------|------|
| 我能有效处理人际冲突 | 1-5分 | 直接计分 |
| 我能建立并维护信任关系 | 1-5分 | 直接计分 |
| 我能影响他人而不引起反感 | 1-5分 | 直接计分 |

---

## 与五路图腾的关联

| 情商维度 | 五路图腾对应 | 整合应用 |
|----------|--------------|----------|
| 自我觉察 | 六祖慧能（直觉） | 身体信号识别 |
| 自我管理 | 观自在（状态） | 情绪调节能力 |
| 社会觉察 | 孔子（伦理） | 感知他人需求 |
| 关系管理 | 孔子（伦理） | 关系建设能力 |

---

## 开发计划

| 阶段 | 时间 | 任务 |
|------|------|------|
| **设计** | 第1-2周 | 完善问卷、设计评分算法 |
| **开发** | 第3-6周 | 实现核心评估逻辑 |
| **测试** | 第7-10周 | 内部测试、校准评分标准 |
| **试点** | 第11-12周 | 2-3个客户试点 |

---

## 风险评估

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| 自评偏差 | 高 | 结合面试观察和360反馈 |
| 文化适应性 | 中 | 针对中国创业者调整题目 |
| 效度验证 | 中 | 与合伙成功率做相关性验证 |

---

**设计文档版本**: 0.1  
**下次更新**: 开发启动前完善问卷细节
