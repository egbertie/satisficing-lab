---
# 知识元数据 (5标准化)
knowledge_id: W5-681E35
title: API 清单 (API Inventory)
category: 12_记忆档案
source: docs/archive/API_INVENTORY.md
ingested_at: 2026-03-27 17:59:30
word_count: 1379
week: 5
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# API 清单 (API Inventory)

> **知识ID**: W5-681E35  
> **分类**: 12_记忆档案  
> **来源**: `docs/archive/API_INVENTORY.md`  
> **入库时间**: 2026-03-27

---

## 正文

# API 清单 (API Inventory)

本文档记录所有已配置的API服务和凭证信息。

---

## 🚀 GitHub Models API

**状态:** ✅ 已配置并验证  
**更新时间:** 2026-03-10 22:53

### 基本信息
| 属性 | 值 |
|------|-----|
| 名称 | GitHub Models (GPT-4o) |
| 提供商 | GitHub Models |
| 端点 | https://models.inference.ai.azure.com |
| 模型 | gpt-4o |
| 状态 | active |

### 认证信息
- **类型:** Bearer Token
- **Token:** `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` *(已验证)*

### 能力支持
| 功能 | 支持状态 |
|------|----------|
| 对话 (Chat) | ✅ |
| 函数调用 (Function Calling) | ✅ |
| 视觉 (Vision) | ✅ |
| 流式输出 (Streaming) | ✅ |

### 使用限制
- **每分钟请求数 (RPM):** 15
- **每日请求数:** 150
- **备注:** GitHub Models免费版限制

### 配置路径
```
config/github_models.json
scripts/test_github_models.py
```

### 使用示例
```python
import requests

endpoint = "https://models.inference.ai.azure.com"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

response = requests.post(
    f"{endpoint}/chat/completions",
    headers=headers,
    json={
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "你好！"}],
        "temperature": 0.7
    }
)

print(response.json()['choices'][0]['message']['content'])
```

### 测试结果
- ✅ 简单对话测试通过
- ✅ 中文对话测试通过  
- ✅ 代码生成测试通过

---

## 历史记录

| 日期 | 操作 | 描述 |
|------|------|------|
| 2026-03-10 | 添加 | 配置GitHub Models API (GPT-4o) 作为Claude的免费替代 |

---

*最后更新: 2026-03-10 22:53*
