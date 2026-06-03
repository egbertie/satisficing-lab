# Skill: psychological-safety-monitor
## 心理安全监测 - P1级Skill设计文档

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **Skill ID** | `psychological-safety-monitor` |
| **名称** | 心理安全监测 |
| **理论来源** | Psychological Safety (Edmondson, 1999) |
| **优先级** | P1 |
| **版本** | 0.1 (设计阶段) |
| **计划引入** | V1.2 (3个月内) |

---

## 设计目标

基于心理安全感理论，帮助创业团队监测合伙人之间的信任氛围，识别心理安全隐患，提供建设健康合伙关系的具体建议。

---

## 架构设计

### 功能模块

```
┌─────────────────────────────────────────────────────────────┐
│                  心理安全监测 Skill 架构                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐      ┌───────────────┐                  │
│  │   基线评估     │  →   │   持续监测     │                  │
│  │   Baseline    │      │   Monitoring  │                  │
│  └───────┬───────┘      └───────┬───────┘                  │
│          │                       │                          │
│          └───────────┬───────────┘                          │
│                      ▼                                      │
│              ┌───────────────┐                             │
│              │   风险预警     │                             │
│              │    Alert      │                             │
│              └───────┬───────┘                             │
│                      │                                      │
│                      ▼                                      │
│              ┌───────────────┐                             │
│              │   干预建议     │                             │
│              │ Intervention  │                             │
│              └───────────────┘                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 心理安全维度

| 维度 | 定义 | 合伙人场景指标 |
|------|------|----------------|
| **敢于提问** | 不怕被嘲笑，敢于提出疑问 | 合伙人是否敢于质疑决策 |
| **承认错误** | 不怕被惩罚，敢于承认失误 | 失败时是否互相指责 |
| **提出不同意见** | 不怕关系受损，敢于表达异议 | 决策冲突时是否压抑想法 |
| **寻求帮助** | 不怕显得无能，敢于求助 | 遇到困难时是否独自硬撑 |
| **表达担忧** | 不怕被视为负能量，敢于表达担忧 | 风险是否被充分讨论 |

---

## 接口定义

### 输入接口

```typescript
interface PsychologicalSafetyInput {
  // 评估类型
  assessmentType: 'baseline' | 'pulse' | 'intervention';
  
  // 团队信息
  team: {
    members: Array<{
      name: string;
      role: string;
      tenure: number;  // 合作月数
    }>;
    stage: 'forming' | 'storming' | 'norming' | 'performing';
    recentEvents: string[];  // 近期重大事件
  };
  
  // 问卷数据（基线评估）
  surveyData?: {
    responses: Array<{
      member: string;
      dimension: string;
      score: 1-7;
      comments: string;
    }>;
  };
  
  // 脉冲检查数据（持续监测）
  pulseData?: {
    indicators: {
      meetingParticipation: 'high' | 'medium' | 'low';
      conflictFrequency: 'high' | 'medium' | 'low';
      turnoverRisk: 'high' | 'medium' | 'low';
      communicationQuality: 'high' | 'medium' | 'low';
    };
    recentIncidents: string[];
  };
  
  // 干预情境（如适用）
  interventionContext?: {
    issue: string;
    severity: 'low' | 'medium' | 'high';
    involvedParties: string[];
  };
}
```

### 输出接口

```typescript
interface PsychologicalSafetyOutput {
  // 安全度评分
  safetyScore: {
    overall: 1-100;
    level: 'high' | 'medium' | 'low' | 'critical';
    trend: 'improving' | 'stable' | 'declining';
  };
  
  // 维度分析
  dimensionScores: Array<{
    dimension: string;
    score: 1-100;
    interpretation: string;
    redFlags: string[];
  }>;
  
  // 风险预警
  riskAlerts: Array<{
    risk: string;
    probability: 'low' | 'medium' | 'high';
    impact: 'low' | 'medium' | 'high';
    earlyWarning: string[];
  }>;
  
  // 干预建议
  interventions: {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
    teamExercises: string[];
  };
  
  // 监测计划
  monitoring: {
    recommendedFrequency: 'weekly' | 'biweekly' | 'monthly';
    keyIndicators: string[];
    alertThresholds: Record<string, number>;
  };
}
```

---

## 问卷设计（Edmondson量表改编）

### 基线评估问卷

| 维度 | 题目 | 计分 |
|------|------|------|
| **敢于提问** | 在这个团队中，提出问题是安全的 | 1-7分 |
| **承认错误** | 团队成员可以承认错误而不被惩罚 | 1-7分 |
| **提出不同意见** | 表达与创始人不同的意见是安全的 | 1-7分 |
| **寻求帮助** | 在困难时向其他合伙人求助是安全的 | 1-7分 |
| **表达担忧** | 表达对项目风险的担忧不会被视为负能量 | 1-7分 |

### 评分标准

| 分数区间 | 等级 | 解读 |
|----------|------|------|
| 6-7分 | 高安全感 | 健康的团队氛围 |
| 4-5分 | 中等安全感 | 有改进空间 |
| 2-3分 | 低安全感 | 需要干预 |
| 1分 | 危险 | 关系危机 |

---

## 监测指标

### 定量指标

| 指标 | 测量方式 | 预警阈值 |
|------|----------|----------|
| 会议发言频率 | 统计每人发言占比 | 有人连续3次会议发言<5% |
| 决策参与度 | 投票/讨论参与统计 | 重要决策缺席率>20% |
| 冲突解决时间 | 从冲突发生到解决的天数 | 超过7天未解决 |
| 1-on-1频率 | 合伙人之间一对一交流频率 | 低于每两周一次 |

### 定性指标

| 指标 | 观察点 | 预警信号 |
|------|--------|----------|
| 沟通质量 | 会议中的互动 | 沉默、打断、冷嘲热讽 |
| 情绪表达 | 日常交流中的情绪 | 压抑、爆发、冷漠 |
| 求助行为 | 遇到困难时的反应 | 独自硬撑、从不求助 |
| 反馈文化 | 给予和接受反馈 | 无反馈、防御性反应 |

---

## 干预建议库

### 高安全感维护

- 定期团队复盘
- 建立反馈机制
- 庆祝失败（从失败中学习）
- 创始人以身作则

### 中等安全感提升

- 结构化讨论（确保人人发言）
- 匿名反馈渠道
- 冲突调解
- 团队建设活动

### 低安全感修复

- 第三方调解
- 创始人深度对话
- 重新定义团队规范
- 考虑人员调整

---

## 与五路图腾的关联

| 心理安全概念 | 五路图腾对应 | 整合应用 |
|--------------|--------------|----------|
| 安全氛围 | 观自在（状态） | 放松的决策环境 |
| 信任建设 | 孔子（伦理） | 仁义礼智信的体现 |
| 健康冲突 | 司马贺（方法） | 理性的分歧处理 |

---

## 开发计划

| 阶段 | 时间 | 任务 |
|------|------|------|
| **设计** | 第1-2周 | 完善问卷、设计监测指标 |
| **开发** | 第3-6周 | 实现评估和预警逻辑 |
| **测试** | 第7-10周 | 内部测试、信效度验证 |
| **试点** | 第11-12周 | 2-3个团队试点 |

---

## 与现有工具的整合

| 现有工具 | 整合点 |
|----------|--------|
| 五路图腾校准清单 | 增加心理安全维度 |
| 合伙人访谈指南 | 增加安全感相关问题 |
| 团队复盘模板 | 整合安全感检查 |

---

**设计文档版本**: 0.1  
**下次更新**: 开发启动前完善干预建议库
