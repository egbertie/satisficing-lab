---
# 知识元数据 (5标准化)
knowledge_id: W12-1EE727
title: Multi Search Engine
category: 11_Skill文档
source: skills/.archive_multi-search-engine/CHANNELLOG.md
ingested_at: 2026-03-27 17:59:30
word_count: 788
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Multi Search Engine

> **知识ID**: W12-1EE727  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_multi-search-engine/CHANNELLOG.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Multi Search Engine

## 基本信息

- **名称**: multi-search-engine
- **版本**: v2.0.1
- **描述**: 集成17个搜索引擎（8国内+9国际），支持高级搜索语法
- **发布时间**: 2026-02-06

## 搜索引擎

**国内（8个）**: 百度、必应、360、搜狗、微信、头条、集思录
**国际（9个）**: Google、DuckDuckGo、Yahoo、Brave、Startpage、Ecosia、Qwant、WolframAlpha

## 核心功能

- 高级搜索操作符（site:, filetype:, intitle:等）
- DuckDuckGo Bangs快捷命令
- 时间筛选（小时/天/周/月/年）
- 隐私保护搜索
- WolframAlpha知识计算

## 更新记录

### v2.0.1 (2026-02-06)
- 精简文档，优化发布

### v2.0.0 (2026-02-06)
- 新增9个国际搜索引擎
- 强化深度搜索能力

### v1.0.0 (2026-02-04)
- 初始版本：8个国内搜索引擎

## 使用示例

```javascript
// Google搜索
web_fetch({"url": "https://www.google.com/search?q=python"})

// 隐私搜索
web_fetch({"url": "https://duckduckgo.com/html/?q=privacy"})

// 站内搜索
web_fetch({"url": "https://www.google.com/search?q=site:github.com+python"})
```

MIT License
