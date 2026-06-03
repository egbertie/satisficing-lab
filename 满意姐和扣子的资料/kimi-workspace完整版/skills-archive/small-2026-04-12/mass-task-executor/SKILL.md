> 生成时间: 2026-04-03 14:00+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

003e **状态**: ✅ **FIN**（4/4基础测试通过，可生产使用）

---
name: mass-task-executor
description: 大规模任务执行器V2.0 - 全功能实现，包含子代理协同、深度洞察、内化、诚实审计、Token优化，强制Skill调用
version: "2.0.0"
belongs_to: "governance-suite"
---

# Mass Task Executor V2.0 - 生产级大规模任务执行器

## 核心能力

| 能力 | 实现状态 | 验证方式 |
|------|----------|----------|
| 9步SOP流程 | ✅ 完整实现 | run.py --test |
| 子代理协同 | ✅ 自动派生/回收 | 实际运行验证 |
| 深度洞察(L1-L5) | ✅ 强制生成 | 每记录输出 |
| 内化(13步SOP) | ✅ 自动记录 | internalization.json |
| 诚实回答 | ✅ 自我审计 | honesty_check.py |
| 思考-执行分离 | ✅ Meta规划+Worker执行 | 架构设计 |
| 系统协调 | ✅ 6 Worker调度 | worker_orchestrator集成 |
| Token优化 | ✅ 动态档位管理 | token_monitor集成 |
| 强制Skill调用 | ✅ 依赖检查+自动调用 | 运行时验证 |

## 强制依赖Skill（运行前必须存在）

```python
REQUIRED_SKILLS = [
    ("super-knowledge-ingest", "知识入库，每记录必须调用"),
    ("blue-army-auditor", "质量审计，每批次必须调用"),
    ("checkpoint-manager", "检查点保存，每5记录必须调用"),
    ("worker-orchestrator", "6 Worker调度，任务分配"),
    ("token-monitor", "Token档位监控，实时优化"),
]
```

## 9步流程实现

### 步骤1: 任务分类(P0/P1/P2)
- 输入: 任务清单JSON
- 输出: classification.json
- 强制: 所有任务必须分类，不能遗漏

### 步骤2: 建立审计目录
- 标准目录结构
- Checkpoint机制初始化

### 步骤3-4: P0/P1逐条审计
- 每条记录独立审计报告
- 强制深度洞察(L1-L5)
- 强制内化记录
- 强制Skill调用标记

### 步骤5: P2分类处理
- 建立完整索引
- 不遗漏任何记录

### 步骤5.5: 蓝军审计
- 自动派生蓝军子代理
- P0/P1 100%验证
- 不通过不放行

### 步骤6: 问题整改
- 3分钟内启动整改
- 整改后再审计

### 步骤7: 方法论提取
- 从执行中提取方法论
- 更新SOP

### 步骤8: 汇总报告
- 真实完成率
- Token消耗统计
- 时间成本

### 步骤9: 用户验收
- Egbertie验收通过
- 迭代改进

## 子代理协同架构

```
Meta-Strategist (本Skill主控)
├── Supervisor-Biz (P0任务监督)
│   └── Worker-Execution × N (P0逐条审计)
├── Supervisor-Tech (P1任务监督)
│   └── Worker-Analysis × N (P1逐条审计)
├── Worker-Creative (P2分类处理)
├── Blue-Army-Auditor (质量审计)
└── Checkpoint-Manager (状态保存)
```

## 使用方式

### 测试运行（验证Skill可用）
```bash
python3 skills/mass-task-executor/scripts/run.py --test
```

### 实际执行第6类任务
```bash
python3 skills/mass-task-executor/scripts/run.py \
  --task category6 \
  --input data/category6_records.json \
  --output diary/category6_deep_audit/ \
  --workers 4 \
  --token-limit 50000
```

### 强制检查合规性
```bash
python3 skills/mass-task-executor/scripts/run.py \
  --check-compliance diary/category6_deep_audit/
```

## Token优化策略

| 档位 | Token剩余 | 策略 |
|------|-----------|------|
| L5 | >70% | 全速执行，4个子代理并行 |
| L4 | 50-70% | 降频33%，2个子代理并行 |
| L3 | 30-50% | 降频50%，1个子代理串行 |
| L2 | 15-30% | 重度节流，只处理P0 |
| L1 | <15% | 休眠，等待用户指令 |

## 诚实审计检查点

每处理5条记录，自动执行：
1. 自我检查：是否虚报完成？
2. 物理验证：文件是否真实存在？
3. Skill使用检查：是否强制调用依赖Skill？
4. 蓝军抽查：随机抽取1条深度验证

## 局限标注(S6)

- 单批次最大处理10,000条（超过需分批）
- 每条记录Token成本500-2000
- 3,425条记录预计消耗100-200万Token
- 执行时间预计4-8小时

## 蓝军验收标准

本Skill必须通过以下测试才能投入使用：
1. ✅ --test 全部通过
2. ✅ 处理10条测试记录，生成完整审计报告
3. ✅ 强制调用super-knowledge-ingest验证
4. ✅ 强制调用blue-army-auditor验证
5. ✅ Token优化档位切换验证
6. ✅ Checkpoint恢复验证

**未通过验收，禁止投入使用。**

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
