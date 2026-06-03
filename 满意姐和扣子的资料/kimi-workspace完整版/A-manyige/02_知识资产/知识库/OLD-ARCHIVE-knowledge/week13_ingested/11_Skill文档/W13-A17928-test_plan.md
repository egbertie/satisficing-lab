---
# 知识元数据 (5标准化)
knowledge_id: W13-A17928
title: Task Coordinator Skill 质量评估测试套件
category: 11_Skill文档
source: skills/.archive_task-coordinator/tests/test_plan.md
ingested_at: 2026-03-27 17:59:30
word_count: 2155
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Task Coordinator Skill 质量评估测试套件

> **知识ID**: W13-A17928  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_task-coordinator/tests/test_plan.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Task Coordinator Skill 质量评估测试套件

## 评估目标
评估 task-coordinator Skill 的任务协调能力，包括模式切换、遗漏检测、预警机制等核心功能。

## 测试设计原则
1. **覆盖性**: 覆盖所有执行模式（sequential/parallel/notify_user/hybrid）
2. **边界性**: 测试阈值边界条件
3. **压力性**: 模拟高负载并发场景
4. **实用性**: 基于真实使用场景设计

## 测试场景概览

### 正例测试场景 (10个)
测试 Skill 应该正确触发的场景

| 编号 | 场景名称 | 测试目标 | 预期模式 |
|------|----------|----------|----------|
| P01 | 严重过期任务处理 | 验证过期任务触发 sequential 模式 | sequential |
| P02 | 多过期任务并行补救 | 验证多过期任务使用子代理并行 | sequential+parallel |
| P03 | 阻塞任务批量确认 | 验证阻塞任务触发 notify_user 模式 | notify_user |
| P04 | 正常任务并行执行 | 验证无紧急任务时进入 parallel 模式 | parallel |
| P05 | 混合模式调度 | 验证风险任务+正常任务 hybrid 处理 | hybrid |
| P06 | 临界风险分数触发 | 验证 risk_score=10 时正确触发 | sequential |
| P07 | 长期阻塞检测 | 验证阻塞超过2天的任务被识别 | notify_user |
| P08 | 高风险即将到期 | 验证12小时内到期任务被标记 | hybrid/sequential |
| P09 | 学习模式识别 | 验证历史数据用于优化策略 | N/A |
| P10 | 资源分配计算 | 验证不同模式下的资源分配比例 | 各模式 |

### 负例测试场景 (10个)
测试 Skill 不应误触发的边界情况

| 编号 | 场景名称 | 测试条件 | 不应触发 |
|------|----------|----------|----------|
| N01 | 空任务列表 | 无任何任务 | sequential |
| N02 | 轻微逾期 | 逾期1小时非关键任务 | sequential |
| N03 | 短期阻塞 | 阻塞0.5天任务 | notify_user |
| N04 | 充足时间任务 | 24小时后到期普通任务 | hybrid |
| N05 | 已完成任务干扰 | 已完成任务被误判 | 任何特殊模式 |
| N06 | 未来任务提前 | 一周后任务被提前处理 | 任何模式 |
| N07 | 阈值边界下 | risk_score=9 时不应 sequential | sequential |
| N08 | 无阻塞时notify | 无阻塞任务时不应 notify_user | notify_user |
| N09 | 有阻塞时parallel | 有阻塞任务时不应 parallel | parallel |
| N10 | 过期时hybrid | 有过期任务时不应 hybrid | hybrid |

### 压力测试场景 (5个)
测试复杂多任务并发处理能力

| 编号 | 场景名称 | 负载规模 | 测试指标 |
|------|----------|----------|----------|
| S01 | 大规模过期任务 | 20+ 过期任务 | 响应时间、内存使用 |
| S02 | 混合高并发 | 50+ 各类任务 | 决策准确性 |
| S03 | 快速连续触发 | 1秒内10次检查 | 并发安全 |
| S04 | 极端阻塞堆积 | 30+ 阻塞任务 | 批量处理效率 |
| S05 | 资源耗尽模拟 | 100+ 任务+极端参数 | 稳定性、降级能力 |

## 评估指标

### 功能指标
- **准确率**: 决策模式与预期一致的比例
- **召回率**: 正确识别紧急任务的比例
- **误报率**: 错误触发特殊模式的比例

### 性能指标
- **响应时间**: 单次分析耗时（目标<100ms）
- **内存占用**: 峰值内存使用
- **并发安全**: 多线程/多进程环境下稳定性

### 质量指标
- **代码覆盖率**: 测试覆盖的代码行数比例
- **边界覆盖**: 阈值边界条件的测试覆盖
- **场景覆盖**: 真实使用场景的模拟程度

## 测试执行计划

### Phase 1: 单元测试
- 测试各个独立函数
- 验证边界条件处理

### Phase 2: 集成测试
- 测试完整工作流
- 验证模块间协作

### Phase 3: 压力测试
- 模拟高负载场景
- 测试性能极限

### Phase 4: 回归测试
- 验证修复不引入新问题
- 长期稳定性测试
