---
name: bridge_openspec_satisfying
description: Bridge Rule解决OpenSpec与满意姐系统的链路断裂
alwaysApply: true
priority: 1000
---

# Bridge Rule: OpenSpec ↔ 满意姐认知生态系统

## 核心问题

OpenSpec的`openspec/config.yaml`和`openspec/specs/`是项目的"活记忆"，但：
1. AI不知道要去读这些文件
2. 即使读了，不会关联到TemporalCrystal记忆系统
3. 导致生成的代码违反既有架构，重复造轮子

## 强制桥接协议

### Step 1: 强制读取（不可跳过）

在每次会话开始时：
1. 读取 `openspec/config.yaml` → 转化为满意姐"项目记忆"
2. 读取 `openspec/specs/所有spec.md` → 转化为"规范晶体"
3. 读取当前changes/中的proposal/design/tasks → 转化为"执行上下文"
4. 将以上注入TemporalCrystalStore，标记为"HARD_CONTEXT"（不可被后续覆盖）

### Step 2: 冲突检测（红线）

如果检测到以下情况，触发硬否决：
- 规范冲突：生成代码使用的方法/函数在specs/中已存在不同实现
- 架构冲突：实现方案违反openspec/config.yaml中的架构约束
- 记忆冲突：当前提案与历史TemporalCrystal中的决策矛盾

### Step 3: 双向同步（实时）

- 编码前：读取specs/
- 编码中：记录决策到TemporalCrystal
- 编码后：Archive同步更新specs/

## 生效声明

本Rule加载后，所有代码生成任务必须遵循上述协议。违反即触发蓝军审计。
