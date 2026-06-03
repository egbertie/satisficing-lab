> 生成时间: 2026-04-03 13:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

---
name: category6-full-task-processor
status: ✅ FIN（4/4测试通过，可生产使用）
description: 第6类历史机制全量任务处理器，基于9步SOP流程，强制使用深度洞察、内化、Skill模块，蓝军实时监督
version: "1.0.0"
belongs_to: "governance-suite"
---

# Category6 Full Task Processor V1.0

## 归属映射
- **归属系统**: governance-suite
- **角色**: 全量任务标准化处理器
- **依赖**: super-knowledge-ingest, blue-army-auditor

---

## 功能概述

本Skill是`docs/FULL_TASK_PROCESSING_SOP_V1.0.md`的Skill化实现，强制要求：
1. ✅ 使用9步SOP流程
2. ✅ 每条记录深度洞察（L1-L5）
3. ✅ 内化记录（13步内化SOP）
4. ✅ 强制Skill模块（super-knowledge-ingest入库）
5. ✅ 蓝军实时监督

---

## 9步流程Skill化

### 步骤1: 任务分类（P0/P1/P2）
**输入**: 全量任务清单  
**输出**: `classification.json`  
**强制**: 使用本Skill的`classify_tasks()`函数

### 步骤2: 建立审计目录结构
**输出**: 标准目录结构  
**强制**: 使用本Skill的`create_audit_structure()`函数

### 步骤3: P0核心逐条审计
**输入**: P0清单  
**输出**: `p0/P0-{NNN}_{name}_audit.md`（每条一个文件）  
**强制**: 
- 每条必须包含深度洞察（L1-L5）
- 每条必须包含内化记录
- 必须使用`super-knowledge-ingest` Skill入库

### 步骤4: P1重要逐条审计（全覆盖）
**输入**: P1清单  
**输出**: `p1/P1-{NNN}_{name}_audit.md`（每条一个文件）  
**强制**: 同P0标准

### 步骤5: P2一般分类处理
**输入**: P2清单  
**输出**: `p2/P2_INDEX.md` + `p2/classification.json`  
**强制**: 建立完整索引，不遗漏

### 步骤5.5: 蓝军审计验证 ⭐关键
**执行者**: 蓝军子代理（通过本Skill调用）  
**审计范围**: P0 100% / P1 100% / P2 10%  
**强制**: 蓝军独立审计，不走过场

### 步骤6: 问题整改
**输入**: 蓝军标记问题  
**输出**: 整改报告  
**强制**: 3分钟内启动整改

### 步骤7: 方法论提取
**输出**: `METHODOLOGY_EXTRACTED.md`  
**强制**: 从审计中提取可复用方法论

### 步骤8: 汇总报告+持续监控
**输出**: `CATEGORY6_FINAL_REPORT.md`  
**强制**: 完整报告，包含真实完成率

### 步骤9: 用户验收与迭代
**输入**: Egbertie验收  
**强制**: 验收通过才算完成

---

## 强制检查清单

每条记录审计前必须确认：
- [ ] 使用了本Skill的`audit_record()`函数
- [ ] 包含L1-L5深度洞察
- [ ] 包含内化记录（13步SOP）
- [ ] 使用`super-knowledge-ingest` Skill入库
- [ ] 蓝军已审计（或已标记待审计）

---

## 使用方式

### 标准调用
```bash
python3 skills/category6-full-task-processor/scripts/run.py --category 6 --input records.json --output diary/category6_deep_audit/
```

### 强制检查
```bash
python3 skills/category6-full-task-processor/scripts/run.py --check-compliance diary/category6_deep_audit/
```

---

## 依赖Skill

| Skill | 用途 | 强制 |
|-------|------|------|
| super-knowledge-ingest | 知识入库 | ✅ 必须使用 |
| blue-army-auditor | 质量审计 | ✅ 必须使用 |
| checkpoint-manager | 检查点保存 | ✅ 推荐使用 |

---

## 局限标注（S6）

- 大规模任务（>10,000条）需分批处理
- 每条审计报告Token成本约500-1000
- 蓝军审计可能发现新问题需整改

---

## 蓝军验收标准

本Skill必须通过以下验收：
1. 9步流程完整实现
2. 深度洞察模块集成
3. 内化模块集成
4. 强制Skill调用验证
5. 蓝军监督接口可用

**未通过蓝军验收，禁止使用。**

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
