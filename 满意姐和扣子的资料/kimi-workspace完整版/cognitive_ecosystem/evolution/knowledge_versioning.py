"""
知识版本控制系统
认知晶体的Git式管理 + 自动进化
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

from base.crystal_models import CognitiveCrystal, TemporalCrystal
from memory.temporal_store import TemporalCrystalStore


class CrystalVersionControl:
    """晶体版本控制"""

    def __init__(self):
        self.versions: Dict[str, List[Dict]] = {}

    def commit_crystal(self,
                       crystal: CognitiveCrystal,
                       commit_msg: str,
                       parent_ids: List[str] = None) -> str:
        version_id = f"v{len(self.versions.get(crystal.crystal_id, [])) + 1}"
        version = {
            "version_id": version_id,
            "crystal": crystal.model_dump(),
            "commit_msg": commit_msg,
            "parent_ids": parent_ids or [],
            "timestamp": datetime.now().isoformat(),
            "hash": self._compute_hash(crystal)
        }
        if crystal.crystal_id not in self.versions:
            self.versions[crystal.crystal_id] = []
        self.versions[crystal.crystal_id].append(version)
        return version_id

    def _compute_hash(self, crystal: CognitiveCrystal) -> str:
        content = json.dumps(crystal.model_dump(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def diff_crystals(self, crystal_id: str, v1: str, v2: str) -> Dict:
        versions = self.versions.get(crystal_id, [])
        ver1 = next((v for v in versions if v["version_id"] == v1), None)
        ver2 = next((v for v in versions if v["version_id"] == v2), None)
        if not ver1 or not ver2:
            return {"error": "版本不存在"}
        c1 = CognitiveCrystal(**ver1["crystal"])
        c2 = CognitiveCrystal(**ver2["crystal"])
        entities_added = set(c2.primary_entities) - set(c1.primary_entities)
        entities_removed = set(c1.primary_entities) - set(c2.primary_entities)
        rels_added = [r for r in c2.key_relations if r not in c1.key_relations]
        return {
            "from": v1,
            "to": v2,
            "entities_added": list(entities_added),
            "entities_removed": list(entities_removed),
            "relations_added": rels_added,
            "confidence_change": c2.confidence_score - c1.confidence_score,
        }


class KnowledgeEvolutionEngine:
    """知识进化引擎"""

    def __init__(self, store: TemporalCrystalStore):
        self.store = store
        self.vcs = CrystalVersionControl()

    def evolution_cycle(self):
        """进化周期（每日00:00执行）"""
        expired = self._detect_expired_knowledge()
        contradictions = self._detect_contradiction_clusters()
        # 简单的记忆巩固
        for cluster in ["system_architecture", "partner_matching", "knowledge_management", "totem_system"]:
            self.store.consolidate_memory(cluster)

    def _detect_expired_knowledge(self) -> List[str]:
        return []

    def _detect_contradiction_clusters(self) -> List[Dict]:
        return []
