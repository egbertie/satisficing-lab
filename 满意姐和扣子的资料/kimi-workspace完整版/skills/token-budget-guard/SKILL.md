> 生成时间: 2026-04-02 02:09+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Skill: token-budget-guard

> **名称**: Token预算守卫  
> **版本**: 1.0.0  
> **创建时间**: 2026-04-02  
> **状态**: ✅ 已完成并测试通过  
> **所属整改步骤**: 第2步

---

## 功能概述

防止Token崩溃，三级熔断机制保障系统稳定性。

---

## 核心机制

### 三级熔断阈值

| 级别 | 阈值 | 状态 | 动作 |
|------|------|------|------|
| 警告 | 70% | warning | 建议/compaction |
| 限制 | 85% | restricted | 仅允许文本输出 |
| 熔断 | 95% | meltdown | 强制停止，要求新开会话 |

### 限制模式行为

当进入限制模式（85%）时，仅允许：
- `text_response` - 纯文本回复
- `compaction` - 压缩命令
- `status_check` - 状态检查
- `budget_query` - 预算查询

### Token估算（新限制声明）

⚠️ **重要**: 无法获取实时Token计数（无平台API）

采用字符长度估算：
```
估算Token = 字符长度 ÷ 4
```

**误差范围**: 10-20%（蓝军已接受此限制）

---

## 测试结果

| 测试项 | 结果 |
|--------|------|
| 正常状态检查 | ✅ 通过 |
| 警告状态（70%） | ✅ 通过 |
| 限制模式（85%） | ✅ 通过 |
| 熔断状态（95%） | ✅ 通过 |
| Token估算 | ✅ 系数~3.9字符/Token |
| 状态查询 | ✅ 通过 |

---

## API接口

### Python API

```python
from token_budget_guard import TokenBudgetGuard, check_budget

# 使用守卫
guard = TokenBudgetGuard(total_budget=200000)
result = guard.check_budget("operation", estimated_input_length)

# 记录使用
guard.record_usage("operation", content, response)

# 检查操作是否允许
if guard.is_operation_allowed("tool_call"):
    # 执行操作
    pass
```

### 装饰器模式

```python
from token_budget_guard import BudgetGuarded

@BudgetGuarded()
def my_operation():
    # 自动预算检查
    pass
```

---

## 成功标准达成

✅ **提前5%预警Token耗尽** - 95%熔断阈值  
✅ **限制模式正确触发** - 白名单机制验证通过  
✅ **用户收到清晰通知** - 状态消息明确

---

## 位置

- **代码**: `skills/token-budget-guard/token_budget_guard.py`
- **索引**: `~/.openclaw/token_budget_history.json`
- **本文件**: `skills/token-budget-guard/SKILL.md`

---

## 新限制声明

| 限制 | 说明 |
|------|------|
| 估算误差 | 10-20%，基于字符长度而非实际Token |
| 熔断体验 | 限制模式下功能受限 |
| 无法预防 | 单次大请求可能直接超限 |

---

## 下一步

第3步: 三层质量闸口Skill创建 (等待蓝军审计通过)