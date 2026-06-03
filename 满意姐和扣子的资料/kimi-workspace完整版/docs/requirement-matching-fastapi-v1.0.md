---
kia-version: 1.0
tier: T0
title: Partner Matching Engine - FastAPI服务层需求
source: docs/requirement-matching-fastapi-v1.0.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

> 生成时间: 2026-04-03 19:40+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Partner Matching Engine - FastAPI服务层需求

> 需求版本: v1.0  
> 提出方: 满意解研究所 / Egbertie  
> 基础: 已有核心算法实现 (680行代码，16测试通过)  
> 目标: 添加HTTP API服务层，提升可用性  

---

## 背景

合伙人匹配引擎核心算法已完成实现:
- ✅ SatisficingMatcher - 满意解匹配
- ✅ ComplementarityScorer - 互补性评估
- ✅ ConfucianEthicsEvaluator - 儒商五维评估
- ✅ ProspectTheoryScorer - 前景理论风险
- ✅ ExplanationGenerator - 可解释性生成

**缺失**: HTTP API服务层，目前仅有CLI接口。

**核心代码路径**: `skills/partner-matching-engine/scripts/partner_matching.py`

---

## 需求范围

基于已有核心算法，构建完整的FastAPI服务层。

### 1. FastAPI服务入口

**文件**: `api/main.py`

**功能**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Partner Matching Engine API",
    description="基于满意解理论的合伙人匹配决策引擎",
    version="1.0.0"
)

# 启动时加载匹配器
matcher = SatisficingMatcher()
explainer = ExplanationGenerator()
store = MatchingResultStore()
```

---

### 2. RESTful API端点

#### 2.1 执行匹配
```
POST /api/v1/match
```

**Request**:
```json
{
  "founder": {
    "name": "张创始人",
    "industry": "AI芯片",
    "stage": "pre_a",
    "capability_matrix": {
      "technical_depth": 9,
      "business_acumen": 3,
      "fundraising": 2
    },
    "value_dimensions": {
      "ren": 8, "yi": 7, "li": 6, "zhi": 8, "xin": 9
    },
    "partner_requirements": {
      "must_have_capabilities": ["fundraising", "business_acumen"],
      "deal_breakers": ["诚信问题", "竞业限制"]
    }
  },
  "candidates": [
    {
      "name": "王CFO",
      "current_role": "前上市公司CFO",
      "capability_matrix": {...},
      "value_dimensions": {...},
      "risk_indicators": {...}
    }
  ],
  "thresholds": {
    "complementarity": 70,
    "values_alignment": 75,
    "risk_compatibility": 70,
    "growth_potential": 60
  }
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "candidate_id": "uuid",
        "candidate_name": "王CFO",
        "overall_score": 72.5,
        "dimension_scores": {
          "complementarity": 50,
          "values_alignment": 90,
          "risk_compatibility": 85,
          "growth_potential": 65
        },
        "deal_breakers": [],
        "satisficing_met": false,
        "ranking": 1,
        "explanation": {
          "executive_summary": "...",
          "analogy": "...",
          "why_selected": "...",
          "key_strengths": [...],
          "risk_factors": [...]
        }
      }
    ],
    "best_match": {...},
    "satisficing_candidates": [...],
    "thresholds_used": {...}
  },
  "request_id": "req_uuid",
  "processing_time_ms": 150
}
```

#### 2.2 单候选人评估
```
POST /api/v1/evaluate
```

**Request**: 单个候选人评估  
**Response**: 详细评分和解释

#### 2.3 获取解释
```
GET /api/v1/explain/{result_id}
```

**Response**: 完整解释文本

#### 2.4 健康检查
```
GET /api/v1/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "matcher": "ok",
    "database": "ok"
  }
}
```

#### 2.5 获取阈值建议
```
POST /api/v1/thresholds/suggest
```

基于历史案例推荐合适的满意解阈值。

---

### 3. Pydantic模型

**文件**: `api/models.py`

需定义:
- `FounderProfileRequest`
- `CandidateProfileRequest`
- `MatchingRequest`
- `MatchingResponse`
- `DimensionScoresResponse`
- `ExplanationResponse`
- `HealthResponse`

**要求**:
- 完整的字段验证
- 示例数据 (Field(..., example="..."))
- 字段描述文档

---

### 4. Prompt模板优化

**文件**: `api/prompts.py`

优化ExplanationGenerator的Prompt模板，提供API友好的版本:

```python
EXPLANATION_PROMPTS = {
    "executive_summary": "...",
    "analogy_generation": "...",
    "confucian_analysis": "...",
    "risk_assessment": "..."
}
```

**要求**:
- 结构化JSON输出
- 支持中英文
- 可配置风格 (正式/通俗)

---

### 5. 中间件和错误处理

**要求**:
- 请求日志记录
- 异常捕获和统一错误响应
- 限流 (Rate Limiting)
- CORS配置
- 请求ID追踪

**错误响应格式**:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid capability matrix",
    "details": {...}
  },
  "request_id": "req_uuid"
}
```

---

### 6. Docker部署配置

**文件**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/ ./scripts/
COPY api/ ./api/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**文件**: `docker-compose.yml`

```yaml
version: '3.8'
services:
  partner-matching-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/matching.db
```

---

### 7. API文档

**文件**: `README.md`

包含:
- 快速开始指南
- API端点列表
- 请求/响应示例
- 错误代码说明
- 本地运行指南
- Docker部署指南

---

## 依赖要求

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
```

**注意**: 已有核心算法依赖无需重复

---

## 集成现有代码

**核心类引用**:
```python
import sys
sys.path.insert(0, '../scripts')

from partner_matching import (
    SatisficingMatcher,
    ExplanationGenerator,
    MatchingResultStore,
    FounderProfile,
    CandidateProfile,
    SatisficingThresholds
)
```

**数据转换**:
```python
def to_founder_profile(request: FounderProfileRequest) -> FounderProfile:
    """转换Pydantic模型到内部模型"""
    return FounderProfile(
        id=str(uuid.uuid4()),
        name=request.name,
        industry=request.industry,
        ...
    )
```

---

## 交付物

| # | 交付物 | 路径 | 说明 |
|---|--------|------|------|
| 1 | FastAPI主应用 | `api/main.py` | 服务入口 |
| 2 | Pydantic模型 | `api/models.py` | 请求/响应模型 |
| 3 | Prompt模板 | `api/prompts.py` | 优化Prompt |
| 4 | Dockerfile | `Dockerfile` | 容器化配置 |
| 5 | Docker Compose | `docker-compose.yml` | 编排配置 |
| 6 | API文档 | `README.md` | 使用指南 |
| 7 | 依赖文件 | `requirements-api.txt` | API层依赖 |
| 8 | 集成测试 | `tests/test_api.py` | API端点测试 |

---

## 验收标准

1. **功能**: 所有API端点可正常调用
2. **文档**: Swagger UI自动生成 (`/docs`)
3. **测试**: API测试覆盖率>=80%
4. **性能**: 单次匹配请求 < 500ms (100候选人)
5. **部署**: `docker-compose up` 一键启动

---

## 测试用例

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 执行匹配
curl -X POST http://localhost:8000/api/v1/match \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

---

**期望交付时间**: 收到需求后 5-7 个工作日  
**紧急程度**: P0 (提升可用性)
