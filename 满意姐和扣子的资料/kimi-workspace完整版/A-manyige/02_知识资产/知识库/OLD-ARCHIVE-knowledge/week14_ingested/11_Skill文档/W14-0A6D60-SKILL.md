---
# 知识元数据 (5标准化)
knowledge_id: W14-0A6D60
title: Unified Search
category: 11_Skill文档
source: skills/.archive_unified-search/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 6018
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Unified Search

> **知识ID**: W14-0A6D60  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_unified-search/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: unified-search
description: Unified search suite - Single interface for multiple search engines including Tavily, Brave, Exa, and Firecrawl. Replaces brave-search, tavily, firecrawl-search, and openclaw-tavily-search with intelligent routing, multi-engine aggregation, and local caching. Use for: web search, news search, academic research, company search, patent search, content extraction.
triggers: ["search", "web search", "google", "搜索", "查找", "查询", "research", "news", "academic"]
---

# Unified Search

**统一搜索套件** - 一个接口，多引擎支持，智能路由，完全自建替代方案。

> 🎯 替代: brave-search + tavily + firecrawl-search + openclaw-tavily-search

---

## 核心能力

1. **智能路由** - 根据查询类型自动选择最佳搜索引擎
2. **多引擎聚合** - 并行查询多个引擎，结果去重排序
3. **本地缓存** - DuckDB缓存，相同查询24小时内直接返回，降本80%
4. **统一接口** - 不管什么引擎，调用方式完全一致
5. **完全自建** - 本地管理API keys，无外部Skill依赖

---

## 整合的搜索引擎

| 引擎 | 优势 | 适用场景 | 状态 |
|------|------|----------|------|
| **Tavily** | AI优化结果 | 通用搜索、研究查询 | ✅ 已集成 |
| **Brave** | 速度快 | 实时新闻、快速查询 | ✅ 已集成 |
| **Exa** | 语义搜索 | 学术、技术概念 | ✅ 已集成 |
| **Firecrawl** | 深度爬取 | 需要完整网页内容 | ✅ 已集成 |
| **Kimi Search** | 中文优化 | 中文内容搜索 | ✅ 已集成 |

---

## 快速开始

### CLI使用

```bash
# 基础搜索 (自动选择引擎)
ussearch "硬科技投资趋势 2024"

# 指定搜索类型
ussearch "AI初创企业融资" --type news
ussearch "合伙人选择决策模型" --type academic
ussearch "人工智能芯片" --type patent

# 指定引擎
ussearch "量子计算" --engine tavily
ussearch "最新新闻" --engine brave
ussearch "深度内容" --engine firecrawl

# 多引擎聚合
ussearch "黎红雷 儒商" --engines tavily,brave,exa --aggregate

# 高级选项
ussearch "满意解决策理论" \
  --type academic \
  --max-results 20 \
  --include-answer \
  --cache-ttl 86400
```

### Python API

```python
from unified_search import UnifiedSearch

search = UnifiedSearch()

# 自动路由搜索
results = search.query("硬科技投资趋势 2024")

# 指定类型搜索
news = search.query("AI初创企业融资", search_type="news")
papers = search.query("合伙人选择决策模型", search_type="academic")

# 多引擎并行
results = search.query(
    "黎红雷 儒商",
    engines=["tavily", "brave", "exa"],
    aggregate=True
)

# 高级搜索
results = search.query(
    query="满意解决策理论",
    search_type="academic",
    max_results=20,
    include_answer=True,
    cache_ttl=86400
)
```

---

## 智能路由规则

```python
ROUTING_RULES = {
    "news": {
        "engines": ["brave", "tavily"],
        "reason": "新闻优先Brave（速度快）"
    },
    "academic": {
        "engines": ["exa", "tavily"],
        "reason": "学术优先Exa（语义搜索强）"
    },
    "patent": {
        "engines": ["tavily"],
        "reason": "专利搜索用Tavily"
    },
    "company": {
        "engines": ["brave", "tavily"],
        "reason": "公司信息综合搜索"
    },
    "general": {
        "engines": ["tavily", "brave", "exa"],
        "reason": "默认多引擎聚合"
    },
    "deep_content": {
        "engines": ["firecrawl"],
        "reason": "需要完整网页内容"
    }
}
```

---

## 缓存机制

**目标**: 降本80%

```sql
-- 缓存表结构
CREATE TABLE search_cache (
    id VARCHAR PRIMARY KEY,           -- query_hash
    query VARCHAR NOT NULL,
    query_type VARCHAR,
    engines_used JSON,
    results JSON,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 1
);

-- 自动清理过期缓存
DELETE FROM search_cache WHERE expires_at < CURRENT_TIMESTAMP;
```

**缓存命中策略:**
- 精确匹配: 相同查询直接返回
- 语义匹配: 相似查询(余弦相似度>0.9)复用结果
- 时间衰减: 新闻类缓存1小时，学术类缓存7天

---

## 配置文件

`.env`:
```bash
# API Keys（至少配置一个即可工作）
TAVILY_API_KEY=tvly-xxxxx
BRAVE_API_KEY=brave-xxxxx
EXA_API_KEY=exa-xxxxx
FIRECRAWL_API_KEY=fc-xxxxx

# 默认设置
DEFAULT_ENGINE=tavily
DEFAULT_CACHE_EXPIRY=86400
MAX_RESULTS_PER_ENGINE=10

# 缓存设置
CACHE_ENABLED=true
CACHE_TYPE=duckdb  # duckdb | redis | memory
DUCKDB_PATH=./search_cache.duckdb

# 路由设置
AUTO_ROUTING=true
FALLBACK_ENGINE=tavily
```

---

## 输出格式

```json
{
  "query": "硬科技投资趋势",
  "type": "news",
  "engines_used": ["tavily", "brave"],
  "total_results": 15,
  "results": [
    {
      "title": "2024年硬科技投资报告",
      "url": "https://example.com/article",
      "content": "硬科技投资在2024年呈现...",
      "source": "tavily",
      "score": 0.95,
      "published_date": "2024-03-15"
    }
  ],
  "ai_summary": "根据搜索结果，硬科技投资趋势显示...",
  "from_cache": false,
  "search_time_ms": 1200,
  "cost_estimate": "$0.002"
}
```

---

## 与原外部Skill的完全替代

| 原外部Skill | 原使用方式 | 新统一方式 | 替代状态 |
|------------|-----------|-----------|---------|
| `brave-search` | `braveSearch("query")` | `ussearch "query" --engine brave` | ✅ 完全替代 |
| `tavily` | `tavily_search "query"` | `ussearch "query" --engine tavily` | ✅ 完全替代 |
| `firecrawl-search` | `firecrawl_search "query"` | `ussearch "query" --engine firecrawl` | ✅ 完全替代 |
| `openclaw-tavily-search` | `openclaw_tavily "query"` | `ussearch "query" --engine tavily` | ✅ 完全替代 |

**迁移示例:**

```bash
# 原 brave-search
brave-search "最新科技新闻"

# 新 unified-search
ussearch "最新科技新闻" --engine brave

# 原 tavily
tavily_search "AI发展趋势"

# 新 unified-search
ussearch "AI发展趋势" --engine tavily

# 原 firecrawl-search
firecrawl_search "深度技术文章"

# 新 unified-search
ussearch "深度技术文章" --engine firecrawl
```

---

## 高级功能

### 内容提取

```bash
# 提取网页全文
ussearch extract "https://example.com/article" --full-content

# 提取并转换为Markdown
ussearch extract "https://example.com/article" --format markdown
```

### 批量搜索

```bash
# 批量查询
ussearch batch queries.txt --output results.json

# 并行搜索多个查询
ussearch parallel "query1" "query2" "query3" --aggregate
```

### 搜索分析

```bash
# 查看缓存统计
ussearch stats cache

# 查看成本分析
ussearch stats cost --days 30

# 查看搜索历史
ussearch history --limit 100
```

---

## 依赖安装

```bash
# 基础依赖
pip install requests duckdb pydantic

# 完整依赖
pip install -r requirements.txt
```

---

## 成本对比

| 方案 | 月成本 | 说明 |
|------|--------|------|
| 单独使用4个外部搜索Skill | $20-40 | 各自独立调用，无缓存共享 |
| **unified-search（无缓存）** | $15-30 | 智能路由减少重复查询 |
| **unified-search（有缓存）** | **$5-10** | 缓存命中率60%+，大幅降本 |

**成本优化策略:**
1. 启用本地缓存: 减少60% API调用
2. 智能路由: 选择最经济的引擎
3. 批量查询: 合并请求减少开销

---

## 故障转移

当某个引擎不可用时，自动切换到备用引擎:

```python
FAILOVER_CHAIN = {
    "tavily": ["brave", "exa"],
    "brave": ["tavily", "exa"],
    "exa": ["tavily", "brave"],
    "firecrawl": ["tavily"]
}
```

---

**状态**: ✅ 生产就绪
**自建替代计数**: +4 (brave-search, tavily, firecrawl-search, openclaw-tavily-search)
