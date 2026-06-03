---
# 知识元数据 (5标准化)
knowledge_id: W11-A169AB
title: SKILL: multi-agent-debater
category: 11_Skill文档
source: skills/.archive_multi-agent-debater/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 9552
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL: multi-agent-debater

> **知识ID**: W11-A169AB  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_multi-agent-debater/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# SKILL: multi-agent-debater

## 元数据
- **名称**: multi-agent-debater
- **版本**: 1.0.0
- **描述**: 多智能体辩论系统，借鉴AlphaGo自我对弈机制
- **作者**: 满意解研究所
- **创建日期**: 2026-03-15

---

## 能力声明

### 核心功能
1. 多智能体协同辩论（黎红雷/罗汉/客户替身/蓝军）
2. 初始方案优化与变体生成
3. 风险评估与弱点识别
4. 共识提炼与分歧记录
5. 决策模式标注数据生成

### 辩论模式

| 模式 | 描述 | 回合数 | 适用场景 |
|------|------|--------|----------|
| 完整模式 | 全部智能体参与 | 5 | 高风险复杂决策 |
| 标准模式 | 4个核心智能体 | 3 | 常规决策 |
| 快速模式 | 2个关键智能体 | 2 | 紧急决策 |
| 专家模式 | 仅专家替身 | 2 | 专业问题 |

---

## 使用方式

### 命令行调用

```bash
# 启动辩论
debate start \
  --topic "股权分配方案" \
  --proposal proposal.yaml \
  --client-persona zhangjianguo \
  --mode standard \
  --rounds 3

# 查看辩论状态
debate status --id DEB-001

# 导出结果
debate export --id DEB-001 --format yaml

# 生成决策建议
debate recommend --id DEB-001
```

### API调用

```python
from skills import MultiAgentDebater

# 初始化辩论
debater = MultiAgentDebater(
    topic="股权分配",
    participants=["lihonglei", "luohan", "zhangjianguo", "blue_team"]
)

# 设置初始方案
proposal = {
    "description": "给合伙人20%股权",
    "vesting": "4年归属期",
    "cliff": "1年cliff"
}

# 启动辩论
result = debater.debate(
    initial_proposal=proposal,
    rounds=3,
    time_limit=30  # 每回合分钟数
)

# 获取结果
print(result.consensus)
print(result.variants)
print(result.risks)
```

---

## 系统架构

### 组件架构

```
┌─────────────────────────────────────────────────────────┐
│                   multi-agent-debater                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Debate     │  │  Participant │  │   Moderator  │   │
│  │   Engine     │  │    Factory   │  │  (满意妞)     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│         │                   │                 │         │
│         ▼                   ▼                 ▼         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Participant Pool                     │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐  │   │
│  │  │黎红雷替身│ │ 罗汉替身 │ │客户替身 │ │ 蓝军   │  │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Variant    │  │   Risk       │  │   Pattern    │   │
│  │   Generator  │  │   Analyzer   │  │   Extractor  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 智能体角色定义

```python
PARTICIPANTS = {
    "lihonglei": {
        "name": "黎红雷替身",
        "role": "伦理法官",
        "style": "儒家逻辑，强调仁义",
        "focus": ["合伙伦理", "价值观对齐", "长期关系"],
        "debate_strategy": "从仁义礼智信角度质疑"
    },
    "luohan": {
        "name": "罗汉替身",
        "role": "数学守门人",
        "style": "概率思维，量化分析",
        "focus": ["风险评估", "逻辑严密性", "期望效用"],
        "debate_strategy": "用数字和概率说话"
    },
    "client_persona": {
        "name": "客户替身",
        "role": "需求验证者",
        "style": "实用主义，关注落地",
        "focus": ["可接受度", "执行可行性", "情感反应"],
        "debate_strategy": "从目标客户视角提问"
    },
    "blue_team": {
        "name": "蓝军替身",
        "role": "批判者",
        "style": "挑刺，找漏洞",
        "focus": ["所有潜在风险", "极端场景", "假设质疑"],
        "debate_strategy": "系统性攻击弱点"
    }
}
```

---

## 辩论流程

### 流程配置

```yaml
debate_flow:
  round_structure:
    - step: "initial_proposal"
      actor: "moderator"
      duration: 2
      
    - step: "ethical_review"
      actor: "lihonglei"
      duration: 3
      
    - step: "quantitative_analysis"
      actor: "luohan"
      duration: 3
      
    - step: "customer_validation"
      actor: "client_persona"
      duration: 3
      
    - step: "critique"
      actor: "blue_team"
      duration: 3
      
    - step: "free_debate"
      actor: "all"
      duration: 10
      rules:
        - "每人发言不超过2分钟"
        - "必须回应他人观点"
        
    - step: "summarize"
      actor: "moderator"
      duration: 4
      
    - step: "generate_variants"
      actor: "moderator"
      duration: 2
```

### 回合执行

```python
class DebateRound:
    """单回合辩论执行器"""
    
    def __init__(self, round_num, participants, proposal):
        self.round_num = round_num
        self.participants = participants
        self.proposal = proposal
        self.transcript = []
        
    def execute(self):
        """执行回合"""
        
        # T+0: 满意妞提出初始方案
        self._moderator_open()
        
        # T+2: 各智能体依次回应
        for participant in self.participants:
            response = participant.respond(
                proposal=self.proposal,
                previous_responses=self.transcript
            )
            self.transcript.append(response)
        
        # T+14: 自由辩论
        self._free_debate()
        
        # T+24: 总结
        consensus, disagreements = self._summarize()
        
        # T+28: 生成变体
        variants = self._generate_variants(consensus, disagreements)
        
        return DebateRoundResult(
            transcript=self.transcript,
            consensus=consensus,
            disagreements=disagreements,
            variants=variants
        )
```

---

## DPUCT算法实现

### 探索-利用平衡

```python
class DPUCT:
    """辩论用的PUCT变体"""
    
    def __init__(self, c_debate=2.0):
        self.c_debate = c_debate
        
    def calculate(self, decision, parent_visits):
        """
        计算DPUCT值
        
        DPUCT(d) = Q(d) + c_debate * P(d) * sqrt(N_parent) / (N_d + 1)
        
        Args:
            decision: 决策方案
            parent_visits: 父节点访问次数
            
        Returns:
            DPUCT值
        """
        Q = decision.quality_score  # 质量评分
        P = decision.prior_prob     # 先验概率
        N_d = decision.visit_count  # 访问次数
        
        exploitation = Q
        exploration = (self.c_debate * P * 
                      math.sqrt(parent_visits) / (N_d + 1))
        
        return exploitation + exploration
    
    def select(self, decisions, parent_visits):
        """选择下一个辩论的方案"""
        scores = {
            d: self.calculate(d, parent_visits) 
            for d in decisions
        }
        return max(scores, key=scores.get)
```

---

## 输出格式

### 辩论记录

```yaml
debate_record:
  debate_id: "DEB-2026-001"
  timestamp: "2026-03-15T14:00:00Z"
  topic: "张建国股权分配决策"
  mode: "standard"
  rounds: 3
  
  initial_proposal:
    description: "给合伙人20%股权，4年归属期"
    proposer: "moderator"
    
  rounds:
    - round: 1
      transcript:
        - speaker: "moderator"
          content: "初始方案：20%股权..."
          time: "T+0"
        - speaker: "lihonglei"
          content: "从伦理角度，20%偏高..."
          time: "T+2"
          key_points: ["价值观对齐", "长期稳定性"]
        - speaker: "luohan"
          content: "量化分析显示，15%更合理..."
          time: "T+5"
          key_points: ["市场数据", "概率评估"]
        # ...
      
      consensus:
        - "股权应在10-25%之间"
        - "需要动态调整机制"
        
      disagreements:
        - topic: "具体比例"
          positions:
            lihonglei: "15%，保守优先"
            luohan: "20%，激励优先"
            
      variants_generated:
        - variant_id: "V1"
          name: "保守方案"
          description: "15%，无对赌"
        - variant_id: "V2"
          name: "平衡方案"
          description: "20%，轻对赌"
          
  final_result:
    recommendation: "V2平衡方案"
    confidence: 0.82
    reasoning: "兼顾激励与风险控制"
```

### 风险评估表

```yaml
risk_assessment:
  debate_id: "DEB-2026-001"
  
  proposals:
    - proposal_id: "initial"
      description: "20%股权"
      risks:
        - type: "控制权风险"
          level: "中"
          probability: 0.3
          impact: "高"
          mitigation: "设置动态调整机制"
        - type: "合伙人积极性"
          level: "低"
          probability: 0.2
          impact: "中"
      overall_risk: "中"
      
    - proposal_id: "V1"
      description: "15%股权"
      risks:
        - type: "激励不足"
          level: "中"
          probability: 0.4
          impact: "中"
      overall_risk: "中低"
```

---

## 使用示例

### 示例：股权分配辩论

```python
# 初始化辩论系统
debater = MultiAgentDebater()

# 配置参与者
debater.configure_participants([
    "lihonglei",
    "luohan", 
    "zhangjianguo",  # 客户替身
    "blue_team"
])

# 设置初始提案
proposal = {
    "title": "A轮融资后股权分配",
    "content": {
        "co_founder_equity": 20,
        "vesting_period": "4年",
        "cliff": "1年"
    }
}

# 启动辩论（3回合）
result = debater.run(
    initial_proposal=proposal,
    rounds=3,
    output_formats=["record", "variants", "risks", "consensus"]
)

# 查看结果
print("共识点:", result.consensus)
print("分歧点:", result.disagreements)
print("推荐方案:", result.recommendation)

# 导出决策模式标注数据
result.export_pattern_data("DP-001-01")
```

---

## 扩展指南

### 添加新智能体

1. 创建智能体配置
```yaml
# participants/financial_expert.yaml
id: "financial_expert"
name: "财务专家替身"
role: "财务分析师"
style: "财务数据导向，关注现金流"
focus: ["现金流", "估值", "退出机制"]
debate_strategy: "从财务可持续性角度分析"
```

2. 注册智能体
```bash
debate register-participant --config financial_expert.yaml
```

3. 在辩论中使用
```python
debater.configure_participants([
    "lihonglei", "luohan", "zhangjianguo", "blue_team", "financial_expert"
])
```

---

## 与AlphaGo的对应

| AlphaGo组件 | 多智能体辩论对应 | 说明 |
|-------------|------------------|------|
| MCTS | 多回合辩论 | 多轮搜索优化 |
| PUCT | DPUCT | 探索-利用平衡公式 |
| rollout | 单回合辩论 | 单次模拟 |
| 策略网络 | 模式网络 | 生成候选方案 |
| 价值网络 | 评估网络 | 评估方案质量 |
| 自我对弈 | 多智能体辩论 | 生成训练数据 |
| 棋盘状态 | 决策情境 | 当前决策环境 |
| 落子 | 决策建议 | 选择的行动 |

---

*Skill版本: 1.0.0*
*最后更新: 2026-03-15*
*参考: AlphaGo/AlphaZero技术架构*
