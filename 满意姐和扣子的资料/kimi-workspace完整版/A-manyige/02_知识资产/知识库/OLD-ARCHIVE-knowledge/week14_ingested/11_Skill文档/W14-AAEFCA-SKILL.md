---
# 知识元数据 (5标准化)
knowledge_id: W14-AAEFCA
title: Unified Communication Suite
category: 11_Skill文档
source: skills/.archive_unified-communication-suite/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1714
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Unified Communication Suite

> **知识ID**: W14-AAEFCA  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_unified-communication-suite/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: unified-communication-suite
description: Unified communication platform suite for Feishu/Lark/DingTalk integration. Replaces feishu-messaging, feishu-send-file, feishu-doc-manager, feishu-file-sender, feishu-docx-powerwrite, dingtalk-feishu-cn, sendfiles-to-feishu with single integrated interface. Use for: sending messages, sharing files, managing documents, automated notifications, group collaboration.
triggers: ["feishu", "lark", "dingtalk", "message", "send file", "document", "notification", "协作"]
---

# Unified Communication Suite

**统一通讯平台套件** - 整合飞书/钉钉的消息、文件、文档管理能力。

> 🎯 替代: feishu-messaging + feishu-send-file + feishu-doc-manager + feishu-file-sender + feishu-docx-powerwrite + dingtalk-feishu-cn + sendfiles-to-feishu

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **消息发送** | 个人消息、群消息、富文本、卡片消息 |
| **文件传输** | 上传下载、批量发送、文件夹同步 |
| **文档管理** | 创建、编辑、协作、权限管理 |
| **自动化通知** | 定时通知、事件触发、工作流集成 |
| **多平台支持** | 飞书、钉钉统一接口 |

---

## 快速开始

### CLI使用

```bash
# 发送消息
ucs message send --platform feishu --to "user_id" --content "Hello"

# 发送文件
ucs file send --platform feishu --to "chat_id" --file "document.pdf"

# 创建文档
ucs doc create --title "会议纪要" --content "# 会议内容..." --folder "会议记录"

# 批量发送
ucs batch --config notification.yaml
```

---

## 替代关系

| 原Skill | 原功能 | 新命令 |
|---------|--------|--------|
| feishu-messaging | 发送消息 | `ucs message send` |
| feishu-send-file | 发送文件 | `ucs file send` |
| feishu-doc-manager | 文档管理 | `ucs doc create/manage` |
| feishu-file-sender | 文件发送 | `ucs file send` |
| feishu-docx-powerwrite | 文档生成 | `ucs doc create --template` |
| dingtalk-feishu-cn | 钉钉集成 | `ucs --platform dingtalk` |
| sendfiles-to-feishu | 批量发送 | `ucs batch` |

---

**自建替代计数**: +7
