---
# 知识元数据 (5标准化)
knowledge_id: W15-71D981
title: 429错误处理机制 [RULE]
category: 11_Skill文档
source: skills/error-handler/RATE_LIMIT_HANDLING.md
ingested_at: 2026-03-27 17:59:30
word_count: 702
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 429错误处理机制 [RULE]

> **知识ID**: W15-71D981  
> **分类**: 11_Skill文档  
> **来源**: `skills/error-handler/RATE_LIMIT_HANDLING.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 429错误处理机制 [RULE]

## 问题定义
频繁遇到 `429 {"error":{"type":"rate_limit_error","message":"The engine is currently overloaded"}}`，严重影响对话流畅性。

## 触发条件
- 对话历史过长（上下文超过50KB）
- 短时间内多次工具调用
- 并发任务过多
- API服务负载过高

## 处理规则

### 规则1：自动上下文压缩 [MUST]
当检测到上下文超过阈值时，自动请求压缩：
- 上下文 > 30KB：提示用户进行压缩
- 上下文 > 50KB：强制压缩，只保留最近10轮对话

### 规则2：错误恢复流程 [MUST]
遇到429错误时：
1. **立即停止当前操作**
2. **等待5秒后重试**（最多3次）
3. **如果仍失败**：
   - 简化请求内容
   - 拆分任务为更小批次
   - 或建议用户压缩上下文

### 规则3：预防性措施 [SHOULD]
- 单轮对话工具调用不超过5个
- 复杂任务使用`sessions_spawn`后台执行
- 定期提醒用户压缩对话历史

### 规则4：用户通知 [MUST]
发生429错误时，向用户说明：
- 错误原因（上下文过长/请求过频）
- 正在采取的措施
- 预计恢复时间

---

## 执行检查清单

- [ ] 当前对话上下文大小检查
- [ ] 工具调用频率控制
- [ ] 错误重试机制启用
- [ ] 用户通知已发送

## 版本
- V1.0 (2026-03-10) - 初始版本
