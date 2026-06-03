---
# 知识元数据 (5标准化)
knowledge_id: W11-60BE18
title: Skill: knowledge-upkeep
category: 11_Skill文档
source: skills/.archive_knowledge-upkeep/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 8097
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Skill: knowledge-upkeep

> **知识ID**: W11-60BE18  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_knowledge-upkeep/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Skill: knowledge-upkeep
# 知识维护者
# 版本: 1.0
# 创建: 2026-03-20
# 核心原则: 精准标注、周期维护、持续增值
# 5标准: 全局✅ 系统✅ 迭代✅ Skill化✅ 自动化✅

triggers:
  - 档案更新
  - 记忆维护
  - 知识沉淀
  - 定期巡检
  - 归档整理

---

## 一、第一性原理：知识管理的本质是什么？

### 1.1 知识管理的本质
> **将个体经验转化为组织资产，并确保其时效性、可检索性、可用性**

### 1.2 为什么需要知识维护？
- ❌ 无专家档案：人才信息散落，无法快速匹配
- ❌ 无记忆维护：知识过期失效，决策依据错误
- ❌ 无系统管理：知识孤岛林立，复用困难
- ✅ 三位一体：精准标注+周期维护+持续增值

### 1.3 第一性重构
| 传统做法 | 第一性原理重构 |
|:---|:---|
| 文档堆积 | 结构化标注，精准检索 |
| 一次性整理 | 周期性维护，动态更新 |
| 静态存储 | 持续加工，知识增值 |
| 人找知识 | 知识找人，主动推送 |

---

## 二、两大机制整合架构

### 2.1 整合逻辑
```
┌─────────────────────────────────────────────────────┐
│                   knowledge-upkeep                   │
│                      知识维护者                      │
├─────────────────────────────────────────────────────┤
│   专家档案标注规则  +   记忆维护周期规则             │
│         ↓                      ↓                    │
│     人才知识化              知识时效化               │
│         ↓                      ↓                    │
│     标签体系                更新周期                │
│     能力图谱                过期检测                │
│     匹配推荐                归档清理                │
│     动态更新                价值评估                │
└─────────────────────────────────────────────────────┘
```

### 2.2 核心功能模块

| 模块 | 职责 | 触发条件 | 输出物 |
|:---|:---|:---|:---|
| **专家档案标注** | 建立专家能力标签体系 | 入职/项目完成/能力提升 | 专家画像、能力图谱 |
| **记忆维护周期** | 确保知识时效性 | 定期巡检/知识触发 | 更新提醒、归档建议 |

---

## 三、专家档案标注规则

### 3.1 标注原则
> **全面、准确、动态、可用**

### 3.2 专家档案结构

```yaml
expert_profile:
  profile_id: "exp_001"
  basic_info:
    name: "..."
    role: "..."
    department: "..."
    join_date: "..."
  
  capability_tags:
    technical:          # 技术能力
      - name: "Python"
        level: "expert"  # novice/intermediate/advanced/expert
        verified_by: ["proj_001", "proj_003"]
      - name: "Machine Learning"
        level: "advanced"
        verified_by: ["proj_002"]
    
    domain:             # 领域知识
      - name: "Fintech"
        level: "expert"
        years: 5
      - name: "Risk Management"
        level: "intermediate"
        years: 2
    
    soft_skills:        # 软技能
      - name: "Public Speaking"
        level: "advanced"
      - name: "Team Leadership"
        level: "expert"
  
  project_history:
    - project_id: "proj_001"
      role: "Tech Lead"
      contributions: ["...", "..."]
      outcomes: "..."
      lessons_learned: "..."
  
  learning_path:
    certifications: []
    courses_completed: []
    self_study_areas: []
  
  availability:
    current_workload: "80%"
    available_for: ["consulting", "mentoring", "new_project"]
    preferred_project_size: "medium"
  
  metadata:
    last_updated: "2026-03-20"
    updated_by: "system"
    version: 3
```

### 3.3 标签体系设计

#### 3.3.1 技术能力标签 (Technical)
| 维度 | 示例标签 | 等级定义 |
|:---|:---|:---|
| 编程语言 | Python, Java, Go, Rust | novice/intermediate/advanced/expert |
| 框架工具 | React, Django, K8s, TensorFlow | 同上 |
| 架构能力 | Microservices, Serverless, Event-driven | 同上 |
| 数据能力 | SQL, NoSQL, Data Pipeline, Analytics | 同上 |

#### 3.3.2 领域知识标签 (Domain)
| 维度 | 示例标签 | 属性 |
|:---|:---|:---|
| 行业领域 | Fintech, HealthTech, EdTech | 年限+深度 |
| 业务职能 | Product, Marketing, Sales, Operations | 年限+成果 |
| 专业领域 | Risk, Compliance, UX Research | 认证+项目 |

#### 3.3.3 软技能标签 (Soft Skills)
| 维度 | 示例标签 | 评估方式 |
|:---|:---|:---|
| 沟通能力 | Public Speaking, Writing, Negotiation | 360评估+实际表现 |
| 协作能力 | Teamwork, Cross-functional, Remote | 同僚评价+项目结果 |
| 领导能力 | Leadership, Mentoring, Decision Making | 下属评价+成果 |

### 3.4 标注流程

```
Step 1: 信息采集
        ├── 自我评估问卷
        ├── 项目历史分析
        ├── 技能测试结果
        └── 同僚反馈收集
        ↓
Step 2: 标签生成
        ├── 系统自动提取标签
        ├── 专家确认/补充
        └── 等级初步评定
        ↓
Step 3: 验证校准
        ├── 项目成果验证
        ├── 同行评议
        └── 等级调整
        ↓
Step 4: 档案生成
        ├── 生成专家画像
        ├── 建立能力图谱
        └── 录入专家库
        ↓
Step 5: 动态更新
        ├── 项目完成后自动更新
        ├── 定期复核
        └── 专家自主更新
```

### 3.5 专家匹配机制

| 匹配场景 | 匹配逻辑 | 输出 |
|:---|:---|:---|
| **项目组队** | 技能需求匹配+可用性+工作负载 | 推荐专家列表 |
| **问题咨询** | 领域匹配+经验深度+响应速度 | 推荐专家 |
| **导师配对** | 技能差距+学习目标+性格匹配 | 推荐导师 |
| **培训讲师** | 专业能力+表达能力+经验 | 推荐讲师 |

---

## 四、记忆维护周期规则

### 4.1 维护原则
> **及时更新、定期巡检、过期清理、价值评估**

### 4.2 知识分类与维护周期

| 知识类型 | 更新周期 | 巡检周期 | 过期标准 |
|:---|:---|:---|:---|
| **战略知识** | 季度更新 | 每月巡检 | 战略方向改变 |
| **流程规范** | 实时更新 | 每周巡检 | 流程废止 |
| **技术文档** | 迭代更新 | 每月巡检 | 技术过时 |
| **项目文档** | 结项更新 | 每季巡检 | 项目结束1年 |
| **市场信息** | 每日更新 | 每日巡检 | 1个月未更新 |
| **外部资料** | 定期更新 | 每季巡检 | 来源失效 |

### 4.3 维护周期矩阵

```yaml
maintenance_schedule:
  knowledge_types:
    strategic:
      update_frequency: "quarterly"
      review_frequency: "monthly"
      owner: "strategy_team"
      retention_period: "5_years"
    
    procedural:
      update_frequency: "as_needed"
      review_frequency: "weekly"
      owner: "operations_team"
      retention_period: "3_years"
    
    technical:
      update_frequency: "per_iteration"
      review_frequency: "monthly"
      owner: "tech_leads"
      retention_period: "2_years"
    
    project:
      update_frequency: "on_completion"
      review_frequency: "quarterly"
      owner: "project_managers"
      retention_period: "1_year"
    
    market:
      update_frequency: "daily"
      review_frequency: "daily"
      owner: "market_team"
      retention_period: "6_months"
```

### 4.4 知识状态生命周期

```
创建 → 活跃 → 维护中 → 归档 → 销毁
  ↓      ↓       ↓        ↓       ↓
新录入  正常使用  待更新   历史参考  彻底删除
  ↓      ↓       ↓        ↓
标记    定期    提醒     只读
时间    巡检    更新     权限
```

### 4.5 过期检测规则

| 检测规则 | 触发条件 | 处理动作 |
|:---|:---|:---|
| **时间过期** | 超过更新周期未更新 | 标记为"待更新"，通知责任人 |
| **引用过期** | 引用的内容已失效 | 标记为"引用失效"，建议更新 |
| **相关性过期** | 与当前业务不再相关 | 标记为"待归档"，人工确认 |
| **准确性过期** | 内容被证实有误 | 标记为"待修正"，紧急通知 |

### 4.6 归档与清理

| 阶段 | 条件 | 操作 |
|:---|:---|:---|
| **软归档** | 知识过时但仍有参考价值 | 移至归档区，保留检索，只读权限 |
| **硬归档** | 知识完全过时 | 移至冷存储，仅限管理员访问 |
| **清理** | 硬归档超过保留期 | 彻底删除，仅保留元数据 |

---

## 五、自动化执行

### 5.1 自动触发器

```python
# 专家档案更新触发器
triggers:
  - event: "project_completed"      # 项目完成
  - event: "certification_earned"   # 获得认证
  - event: "skill_assessment_done"  # 技能评估
  - schedule: "0 0 1 * *"           # 每月1日定期复核
  - event: "expert_self_update"     # 专家自主更新

# 记忆维护触发器
triggers:
  - schedule: "0 9 * * *"           # 每日巡检
  - event: "knowledge_created"       # 新知识创建
  - event: "update_due"              # 到期提醒
  - event: "reference_broken"        # 引用失效
  - event: "accuracy_questioned"     # 准确性质疑
```

### 5.2 自动化工作流

```yaml
automated_workflow:
  expert_profile:
    - detect_event          # 检测触发事件
    - collect_data          # 收集相关数据
    - analyze_contribution  # 分析贡献
    - update_tags           # 更新标签
    - adjust_levels         # 调整等级
    - notify_expert         # 通知专家
    - archive_history       # 归档历史
  
  memory_maintenance:
    - scan_knowledge        # 扫描知识库
    - check_freshness       # 检查时效
    - detect_outdated       # 检测过期
    - send_reminders        # 发送提醒
    - track_updates         # 跟踪更新
    - archive_old           # 归档旧知识
    - clean_expired         # 清理过期
  
  knowledge_valuation:
    - track_usage           # 跟踪使用情况
    - collect_feedback      # 收集反馈
    - calculate_value       # 计算价值
    - identify_gaps         # 识别缺口
    - suggest_updates       # 建议更新
```

### 5.3 智能推荐

| 场景 | 推荐逻辑 | 输出 |
|:---|:---|:---|
| **知识找人** | 根据用户角色/任务推荐相关知识 | 知识推送 |
| **专家找人** | 根据问题类型推荐相关专家 | 专家推荐 |
| **更新提醒** | 根据知识使用频率推荐优先更新 | 更新优先级列表 |
| **归档建议** | 根据知识活跃度建议归档 | 归档候选列表 |

---

## 六、你可能没思考到的

### 6.1 隐私边界
**问题**：专家档案涉及个人隐私，如何平衡？
**解决方案**:
- 分级可见：基础信息公开，详细档案限权
- 自主控制：专家可设置某些标签不公开
- 用途限定：明确档案使用范围，禁止滥用

### 6.2 标签僵化
**问题**：标签体系固化，无法适应新能力
**解决方案**:
- 动态标签：允许专家自主添加新标签
- 标签审核：新标签需审核通过后纳入体系
- 定期审视：每季度审视标签体系有效性

### 6.3 维护负担
**问题**：知识维护成为沉重负担
**解决方案**:
- 智能维护：自动生成更新建议
- 众包维护：允许社区参与维护
- 重要性分级：重要知识重点维护，次要知识简化

### 6.4 知识过时焦虑
**问题**：担心知识被标记为过时而焦虑
**解决方案**:
- 价值导向：过时不等于无价值，历史知识有价值
- 温和过渡：软归档而非直接删除
- 贡献认可：维护知识也是一种贡献，给予认可

---

## 七、与其他Skill的协作

| Skill | 协作场景 | 数据交换 |
|:---|:---|:---|
| **management-enforcer** | 专家绩效评估数据 | 项目贡献记录 |
| **decision-guardian** | 决策知识归档 | 决策案例 |
| **file-integrity** | 知识文件存证 | 文档哈希 |
| **zero-idle** | 待维护任务提醒 | 待办清单 |

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*
