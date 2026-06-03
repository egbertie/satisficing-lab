---
# 知识元数据 (5标准化)
knowledge_id: W16-DE7DB2
title: Metacognitive Loop Enforcer Skill
category: 11_Skill文档
source: skills/metacognitive-loop-enforcer/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 5391
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Metacognitive Loop Enforcer Skill

> **知识ID**: W16-DE7DB2  
> **分类**: 11_Skill文档  
> **来源**: `skills/metacognitive-loop-enforcer/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Metacognitive Loop Enforcer Skill

> **Skill Level: 5** | 元认知循环执行器 - 系统化的自我反思与错误追踪机制

---

## 🏆 Standard Declaration

**本 Skill 已达到 Level 5 标准，符合以下 5 项核心要求：**

| 标准 | 状态 | 说明 |
|------|------|------|
| ✅ **S1** | 输入规范 | 完整的错误/反馈输入格式定义 |
| ✅ **S2** | 处理流程 | 五阶段元认知循环（记录→分类→分析→改进→验证）|
| ✅ **S3** | 输出规范 | 3类标准输出产物（改进文档/验证报告/模式分析）|
| ✅ **S4** | 自动化 | 每周六22:00自动执行复盘 |
| ✅ **S5** | 承诺追踪 | 错误不重复承诺+追踪表机制 |
| ✅ **S6** | 认知局限 | 6类已知局限标注 |
| ✅ **S7** | 对抗验证 | 主动模式匹配与压力测试机制 |

> **Self-Check Status**: ✅ 7S 全项通过 | **Last Verified**: 2026-03-21

---

## Overview

本Skill建立一套完整的元认知循环系统，通过记录、分类、分析、改进、验证五个步骤，确保错误不被重复，实现持续自我优化。

---

## Core Standards (7S)

### S1: 输入规范 (Input Specification)

**可接受的输入类型：**
1. **错误报告** - 运行时异常、逻辑错误、边界条件失败
2. **审计发现** - 代码审查、性能分析、安全扫描结果
3. **用户反馈** - 明确指出的问题、改进建议、负面体验

**输入格式：**
```yaml
error_id: "ERR-YYYYMM-NNNN"
timestamp: "ISO8601"
category: [logic|runtime|performance|security|ux|communication]
severity: [critical|high|medium|low]
description: "详细描述"
context:
  source_file: ""
  line_number: 0
  related_skill: ""
  session_id: ""
impact: "影响范围描述"
root_cause_analysis: "初步根因"
```

---

### S2: 处理流程 (Processing Pipeline)

```
记录(Record) → 分类(Classify) → 分析(Analyze) → 改进(Improve) → 验证(Verify)
```

**阶段1: 记录 (Record)**
- 捕获原始错误信息
- 验证必填字段完整性
- 生成唯一错误ID
- 写入error-registry.yaml

**阶段2: 分类 (Classify)**
- 自动识别错误模式
- 与历史错误匹配
- 标记潜在重复
- 更新分类统计

**阶段3: 分析 (Analyze)**
- 根因深度分析
- 影响面评估
- 关联关系识别
- 相似错误聚类

**阶段4: 改进 (Improve)**
- 制定改进措施
- 更新相关Skill文档
- 创建预防机制
- 设置监控告警

**阶段5: 验证 (Verify)**
- 7天内追踪改进效果
- 30天内进行效果验证
- 记录验证结果
- 更新错误状态

---

### S3: 输出规范 (Output Specification)

**输出产物：**

1. **改进措施文档**
   - 位置: `memory/improvements/{error_id}.md`
   - 内容: 问题描述、改进方案、实施步骤

2. **验证报告**
   - 位置: `memory/verification/{error_id}-{date}.md`
   - 内容: 验证方法、测试结果、是否达标

3. **模式识别报告**
   - 位置: `memory/patterns/{quarter}.md`
   - 内容: 错误模式分析、高频问题、系统性改进建议

**输出格式示例：**
```yaml
output:
  improvement_plan:
    priority: high
    deadline: "7 days"
    actions:
      - action: "具体行动"
        owner: "skill_name"
        status: pending
  verification:
    method: "回归测试/人工验证"
    expected_result: "..."
    actual_result: "..."
    passed: true/false
```

---

### S4: 自动化执行 (Automation)

**cron配置:** 每周六 22:00 自动执行复盘

**自动化任务：**
1. 扫描本周新增错误
2. 计算错误重复率
3. 生成周度复盘报告
4. 检查待验证改进项
5. 更新错误统计仪表板

**执行脚本:** `loop-tracker.py --weekly-review`

**输出位置:**
- 报告: `memory/reports/weekly/{year}-W{week}.md`
- 告警: 通过message工具发送（如重复率>阈值）

---

### S5: 承诺与追踪 (Commitment & Tracking)

#### 错误不重复承诺书

我承诺：
1. 每个已记录的错误都将被认真对待
2. 相同类别的错误不会重复发生超过2次
3. 所有关键错误都有对应的预防措施
4. 每周回顾并更新错误追踪表

#### 错误追踪表

| 错误ID | 类别 | 发生时间 | 状态 | 改进措施 | 验证结果 | 重复次数 |
|--------|------|----------|------|----------|----------|----------|
| ERR-202603-0001 | logic | 2026-03-21 | resolved | 边界检查 | ✅通过 | 0 |

---

### S6: 认知局限标注 (Cognitive Limitations)

**以下错误类型可能重复，需要特别关注：**

| 局限类型 | 说明 | 预防措施 |
|----------|------|----------|
| 边界条件忽略 | 极端输入、空值、超长内容 | 使用边界检查清单 |
| 并发处理缺陷 | 竞态条件、资源死锁 | 强制并发测试 |
| 语义理解偏差 | 用户意图误判 | 确认式追问机制 |
| 上下文遗漏 | 会话历史丢失 | 自动上下文加载 |
| 工具使用错误 | 参数格式、调用顺序 | 工具使用模板 |
| 过度自信 | 未经验证的假设 | 强制验证步骤 |

**重复风险等级：**
- 🔴 高风险: 边界条件、并发问题
- 🟡 中风险: 语义理解、上下文遗漏
- 🟢 低风险: 工具使用（有模板后）

---

### S7: 对抗验证 (Adversarial Verification)

**主动寻找类似错误机制：**

1. **模式匹配搜索**
   - 分析错误特征
   - 在代码库中搜索相似模式
   - 标记潜在风险点

2. **压力测试**
   - 针对错误类别设计边界测试
   - 模拟极端场景
   - 验证修复是否彻底

3. **反向验证清单**
   - 创建"如何避免此类错误"检查单
   - 在相关Skill中添加防御性编程要求
   - 定期执行反向验证

**验证命令：**
```bash
# 搜索潜在相似错误
python3 loop-tracker.py --find-similar ERR-202603-0001

# 执行对抗测试
python3 loop-tracker.py --adversarial-test --category logic
```

---

## Usage

### 记录新错误

```bash
python3 skills/metacognitive-loop-enforcer/loop-tracker.py \
  --record \
  --category logic \
  --severity high \
  --description "边界条件未处理导致数组越界"
```

### 查询错误状态

```bash
python3 skills/metacognitive-loop-enforcer/loop-tracker.py \
  --query ERR-202603-0001
```

### 手动触发复盘

```bash
python3 skills/metacognitive-loop-enforcer/loop-tracker.py \
  --weekly-review
```

### 查看统计

```bash
python3 skills/metacognitive-loop-enforcer/loop-tracker.py \
  --stats
```

---

## File Structure

```
skills/metacognitive-loop-enforcer/
├── SKILL.md              # 本文件 - 技能文档
├── loop-tracker.py       # 错误追踪脚本
├── cron.json            # 定时任务配置
└── error-registry.yaml  # 错误注册表
```

**相关数据文件（运行时生成）：**
- `memory/improvements/` - 改进措施文档
- `memory/verification/` - 验证报告
- `memory/reports/weekly/` - 周度复盘报告
- `memory/patterns/` - 模式分析报告

---

## Error Categories

| 类别代码 | 名称 | 说明 |
|----------|------|------|
| logic | 逻辑错误 | 算法缺陷、条件判断错误 |
| runtime | 运行时错误 | 异常、崩溃、资源耗尽 |
| performance | 性能问题 | 响应慢、资源占用高 |
| security | 安全问题 | 注入、越权、数据泄露 |
| ux | 用户体验 | 交互设计、反馈不及时 |
| communication | 沟通问题 | 理解偏差、信息遗漏 |
| tool_usage | 工具使用 | 参数错误、调用顺序 |

---

## Metrics & KPIs

**关键指标：**
- 错误重复率: 目标 < 5%
- 平均修复时间: 目标 < 24h（高优先级）
- 验证通过率: 目标 > 95%
- 周度新错误数: 趋势下降

**告警阈值：**
- 重复率 > 10%: 黄色告警
- 重复率 > 20%: 红色告警
- 同一错误重复 > 2次: 紧急处理

---

## Self-Check (7S Compliance Verification)

```bash
# 运行自检
python3 loop-tracker.py --self-check
```

**检查项：**
- [x] S1: 输入规范完整定义
- [x] S2: 五阶段处理流程清晰
- [x] S3: 输出规范包含3类文档
- [x] S4: cron配置每周六22:00执行
- [x] S5: 承诺书和追踪表机制完整
- [x] S6: 6类认知局限已标注
- [x] S7: 对抗验证机制已定义

---

## Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-21 | 初始版本，7S标准完整实现 |

---

## See Also

- `error-registry.yaml` - 错误注册表示例
- `loop-tracker.py --help` - 脚本使用帮助
- `memory/reports/` - 历史复盘报告
