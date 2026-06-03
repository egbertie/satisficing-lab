# Skill: network-value-mapper
## 网络价值映射 - P1级Skill设计文档

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **Skill ID** | `network-value-mapper` |
| **名称** | 网络价值映射 |
| **理论来源** | Social Network Analysis (Granovetter, Burt) |
| **优先级** | P1 |
| **版本** | 0.1 (设计阶段) |
| **计划引入** | V1.2 (3个月内) |

---

## 设计目标

基于社会网络分析理论，帮助创业者评估候选人的网络资源价值，识别结构洞和弱连接机会，优化合伙人选择中的网络互补性。

---

## 架构设计

### 功能模块

```
┌─────────────────────────────────────────────────────────────┐
│                  网络价值映射 Skill 架构                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  网络数据采集  │ → │  网络结构分析  │ → │  价值评估计算  │     │
│  │  Data       │    │  Structure  │    │  Value      │     │
│  │  Collection │    │  Analysis   │    │  Assessment │     │
│  └─────────────┘    └──────┬──────┘    └─────────────┘     │
│                            │                                │
│                            ▼                                │
│                   ┌─────────────────┐                      │
│                   │   互补性匹配     │                      │
│                   │   Matching      │                      │
│                   └────────┬────────┘                      │
│                            │                                │
│                            ▼                                │
│                   ┌─────────────────┐                      │
│                   │    策略建议      │                      │
│                   │  Recommendations │                      │
│                   └─────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心概念映射

| SNA概念 | 合伙人场景解释 | 评估指标 |
|---------|----------------|----------|
| **中心性** | 候选人在其网络中的重要性 | 连接数量、连接质量 |
| **结构洞** | 连接不同圈子的能力 | 跨群体连接数、桥接价值 |
| **弱连接** | 不同圈子的弱关系 | 新信息获取能力 |
| **网络密度** | 网络的紧密程度 | 资源动员能力 |

---

## 接口定义

### 输入接口

```typescript
interface NetworkMappingInput {
  // 当前团队网络
  currentTeam: {
    members: Array<{
      name: string;
      role: string;
      networks: string[];  // 所属网络（如：清华系、阿里系、投资圈）
      keyConnections: string[];  // 关键人脉描述
    }>;
    networkGaps: string[];  // 已知网络缺口
  };
  
  // 候选人网络信息
  candidate: {
    name: string;
    role: string;
    networkProfile: {
      primaryNetworks: string[];  // 主要所属网络
      bridgeNetworks: string[];   // 桥接的网络
      keyConnections: Array<{
        description: string;
        value: 'high' | 'medium' | 'low';
        accessibility: 'direct' | 'indirect' | 'potential';
      }>;
    };
    previousCollaborations: string[];  // 过往合作网络
  };
  
  // 业务需求
  businessNeeds: {
    targetMarkets: string[];
    neededConnections: string[];  // 需要的连接类型
    partnershipGoals: string[];
  };
}
```

### 输出接口

```typescript
interface NetworkMappingOutput {
  // 候选人网络画像
  candidateProfile: {
    networkCentrality: {
      score: 1-10;
      description: string;
    };
    structuralHoles: Array<{
      betweenNetworks: string[];
      value: 'high' | 'medium' | 'low';
      description: string;
    }>;
    weakTies: Array<{
      network: string;
      potentialValue: string;
    }>;
  };
  
  // 互补性分析
  complementarity: {
    overallScore: 1-10;
    gapFillers: string[];  // 填补的网络缺口
    overlapAnalysis: {
      redundantNetworks: string[];
      uniqueNetworks: string[];
    };
    synergyPotential: string[];
  };
  
  // 网络价值评估
  networkValue: {
    immediateValue: string[];  // 立即可用的连接
    strategicValue: string[];  // 长期战略价值
    riskValue: string[];       // 潜在风险（如竞业关系）
  };
  
  // 建议
  recommendations: {
    networkUtilization: string[];  // 如何利用这些网络
    relationshipBuilding: string[];  // 如何建立信任
    riskMitigation: string[];  // 风险缓释
  };
}
```

---

## 网络分析模型

### 结构洞识别算法

```typescript
interface StructuralHole {
  ego: string;           // 中心节点
  networkA: string;      // 网络A
  networkB: string;      // 网络B
  constraint: number;    // 约束系数（越低越有价值）
  betweenness: number;   // 中介中心性
}

function identifyStructuralHoles(
  candidate: Candidate,
  team: Team
): StructuralHole[] {
  const holes = [];
  
  // 识别候选人所连接的不同网络
  const candidateNetworks = candidate.networkProfile.primaryNetworks;
  
  // 检查这些网络之间的连接情况
  for (let i = 0; i < candidateNetworks.length; i++) {
    for (let j = i + 1; j < candidateNetworks.length; j++) {
      const networkA = candidateNetworks[i];
      const networkB = candidateNetworks[j];
      
      // 检查团队是否缺少这两个网络之间的连接
      const teamHasBridge = team.members.some(m => 
        m.networks.includes(networkA) && m.networks.includes(networkB)
      );
      
      if (!teamHasBridge) {
        holes.push({
          ego: candidate.name,
          networkA,
          networkB,
          constraint: calculateConstraint(candidate, networkA, networkB),
          betweenness: calculateBetweenness(candidate, networkA, networkB)
        });
      }
    }
  }
  
  return holes.sort((a, b) => b.betweenness - a.betweenness);
}
```

### 网络价值评分模型

```
网络价值总分 = 
  中心性得分 × 0.25 +
  结构洞价值 × 0.35 +  (权重最高，填补缺口最重要)
  弱连接价值 × 0.25 +
  与业务需求匹配度 × 0.15
```

---

## 可视化设计

### 网络图谱展示

```
                    [候选人]
                   /   |   \
                  /    |    \
            [网络A] [网络B] [网络C]
            /    \      |      /    \
           /      \     |     /      \
      [资源1]  [资源2] [资源3] [资源4]

图例:
━━━ 强连接（团队已有）
- - 弱连接（候选人的独特价值）
═══ 结构洞（填补缺口）
```

---

## 与五路图腾的关联

| SNA概念 | 五路图腾对应 | 整合应用 |
|---------|--------------|----------|
| 网络中心性 | 司马贺（方法） | 量化评估网络价值 |
| 结构洞 | 六祖慧能（直觉） | 发现潜在机会 |
| 弱连接 | 刘禹锡（价值） | 识别独特价值 |

---

## 开发计划

| 阶段 | 时间 | 任务 |
|------|------|------|
| **设计** | 第1-2周 | 完善评估模型、设计可视化 |
| **开发** | 第3-6周 | 实现核心分析逻辑 |
| **测试** | 第7-10周 | 内部测试、案例验证 |
| **试点** | 第11-12周 | 2-3个客户试点 |

---

## 数据获取策略

| 数据来源 | 方法 | 隐私考虑 |
|----------|------|----------|
| 公开信息 | LinkedIn、媒体报道 | 仅使用公开信息 |
| 候选人自报 | 问卷调查 | 明确告知用途 |
| 共同联系人 | 三方验证 | 保护各方隐私 |

---

**设计文档版本**: 0.1  
**下次更新**: 开发启动前完善数据获取细节
