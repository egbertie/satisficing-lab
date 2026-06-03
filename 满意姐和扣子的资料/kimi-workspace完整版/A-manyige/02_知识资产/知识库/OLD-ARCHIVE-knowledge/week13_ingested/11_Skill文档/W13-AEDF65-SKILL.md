---
# 知识元数据 (5标准化)
knowledge_id: W13-AEDF65
title: Satisficing Web Fetcher
category: 11_Skill文档
source: skills/.archive_satisficing-web-fetcher/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 3256
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Satisficing Web Fetcher

> **知识ID**: W13-AEDF65  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_satisficing-web-fetcher/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: satisficing-web-fetcher
description: 满意解Web抓取器 - 安全、高效、受控的网页抓取技能。基于Scrapling最佳实践自建，集成反爬绕过、自适应解析、沙箱隔离和安全审计。零外部API成本，所有数据本地处理。
metadata:
  version: "1.0.0"
  author: "OpenClaw"
  license: "MIT"
  openclaw:
    emoji: "🕷️"
    requires:
      bins: ["python3"]
      python_packages: ["requests", "playwright"]
---

# Satisficing Web Fetcher

满意解Web抓取器 - 安全、高效、受控的网页抓取技能。

## 核心设计理念

基于**第一性原则**构建：
1. **本质需求**：增强信息获取能力，而非简单安装工具
2. **风险控制**：安全沙箱、审计日志、数据不出境
3. **成本控制**：零外部API费用
4. **满意解**：在功能、安全、成本间取得平衡

## 功能特性

### 1. 三级抓取策略
| 级别 | 模式 | 适用场景 | 资源消耗 |
|------|------|----------|----------|
| Level 1 | HTTP基础抓取 | 静态页面、API | 低 |
| Level 2 | Stealthy抓取 | 反爬页面、Cloudflare | 中 |
| Level 3 | 浏览器动态渲染 | 重度JS依赖页面 | 高 |

### 2. 自适应解析
- 智能元素追踪：页面结构变化后仍能定位元素
- 自动选择器生成：减少人工维护成本
- 相似元素查找：基于内容相似度自动匹配

### 3. 安全沙箱
- **内存限制**：浏览器进程2GB上限，超限自动终止
- **超时控制**：单次请求30秒，浏览器会话5分钟
- **域名白名单**：仅允许配置域名，默认拒绝所有
- **审计日志**：所有请求记录到本地日志文件

### 4. 内容安全
- 自动过滤敏感内容（身份证、手机号、银行卡）
- PII检测与脱敏
- 响应内容大小限制（最大10MB）

## 快速开始

### 基础抓取
```python
from fetcher import HTTPFetcher

fetcher = HTTPFetcher()
result = fetcher.fetch("https://example.com")
print(result.text)
```

### 反爬绕过
```python
from fetcher import StealthyFetcher

fetcher = StealthyFetcher(headless=True)
result = fetcher.fetch("https://protected-site.com")
print(result.css("h1::text").get())
```

### 自适应解析
```python
from fetcher import AdaptiveParser

parser = AdaptiveParser(result.html)
# 首次抓取，保存元素指纹
products = parser.css(".product", auto_save=True)

# 页面结构变化后，仍能定位
products = parser.css(".product", adaptive=True)
```

## CLI使用

```bash
# 基础抓取
python3 cli.py fetch "https://example.com"

# Stealthy模式
python3 cli.py fetch "https://protected-site.com" --mode stealthy

# 使用CSS选择器提取
python3 cli.py fetch "https://example.com" --css "h1::text"

# 查看审计日志
python3 cli.py audit
```

## 配置

### 域名白名单
编辑 `security/domain_whitelist.py`:
```python
ALLOWED_DOMAINS = [
    "example.com",
    "api.github.com",
    "*.wikipedia.org",
]
```

### 安全策略
编辑 `security/policy.yaml`:
```yaml
rate_limit: 1  # 每秒最大请求数
max_content_size: 10485760  # 10MB
enable_pii_filter: true
audit_retention_days: 30
```

## 安全红线

1. **禁止**：抓取登录后才能访问的内容
2. **禁止**：抓取个人隐私数据
3. **禁止**：高频/大规模抓取（rate limit: 1req/s）
4. **禁止**：自动绕过验证码
5. **必须**：所有请求记录审计日志
6. **必须**：浏览器进程沙箱隔离

## 架构

```
satisficing-web-fetcher/
├── fetcher.py              # 主模块
│   ├── HTTPFetcher         # 基础抓取
│   ├── StealthyFetcher     # 反爬绕过
│   └── AdaptiveParser      # 自适应解析
├── sandbox/                # 沙箱隔离
│   ├── browser_controller.py
│   ├── memory_limiter.py
│   └── timeout_guard.py
├── security/               # 安全控制
│   ├── audit_logger.py
│   ├── domain_whitelist.py
│   └── content_filter.py
├── cli.py                  # 命令行工具
└── examples/               # 使用示例
```

## 与现有工具对比

| 特性 | web_fetch | smart-web-fetch | satisficing-web-fetcher |
|------|-----------|-----------------|-------------------------|
| 基础HTTP | ✅ | ✅ | ✅ |
| 内容清洗 | ❌ | ✅ | ✅ |
| JS渲染 | ❌ | ❌ | ✅ |
| Cloudflare绕过 | ❌ | ❌ | ✅ |
| 自适应解析 | ❌ | ❌ | ✅ |
| 沙箱隔离 | ❌ | ❌ | ✅ |
| 审计日志 | ❌ | ❌ | ✅ |
| 外部成本 | 无 | 无 | 无 |

## 依赖安装

```bash
# 基础依赖
pip install requests playwright

# 安装浏览器
playwright install chromium
```

## 评估报告

详见 `ASSESSMENT_REPORT.md` - 包含3个Scrapling skill的综合评估、自建决策理由和详细技术对比。
