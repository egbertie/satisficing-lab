> 生成时间: 2026-04-05 08:19+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# totem_engine - 四层架构元框架

## 描述
Kimi Claw核心引擎的四层架构元框架（Layered Architecture Meta-Framework）。基于外援AI决策系统设计的本地化实现，构建从认知到进化的可扩展Agent系统。

## 触发条件
- 开发新的Agent或图腾角色
- 需要设计层间通信协议
- 合伙人匹配引擎需要扩展为多Agent审议架构

## 四层架构
```
Layer 4: 进化层 (Evolution)
         ↑ 共同进化、反馈闭环、模型校准
Layer 3: 知识层 (Knowledge)
         ↑ SECI内化闭环、知识发酵池
Layer 2: 学习层 (Learning)
         ↑ 决策风格习得、偏好推断
Layer 1: 认知层 (Cognition)
         ↑ 五图腾Agent、多视角评估
```

## 核心抽象
- `Layer` (ABC) - 所有层的基类，定义 `process()` 与 `communicate()` 接口
- `Scenario` - 输入到认知层的情境（背景、约束、创始人画像、候选人列表）
- `Perspective` - 认知层输出的观点（图腾名、维度、得分、分析、建议）
- `Decision` - 最终决策结果
- `EvolutionFeedback` - 进化层的反馈信号

## 层间通信协议
- 层与层之间通过强类型 dataclass 传递数据
- 支持上下行双向通信
- 每层可注册多个Agent，Agent输出汇总后传入下一层

## 关键文件
- `layers/architecture.py` - 核心框架定义
- `layers/test_architecture.py` - 框架测试

## 使用方法
```python
from skills.totem_engine.layers.architecture import CognitionLayer, Scenario

scenario = Scenario(
    context="...",
    constraints=["..."],
    founder_profile={...},
    candidates=[...]
)
```

## 依赖
- Python 3.10+
- 标准库（abc, dataclasses, typing, enum, json, datetime）

## 版本
- 当前状态：架构设计完成，接口定义稳定
- 用途：为 partner-matching-engine 提供可扩展的多Agent架构基础
