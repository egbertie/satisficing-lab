---
kia-version: 1.0
tier: T0
title: 重复消息防复发协议 V1.0
source: docs/anti-duplicate-protocol-v1.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchA-docs-01]
---

# 重复消息防复发协议 V1.0

> **生效日期**: 2026-04-10
> **原因**: 用户观察到对话框内同一回答出现 2-3 次，违反双经济要求
> **目标**: 从行为端彻底杜绝重复发送

---

## 原则

对每个 assistant turn 执行 **「一问一答」** 检查：
- 这个 turn 里，我已经向用户传递过实质性内容了吗？
- 如果有，那么**本 turn 剩余部分只能输出 NO_REPLY**
- 决不在同一个 turn 里输出两段可被用户阅读的文字

---

## 高频致因与对策

### 1. `message` 工具与文本回复混用
**现象**: 调用了 `message(action=send)` 发送消息，同时 assistant 又输出了文本内容 → 两者都被投递，变成两条消息。

**对策**:
- 如果使用了 `message(action=send)`，必须回复 **ONLY: `NO_REPLY`**
- ❌ 错误: 先 `message(send)`，再写一段总结文字
- ✅ 正确: 先 `message(send)`，然后 `NO_REPLY`

### 2. 分裂 turn（Split Turn）中的重复收尾
**现象**: 长对话被系统拆成多个子 turn。如果在每个子 turn 结尾都写"以上就是全部内容"，用户会看到多次同样的总结。

**对策**:
- 第一个子 turn 负责执行和中间推理
- 最后一个子 turn 只负责最终输出
- **中间 turn 结尾不写任何结论性段落**，直接用 `NO_REPLY` 或等待下一步

### 3. 心跳/定时任务连续发送相似内容
**现象**: 多个 cron job 在相近时间发送主题相近的消息（如 morning-report 和 milestone-check 都提到"官宣倒计时"）。

**对策**:
- 已删除重复的 `morning-report` job
- 不同 job 的消息模板必须有明确的标题区分，避免用户误以为重复
- Cron job 时间必须严格错开（至少 10 分钟以上）

### 4. 平台级/网关级重投（不可控但可识别）
**现象**: 偶发的网络或解析故障导致网关把同一条 assistant 回复投递多次。

**对策**:
- 记录每次重复发生的时间点、内容和环境（是否有 tool call、是否有 heartbeat）
- 如果 48 小时内再次发生，收集日志并向用户报告，判断是否需要升级 OpenClaw/Gateway

---

## 执行检查清单（每次回复前默念）

- [ ] **本 turn 是否已经用 `message` 发过消息？** → 若是，输出 `NO_REPLY`
- [ ] **本 turn 是否是 split turn 的中间段？** → 若是，不输出最终总结
- [ ] **本回复是否与上一条已发送的内容实质相同？** → 若是，输出 `NO_REPLY`
- [ ] **是否只有一条可阅读文本离开我的手？** → 若不是，立即截断

---

## 监控规则

**下次发生重复回复时，必须记录**:
1. 发生时间
2. 重复次数（2 次 / 3 次）
3. 是否涉及 tool call
4. 是否涉及 `message` 工具
5. 是否发生在 split turn 中

**记录位置**: `memory/duplicate-reply-incidents.md`

**上报阈值**: 若 7 天内发生 ≥2 次，则判定为系统性 bug，需进一步排查 OpenClaw Gateway / kimi-claw 插件。
