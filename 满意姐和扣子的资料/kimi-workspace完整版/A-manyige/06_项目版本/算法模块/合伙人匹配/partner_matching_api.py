#!/usr/bin/env python3
"""
partner_matching_api.py
合伙人匹配 FastAPI 服务网关 V1.0

部署方式:
  直接运行: uvicorn partner_matching_api:app --host 0.0.0.0 --port 8000 --reload
  后台运行: nohup uvicorn partner_matching_api:app --host 0.0.0.0 --port 8000 &

约束:
- 不引入 Docker，直接在现有 Linux 主机运行
- 使用 SQLite 做本地持久化
- 简单 API Key 认证
"""

import os
import sys
import json
import time
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

sys.path.insert(0, "/root/.openclaw/workspace")
from sku_a_assessment_orchestrator import SkuAAssessmentOrchestrator
from sri_asset_flywheel import ManagementIndicators, EnterpriseAssetFlywheel
import partner_matching_db as db

# 简单 API Key 配置（读取环境变量，默认开发密钥）
API_KEY = os.environ.get("PARTNER_MATCHING_API_KEY", "dev-sri-key-2026")

app = FastAPI(
    title="满意解研究所 - 合伙人匹配 API",
    description="SKU-A/B/C 合伙人匹配评估服务层",
    version="1.0.0",
)

# 请求/响应模型

class SkuARequest(BaseModel):
    company_name: str = Field(..., description="企业名称")
    founded_months: int = Field(..., ge=0, description="成立月数")
    tech_founder_stake: float = Field(0.4, ge=0.0, le=1.0, description="技术创始人持股比例")
    has_veto: bool = Field(False, description="是否有技术路线一票否决权")
    resource_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    has_exit_agreement: bool = Field(False)
    has_stop_loss: bool = Field(False)
    has_stage_vesting: bool = Field(False)
    vesting_stages: List[str] = Field(default_factory=list)
    tech_route_disputes_monthly: float = Field(0.0, ge=0.0)
    communication_frequency_weekly: float = Field(3.0, ge=0.0)
    equity_change_count: int = Field(0, ge=0)
    funding_deviation_rate: float = Field(0.0, ge=0.0)
    mentor_involved: bool = Field(False)
    stage: str = Field("种子期", description="创业阶段")
    actions_done: List[str] = Field(default_factory=lambda: ["能力评估"])
    pattern_flags: Dict[str, bool] = Field(
        default_factory=lambda: {
            "has_tech_biz_complement": True,
            "value_aligned": True,
            "shared_stress_test": False,
            "dynamic_equity": True,
            "transparent_comm": True,
            "equity_imbalanced": False,
            "capability_overlap": False,
            "founder_dependent": False,
        }
    )


class AssessmentResponse(BaseModel):
    assessment_id: str
    company_name: str
    sku_type: str
    overall_score: int
    overall_risk: str
    dimensions: List[Dict[str, Any]]
    markdown_report_path: str


class AssessmentDetail(BaseModel):
    assessment_id: str
    sku_type: str
    company_name: str
    created_at: str
    overall_risk: Optional[str]
    overall_score: Optional[int]
    markdown_report_path: Optional[str]
    dimensions: List[Dict[str, Any]]
    raw_json: Dict[str, Any]


# 认证中间件（简单版）
def _verify_api_key(x_api_key: Optional[str]) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round(time.time() - start, 3)
    # 结构化日志打印
    print(json.dumps({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": duration * 1000,
    }, ensure_ascii=False))
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "partner-matching-api", "version": "1.0.0"}


@app.post("/v1/assessments/sku-a", response_model=AssessmentResponse)
async def create_sku_a_assessment(
    payload: SkuARequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    _verify_api_key(x_api_key)
    try:
        start = time.time()
        orch = SkuAAssessmentOrchestrator()
        duration_seconds = time.time() - start
        result = orch.run(payload.model_dump(), duration_seconds=duration_seconds)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.get("/v1/assessments/{assessment_id}", response_model=AssessmentDetail)
async def get_assessment(
    assessment_id: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    _verify_api_key(x_api_key)
    row = db.get_assessment(assessment_id)
    if not row:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return row


@app.get("/v1/assessments")
async def list_assessments(
    limit: int = 20,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    _verify_api_key(x_api_key)
    rows = db.list_recent_assessments(limit=limit)
    return {"items": rows, "count": len(rows)}


@app.get("/v1/assets/status")
async def get_assets_status(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    _verify_api_key(x_api_key)
    fw = EnterpriseAssetFlywheel()
    return fw.export_dashboard()


@app.get("/v1/metrics/dashboard")
async def get_metrics_dashboard(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    _verify_api_key(x_api_key)
    mi = ManagementIndicators()
    return mi.dashboard()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
