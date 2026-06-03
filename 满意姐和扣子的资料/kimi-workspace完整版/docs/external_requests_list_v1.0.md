---
kia-version: 1.0
tier: T0
title: 外援需求清单 v1.0
source: docs/external_requests_list_v1.0.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

> 生成时间: 2026-04-03 19:37+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 外援需求清单 v1.0

> 整理时间: 2026-04-03_19:38  
> 当前P0进度: 5/6完成 (83%)  

---

## 已完成 (无需外援)

| # | 项目 | 状态 | 说明 |
|---|------|------|------|
| 1 | skill-usage-tracker | ✅ | 580行代码，13测试 |
| 2 | case-repository | ✅ | 620行代码，10测试+4案例 |
| 3 | theory-miner | ✅ | 680行代码，7测试 |
| 4 | partner-matching-engine核心 | ✅ | 680行代码，16测试，满意解算法完整 |
| 5 | totem-avatar框架 | ✅ | 640行代码，16测试，五图腾框架就绪 |

---

## 需要外援的3个需求

### 需求1: 项目情报采集系统 (P1)
**优先级**: P1 (重要但不阻塞)  
**复杂度**: 高  
**我能否自建**: 可以，但涉及数据源接入和爬虫，外援更专业

**需求范围**:
- 数据源接入: IT桔子、36氪、动脉网、企名片等
- 采集策略: 硬科技领域标签筛选、融资阶段筛选
- 数据清洗: 去重、字段标准化、格式转换
- AI摘要: 项目描述生成、关键信息提取
- 推送机制: 飞书机器人推送、关键词告警
- 存储: SQLite/JSON存储，支持历史查询

**已有参考**:
- 外援方案已提供初步架构 (`docs/requirement-intelligence-system-v1.0.md`)
- 需细化为可执行代码

**交付物**:
- 完整采集模块代码
- 数据源API对接示例
- AI摘要Prompt模板
- 飞书推送集成代码
- 测试用例

---

### 需求2: 图腾数字替身 - 四图腾详细方案
**优先级**: P0 (与现有框架配套)  
**复杂度**: 中  
**我能否自建**: 可以写基础版本，但深度不够

**当前状态**:
- ✅ 司马贺: 2980字详细System Prompt (外援提供)
- ⚠️ 刘禹锡: 只有基础prompt框架，缺详细知识库
- ⚠️ 观自在: 只有基础prompt框架，缺详细知识库
- ⚠️ 孔子: 只有基础prompt框架，缺详细知识库
- ⚠️ 慧能: 只有基础prompt框架，缺详细知识库

**需求范围**:
为剩余四图腾各提供:
- 详细System Prompt (2000-3000字)
- 经典语录知识库 (JSON格式)
- 决策模式定义
- 语气模板和句式结构
- 输出格式规范

**参考标准**:
- 司马贺prompt的质量和深度
- 需包含: 身份定义、核心认知框架、语言模式、决策流程、输出格式、知识调用指引

**交付物**:
- `liuyuxi_prompt.md` - 刘禹锡完整prompt
- `guanzizai_prompt.md` - 观自在完整prompt
- `confucius_prompt.md` - 孔子完整prompt
- `huineng_prompt.md` - 慧能完整prompt
- `totem_knowledge.json` - 四图腾知识库合并文件

---

### 需求3: Partner Matching Engine - FastAPI服务层
**优先级**: P0 (提升可用性)  
**复杂度**: 中  
**我能否自建**: 可以，但外援方案已有设计，直接采用更省时间

**当前状态**:
- ✅ 核心算法: SatisficingMatcher, ComplementarityScorer, ConfucianEthicsEvaluator, ExplanationGenerator
- ❌ API服务: 只有CLI，没有HTTP API
- ❌ Prompt模板: 需要补充

**需求范围**:
基于已有核心算法，补充:
- FastAPI服务入口 (`main.py`)
- RESTful API设计:
  - POST /match - 执行匹配
  - POST /evaluate - 单候选人评估
  - GET /explain/{result_id} - 获取解释
  - GET /health - 健康检查
- 请求/响应Pydantic模型
- API文档 (Swagger/OpenAPI)
- Prompt模板优化版本
- Docker部署配置

**已有参考**:
- 外援方案v2已提供完整FastAPI设计
- 我的实现: `skills/partner-matching-engine/scripts/partner_matching.py`

**交付物**:
- `api/main.py` - FastAPI服务
- `api/models.py` - Pydantic模型
- `api/prompts.py` - 优化Prompt模板
- `Dockerfile` - 容器化配置
- `README.md` - API使用文档

---

## 建议优先级

```
立即外求 (本周):
├── 需求2: 图腾四图腾详细方案 (阻塞完整体验)
└── 需求3: Partner Matching FastAPI (提升可用性)

可稍后外求 (下周):
└── 需求1: 项目情报采集系统 (P1，不阻塞主线)
```

---

## 我可以继续自建的部分

1. **project-intelligence基础版** - 简单的新闻聚合和存储
2. **图腾系统集成测试** - 验证五图腾切换和对话
3. **案例库与匹配引擎集成** - 打通已有模块

---

**结论**: 建议立即外求需求2和需求3，我可以同时自建project-intelligence基础版和集成测试。
