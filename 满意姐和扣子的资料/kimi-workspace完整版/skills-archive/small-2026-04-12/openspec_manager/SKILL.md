> 生成时间: 2026-04-05 16:54+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

---
name: openspec_integration_manager
description: >
  OpenSpec契约系统与满意姐认知生态的整合管理器。
  实现规范驱动开发(SDD)，强制所有代码类任务通过Proposal/Design/Tasks三阶契约。
  解决"AI不读规范"的链路断裂问题。
version: 1.0.0
author: 蓝军Skeptor-7
tags: [openspec, spec_driven, contract, bridge_rule, zero_coding]
---

# OpenSpec整合管理器 v1.0

## 强制工作流

```
Step1: /opsx:propose → 生成契约文件
   ↓ [阻塞: proposal.md未生成禁止进入Step2]
Step2: 人工评审契约 → 蓝军审计
   ↓ [阻塞: 未通过议会审计禁止进入Step3]
Step3: /opsx:apply → AI自动编码
   ↓ [阻塞: 测试失败禁止进入Step4]
Step4: 自动测试验证 → P8引擎L2-L3审计
   ↓ [阻塞: 测试未通过禁止进入Step5]
Step5: 人工代码审查 → 孔子+观自在双审
   ↓ [阻塞: 未通过审查禁止进入Step6]
Step6: /opsx:archive → 归档并入specs/
```

## 核心命令

- `/opsx:propose`
- `/opsx:apply`
- `/opsx:archive`
- `/opsx:verify`

## Bridge Rule 2.0

每次会话强制加载 `openspec/config.yaml` 和 `openspec/specs/`，转化为 TemporalCrystal 的 HARD_CONTEXT。
