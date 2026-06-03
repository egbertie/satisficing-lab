---
# 知识元数据 (5标准化)
knowledge_id: W17-FFD14E
title: tavily-search Skill V5标准版本
category: 11_Skill文档
source: skills/tavily-search/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1387
week: 17
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# tavily-search Skill V5标准版本

> **知识ID**: W17-FFD14E  
> **分类**: 11_Skill文档  
> **来源**: `skills/tavily-search/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# tavily-search Skill V5标准版本

## S1: 全局考虑

### 输入
- 搜索查询词
- 搜索深度（basic/advanced）
- 结果数量
- 时间范围

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 研究人员、分析师、决策者 |
| **事** | 深度搜索、问答、研究辅助 |
| **物** | 查询词、搜索结果、引用来源 |
| **环境** | API配额、网络环境 |
| **外部集成** | Tavily API |
| **边界情况** | API限流、无结果、超时 |

---

## S2: 系统考虑

### 处理流程
```
接收查询 → 调用Tavily API → 解析结果 → 格式化输出
```

### 故障处理
- **API限流**: 返回错误，提示重试
- **无结果**: 返回空列表+建议
- **超时**: 重试1次，失败报错

---

## S3: 输出规范

### 搜索结果格式
```json
{
  "query": "搜索词",
  "answer": "AI总结答案（如适用）",
  "results": [
    {
      "title": "标题",
      "url": "链接",
      "content": "摘要内容",
      "score": 0.95
    }
  ],
  "sources": ["来源1", "来源2"]
}
```

---

## S4: 自动化集成

### 使用方式
```python
from skills.tavily_search import search

# 基础搜索
results = search("query", max_results=10)

# 深度搜索（带AI答案）
results = search("query", search_depth="advanced")
```

---

## S5: 自我验证

### 质量指标
- 结果相关性: >80%
- 响应时间: <5s
- 答案准确性: 人工验证

---

## S6: 认知谦逊

### 局限
- 依赖Tavily API可用性
- AI答案可能不准确
- 不保证信息时效性
- 复杂查询可能理解偏差

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| API Key无效 | 明确报错 |
| 查询为空 | 返回错误 |
| 网络中断 | 超时后报错 |
| 结果质量差 | 标记低置信度 |

---

## 使用说明

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills')
from tavily_search import search

results = search("人工智能最新发展", max_results=5)
for r in results["results"]:
    print(f"{r['title']}: {r['url']}")
```
