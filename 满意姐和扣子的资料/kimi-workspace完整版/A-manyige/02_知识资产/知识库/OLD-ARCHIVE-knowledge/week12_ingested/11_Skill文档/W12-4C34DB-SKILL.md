---
# 知识元数据 (5标准化)
knowledge_id: W12-4C34DB
title: SKILL
category: 11_Skill文档
source: skills/.archive_multi-search-rotator/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1826
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W12-4C34DB  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_multi-search-rotator/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: multi-search-rotator
version: 1.0.0
description: |
  多搜索引擎轮询机制 - 智能轮换17个搜索引擎避免被封禁
  核心价值：自动负载均衡、故障转移、结果聚合
  适用：大规模搜索、爬虫任务、信息收集
author: OpenClaw
tags:
  - search
  - rotation
  - crawler
  - automation
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["curl", "python3"]
  - cron: true
---

# 多搜索引擎轮询机制 Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 搜索引擎全覆盖

| 区域 | 引擎 | 状态 | 优先级 |
|------|------|------|--------|
| 国内 | Baidu | ✅ | 1 |
| 国内 | Bing CN | ✅ | 2 |
| 国内 | 360 | ✅ | 3 |
| 国内 | Sogou | ✅ | 4 |
| 国内 | WeChat | ✅ | 5 |
| 国际 | Google | ✅ | 1 |
| 国际 | DuckDuckGo | ✅ | 2 |
| 国际 | Brave | ✅ | 3 |
| 国际 | Startpage | ✅ | 4 |

### 1.2 搜索场景覆盖

| 场景 | 推荐引擎 | 策略 |
|------|----------|------|
| 国内内容 | Baidu/WeChat | 优先国内 |
| 国际内容 | Google/Brave | 优先国际 |
| 隐私搜索 | DuckDuckGo | 专用通道 |
| 学术搜索 | Google Scholar | 特殊处理 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 轮询流程闭环

```
搜索请求 → 引擎选择 → 请求分发 → 结果获取 → 质量评估 → 故障标记
```

### 2.2 故障转移机制

| 故障类型 | 检测方式 | 转移策略 |
|----------|----------|----------|
| 超时 | 5秒无响应 | 切换下一引擎 |
| 封禁 | 状态码403 | 标记冷却15分钟 |
| 空结果 | 结果数为0 | 重试其他引擎 |

---

## 标准3: 迭代机制（Iterative）

### 3.1 PDCA闭环

| 阶段 | 动作 | 频率 |
|------|------|------|
| **Plan** | 生成搜索计划 | 按需 |
| **Do** | 执行轮询搜索 | 实时 |
| **Check** | 分析成功率 | 每小时 |
| **Act** | 调整引擎权重 | 每天 |

---

## 标准4: Skill化（Skill-ified）

### 4.1 标准Skill结构

```
skills/multi-search-rotator/
├── SKILL.md
├── _meta.json
├── config/
│   └── engines.yaml      # 引擎配置
├── scripts/
│   ├── search.py         # 主搜索脚本
│   └── health_check.py   # 健康检查
└── cron.d/
    └── health-check.cron # 定时健康检查
```

### 4.2 可调用接口

```bash
# 搜索
./scripts/search.py "关键词" --region cn

# 健康检查
./scripts/health_check.py
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 定时任务

```bash
# 引擎健康检查（每15分钟）
*/15 * * * * ./scripts/health_check.py
```

---

*版本: v1.0.0 | 5标准全部满足*
