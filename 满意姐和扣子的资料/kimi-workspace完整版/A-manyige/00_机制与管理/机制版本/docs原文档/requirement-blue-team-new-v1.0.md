---
kia-version: 1.0
tier: T0
title: 蓝军新增外援需求文档（合并版）
source: docs/requirement-blue-team-new-v1.0.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

> 生成时间: 2026-04-04 09:23+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 蓝军新增外援需求文档（合并版）

> **需求编号**: REQUIREMENT-BLUE-TEAM-NEW-V1.0  
> **提出时间**: 2026-04-04 10:15  
> **需求方**: Egbertie + 蓝军Skeptor-7  
> **文档位置**: `docs/requirement-blue-team-new-v1.0.md`  
> **优先级**: P0  
> **包含需求**: >   - P0-010: Skill盘点深度洞察与机制重建  
>   - P0-011: 记忆与重复问题系统重建

---

## 第一部分：Skill盘点深度洞察与机制重建

### 一、问题背景

#### 1.1 现状
Skill盘点已经进行了**多次**，但每次都流于表面：
- 快速生成报告，未真正深度盘点364个Skill
- 用户多次指出问题，但未得到根本解决
- 盘点后没有建立可持续的维护机制

#### 1.2 根本问题
**盘点的目的不清晰** + **盘点后无执行** + **无持续验证机制**

---

### 二、需求目标

#### 2.1 不是"再做一次盘点"

拒绝方案：
- ❌ 再写一份盘点报告
- ❌ 再列一份Skill清单
- ❌ 再做一次表面检查

#### 2.2 而是"建立可持续的Skill治理机制"

需要解决：
1. **盘点的目的是什么？**
2. **盘点后如何确保执行？**
3. **如何防止问题复发？**

---

### 三、详细需求

#### 需求1：Skill盘点的目的澄清与指标设计

**问题**: 为什么要盘点Skill？盘点要解决什么问题？

**需要的输出**:
- Skill盘点目标定义文档
- 盘点成功指标（非"完成报告"，而是"能力提升"）
- 不同场景的Skill优先级矩阵

**参考框架**:
| 场景 | 核心Skill | 辅助Skill | 禁用/慎用 |
|------|-----------|-----------|-----------|
| 文档操作 | feishu-fetch-doc | python脚本 | 手动解析 |
| 文件管理 | feishu-drive-file | bash脚本 | 直接写文件 |
| 消息发送 | feishu-im-user-message | curl | 绕过API |

#### 需求2：Skill使用行为的深度洞察系统

**问题**: 为什么明明知道有Skill，还是不用？

**需要的机制**:
- **惯性检测**: 识别"看到文件就想写代码"的惯性模式
- **实时提醒**: 操作前自动提示可用Skill
- **使用追踪**: 记录每次操作是否使用了Skill
- **模式分析**: 分析什么情况下最容易违规

**技术方案**:
```python
class SkillUsageAnalyzer:
    def analyze_behavior(self, operation):
        # 检测惯性模式
        if operation.type == "file_parse" and operation.method == "manual":
            return INERTIA_DETECTED, "习惯性手动解析"
        
        # 追踪使用频率
        self.usage_stats.record(operation)
        
        # 识别高风险场景
        if self.is_high_risk_scenario(operation):
            return HIGH_RISK, "历史违规率>50%的场景"
```

#### 需求3：强制执行机制（技术约束）

**问题**: 如何让"使用Skill"从"应该做"变成"必须做"？

**需要的机制**:
1. **操作前拦截**: 任何文件/数据操作前，强制查询Skill
2. **违规熔断**: 未使用Skill时，自动阻止操作并提示
3. **Skill推荐**: 根据操作类型，自动推荐最匹配的Skill

**技术方案**:
```bash
# 拦截脚本示例
pre_operation_hook() {
    operation_type=$1
    
    # 查询可用Skill
    available_skills=$(skill_finder --type=$operation_type)
    
    if [ -n "$available_skills" ]; then
        echo "⚠️ 检测到可用Skill: $available_skills"
        echo "❌ 操作被阻止：必须使用Skill，禁止手动实现"
        return 1
    fi
    
    return 0
}
```

#### 需求4：Skill治理的持续验证机制

**问题**: 如何确保Skill治理机制长期有效？

**需要的机制**:
- **定期审计**: 每周抽样检查Skill使用情况
- **趋势分析**: 分析Skill使用率的变化趋势
- **预警系统**: 使用率下降时自动预警
- **反馈循环**: 根据使用反馈优化Skill推荐

**验收标准**:
| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| Skill使用率 | > 95% | 操作日志统计 |
| 违规响应时间 | < 1秒 | 熔断触发时间 |
| 用户满意度 | > 80% | 使用后反馈 |
| 机制可持续性 | 6个月不失效 | 长期追踪 |

#### 需求5：Skill盘点的真正目的实现

**盘点的真正目的不是"列出清单"，而是"提升能力"**。

**需要的能力提升**:
1. **快速识别**: 看到任务能快速判断该用什么Skill
2. **正确使用**: 知道如何正确调用Skill参数
3. **组合应用**: 能将多个Skill组合解决复杂问题
4. **新Skill学习**: 能快速上手新Skill

**验证方式**:
- 不看"盘点报告完成"，看"实际使用Skill能力提升"
- 设置测试场景，验证Skill使用能力

---

### 四、验收标准（Skill盘点）

#### 4.1 功能验收
- [ ] Skill盘点目的澄清文档
- [ ] Skill使用行为分析系统
- [ ] 强制执行机制（操作前拦截）
- [ ] 持续验证机制（定期审计）

#### 4.2 质量验收
- [ ] Skill使用率 > 95%
- [ ] 违规率 < 2%
- [ ] 机制运行6个月不失效

#### 4.3 业务验收
- [ ] 用户不再因Skill问题被批评
- [ ] 盘点后真正提升Skill使用能力

---

## 第二部分：记忆与重复问题系统重建

### 一、问题背景

#### 1.1 现状
**多次回答都记不住，经常反复问同样问题**：
- 用户多次回答过的问题，系统仍然重复询问
- 已经决策过的事项，再次讨论时好像从未发生过
- 工作习惯、规则约定，经常需要重新确认

#### 1.2 典型案例
| 时间 | 问题 | 用户反应 |
|------|------|----------|
| 2026-04-03 | GPU租赁问题 | "刚刚都给你截图了，还是没有回忆和记忆" |
| 2026-04-04 | Workflow vs 知识内化顺序 | "这个问题其实昨天有回答过，你忘记了" |
| 多次 | 文件存放规则 | "这种事情太多了，所以，你永远都在碎片中" |

#### 1.3 根本问题
**工作记忆缺失** + **长期记忆碎片化** + **回忆机制失效**

---

### 二、需求目标

#### 2.1 不是"写更多备忘录"

拒绝方案：
- ❌ 再写一份记忆清单
- ❌ 再建立一份规则文档
- ❌ 再提醒一次"要记住"

#### 2.2 而是"建立不可遗忘的记忆系统"

需要解决：
1. **决策如何被记录？**
2. **记录后如何被召回？**
3. **如何防止重复询问？**
4. **如何验证记忆有效性？**

---

### 三、详细需求

#### 需求1：决策即时固化机制

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
                "type": decision.type,
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

#### 需求2：主动回忆与冲突检测

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

#### 需求3：工作习惯与规则的强制索引

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

#### 需求4：记忆有效性验证

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

#### 需求5：碎片化问题的系统解决

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
```

---

### 四、验收标准（记忆重建）

#### 4.1 功能验收
- [ ] 决策即时固化机制
- [ ] 主动回忆与冲突检测
- [ ] 工作习惯强制索引
- [ ] 记忆有效性验证
- [ ] 上下文管理系统

#### 4.2 质量验收
- [ ] 决策记录率: 100%
- [ ] 相似问题识别率: > 90%
- [ ] 规则遗忘率: < 5%
- [ ] 上下文恢复成功率: > 95%

#### 4.3 业务验收
- [ ] 用户不再重复回答相同问题
- [ ] 用户不再说"你忘记了"
- [ ] 工作有系统性，不再"在碎片中"

---

## 五、综合时间要求

期望交付时间: 2-3周

---

## 六、文档信息

| 项目 | 内容 |
|------|------|
| 合并文档 | `docs/requirement-blue-team-new-v1.0.md` |
| 原文件1 | `docs/requirement-skill-audit-reconstruct-v1.0.md` |
| 原文件2 | `docs/requirement-memory-reconstruct-v1.0.md` |
| 合并时间 | 2026-04-04 |
| 合并人 | 蓝军Skeptor-7 |

---

**联系方式**: 通过 Kimi 文档协作系统交付即可
