"""
AI自主搜寻模块 - 高风险功能
带实时议会审计和硬否决机制
"""

from typing import Dict, Optional
from datetime import datetime

from council.parliament import AntagonisticParliament
from base.crystal_models import TemporalCrystal
from memory.temporal_store import TemporalCrystalStore


class RestrictedAutoSearch:
    """
    受限自动搜寻
    """

    TRUSTED_SOURCES = {
        "36kr.com": {"totem": "simon", "confidence": 0.8},
        "itjuzi.com": {"totem": "simon", "confidence": 0.8},
        "arxiv.org": {"totem": "confucius", "confidence": 0.9},
        "github.com": {"totem": "huineng", "confidence": 0.85},
    }

    BLACKLIST_PATTERNS = [
        "password", "personal data", "medical record", "private"
    ]

    def __init__(self):
        self.parliament = AntagonisticParliament()
        self.daily_search_budget = 10

    def search_trigger(self,
                       trigger_reason: str,
                       suggested_query: str,
                       proposer: str = "system") -> Optional[Dict]:
        """搜寻触发器 - 必须提供充分理由"""
        if self.daily_search_budget <= 0:
            return None

        # 黑名单检查
        if any(bp in suggested_query.lower() for bp in self.BLACKLIST_PATTERNS):
            return None

        audit_proposal = {
            "id": f"SEARCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": f"自主搜寻: {suggested_query[:30]}",
            "description": f"原因: {trigger_reason}. 查询: {suggested_query}",
            "action": "external_api_call",
            "risk_level": "high",
            "estimated_cost": 3,
            "source_reliability": self._check_source_reliability(suggested_query)
        }

        verdict = self.parliament.deliberate(audit_proposal, {
            "current_budget": self.daily_search_budget,
            "system_load": "normal"
        })

        if verdict["status"] in ["hard_veto", "rejected"]:
            return None

        self.daily_search_budget -= 1

        # 返回带低置信度标记的结果（实际搜索URL提取等在此扩展）
        return {
            "query": suggested_query,
            "audit_trail": verdict,
            "confidence": 0.5,
            "watermark": "🔴 AI自主搜寻 - 待人工验证"
        }

    def _check_source_reliability(self, query: str) -> Dict:
        for domain, meta in self.TRUSTED_SOURCES.items():
            if domain in query:
                return meta
        return {"totem": "guanyin", "confidence": 0.4, "warning": "非白名单源"}
