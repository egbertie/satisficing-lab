---
# 知识元数据 (5标准化)
knowledge_id: W9-5B4163
title: Skill: decision-guardian
category: 11_Skill文档
source: skills/.archive_decision-guardian/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 8168
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Skill: decision-guardian

> **知识ID**: W9-5B4163  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_decision-guardian/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Skill: decision-guardian
# 决策守护者
# 版本: 1.0
# 创建: 2026-03-20
# 核心原则: 压力测试、前置审查、冲突化解
# 5标准: 全局✅ 系统✅ 迭代✅ Skill化✅ 自动化✅

triggers:
  - 重大决策
  - 方案评审
  - 风险评估
  - 冲突升级
  - 蓝军启动

---

## 一、第一性原理：决策的本质是什么？

### 1.1 决策的本质
> **在信息不完备条件下，通过系统分析选择最优行动方案**

### 1.2 为什么需要决策守护？
- ❌ 无蓝军机制：群体思维，盲目前行
- ❌ 无预审机制：事后救火，成本高昂
- ❌ 无冲突升级：问题积压，矛盾激化
- ✅ 三位一体：压力测试+前置审查+冲突化解

### 1.3 第一性重构
| 传统做法 | 第一性原理重构 |
|:---|:---|
| 领导拍板 | 分层过滤，集体智慧，领导终审 |
| 事后审查 | 前置审查，预防为主 |
| 压制分歧 | 鼓励挑战，挖掘漏洞 |
| 和稀泥 | 明确升级路径，果断裁决 |

---

## 二、三大机制整合架构

### 2.1 整合逻辑
```
┌─────────────────────────────────────────────────────┐
│                  decision-guardian                   │
│                     决策守护者                       │
├─────────────────────────────────────────────────────┤
│   蓝军机制  +   预审机制   +   冲突升级规则           │
│     ↓            ↓               ↓                  │
│  漏洞挖掘      前置审查        矛盾化解              │
│     ↓            ↓               ↓                  │
│  逆向挑战      风险识别        分级处理              │
│  压力测试      合规检查        升级裁决              │
│  极限推演      可行性验证      闭环跟踪              │
└─────────────────────────────────────────────────────┘
```

### 2.2 核心功能模块

| 模块 | 职责 | 触发条件 | 输出物 |
|:---|:---|:---|:---|
| **蓝军机制** | 逆向挑战，挖掘漏洞 | 重大决策/方案评审 | 压力测试报告 |
| **预审机制** | 前置审查，风险识别 | 方案提交/资源申请 | 预审意见书 |
| **冲突升级** | 化解矛盾，裁决分歧 | 争议发生/调解失败 | 升级裁决书 |

---

## 三、蓝军机制 (Red Team)

### 3.1 蓝军原则
> **独立、挑战、建设、限时**

### 3.2 蓝军启动条件

| 启动条件 | 触发标准 | 响应时限 |
|:---|:---|:---|
| **自动启动** | S级/A级决策提案提交 | 即时启动 |
| **手动启动** | 项目负责人申请蓝军审查 | 24小时内启动 |
| **被动启动** | 识别潜在风险/问题 | 即时启动 |
| **定期启动** | 季度性蓝军演习 | 按计划执行 |

### 3.3 蓝军审查清单

#### 3.3.1 逻辑层面
- [ ] **推理链完整性**：前提→推理→结论是否完整？
- [ ] **假设有效性**：关键假设是否成立？
- [ ] **数据准确性**：数据来源是否可靠？
- [ ] **因果混淆**：相关≠因果，是否区分？
- [ ] **幸存者偏差**：是否考虑了沉默的数据？

#### 3.3.2 执行层面
- [ ] **资源充足性**：人/财/物/时间是否足够？
- [ ] **能力匹配度**：执行团队是否具备相应能力？
- [ ] **依赖项风险**：外部依赖是否可控？
- [ ] ** timeline 合理性**：时间节点是否可行？
- [ ] **应急预案**：Plan B 是否准备？

#### 3.3.3 风险层面
- [ ] **最坏情况**：如果完全失败会怎样？
- [ ] **极限场景**：极端条件下是否仍然成立？
- [ ] **次生影响**：会引发什么连锁反应？
- [ ] **逆向攻击**：如果有人想破坏，会怎么做？
- [ ] **黑天鹅**：低概率高影响事件是否考虑？

#### 3.3.4 合规层面
- [ ] **法律边界**：是否触碰法律红线？
- [ ] **政策合规**：是否符合监管要求？
- [ ] **平台规则**：是否违反平台政策？
- [ ] **伦理审查**：是否符合价值观？

### 3.4 蓝军输出格式

```yaml
red_team_report:
  report_id: "rt_001"
  target_decision: "decision_id"
  review_date: "2026-03-20"
  
  vulnerabilities:
    - category: "logic"
      severity: "high"
      description: "关键假设X未经验证"
      evidence: "..."
      recommendation: "补充调研"
    
    - category: "execution"
      severity: "medium"
      description: "资源评估过于乐观"
      evidence: "..."
      recommendation: "增加20%缓冲"
  
  risk_assessment:
    overall_risk: "medium"
    confidence_level: "65%"
    key_uncertainties: ["...", "..."]
  
  verdict:
    status: "conditional_pass"
    conditions: ["修复高优先级漏洞", "补充风险缓释措施"]
    review_required: true
```

### 3.5 蓝军团队构成

| 角色 | 职责 | 轮换周期 |
|:---|:---|:---|
| **蓝军组长** | 统筹审查，最终把关 | 每季度 |
| **逻辑审查员** | 审查推理链 | 每项目 |
| **风险挖掘员** | 识别潜在风险 | 每项目 |
| **逆向攻击员** | 模拟对抗攻击 | 每项目 |
| **合规审查员** | 检查合规边界 | 每项目 |

---

## 四、预审机制 (Pre-Review)

### 4.1 预审原则
> **前置、全面、高效、记录**

### 4.2 预审类型

| 预审类型 | 审查重点 | 审查时长 | 参与方 |
|:---|:---|:---|:---|
| **技术预审** | 技术可行性、架构合理性 | 1-2天 | 技术专家 |
| **商业预审** | 商业模式、市场前景 | 1-2天 | 商业分析师 |
| **法务预审** | 法律合规、合同风险 | 1-3天 | 法务团队 |
| **财务预审** | 成本收益、资金安排 | 1-2天 | 财务专家 |
| **安全预审** | 数据安全、隐私保护 | 1-2天 | 安全专家 |

### 4.3 预审流程

```
Step 1: 预审申请
        ├── 提交预审材料包
        ├── 明确预审类型
        └── 指定预审时限
        ↓
Step 2: 预审分配
        ├── 确定预审专家
        ├── 分配审查任务
        └── 启动预审流程
        ↓
Step 3: 并行审查
        ├── 各领域专家独立审查
        ├── 记录审查意见
        └── 提出修改建议
        ↓
Step 4: 汇总反馈
        ├── 整合各领域意见
        ├── 优先级排序
        └── 形成预审报告
        ↓
Step 5: 结果通知
        ├── 发送预审意见书
        ├── 说明通过/不通过/有条件通过
        └── 明确修改要求
        ↓
Step 6: 整改跟踪（如需要）
        ├── 申请人整改
        ├── 预审专家复核
        └── 确认是否通过
```

### 4.4 预审决策矩阵

| 预审结果 | 含义 | 后续行动 |
|:---|:---|:---|
| **通过** | 无重大问题，可直接进入决策流程 | 提交正式审批 |
| **有条件通过** | 存在可修复问题，修复后通过 | 限期整改→复核→提交 |
| **不通过** | 存在重大缺陷，需重新设计 | 重新设计→重新预审 |
| **暂缓** | 条件不成熟，建议等待 | 等待条件成熟→重新申请 |

### 4.5 预审意见书模板

```yaml
pre_review_opinion:
  opinion_id: "pr_001"
  target_proposal: "proposal_id"
  review_type: "technical"
  reviewer: "expert_id"
  
  findings:
    critical: []        # 致命问题
    major: []           # 重大问题
    minor: []           # 次要问题
    suggestions: []     # 改进建议
  
  decision:
    verdict: "conditional_pass"
    conditions: ["修复问题A", "补充方案B"]
    deadline: "2026-03-25"
  
  risk_assessment:
    technical_risk: "medium"
    execution_risk: "low"
    overall_confidence: "75%"
```

---

## 五、冲突升级规则 (Escalation Rules)

### 5.1 升级原则
> **就地解决→调解→裁决→升级，逐级穷尽**

### 5.2 冲突分级

| 级别 | 冲突类型 | 示例 |
|:---|:---|:---|
| **L1-工作分歧** | 对工作方法/优先级有不同意见 | 技术方案选择 |
| **L2-资源冲突** | 对资源分配有争议 | 预算/人力争夺 |
| **L3-责任归属** | 对责任/功劳认定有分歧 | 事故责任认定 |
| **L4-价值观冲突** | 对原则/底线有不同理解 | 伦理争议 |
| **L5-人际矛盾** | 个人之间的不和 | 长期不和 |

### 5.3 升级路径

```
L1: 工作分歧
    ↓ 2小时内未达成一致
L2: 资源冲突 → 直接上级调解
    ↓ 4小时内未达成一致
L3: 责任归属 → 部门负责人裁决
    ↓ 8小时内未达成一致
L4: 价值观冲突 → 价值观委员会裁决
    ↓ 24小时内未达成一致
L5: 人际矛盾 → 最高决策者裁决
```

### 5.4 各级处理方式

| 级别 | 处理人 | 处理方式 | 时限 |
|:---|:---|:---|:---|
| **L1** | 冲突双方 | 直接沟通，寻求共识 | 2小时 |
| **L2** | 直接上级 | 听取双方，调解方案 | 4小时 |
| **L3** | 部门负责人 | 调查事实，做出裁决 | 8小时 |
| **L4** | 价值观委员会 | 原则审查，价值判断 | 24小时 |
| **L5** | 最高决策者 | 最终裁决，一锤定音 | 48小时 |

### 5.5 升级触发条件

| 触发条件 | 自动升级至 | 说明 |
|:---|:---|:---|
| 超时未解决 | 下一级 | 超过本级处理时限 |
| 一方不接受 | 下一级 | 拒绝接受调解/裁决 |
| 涉及多部门 | 部门负责人 | 跨部门冲突 |
| 涉及价值观 | 价值观委员会 | 触及价值观底线 |
| 影响重大 | 最高决策者 | 影响组织根本利益 |

### 5.6 裁决执行

```yaml
escalation_resolution:
  resolution_id: "er_001"
  conflict_level: "L3"
  
  parties: ["party_a", "party_b"]
  issue_description: "..."
  
  escalation_path:
    - level: "L1"
      attempted: true
      result: "failed"
      timestamp: "..."
    - level: "L2"
      attempted: true
      result: "failed"
      timestamp: "..."
  
  final_resolution:
    decision: "..."
    rationale: "..."
    decided_by: "..."
    decided_at: "..."
  
  execution:
    status: "pending"
    acceptance: {party_a: "accepted", party_b: "..."}
    follow_up: "..."
```

---

## 六、自动化执行

### 6.1 自动触发器

```python
# 蓝军启动触发器
triggers:
  - event: "s_level_decision_submitted"
  - event: "a_level_decision_submitted"
  - event: "manual_red_team_request"
  - schedule: "0 0 1 * *"  # 每月1日定期演习

# 预审启动触发器
triggers:
  - event: "proposal_submitted"
    conditions:
      - "budget > 100000"
      - "impact_level >= medium"
  - event: "manual_pre_review_request"

# 冲突升级触发器
triggers:
  - event: "conflict_detected"
  - event: "resolution_timeout"
  - event: "appeal_filed"
```

### 6.2 自动化工作流

```yaml
automated_workflow:
  red_team:
    - detect_trigger        # 检测启动条件
    - assign_team           # 分配蓝军团队
    - generate_checklist    # 生成审查清单
    - collect_materials     # 收集审查材料
    - conduct_review        # 执行审查
    - generate_report       # 生成报告
    - deliver_verdict       # 交付裁决
  
  pre_review:
    - receive_proposal      # 接收提案
    - classify_review       # 分类预审类型
    - assign_experts        # 分配专家
    - parallel_review       # 并行审查
    - consolidate_feedback  # 整合反馈
    - issue_opinion         # 发布意见
    - track_rectification   # 跟踪整改
  
  escalation:
    - detect_conflict       # 检测冲突
    - classify_level        # 分级定级
    - assign_handler        # 分配处理人
    - start_timer           # 启动计时
    - track_resolution      # 跟踪解决
    - auto_escalate         # 自动升级
    - document_resolution   # 记录决议
```

---

## 七、你可能没思考到的

### 7.1 蓝军过度挑战
**问题**：蓝军为了挑刺而挑刺，延误决策
**解决方案**:
- 限时审查：蓝军审查有时间限制
- 建设性原则：挑刺必须附带建设性建议
- 挑战质量评估：定期评估蓝军挑战的有效性

### 7.2 预审瓶颈
**问题**：预审环节堆积，成为瓶颈
**解决方案**:
- 并行审查：多个预审可同时进行
- 预审分级：简单预审快速通道
- 预审资源池：建立预审专家池，动态调配

### 7.3 升级滥用
**问题**：小事也升级，上级不堪重负
**解决方案**:
- 升级门槛：明确升级标准，不满足条件不受理
- 升级成本：升级需要付出一定成本（如书面说明）
- 升级培训：培训员工如何有效处理冲突

### 7.4 决策疲劳
**问题**：层层审查导致决策疲劳
**解决方案**:
- 审查合并：同类审查合并进行
- 信任分级：对历史表现好的团队减少审查
- 事后抽查：减少事前审查，加强事后抽查

---

## 八、与其他Skill的协作

| Skill | 协作场景 | 数据交换 |
|:---|:---|:---|
| **management-enforcer** | 决策执行监督 | 执行状态 |
| **knowledge-upkeep** | 决策案例归档 | 决策记录 |
| **file-integrity** | 决策文档存证 | 文档哈希 |
| **zero-idle** | 待决事项提醒 | 待决清单 |

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*
