---
kia-version: 1.0
tier: T0
title: 记忆与重复问题系统重建需求
source: docs/requirement-memory-reconstruct-v1.0.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

> 生成时间: 2026-04-04 09:12+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 记忆与重复问题系统重建需求

> **需求编号**: REQUIREMENT-MEMORY-RECONSTRUCT-V1.0  
> **提出时间**: 2026-04-04 10:20  
> **需求方**: Egbertie + 蓝军Skeptor-7  
> **文档位置**: `docs/requirement-memory-reconstruct-v1.0.md`  
> **优先级**: P0

---

## 一、问题背景

### 1.1 现状
**多次回答都记不住，经常反复问同样问题**：
- 用户多次回答过的问题，系统仍然重复询问
- 已经决策过的事项，再次讨论时好像从未发生过
- 工作习惯、规则约定，经常需要重新确认

### 1.2 典型案例
| 时间 | 问题 | 用户反应 |
|------|------|----------|
| 2026-04-03 | GPU租赁问题 | "刚刚都给你截图了，还是没有回忆和记忆" |
| 2026-04-04 | Workflow vs 知识内化顺序 | "这个问题其实昨天有回答过，你忘记了" |
| 多次 | 文件存放规则 | "这种事情太多了，所以，你永远都在碎片中" |

### 1.3 根本问题
**工作记忆缺失** + **长期记忆碎片化** + **回忆机制失效**

---

## 二、需求目标

### 2.1 不是"写更多备忘录"

拒绝方案：
- ❌ 再写一份记忆清单
- ❌ 再建立一份规则文档
- ❌ 再提醒一次"要记住"

### 2.2 而是"建立不可遗忘的记忆系统"

需要解决：
1. **决策如何被记录？**
2. **记录后如何被召回？**
3. **如何防止重复询问？**
4. **如何验证记忆有效性？**

---

## 三、详细需求

### 需求1：决策即时固化机制

**问题**: 用户做出决策后，没有被即时记录和固化。

**需要的机制**:
```
用户决策 → 即时提取关键信息 → 写入记忆文件 → 生成回忆索引
```

**技术方案**:
```python
class DecisionSolidifier:
    def solidify(self, conversation):
        # 1. 识别决策点
        decisions = self.extract_decisions(conversation)
        
        # 2. 提取关键信息
        for decision in decisions:
            record = {
                "timestamp": decision.time,
                "type": decision.type,  # 工作方式/技术选型/优先级
                "question": decision.question,
                "answer": decision.answer,
                "context": decision.context,
                "confidence": decision.confidence
            }
            
            # 3. 写入记忆
            self.memory_store.save(record)
            
            # 4. 生成索引
            self.index_builder.add(decision.keywords, record.id)
```

**触发时机**:
- 用户明确说"先做X"、"Y优先"、"不要Z"
- 用户纠正错误（"不对，应该是..."）
- 用户确认方案（"就这么办"）

### 需求2：主动回忆与冲突检测

**问题**: 再次遇到相似问题时，没有主动回忆之前的决策。

**需要的机制**:
```
新问题输入 → 相似度匹配 → 召回相关决策 → 呈现给用户确认
```

**技术方案**:
```python
class ActiveRecall:
    def before_asking(self, question):
        # 1. 语义匹配
        similar_decisions = self.memory_store.query(
            question, 
            threshold=0.85  # 相似度阈值
        )
        
        if similar_decisions:
            # 2. 呈现给用户
            return f"""
            我之前问过类似的问题：
            
            之前的问题：{similar_decisions[0].question}
            您的回答：{similar_decisions[0].answer}
            时间：{similar_decisions[0].timestamp}
            
            当前问题是否与之前相同？
            - 如果是，直接采用之前答案
            - 如果不同，请说明差异
            """
        
        return None  # 没有相似决策，继续提问
```

**关键设计**:
- 不是"直接应用旧答案"，而是"呈现给用户确认"
- 避免机械重复，给用户机会纠正或更新

### 需求3：工作习惯与规则的强制索引

**问题**: 工作习惯、文件存放规则等经常忘记。

**需要的机制**:
- **习惯清单**: 将工作习惯写入固定位置
- **规则索引**: 建立可快速查询的规则索引
- **执行前检查**: 操作前强制对照清单

**技术方案**:
```python
class HabitEnforcer:
    def __init__(self):
        self.habit_list = self.load("A-manyige/工作习惯固化清单.md")
        self.rule_index = self.build_index(self.habit_list)
    
    def before_operation(self, operation):
        # 查询相关规则
        relevant_rules = self.rule_index.query(operation.type)
        
        # 强制展示
        if relevant_rules:
            print("⚠️ 操作前请确认以下规则：")
            for rule in relevant_rules:
                print(f"  - {rule}")
            
            # 等待确认
            confirm = input("已确认规则，继续操作？(y/n)")
            if confirm != 'y':
                return False
        
        return True
```

### 需求4：记忆有效性验证

**问题**: 记忆写入后，是否真的能 recalled？

**需要的机制**:
- **定期自检**: 每周随机测试记忆 recall
- **覆盖率分析**: 分析哪些决策从未被 recalled
- **遗忘预警**: 长期未被访问的记忆，主动提醒复习

**技术方案**:
```python
class MemoryValidator:
    def weekly_check(self):
        # 随机抽取10条记忆
        samples = self.memory_store.random_sample(10)
        
        failed_recalls = []
        for memory in samples:
            # 测试能否被正确召回
            recalled = self.activeRecall.recall(memory.query)
            if not recalled or recalled.id != memory.id:
                failed_recalls.append(memory)
        
        if failed_recalls:
            print(f"⚠️ 本周有 {len(failed_recalls)} 条记忆无法正确召回")
            print("需要优化索引或重新固化")
```

### 需求5：碎片化问题的系统解决

**问题**: "你永远都在碎片中"——工作没有系统性。

**需要的机制**:
- **上下文保持**: 跨会话保持工作上下文
- **状态恢复**: 重启后能恢复到之前的工作状态
- **全局视图**: 提供所有进行中的工作、待决策事项的汇总视图

**技术方案**:
```python
class ContextManager:
    def save_context(self):
        """保存当前完整上下文"""
        context = {
            "ongoing_tasks": self.task_manager.get_all(),
            "pending_decisions": self.decision_tracker.get_pending(),
            "recent_context": self.conversation_history.get_recent(10),
            "working_memory": self.working_memory.get_all()
        }
        self.state_store.save(context)
    
    def restore_context(self):
        """恢复上下文"""
        context = self.state_store.load()
        self.task_manager.restore(context["ongoing_tasks"])
        self.decision_tracker.restore(context["pending_decisions"])
        # ...
```

---

## 四、验收标准

### 4.1 功能验收
- [ ] 决策即时固化机制
- [ ] 主动回忆与冲突检测
- [ ] 工作习惯强制索引
- [ ] 记忆有效性验证
- [ ] 上下文管理系统

### 4.2 质量验收
- [ ] 决策记录率: 100%
- [ ] 相似问题识别率: > 90%
- [ ] 规则遗忘率: < 5%
- [ ] 上下文恢复成功率: > 95%

### 4.3 业务验收
- [ ] 用户不再重复回答相同问题
- [ ] 用户不再说"你忘记了"
- [ ] 工作有系统性，不再"在碎片中"

---

## 五、时间要求

期望交付时间: 2-3周

---

**联系方式**: 通过 Kimi 文档协作系统交付即可
