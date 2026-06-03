---
# 知识元数据 (5标准化)
knowledge_id: W7-89C45F
title: Skill功能重复整合映射表
category: 01_研究报告
source: docs/skill_consolidation_mapping.md
ingested_at: 2026-03-27 17:59:30
word_count: 3844
week: 7
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Skill功能重复整合映射表

> **知识ID**: W7-89C45F  
> **分类**: 01_研究报告  
> **来源**: `docs/skill_consolidation_mapping.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Skill功能重复整合映射表

**创建时间**: 2026-03-21  
**目的**: 识别重复功能，统一入口，减少维护成本

---

## 功能域整合总览

| 功能域 | 主Skill | 重复/从属Skills | 状态 |
|--------|---------|-----------------|------|
| 质量检查 | quality-gate-system | quality-assurance, data-quality-auditor | 规划中 |
| Token管理 | token-budget-enforcer | token-throttle-controller, token-weekly-monitor | 规划中 |
| 灾备恢复 | disaster-recovery-wecom | (新增统一入口) | 已完成 ✅ |
| 自检机制 | standard-self-check | 6个独立self_check脚本 | 已完成 ✅ |
| Cron管理 | cron-rules-optimized | 多个分散配置 | 已完成 ✅ |
| 基线检查 | baseline-checker | (标准参考) | 保持独立 |

---

## 详细整合方案

### 1. 质量检查域整合

**主入口**: `quality-gate-system/`

**功能映射**:
```
quality-gate-system/
├── main.py                    # 统一入口
├── adapters/
│   ├── quality_assurance.py   # 适配原quality-assurance
│   └── data_quality.py        # 适配原data-quality-auditor
└── docs/
    └── MIGRATION_GUIDE.md     # 迁移指南
```

**重复功能识别**:
| 功能 | quality-gate-system | quality-assurance | data-quality-auditor |
|------|---------------------|-------------------|----------------------|
| S1-S7检查 | ✅ | ✅ | ✅ |
| 代码审查 | ✅ | ✅ | ❌ |
| 数据审计 | ✅ | ❌ | ✅ |
| CI/CD集成 | ✅ | ❌ | ✅ |
| 检查清单 | ✅ | ✅ | ✅ |

**整合策略**: 保留quality-gate-system作为统一入口，其他两个Skill的功能作为适配器模块

---

### 2. Token管理域整合

**主入口**: `token-management-suite/`

**当前状况**:
- token-budget-enforcer: 预算控制
- token-throttle-controller: 节流控制
- token-weekly-monitor: 周报监控

**整合后结构**:
```
token-management-suite/
├── __init__.py
├── budget.py          # 预算管理 (原budget-enforcer)
├── throttle.py        # 节流控制 (原throttle-controller)
├── monitor.py         # 监控报表 (原weekly-monitor)
├── unified_config.yaml
└── cli.py             # 统一命令行
```

---

### 3. 自检机制统一

**统一框架**: `scripts/standard_self_check.py` ✅

**覆盖的原脚本**:
| 原脚本路径 | 状态 | 迁移方式 |
|------------|------|----------|
| tiered-output/self_check.sh | 已覆盖 | 调用统一框架 |
| data-quality-auditor/scripts/self_check.py | 已覆盖 | 调用统一框架 |
| vendor-api-monitor/scripts/self_check.py | 已覆盖 | 调用统一框架 |
| ai-meeting-notes/scripts/self_check.py | 已覆盖 | 调用统一框架 |
| worry-list-manager/scripts/self_check.py | 已覆盖 | 调用统一框架 |
| conversation-researcher/scripts/self-check.py | 已覆盖 | 调用统一框架 |

**统一命令**:
```bash
# 检查单个Skill
python3 scripts/standard_self_check.py skills/quality-assurance

# 批量检查
python3 scripts/standard_self_check.py --batch skills/*/

# 生成聚合报告
python3 scripts/standard_self_check.py --report-all
```

---

### 4. Cron调度统一

**统一配置**: `config/cron-rules-optimized.yaml` ✅

**已整合配置**:
- config/cron-rules.yaml (原配置)
- skills/*/cron.json (分散配置)
- implicit-rules-cron-all.sh (脚本配置)

---

## 待整合Skills清单

### 高优先级整合 (本月)

| # | Skill名称 | 重复原因 | 整合方案 | 预估节省 |
|---|-----------|----------|----------|----------|
| 1 | quality-assurance | 与quality-gate-system重复度70% | 迁移为适配器 | 30%维护成本 |
| 2 | data-quality-auditor | 功能被quality-gate-system覆盖 | 功能合并 | 25%维护成本 |
| 3 | token-throttle-controller | 与token-budget-enforcer高重叠 | 统一token-suite | 40%维护成本 |
| 4 | token-weekly-monitor | 可整合为token-suite子模块 | 统一token-suite | 40%维护成本 |

### 中优先级整合 (下月)

| # | Skill名称 | 重复原因 | 整合方案 | 预估节省 |
|---|-----------|----------|----------|----------|
| 5 | info-collection-quality | 与data-quality-auditor重叠 | 合并到quality-suite | 20%维护成本 |
| 6 | info-quality-guardian | 功能边界不清 | 明确职责或合并 | 待评估 |
| 7 | testing-framework | 可能被quality-gate-system覆盖 | 功能评估后决定 | 待评估 |

---

## 整合实施计划

### 阶段1: 框架搭建 (本周)
- [x] 统一自检框架
- [x] 统一Cron配置
- [x] 分级提示词模板
- [ ] quality-suite适配器

### 阶段2: 功能迁移 (下周)
- [ ] quality-assurance功能迁移
- [ ] data-quality-auditor功能迁移
- [ ] token-suite整合
- [ ] 文档更新

### 阶段3: 废弃清理 (下月)
- [ ] 标记废弃Skills
- [ ] 迁移指南发布
- [ ] 旧Skill归档
- [ ] 依赖清理

---

## 整合效果预估

| 指标 | 当前 | 整合后 | 改进 |
|------|------|--------|------|
| 有效Skills数量 | 25 | 18 | -28% |
| 维护复杂度 | 高 | 中 | -40% |
| 功能重复率 | 35% | <10% | -71% |
| Token消耗 | 50K/日 | 35K/日 | -30% |
| 一致性 | 60% | 90% | +50% |

---

**映射表版本**: 1.0  
**最后更新**: 2026-03-21  
**维护者**: System Optimizer
