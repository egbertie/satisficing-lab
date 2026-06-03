---
knowledge_id: W1-E30D77
title: Auto-Update Management Philosophy & User Profile Skill
category: 11_Skill文档
source: skills/auto-update-profile/SKILL.md
ingested_at: 2026-03-27T17:44:51.286958
word_count: 1937
---

# Auto-Update Management Philosophy & User Profile Skill

**知识ID**: W1-E30D77  
**分类**: 11_Skill文档  
**原始路径**: skills/auto-update-profile/SKILL.md

---

# Auto-Update Management Philosophy & User Profile Skill

> **命名空间**: SKL-SKILL-v1.0-WIP-260327-Auto-Update-Profile  
> **5标准版本**: v1.0  
> **状态**: WIP (建设中)  
> **创建时间**: 2026-03-27

---

## S1: 输入定义

### 输入类型
- **对话内容**: 用户与AI的对话记录
- **管理哲学更新**: 方法论、理论、决策框架相关内容
- **用户信息更新**: 个人偏好、工作习惯、关键信息变更

### 识别标准（已确认）
```yaml
management_philosophy:  # IMPL-001
  trigger: "所有关于方法论/理论的对话"
  examples:
    - "满意解理论..."
    - "决策框架..."
    - "管理方法论..."
  output: "docs/MANAGEMENT_PHILOSOPHY.md"

user_profile:  # IMPL-002
  trigger: "所有个人信息变更"
  examples:
    - "我喜欢..."
    - "我的工作方式是..."
    - "记住这个..."
  output: "USER.md"
```

---

## S2: 处理流程

### 核心功能

| 功能 | 描述 | 触发条件 |
|------|------|----------|
| `detect_philosophy` | 检测管理哲学内容 | 方法论/理论关键词 |
| `detect_profile` | 检测用户信息变更 | 个人偏好关键词 |
| `extract_insight` | 提取核心洞察 | LLM摘要 |
| `update_file` | 更新目标文件 | 追加模式 |
| `sync_summary` | 同步摘要到用户 | 对话结束时 |

### 处理步骤
1. **监听**: 对话中实时检测触发词
2. **提取**: LLM提取核心洞察（节省Token：仅摘要）
3. **分类**: 判断属于管理哲学还是用户偏好
4. **存储**: 追加到对应文件
5. **确认**: 对话结束时向用户确认

---

## S3: 输出规范

### 输出格式（IMPL-001）
```markdown
## 2026-03-27 更新
**来源**: 对话摘录  
**主题**: 满意解理论应用  
**内容**: 在合伙人匹配中，满意解优于最优解...

[原文摘要]
```

### 输出格式（IMPL-002）
```markdown
## 2026-03-27 更新
**类型**: 工作偏好  
**内容**: 用户偏好早晨处理重要决策
```

---

## S4: 自动化集成

### 触发方式
- **实时**: 对话中检测到触发词
- **批量**: 对话结束后统一处理
- **手动**: 用户说"更新我的档案"

### 集成点
- 对话系统: 实时监听
- 文件系统: 自动追加
- 用户通知: 对话结束确认

---

## S5: 准确性验证

### 验证清单
- [x] 触发词检测准确
- [x] 内容分类正确
- [x] 文件追加无误
- [x] 不覆盖原有内容

---

## S6: 局限标注

### 已知局限
1. 依赖关键词匹配，可能漏检
2. LLM摘要可能丢失细节
3. 需用户最终确认才写入

---

## S7: 对抗测试

| 缺陷类型 | 预期行为 |
|----------|----------|
| 误触发 | 非相关内容不写入 |
| 重复内容 | 检测并去重 |
| 文件损坏 | 备份后写入 |
| 用户拒绝 | 不写入，记录日志 |

---

## 文件清单

| 文件 | 路径 |
|------|------|
| SKILL.md | `skills/auto-update-profile/SKILL.md` |
| auto_update.py | `skills/auto-update-profile/auto_update.py` |
| triggers.json | `skills/auto-update-profile/triggers.json` |

---

*5标准化完成时间: 2026-03-27*
