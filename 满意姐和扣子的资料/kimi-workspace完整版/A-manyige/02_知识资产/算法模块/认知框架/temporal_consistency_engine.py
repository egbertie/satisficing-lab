#!/usr/bin/env python3
"""
temporal_consistency_engine.py - 时间一致性引擎（记忆V3.0核心）
来源: 系统深度优化方案.docx - 第十九轮
功能: 时间锚定、记忆公证、时间线分叉检测
"""
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime
import sys


class TemporalConsistencyEngine:
    """
    时间一致性引擎：防止跨时间幻觉
    1. 时间锚点（Timeline Anchors）
    2. 记忆公证（Memory Notarization）
    3. 时间线分叉检测（Branch Detection）
    """

    def __init__(self):
        self.timeline = []
        self.pending_events = []
        self.branch_points = []

    def create_temporal_anchor(self, event_data: Dict, anchor_type: str = "FACT") -> Dict:
        timestamp = datetime.now().isoformat()
        event_hash = self._hash_event(event_data, timestamp)
        anchor = {
            "timestamp": timestamp,
            "type": anchor_type,
            "data_hash": event_hash,
            "data_preview": str(event_data)[:100],
            "previous_anchor": self.timeline[-1]["data_hash"] if self.timeline else "GENESIS",
            "confirmation_count": 1,
        }
        self.pending_events.append(anchor)
        return anchor

    def _hash_event(self, data: Dict, timestamp: str) -> str:
        content = json.dumps(data, sort_keys=True) + timestamp
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def notarize_pending_events(self, cross_reference_sources: List[Dict]) -> Dict:
        notarized = []
        rejected = []
        for event in self.pending_events:
            confirmations = self._cross_verify(event, cross_reference_sources)
            if confirmations >= 2:
                event["confirmation_count"] = confirmations
                event["notarization_time"] = datetime.now().isoformat()
                self.timeline.append(event)
                notarized.append(event)
            else:
                rejected.append(
                    {
                        "event": event,
                        "reason": f"确认数不足({confirmations}<2)，可能是幻觉",
                        "suggestion": "标记为待验证，不进入主时间线",
                    }
                )
        self.pending_events = []
        return {
            "notarized_count": len(notarized),
            "rejected_count": len(rejected),
            "rejected_events": rejected,
            "timeline_length": len(self.timeline),
        }

    def _cross_verify(self, event: Dict, sources: List[Dict]) -> int:
        count = 1
        event_content = event["data_preview"]
        for source in sources:
            if self._content_similarity(event_content, str(source)) > 0.8:
                count += 1
        return count

    def _content_similarity(self, c1: str, c2: str) -> float:
        s1 = set(c1.lower().split())
        s2 = set(c2.lower().split())
        if not s1 or not s2:
            return 0.0
        return len(s1 & s2) / len(s1 | s2)

    def detect_temporal_paradox(self, new_claim: Dict) -> Optional[Dict]:
        paradoxes = []
        for anchor in self.timeline:
            if self._is_contradictory(new_claim, anchor):
                paradoxes.append(
                    {
                        "type": "TEMPORAL_PARADOX",
                        "new_claim_time": new_claim.get("timestamp"),
                        "conflicting_anchor_time": anchor["timestamp"],
                        "conflicting_anchor_hash": anchor["data_hash"],
                        "resolution": "REJECT_NEW"
                        if anchor["type"] == "FACT"
                        else "MERGE_REQUIRED",
                    }
                )
        return paradoxes[0] if paradoxes else None

    def _is_contradictory(self, claim: Dict, anchor: Dict) -> bool:
        claim_str = json.dumps(claim, ensure_ascii=False)
        anchor_str = anchor.get("data_preview", "")
        negations = [("投资", "不投资"), ("支持", "反对"), ("增加", "减少"), ("进入", "退出")]
        for pos, neg in negations:
            if pos in claim_str and neg in anchor_str:
                return True
            if neg in claim_str and pos in anchor_str:
                return True
        return False

    def generate_temporal_attestation(self, query_time: datetime) -> Dict:
        relevant_anchors = [
            a for a in self.timeline if a["timestamp"] <= query_time.isoformat()
        ]
        combined_hash = ""
        for anchor in relevant_anchors:
            combined_hash = hashlib.sha256(
                (combined_hash + anchor["data_hash"]).encode()
            ).hexdigest()[:16]
        return {
            "query_time": query_time.isoformat(),
            "attested_events_count": len(relevant_anchors),
            "temporal_root_hash": combined_hash,
            "verification": f"该状态由{len(relevant_anchors)}个公证事件组成，最终哈希{combined_hash}",
        }


if __name__ == "__main__":
    tce = TemporalConsistencyEngine()

    event1 = {"decision": "投资半导体", "confidence": 0.8}
    anchor1 = tce.create_temporal_anchor(event1, "DECISION")
    print(f"✓ 创建锚点: {anchor1['timestamp']} 哈希{anchor1['data_hash'][:8]}...")

    sources = [{"decision": "投资半导体", "confidence": 0.8}, {"other": "data"}]
    result = tce.notarize_pending_events(sources)
    assert result["notarized_count"] == 1, "应成功公证1个事件"
    print(f"✓ 事件公证: {result['notarized_count']}通过, {result['rejected_count']}拒绝")

    contradictory_claim = {"decision": "不投资半导体", "confidence": 0.9}
    paradox = tce.detect_temporal_paradox(contradictory_claim)
    assert paradox is not None, "应检测到矛盾"
    print(f"✓ 悖论检测: 发现{paradox['type']}，建议{paradox['resolution']}")

    attestation = tce.generate_temporal_attestation(datetime.now())
    assert "temporal_root_hash" in attestation, "应生成根哈希"
    print(f"✓ 时间证明: 包含{attestation['attested_events_count']}个事件，根哈希{attestation['temporal_root_hash']}")

    print("\n✓ 时间一致性引擎验证通过")
    sys.exit(0)
