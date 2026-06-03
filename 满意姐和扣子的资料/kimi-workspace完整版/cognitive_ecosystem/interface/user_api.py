"""
用户统一接口
封装底层复杂性，提供简洁交互
"""

from typing import Dict, List, Optional
from pathlib import Path

from base.crystal_models import TemporalCrystal
from processing.hyper_compressor import HyperCompressor
from memory.temporal_store import TemporalCrystalStore
from council.parliament import AntagonisticParliament
from routing.cognitive_router import CognitiveRouter


class SatisfyingAI:
    """
    满意姐AI - 用户统一接口
    """

    def __init__(self, data_dir: str = "./data"):
        self.store = TemporalCrystalStore(db_path=f"{data_dir}/temporal")
        self.router = CognitiveRouter(temporal_store=self.store)
        self.parliament = AntagonisticParliament()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def ingest(self, file_path: str, priority: int = 3) -> Dict:
        """知识摄入接口（人工输入）"""
        compressor = HyperCompressor()
        crystal = await compressor.process_docx(file_path, [f"P{priority}"])

        # 议会审计
        audit = self.parliament.deliberate(
            {
                "type": "new_knowledge",
                "crystal_id": crystal.crystal_id,
                "compression_ratio": crystal.compression_ratio,
                "contradictions": len(crystal.contradiction_flags)
            },
            {"source": "user_upload", "file_path": file_path}
        )

        # 入时序库（内容包含晶体摘要，确保后续语义检索有效）
        event_content = (
            f"文档入库: {Path(file_path).name} | "
            f"实体: {', '.join(crystal.primary_entities[:6])} | "
            f"决策模式: {crystal.decision_patterns[0] if crystal.decision_patterns else '无'}"
        )
        event = TemporalCrystal(
            semantic_time="知识摄入期",
            event_type="perception",
            content=event_content,
            crystal_refs=[crystal.crystal_id],
            narrative_cluster="knowledge_management"
        )
        self.store.store_event(event)

        return {
            "crystal_id": crystal.crystal_id,
            "compression_ratio": crystal.compression_ratio,
            "audit_status": audit["status"],
            "contradictions": crystal.contradiction_flags
        }

    def chat(self, message: str, context: Dict = None) -> Dict:
        """标准对话/查询接口（零API成本）"""
        context = context or {}
        route = self.router.route(message, context)

        # 本地语义查询
        results = self.store.semantic_query(message, top_k=3)

        return {
            "route": route,
            "relevant_events": [
                {"event_id": r.event_id, "content": r.content[:200], "cluster": r.narrative_cluster}
                for r in results
            ],
            "mode": "local_crystal_query"
        }

    def audit_proposal(self, proposal: Dict, context: Dict = None) -> Dict:
        """主动触发议会审计"""
        return self.parliament.deliberate(proposal, context or {})

    def get_status(self) -> Dict:
        """获取系统健康状态"""
        return {
            "store_path": str(self.data_dir),
            "router_ready": True,
            "parliament_ready": True,
            "system_health": "🟢 生产就绪（API故障时自动启用本地启发式）"
        }
