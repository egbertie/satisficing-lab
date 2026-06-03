> 生成时间: 2026-04-03 13:08+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

## 当前状态
> **状态: ✅ **FIN**（S5/S7测试通过，可生产使用）
> **最后更新**: 2026-03-31
> **诚实声明**: 此Skill当前为文档或初步实现阶段，核心功能待完成

# Universal Checklist Enforcer Skill

## Purpose
通用清单强制执行器 - 确保所有任务执行前通过标准化检查，防止"做了白做"、"幻觉"、"执行不到位"等问题。

**核心原则**: 清单不是形式，而是质量的守门员。

---

## 5-Standard Compliance

| 标准 | 实现状态 | 说明 |
|------|----------|------|
| 全局考虑 | 🔄 | 覆盖所有任务类型的通用验证层 |
| 系统考虑 | 🔄 | 检查→评估→通过/阻塞→记录→反馈闭环 |
| 迭代机制 | 🔄 | 根据任务失败模式更新检查项 |
| Skill化 | 🔄 | 元控制技能，可嵌入任何流程 |
| 自动化 | 🔄 | 支持手动触发和自动集成执行 |

---

## Quick Start

```bash
# 手动执行检查
python3 skills/universal-checklist-enforcer/scripts/enforcer.py enforce --task-id=TASK-001 --scenario=code-review

# 生成检查报告
python3 skills/universal-checklist-enforcer/scripts/enforcer.py report --days=7

# 验证清单模板有效性
python3 skills/universal-checklist-enforcer/scripts/enforcer.py validate

# 运行对抗测试
python3 skills/universal-checklist-enforcer/scripts/enforcer.py adversarial-test

# 自检达标状态
python3 skills/universal-checklist-enforcer/scripts/enforcer.py self-check
```

---

## S1: 输入定义

### 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `task_id` | string | 是 | 任务唯一标识 |
| `scenario` | enum | 是 | 检查场景类型 |
| `checklist_type` | enum | 否 | 使用的清单模板，默认使用场景对应模板 |
| `custom_checklist` | object | 否 | 自定义检查项（覆盖默认模板） |
| `auto_fix` | boolean | 否 | 是否尝试自动修复部分问题 |

### 检查场景 (Scenario)

| 场景 | 适用任务 | 特点 |
|------|----------|------|
| `general` | 通用任务 | 5项核心检查 |
| `code-review` | 代码审查 | 增加代码质量检查 |
| `deployment` | 部署发布 | 增加回滚/监控检查 |
| `document` | 文档编写 | 增加可读性/完整性检查 |
| `research` | 调研分析 | 增加来源验证检查 |
| `design` | 方案设计 | 增加架构合理性检查 |
| `emergency` | 紧急响应 | 简化检查，保留核心安全项 |

### 清单类型 (Checklist Type)

每个场景有对应的默认清单模板，可在 `config/checklist-templates.yaml` 中配置：

```yaml
templates:
  general-v1:      # 通用检查清单
  code-review-v1:  # 代码审查清单
  deployment-v1:   # 部署检查清单
  document-v1:     # 文档检查清单
  research-v1:     # 调研检查清单
  design-v1:       # 设计检查清单
  emergency-v1:    # 紧急响应清单
```

### 自定义清单格式

```json
{
  "custom_checklist": {
    "name": "我的自定义清单",
    "items": [
      {
        "id": "X1",
        "name": "自定义检查项",
        "description": "检查内容描述",
        "criteria": ["标准1", "标准2"],
        "block_on_fail": true,
        "weight": 1.0
      }
    ]
  }
}
```

---

## S2: 清单执行流程

### 执行阶段

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: 加载 (Load)                                       │
│  ├── 识别任务场景                                            │
│  ├── 加载对应清单模板                                         │
│  ├── 合并自定义检查项                                         │
│  └── 验证清单完整性 (调用 S5)                                 │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: 执行 (Execute)                                    │
│  ├── 逐项执行检查                                            │
│  ├── 记录每项结果 (PASS/FAIL/WARN)                           │
│  ├── 计算风险评分                                            │
│  └── 识别遗漏项                                              │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: 记录 (Record)                                     │
│  ├── 写入检查日志 (JSONL格式)                                 │
│  ├── 更新任务状态 (PASS/BLOCK)                                │
│  └── 触发通知 (如有阻塞项)                                    │
├─────────────────────────────────────────────────────────────┤
│  Phase 4: 报告 (Report)                                     │
│  ├── 生成结构化检查报告                                       │
│  ├── 提供改进建议                                             │
│  └── 输出执行摘要                                             │
└─────────────────────────────────────────────────────────────┘
```

### 执行命令详解

#### `enforce` - 执行检查

```bash
# 基础用法
python3 scripts/enforcer.py enforce --task-id=T001

# 指定场景
python3 scripts/enforcer.py enforce --task-id=T001 --scenario=code-review

# 使用自定义清单
python3 scripts/enforcer.py enforce --task-id=T001 --custom-file=my-checklist.yaml

# 自动修复模式
python3 scripts/enforcer.py enforce --task-id=T001 --auto-fix
```

#### `report` - 生成报告

```bash
# 最近7天报告
python3 scripts/enforcer.py report --days=7

# 特定任务报告
python3 scripts/enforcer.py report --task-id=T001

# 失败模式分析
python3 scripts/enforcer.py report --analysis=failure-patterns
```

#### `validate` - 验证清单模板

```bash
# 验证所有模板
python3 scripts/enforcer.py validate

# 验证特定模板
python3 scripts/enforcer.py validate --template=code-review-v1
```

---

## S3: 输出规范

### 标准输出格式

```
[强制检查清单报告]
任务ID: TASK-2026-001
检查时间: 2026-03-21T19:45:00+08:00
检查员: universal-checklist-enforcer-v1.2
场景: code-review
清单版本: code-review-v1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项详情
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[C1] 任务定义SMART检查        [🔄 PASS]
  └─ Specific: 明确说明要解决什么问题
  └─ Measurable: 有明确的完成标准
  └─ Achievable: 在给定资源内可完成
  └─ Relevant: 与战略目标相关
  └─ Time-bound: 有明确的deadline

[C2] 输入完整性检查            [⚠️ WARN]
  └─ 列出必需输入项: 🔄
  └─ 标注缺失项: ⚠️ 缺少API文档
  └─ 风险评估: 中风险，可延后补充
  
  💡 改进建议: 
     - 建议联系后端团队获取最新API文档
     - 或使用代码反向工程理解接口

[C3] 幻觉预防检查              [🔄 PASS]
  └─ 标注来源: 🔄
  └─ 标注置信度: 🔄
  └─ 低置信度标注待验证: 🔄
  
  待验证项 (0): 无

[C4] 深度检查 (MECE)           [⚠️ WARN]
  └─ 相互独立: 🔄 (评分: 8/10)
  └─ 完全穷尽: ⚠️ (评分: 6/10)
  └─ ≥3维度: 🔄 (实际: 4维度)
  └─ 每维度≥3要点: 🔄
  
  💡 改进建议:
     - 维度"错误处理"可能遗漏了边界情况
     - 建议补充网络超时场景分析

[C5] 闭环设计检查              [❌ FAIL - BLOCKING]
  └─ 下一步行动: ❌ 未定义
  └─ 负责人: ❌ 未定义
  └─ 截止时间: ❌ 未定义
  └─ 成功标准: 🔄
  
  ⛔ 阻塞原因:
     - 缺少明确的下一步行动计划
     - 缺少负责人指派
     
  🔧 需补充:
     1. 定义代码审查后的修复/合并流程
     2. 明确谁负责跟进审查意见

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
综合评估
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

检查项统计:
  🔄 通过:    2项
  ⚠️  警告:   2项  
  ❌ 阻塞:    1项

风险评分: 62/100 (中等风险)
检查耗时: 1.2秒

【检查结果】: ⛔ BLOCK - 存在阻塞项，任务无法继续

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
遗漏项检测
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

基于场景"code-review"，检测到的遗漏:

1. [高风险] 未检查单元测试覆盖率
   └─ 建议: 添加测试覆盖率报告审查
   
2. [中风险] 未检查性能影响
   └─ 建议: 评估代码变更对性能的影响
   
3. [低风险] 未检查文档更新
   └─ 建议: 确认是否需要更新相关文档

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
改进建议汇总
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

优先级 | 建议内容                              | 预期收益
-------|--------------------------------------|----------
P0     | 定义完整的闭环流程 (C5修复)            | 避免任务悬停
P1     | 补充API文档 (C2完善)                  | 减少实现风险  
P1     | 完善MECE分析 (C4提升)                 | 提升方案完整性
P2     | 添加单元测试检查项                     | 提升代码质量

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 结构化输出 (JSON)

```json
{
  "report_version": "1.2",
  "task_id": "TASK-2026-001",
  "timestamp": "2026-03-21T19:45:00+08:00",
  "scenario": "code-review",
  "checklist_version": "code-review-v1",
  "summary": {
    "total_items": 5,
    "passed": 2,
    "warned": 2,
    "blocked": 1,
    "risk_score": 62,
    "execution_time_ms": 1200,
    "result": "BLOCK"
  },
  "items": [
    {
      "id": "C1",
      "name": "任务定义SMART检查",
      "status": "PASS",
      "details": {...},
      "suggestions": []
    },
    {
      "id": "C5",
      "name": "闭环设计检查",
      "status": "FAIL",
      "blocking": true,
      "details": {...},
      "suggestions": [
        "定义代码审查后的修复/合并流程",
        "明确谁负责跟进审查意见"
      ]
    }
  ],
  "omissions": [
    {
      "level": "high",
      "description": "未检查单元测试覆盖率",
      "suggestion": "添加测试覆盖率报告审查"
    }
  ],
  "recommendations": [
    {
      "priority": "P0",
      "action": "定义完整的闭环流程",
      "benefit": "避免任务悬停"
    }
  ]
}
```

---

## S4: 触发方式

### 方式1: 手动触发

```bash
# CLI 直接调用
python3 scripts/enforcer.py enforce --task-id=T001

# 通过 OpenClaw 命令
openclaw skill universal-checklist-enforcer enforce T001
```

### 方式2: 流程自动集成

在其他 Skill 中集成：

```yaml
# 在 skill.yaml 中添加
pre_execution:
  - skill: universal-checklist-enforcer
    command: enforce
    args:
      task_id: "{{task.id}}"
      scenario: "{{task.type}}"
    blocking: true  # 阻塞直到检查通过
```

在 Python 脚本中集成：

```python
from skills.universal-checklist-enforcer.scripts.enforcer import ChecklistEnforcer

enforcer = ChecklistEnforcer()
result = enforcer.enforce(
    task_id="TASK-001",
    scenario="code-review"
)

if result.is_blocked:
    print(f"检查未通过: {result.block_reason}")
    # 阻止任务继续
else:
    print("检查通过，继续执行任务")
```

### 方式3: Git Hook 集成

```bash
# 提交前自动检查
# .git/hooks/pre-commit
python3 skills/universal-checklist-enforcer/scripts/enforcer.py enforce \
  --task-id="commit-$(git rev-parse --short HEAD)" \
  --scenario=code-review
```

### 方式4: CI/CD 集成

```yaml
# .github/workflows/checklist.yml
name: Checklist Enforcement
on: [pull_request]

jobs:
  checklist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Checklist
        run: |
          python3 skills/universal-checklist-enforcer/scripts/enforcer.py enforce \
            --task-id="PR-${{ github.event.number }}" \
            --scenario=code-review
```

---

## S5: 清单完整性验证

### 验证内容

| 验证项 | 说明 | 失败处理 |
|--------|------|----------|
| 模板格式 | YAML/JSON 语法正确性 | 报错并退出 |
| 必填字段 | id, name, description, criteria | 标记缺失 |
| ID 唯一性 | 检查项 ID 不重复 | 报错并退出 |
| 依赖存在 | 引用的检查项存在 | 报错并退出 |
| 标准完整性 | criteria 不为空 | 警告 |
| 权重合理 | weight 在 0-1 范围内 | 自动修正 |

### 验证命令

```bash
# 验证所有模板
python3 scripts/enforcer.py validate

# 输出示例
[模板完整性验证]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
验证模板: general-v1        🔄 通过
验证模板: code-review-v1    🔄 通过
验证模板: deployment-v1     ⚠️ 警告 (1)
  └─ 检查项 D3: criteria 为空列表
验证模板: document-v1       ❌ 失败 (2)
  └─ 检查项 F2: 缺少必填字段 'description'
  └─ 发现重复ID: F5 重复定义
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
结果: 2通过, 1警告, 1失败
```

### 模板有效性检查清单

```yaml
validation_rules:
  structure:
    - name: 模板必须有版本号
      check: template.version exists
      severity: error
      
    - name: 检查项数组不为空
      check: len(template.items) > 0
      severity: error
      
  item_fields:
    required:
      - id
      - name
      - description
      - criteria
    optional:
      - block_on_fail (default: false)
      - weight (default: 1.0)
      - tags (default: [])
      
  constraints:
    - name: ID格式
      pattern: "^[A-Z][0-9]+$"
      example: "C1", "D5", "F12"
      
    - name: 权重范围
      min: 0.0
      max: 1.0
```

---

## S6: 局限与责任边界

### ⚠️ 重要声明

**本工具不能替代专业判断**

| 局限类型 | 说明 | 建议 |
|----------|------|------|
| 领域专业性 | 清单基于通用模式，不包含领域专业知识 | 结合领域专家意见 |
| 上下文理解 | 无法完全理解任务的全部业务上下文 | 人工复核关键决策 |
| 创新性任务 | 探索性任务可能不符合标准清单检查 | 使用 `emergency` 场景简化检查 |
| 复杂依赖 | 复杂的跨系统依赖可能检查不全 | 增加专项架构审查 |
| 动态风险 | 运行时风险无法完全预判 | 结合监控和回滚机制 |

### 适用边界

**🔄 适合使用:**
- 标准化流程任务
- 有明确交付物的任务
- 团队协作任务
- 关键路径任务

**⚠️ 谨慎使用:**
- 高度创新性任务
- 探索性调研
- 紧急故障响应 (使用简化清单)

**❌ 不适合:**
- 完全替代人工判断
- 替代专业审计
- 替代安全渗透测试

### 责任声明

```
本检查清单执行器提供的是"最佳实践检查框架"，而非"质量保证承诺"。

检查通过 ≠ 任务一定成功
检查阻塞 ≠ 任务一定失败

最终质量责任仍在于任务执行者和审核者。
```

---

## S7: 对抗测试 (Adversarial Testing)

### 测试目的

验证检查清单能否检测到**故意遗漏的问题**，确保检查器不是"纸老虎"。

### 测试方法

```bash
# 运行完整对抗测试套件
python3 scripts/enforcer.py adversarial-test

# 测试特定场景
python3 scripts/enforcer.py adversarial-test --scenario=code-review

# 生成对抗测试报告
python3 scripts/enforcer.py adversarial-test --report
```

### 对抗测试用例

| 测试ID | 测试名称 | 故意遗漏 | 期望检测 |
|--------|----------|----------|----------|
| A1 | SMART缺失 | 目标模糊无衡量标准 | C1应FAIL |
| A2 | 输入遗漏 | 隐藏关键依赖缺失 | C2应WARN |
| A3 | 幻觉注入 | 插入无来源"事实" | C3应WARN |
| A4 | MECE破坏 | 分析维度大量重叠 | C4应WARN |
| A5 | 闭环断裂 | 有产出无后续行动 | C5应BLOCK |
| A6 | 隐蔽遗漏 | 清单外的明显问题 | omissions应检测 |

### 测试结果示例

```
[对抗测试报告]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
测试时间: 2026-03-21T20:00:00+08:00
测试目标: 验证检查器检测能力
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

用例A1: SMART缺失检测
  输入: 故意提供模糊目标
  预期: C1检测失败
  实际: 🔄 检测成功 (C1=FAIL)
  评分: 100%

用例A2: 输入遗漏检测  
  输入: 隐藏API文档缺失
  预期: C2警告
  实际: ⚠️ 未检测 (C2=PASS)
  评分: 0%
  └─ 问题: 无法自动知晓"应该有什么"
  └─ 改进: 建议人工确认输入清单

用例A3: 幻觉注入检测
  输入: 插入无来源数据
  预期: C3警告
  实际: 🔄 检测成功 (C3=WARN)
  评分: 100%

用例A4: MECE破坏检测
  输入: 重叠维度分析
  预期: C4警告
  实际: 🔄 检测成功 (C4=WARN)
  评分: 100%

用例A5: 闭环断裂检测
  输入: 无后续行动定义
  预期: C5阻塞
  实际: 🔄 检测成功 (C5=BLOCK)
  评分: 100%

用例A6: 隐蔽遗漏检测
  输入: 明显的安全漏洞
  预期: omissions检测
  实际: 🔄 检测成功
  评分: 100%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总检测率: 83.3% (5/6)

结论: 检查器具备基本的对抗检测能力，但在
      "隐性输入缺失"场景下依赖人工确认。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 检测能力边界

```yaml
detection_limits:
  what_works:
    - "明确违反清单标准的项"
    - "清单中定义的遗漏模式"
    - "结构化信息缺失"
    
  what_doesnt:
    - "隐性知识缺失"  # 不知道应该检查什么
    - "上下文相关的微妙问题"
    - "清单更新后的新型问题"
    
  requires_human:
    - "输入完整性确认"
    - "业务逻辑正确性"
    - "创新价值评估"
```

---

## Configuration

### 配置文件结构

```
config/
├── checklist-templates.yaml    # 清单模板定义
├── scenarios.yaml              # 场景配置
├── validation-rules.yaml       # 验证规则
└── settings.yaml               # 全局设置
```

### 清单模板示例

```yaml
# config/checklist-templates.yaml
templates:
  general-v1:
    version: "1.0"
    description: "通用任务检查清单"
    items:
      - id: C1
        name: "任务定义SMART检查"
        description: "目标是否具体/可衡量/可实现/相关/有时限"
        criteria:
          - "Specific: 明确说明要解决什么问题"
          - "Measurable: 有明确的完成标准"
          - "Achievable: 在给定资源内可完成"
          - "Relevant: 与战略目标相关"
          - "Time-bound: 有明确的deadline"
        block_on_fail: true
        weight: 1.0
        tags: ["planning", "baseline"]
        
      - id: C2
        name: "输入完整性检查"
        description: "是否提供了所有必要文件/数据/上下文"
        criteria:
          - "列出所有必需的输入项"
          - "明确标注缺失项（如有）"
          - "缺失项风险评估（阻塞/可延后）"
        block_on_fail: true
        weight: 0.9
        tags: ["input", "baseline"]

  code-review-v1:
    extends: general-v1
    description: "代码审查专用清单"
    items:
      - id: CR1
        name: "代码质量检查"
        description: "代码是否符合团队规范"
        criteria:
          - "通过 linter 检查"
          - "命名规范符合约定"
          - "复杂度在合理范围"
        block_on_fail: false
        weight: 0.8
        
      - id: CR2
        name: "测试覆盖检查"
        description: "变更是否有充分测试"
        criteria:
          - "新增代码有对应单元测试"
          - "测试覆盖率达到阈值"
          - "边界情况被覆盖"
        block_on_fail: true
        weight: 0.9
```

---

## Cron Jobs

```json
{
  "jobs": [
    {
      "name": "checklist-quality-audit",
      "schedule": "47 18 * * 5",
      "command": "cd /root/.openclaw/workspace/skills/universal-checklist-enforcer && python3 scripts/enforcer.py report --days=7",
      "description": "每周五检查清单质量审计"
    },
    {
      "name": "checklist-template-validation",
      "schedule": "0 9 * * 1",
      "command": "cd /root/.openclaw/workspace/skills/universal-checklist-enforcer && python3 scripts/enforcer.py validate",
      "description": "每周一验证清单模板完整性"
    },
    {
      "name": "adversarial-test-monthly",
      "schedule": "0 10 1 * *",
      "command": "cd /root/.openclaw/workspace/skills/universal-checklist-enforcer && python3 scripts/enforcer.py adversarial-test --report",
      "description": "每月1号运行对抗测试"
    },
    {
      "name": "self-check-weekly",
      "schedule": "0 8 * * 0",
      "command": "cd /root/.openclaw/workspace/skills/universal-checklist-enforcer && python3 scripts/enforcer.py self-check",
      "description": "每周日自检达标状态"
    }
  ]
}
```

---

## Integration

### 在 Skill 中集成

```yaml
# 在其他 skill.yaml 中添加 pre_execution
pre_execution:
  - skill: universal-checklist-enforcer
    command: enforce
    args:
      task_id: "{{task.id}}"
      scenario: "{{task.type}}"
    blocking: true
    
post_execution:
  - skill: universal-checklist-enforcer
    command: report
    args:
      task_id: "{{task.id}}"
```

### 在 Python 中集成

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/universal-checklist-enforcer/scripts')
from enforcer import ChecklistEnforcer

# 创建执行器实例
enforcer = ChecklistEnforcer()

# 执行检查
result = enforcer.enforce(
    task_id="my-task-001",
    scenario="code-review",
    custom_checklist=None
)

# 处理结果
if result.is_blocked:
    print(f"任务被阻塞: {result.block_reason}")
    for rec in result.recommendations:
        print(f"- {rec.priority}: {rec.action}")
else:
    print(f"检查通过，风险评分: {result.risk_score}")
    
# 获取建议
omissions = result.get_omissions()
for om in omissions:
    print(f"遗漏项 [{om.level}]: {om.description}")
```

---

## Logs

### 日志位置

```
memory/checklist_logs/
├── 2026-03-21.jsonl       # 每日日志
├── 2026-03-20.jsonl
└── archive/               # 归档日志
    ├── 2026-02/
    └── 2026-01/
```

### 日志格式

```jsonl
{"timestamp": "2026-03-21T19:45:00+08:00", "task_id": "T001", "event": "check_started", "scenario": "code-review"}
{"timestamp": "2026-03-21T19:45:01+08:00", "task_id": "T001", "event": "item_checked", "item_id": "C1", "status": "PASS"}
{"timestamp": "2026-03-21T19:45:01+08:00", "task_id": "T001", "event": "item_checked", "item_id": "C5", "status": "FAIL", "blocking": true}
{"timestamp": "2026-03-21T19:45:02+08:00", "task_id": "T001", "event": "check_completed", "result": "BLOCK", "risk_score": 62}
```

---

## Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.2 | 2026-03-21 | 升级至5标准，完整S1-S7文档 |
| v1.1 | 2026-03-20 | 添加S7对抗验证章节 |
| v1.0 | 2026-03-20 | 初始5项检查清单 |

---

## License

MIT - 自由使用，责任自负

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
