---
# 知识元数据 (5标准化)
knowledge_id: W14-6FEFD8
title: SKILL
category: 11_Skill文档
source: skills/.archive_workflow-blueprint-generator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2665
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W14-6FEFD8  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_workflow-blueprint-generator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: workflow-blueprint-generator
version: 1.0.0
description: |
  工作流蓝图生成器 - 将多步骤流程转化为可执行的工作流蓝图：
  1. 全局考虑：覆盖触发器、动作、依赖、回退全要素
  2. 系统考虑：输入→规范化→蓝图→导出完整闭环
  3. 迭代机制：根据执行反馈优化蓝图结构
  4. Skill化：标准接口，可对接n8n等自动化平台
  5. 流程自动化：自动生成标准化工作流定义
author: Satisficing Institute
tags:
  - workflow
  - blueprint
  - automation
  - orchestration
requires:
  - model: "kimi-coding/k2p5"
---

# 工作流蓝图生成器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 工作流要素全覆盖

| 要素 | 说明 | 必含 |
|------|------|------|
| **触发器** | 工作流启动条件 | ✅ |
| **步骤** | 有序执行的动作 | ✅ |
| **依赖** | 步骤间依赖关系 | ✅ |
| **回退** | 失败处理策略 | ✅ |
| **输出** | 执行结果定义 | ✅ |

### 1.2 平台适配

| 平台 | 输出格式 | 特殊处理 |
|------|----------|----------|
| n8n | JSON | 节点映射 |
| GitHub Actions | YAML | 语法转换 |
| Make/Zapier | 自定义 | API适配 |
| 内部编排器 | JSON/YAML | 标准接口 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 蓝图生成流程

```
需求输入 → 步骤拆解 → 依赖分析 → 蓝图构建 → 格式导出 → 验证
```

### 2.2 规范化规则

| 规则 | 说明 | 示例 |
|------|------|------|
| 单目的 | 每个步骤单一职责 | 不要"检查并发送" |
| 原子性 | 步骤不可再分 | 可独立执行 |
| 可回退 | 每个步骤有回退策略 | 失败处理定义 |

---

## 标准3: 迭代机制（Iterative）

### 3.1 蓝图优化

| 优化类型 | 触发条件 | 优化动作 |
|----------|----------|----------|
| 并行化 | 步骤间无依赖 | 合并为并行节点 |
| 简化 | 步骤过于复杂 | 拆分为子流程 |
| 增强 | 缺少回退策略 | 添加错误处理 |

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
workflow-blueprint-generator/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── generate_blueprint.py   # 主生成脚本
│   ├── analyze_dependencies.py # 依赖分析
│   ├── normalize_steps.py      # 步骤规范化
│   ├── export_n8n.py           # n8n格式导出
│   └── export_github_actions.py # GitHub Actions导出
└── templates/
    ├── n8n_template.json
    └── github_action_template.yml
```

### 4.2 调用接口

```python
from workflow_blueprint_generator import BlueprintGenerator

generator = BlueprintGenerator()

# 生成蓝图
blueprint = generator.generate(
    name="内容发布流程",
    trigger="文档更新",
    steps=[...]
)

# 导出指定格式
n8n_json = generator.export(blueprint, format="n8n")
github_yaml = generator.export(blueprint, format="github_actions")
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 生成工作流蓝图
openclaw skill run workflow-blueprint-generator generate \
  --name "内容发布" \
  --trigger "文档更新" \
  --steps "检查质量,生成摘要,发布到各平台"

# 导出n8n格式
openclaw skill run workflow-blueprint-generator export \
  --blueprint workflow.json \
  --format n8n \
  --output n8n_workflow.json
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 工作流要素全覆盖 | ✅ |
| **2. 系统** | 输入→蓝图→导出闭环 | ✅ |
| **3. 迭代** | 蓝图优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动生成标准化蓝图 | ✅ |

---

*版本: v1.0.0*  
*来源: agentic-workflow-automation散落机制提取*  
*创建: 2026-03-20*
