---
# 知识元数据 (5标准化)
knowledge_id: W11-D20F95
title: SKILL
category: 11_Skill文档
source: skills/.archive_meeting-action-extractor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2845
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W11-D20F95  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_meeting-action-extractor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: meeting-action-extractor
version: 1.0.0
description: |
  会议纪要行动项提取器 - 从会议纪要自动提取行动项并结构化：
  1. 全局考虑：覆盖摘要、行动项、决策、问题、后续步骤全要素
  2. 系统考虑：输入→解析→提取→保存→反馈完整闭环
  3. 迭代机制：根据用户反馈优化提取准确度
  4. Skill化：标准接口，支持多种输入格式
  5. 流程自动化：全自动提取和结构化存储
author: Satisficing Institute
tags:
  - meeting
  - action-items
  - extraction
  - productivity
requires:
  - model: "kimi-coding/k2p5"
---

# 会议纪要行动项提取器标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 提取要素全覆盖

| 要素 | 说明 | 输出格式 |
|------|------|----------|
| **摘要** | 2-3句话会议概述 | 文本 |
| **行动项** | 任务+负责人+截止日期 | `- [ ] @Owner: Task — Deadline` |
| **决策** | 已确认的决定 | 列表 |
| **问题** | 未解决的问题 | 列表 |
| **后续步骤** | 下一步行动 | 列表 |
| **参与者** | 与会人员 | 列表 |

### 1.2 输入格式适配

| 格式 | 处理方式 | 特殊处理 |
|------|----------|----------|
| 原始笔记 | 自然语言解析 | 降噪处理 |
| 录音转录 | 时间戳清理 | 发言人识别 |
| 邮件线程 | 线程解析 | 关键信息提取 |
| 聊天记录 | 上下文重建 | 话题分割 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 提取流程

```
输入内容 → 格式识别 → 要素提取 → 结构化 → 保存文件 → 生成摘要
```

### 2.2 文件管理

```
meeting-notes/
├── YYYY-MM-DD_topic.md         # 会议记录
├── todo.md                      # 待办汇总
└── index.json                   # 索引
```

### 2.3 命名规范

```
YYYY-MM-DD_topic.md
- 日期前缀（排序）
- 下划线分隔
- 小写
- 无空格
```

---

## 标准3: 迭代机制（Iterative）

### 3.1 准确度优化

| 反馈类型 | 优化动作 |
|----------|----------|
| 漏提取 | 增强该类型模式识别 |
| 误提取 | 添加排除规则 |
| 格式问题 | 更新模板 |

### 3.2 学习机制

- 记录用户修正
- 周期性更新提取规则
- 领域适配优化

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
meeting-action-extractor/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── extract.py              # 主提取脚本
│   ├── parse_notes.py          # 笔记解析
│   ├── parse_transcript.py     # 转录解析
│   ├── structure_output.py     # 结构化输出
│   └── save_meeting.py         # 保存会议记录
└── templates/
    └── meeting_template.md
```

### 4.2 调用接口

```python
from meeting_action_extractor import MeetingExtractor

extractor = MeetingExtractor()

# 提取会议要素
result = extractor.extract(content, format="raw_notes")

# 保存会议记录
file_path = extractor.save(result, topic="产品同步")

# 获取某人的行动项
items = extractor.get_actions_by_owner("@Sarah")
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 自动流程

| 阶段 | 自动动作 | 输出 |
|------|----------|------|
| 内容输入 | 识别输入格式 | 格式标签 |
| 解析 | 提取关键要素 | 结构化数据 |
| 保存 | 生成规范文件名 | 文件路径 |
| 反馈 | 显示摘要+行动项 | 确认提示 |

### 5.2 使用方法

```bash
# 提取会议纪要
openclaw skill run meeting-action-extractor extract --content "会议内容..."

# 从文件提取
openclaw skill run meeting-action-extractor extract-from-file --file meeting.txt

# 查询某人的行动项
openclaw skill run meeting-action-extractor get-actions --owner "Sarah"
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 五要素提取 + 多格式适配 | ✅ |
| **2. 系统** | 提取→保存→反馈闭环 | ✅ |
| **3. 迭代** | 准确度优化 + 学习机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 全自动提取和存储 | ✅ |

---

*版本: v1.0.0*  
*来源: ai-meeting-notes散落机制提取*  
*创建: 2026-03-20*
