---
# 知识元数据 (5标准化)
knowledge_id: W10-2F85B8
title: Evolution Experiment Lab Skill
category: 11_Skill文档
source: skills/.archive_evolution-experiment-lab/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 924
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Evolution Experiment Lab Skill

> **知识ID**: W10-2F85B8  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_evolution-experiment-lab/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Evolution Experiment Lab Skill

## 功能概述
提供隔离的实验环境，支持小范围试点、数据驱动决策，失败则快速回滚。

## 实验流程
1. **实验设计** - 定义目标、指标、方案
2. **隔离测试** - 在隔离环境验证
3. **小范围试点** - 1-2个Skill试点
4. **评估决策** - 基于数据决策
5. **推广/回滚** - 成功推广，失败回滚

## 使用方法

### 命令
```bash
# 创建实验
openclaw agent --skill evolution-experiment-lab --task create-experiment --design design.md

# 检查实验状态
openclaw agent --skill evolution-experiment-lab --task check-experiments

# 生成实验周报
openclaw agent --skill evolution-experiment-lab --task weekly-report
```

### Python调用
```python
from skills.evolution_experiment_lab import ExperimentManager

manager = ExperimentManager()
exp = manager.create_experiment(design)
# ... 运行实验 ...
result = manager.evaluate(exp.id)
```

## 实验目录
```
experiments/
├── EXP-001-xxx/
│   ├── experiment-design.md
│   ├── isolation-test/
│   ├── pilot/
│   ├── results.md
│   └── decision.md
└── _template/
```

## 作者
满意解研究所 - 持续优化系统

## 版本
v1.0.0 - 2026-03-15
