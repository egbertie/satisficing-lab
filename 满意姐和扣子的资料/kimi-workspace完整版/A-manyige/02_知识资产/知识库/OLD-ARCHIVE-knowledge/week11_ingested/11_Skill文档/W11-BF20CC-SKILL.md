---
# 知识元数据 (5标准化)
knowledge_id: W11-BF20CC
title: Kimi Code Skill
category: 11_Skill文档
source: skills/.archive_kimi-code/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 641
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Kimi Code Skill

> **知识ID**: W11-BF20CC  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_kimi-code/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: kimi-code
description: 调用Kimi API进行代码生成、调试和解释。利用用户自有Kimi会员资源。
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["KIMI_API_KEY"] },
        "emoji": "🌙",
      },
  }

# Kimi Code Skill

利用Kimi K2.5 API进行编程辅助。

## 使用前提

需要设置环境变量：
```bash
export KIMI_API_KEY=sk-xxxxxxxxxx
```

## 功能

### 1. 代码生成
当需要编写代码时，调用此Skill。

**示例**：
```
用户：写一个Python脚本，读取CSV文件并统计分析
AI：调用Kimi Code生成代码...
```

### 2. 代码调试
当代码出错时，提供错误信息，Kimi帮助调试。

### 3. 代码解释
解释复杂代码的逻辑。

## 调用方式

通过`kimi_fetch`或直接HTTP调用Kimi API。

## 模型选择

- 默认：kimi-coding/k2p5（编程专用）
- 长文本：kimi-k2.5（200K上下文）

## 注意事项

1. API Key只保存在本地，不上传到云端
2. 注意Kimi会员额度使用
3. 代码生成后需要人工审核
