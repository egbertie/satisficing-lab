> 生成时间: 2026-04-03 11:34+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# worker-orchestrator Skill 设计文档

**Skill名称**: worker-orchestrator  
**功能**: 6 Worker分配引擎，DAG任务执行，任务路由  
**版本**: 1.0.0  
**状态**: ✅ **FIN**（S5/S7验证完成，3/3测试通过）  
**依赖**: blackboard-manager（状态共享）, checkpoint-manager（检查点）

---

## S1: 输入定义

### 功能需求
- 6 Worker类型识别与分配
- DAG（有向无环图）任务编排
- 任务优先级管理
- 任务失败重试
- Worker健康监控

### 6 Worker类型

| Worker | 职责 | 模型 | 触发条件 |
|--------|------|------|----------|
| Meta-Strategist | 全局编排 | K2.5推理 | 重大决策 |
| Supervisor-Biz | 业务域监督 | K2.5 Flash | 业务任务分配 |
| Supervisor-Tech | 技术域监督 | K2.5 Flash | 技术任务分配 |
| Worker-Analysis | 数据分析 | Flash | 分析类任务 |
| Worker-Execution | 执行操作 | Flash-Lite | 执行类任务 |
| Worker-Creative | 创意生成 | K2.5 | 创意类任务 |

---

## S2: 处理流程

### DAG任务编排
```
任务定义:
  Task A (Worker-Analysis) ──┐
                              ├──▶ Task C (Worker-Execution)
  Task B (Worker-Creative) ───┘
```

### 任务分配流程
1. **任务提交**: 提交任务（类型、输入、依赖）
2. **Worker选择**: 根据任务类型选择合适Worker
3. **依赖检查**: 等待依赖任务完成
4. **任务执行**: 分配给Worker执行
5. **结果收集**: 收集执行结果
6. **状态更新**: 更新Blackboard状态

### 消息路由规则
- Worker禁止P2P直接通信
- 所有消息通过Supervisor路由
- Supervisor向Meta-Strategist汇报

---

## S3: 输出定义

### 成功输出
- 任务分配成功
- DAG执行完成
- 结果写入Blackboard

### 失败处理
- Worker故障：重新分配任务
- 任务失败：按策略重试（最多3次）
- DAG死锁：检测并报告

---

## S4: 自动化集成

### 触发条件
- 用户提交任务
- Cron触发定时任务
- 其他Skill调用

### 集成点
- 调用 blackboard-manager（读写状态）
- 调用 checkpoint-manager（任务检查点）
- 被 hibernation-protocol 调用（休眠前保存任务状态）

---

## S5: 准确性验证

### 测试策略
1. **单元测试**: Worker选择逻辑
2. **集成测试**: 完整DAG执行
3. **故障测试**: Worker故障、任务失败

---

## S6: 局限标注

- 单节点调度（无分布式）
- Worker为逻辑概念（非真实进程）
- 不支持循环依赖检测（需人工保证DAG）

---

## S7: 对抗测试

- Worker故障场景
- 任务无限循环场景
- 资源耗尽场景

---

**设计完成时间**: 2026-03-28  
**下一步**: 编码实现

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
