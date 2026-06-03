---
# 知识元数据 (5标准化)
knowledge_id: W8-D7AB19
title: SKILL: client-persona-simulator
category: 11_Skill文档
source: skills/.archive_client-persona-simulator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 5714
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL: client-persona-simulator

> **知识ID**: W8-D7AB19  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_client-persona-simulator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# SKILL: client-persona-simulator

## 元数据
- **名称**: client-persona-simulator
- **版本**: 1.0.0
- **描述**: 客户数字替身模拟器，用于多智能体辩论和需求验证
- **作者**: 满意解研究所
- **创建日期**: 2026-03-15

---

## 能力声明

### 核心功能
1. 加载并扮演预设客户数字替身
2. 模拟目标客户的决策特征和行为模式
3. 在多智能体辩论中提供客户需求视角
4. 验证决策方案的可接受度

### 支持的客户替身
| ID | 姓名 | 类型 | 适用场景 |
|----|------|------|----------|
| chenmingyuan | 陈明远 | 科学家型 | 学术背景客户模拟 |
| zhangjianguo | 张建国 | 连续创业者 | 有经验客户模拟 |
| lixiaowen | 李晓雯 | 跨界转型者 | 转型期客户模拟 |

---

## 使用方式

### 命令行调用

```bash
# 加载客户替身
client-persona load --id zhangjianguo

# 模拟客户反应
client-persona react --to "股权分配方案" --context "A轮融资后"

# 参与辩论
client-persona debate --topic "合伙人选择" --side customer

# 评估方案可接受度
client-persona evaluate --proposal proposal.yaml
```

### API调用

```python
from skills import ClientPersonaSimulator

# 初始化
simulator = ClientPersonaSimulator()

# 加载替身
persona = simulator.load("zhangjianguo")

# 获取反应
reaction = persona.react(
    stimulus="建议给合伙人20%股权",
    context={"stage": "A轮", "urgency": "high"}
)

# 参与辩论
response = persona.debate(
    topic="股权分配",
    position="客户视角",
    previous_arguments=[...]
)
```

---

## 配置参数

### 基础配置
```yaml
persona_config:
  id: "zhangjianguo"
  name: "张建国"
  type: "连续创业者"
  
  # 动态调整参数
  parameters:
    risk_appetite: 6        # 风险偏好 1-10
    loss_aversion: 9        # 损失厌恶 1-10
    status_quo_bias: 7      # 现状偏见 1-10
    time_pressure: "high"   # 时间压力
    emotional_state: "anxious"  # 情绪状态
    budget_sensitivity: "low"   # 价格敏感度
```

### 响应风格配置
```yaml
response_style:
  tone: "direct"           # direct/cautious/enthusiastic
  verbosity: "medium"      # brief/medium/detailed
  focus: "risk"            # risk/opportunity/balance
  question_frequency: "high"  # 提问频率
```

---

## 行为模型

### 张建国（连续创业者）行为模型

```python
class ZhangJianguoPersona:
    """连续创业者画像"""
    
    def __init__(self):
        self.trauma_history = [
            {"event": "第一次创业", "issue": "股权给太多", "loss": "control"},
            {"event": "第二次创业", "issue": "股权给太少", "loss": "300万"}
        ]
        self.core_fear = "再次踩合伙人坑"
        self.trust_level = "low"  # 对合伙人话题信任度低
        
    def react(self, proposal):
        """对提案的反应逻辑"""
        
        # 检查是否触发创伤记忆
        if "股权" in proposal:
            if proposal.equity > 25:
                return self._trauma_response("too_much")
            elif proposal.equity < 10:
                return self._trauma_response("too_little")
        
        # 评估与创伤经历的相似性
        similarity = self._calculate_similarity(proposal)
        if similarity > 0.7:
            return self._cautious_response(similarity)
        
        # 正常响应
        return self._normal_response(proposal)
    
    def _trauma_response(self, trigger):
        """创伤应激响应"""
        return {
            "emotion": "high_anxiety",
            "response": f"这让我想起我{trigger}那次创业...",
            "concerns": ["担心重蹈覆辙", "需要更多保障"],
            "acceptance": "low"
        }
```

### 通用行为接口

```python
class ClientPersona:
    """客户数字替身基类"""
    
    def react(self, stimulus, context):
        """
        对刺激的反应
        
        Args:
            stimulus: 刺激内容（如提案）
            context: 情境上下文
            
        Returns:
            Reaction对象，包含情感、认知、行为反应
        """
        pass
    
    def debate(self, topic, position, arguments):
        """
        参与辩论
        
        Args:
            topic: 辩论主题
            position: 立场
            arguments: 已有论点列表
            
        Returns:
            DebateResponse对象
        """
        pass
    
    def evaluate(self, proposal):
        """
        评估方案
        
        Args:
            proposal: 待评估方案
            
        Returns:
            Evaluation对象，包含可接受度评分和理由
        """
        pass
```

---

## 输出格式

### 反应输出

```yaml
reaction:
  persona_id: "zhangjianguo"
  timestamp: "2026-03-15T14:30:00Z"
  
  emotional:
    primary: "anxiety"
    intensity: 0.8
    trigger: "股权分配话题"
    
  cognitive:
    thoughts:
      - "这让我想起第一次创业"
      - "20%是不是又太多了"
      - "需要更多保障机制"
    concerns:
      - "控制权风险"
      - "合伙人积极性"
    
  behavioral:
    acceptance: 0.3
    questions:
      - "能设置对赌条款吗"
      - "如果达不到业绩怎么办"
    objections:
      - "股权比例偏高"
      - "缺乏退出机制"
```

### 辩论输出

```yaml
debate_response:
  persona_id: "zhangjianguo"
  topic: "股权分配方案"
  stance: "保守"
  
  arguments:
    - type: "experience"
      content: "我前两次创业都倒在股权上"
      weight: "high"
    - type: "risk"
      content: "20%意味着未来稀释后可能失控"
      weight: "medium"
      
  questions:
    - "有没有动态调整机制"
    - "业绩不达标怎么收回"
    
  counter_proposal:
    description: "建议15%起步，设置业绩对赌"
    reasoning: "既保证激励，又控制风险"
```

---

## 使用示例

### 示例1：评估股权方案

```python
# 加载张建国替身
persona = load_persona("zhangjianguo")

# 评估提案
proposal = {
    "type": "股权分配",
    "equity": 20,
    "vesting": "4年",
    "cliff": "1年"
}

evaluation = persona.evaluate(proposal)
print(evaluation.response)
# 输出: "20%让我有点担心，我前两次创业都...
#       能不能设置对赌？如果业绩不达标...
#       建议从15%开始，达成业绩后再增加"
```

### 示例2：参与辩论

```python
# 辩论场景
debate = Debate(topic="股权分配", round=1)

# 张建国参与
debate.add_participant(persona)

# 获取回应
response = persona.debate(
    topic="股权分配",
    previous_arguments=[
        {"from": "罗汉", "content": "建议20%，符合市场惯例"}
    ]
)

print(response)
# 输出: "我理解20%的市场逻辑，但从我的经历...
#       市场惯例不一定适合每个情况..."
```

---

## 扩展指南

### 添加新替身

1. 创建YAML配置文件
```yaml
# personas/new_client.yaml
id: "wangdawei"
name: "王大伟"
type: "技术专家转型"
background: "..."
decision_features: {...}
```

2. 注册到系统
```bash
client-persona register --config new_client.yaml
```

3. 验证
```bash
client-persona test --id wangdawei
```

---

## 注意事项

1. **情感真实性**: 替身反应应真实反映目标客户的情感模式
2. **一致性**: 同一替身在相似情境下应有一致反应
3. **可调节性**: 参数应可根据具体场景微调
4. **记录反馈**: 真实客户反馈应用于持续优化替身模型

---

*Skill版本: 1.0.0*
*最后更新: 2026-03-15*
