---
# 知识元数据 (5标准化)
knowledge_id: W15-6304FB
title: brave-search Skill V5标准版本
category: 11_Skill文档
source: skills/brave-search/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1159
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# brave-search Skill V5标准版本

> **知识ID**: W15-6304FB  
> **分类**: 11_Skill文档  
> **来源**: `skills/brave-search/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# brave-search Skill V5标准版本

## S1: 全局考虑

### 输入
- 搜索查询词
- 结果数量要求
- 区域/语言偏好

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 用户获取信息、研究人员查资料 |
| **事** | 网页搜索、新闻搜索、图片搜索 |
| **物** | 搜索关键词、返回结果、URL、摘要 |
| **环境** | 网络环境、API配额、速率限制 |
| **外部集成** | Brave Search API、结果格式化 |
| **边界情况** | 无结果、API限流、网络超时 |

---

## S2: 系统考虑

### 处理流程
```
接收查询 → 调用Brave API → 解析结果 → 格式化输出 → 返回用户
```

### 故障处理
- **无结果**: 返回空列表+提示
- **API限流**: 返回错误+重试时间
- **超时**: 重试1次，仍失败则报错

---

## S3: 输出规范

### 搜索结果格式
```json
{
  "query": "搜索词",
  "results": [
    {
      "title": "结果标题",
      "url": "https://example.com",
      "snippet": "摘要内容...",
      "source": "brave"
    }
  ],
  "total": 10,
  "timestamp": "2026-03-22T09:00:00+08:00"
}
```

---

## S4: 自动化集成

### 使用方式
```bash
# 命令行搜索
brave-search "query" --count 10

# Python调用
from skills.brave_search import search
results = search("query", count=10)
```

---

## S5: 自我验证

### 质量指标
- 结果相关性: >80%
- 响应时间: <3s
- 可用性: >99%

---

## S6: 认知谦逊

### 局限
- 依赖Brave API可用性
- 无法访问被墙网站
- 不保证结果实时性

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| API Key无效 | 明确报错，提示配置 |
| 查询为空字符串 | 返回错误，要求输入 |
| 网络断开 | 超时后报错 |
| 结果为空 | 返回空列表+友好提示 |
