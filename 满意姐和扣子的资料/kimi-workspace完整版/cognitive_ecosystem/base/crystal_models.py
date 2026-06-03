"""
认知晶体与事件源数据模型
核心抽象：一切文档/记忆/决策都是时空中的晶体事件
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from enum import Enum
import hashlib


class CognitiveLevel(str, Enum):
    """认知压缩层级"""
    RAW = "raw"
    CHUNK = "chunk"
    ENTITY = "entity"
    RELATION = "relation"
    CRYSTAL = "crystal"


class TotemType(str, Enum):
    """五路图腾类型"""
    CONFUCIUS = "confucius"
    SIMON = "simon"
    GUANYIN = "guanyin"
    LIUYUXI = "liuyuxi"
    HUINENG = "huineng"


class CognitiveCrystal(BaseModel):
    """
    认知晶体：文档的最终蒸馏形态
    不可变，版本更新创建新实例
    """
    crystal_id: str = Field(
        default_factory=lambda: f"CRY-{datetime.now().strftime('%Y%m%d')}-{hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]}"
    )
    source_uris: List[str] = Field(default_factory=list, description="源文件路径列表")
    created_at: datetime = Field(default_factory=datetime.now)
    compression_ratio: float = Field(default=1.0, ge=0.0, le=1.0, description="压缩率")

    # 语义核心
    primary_entities: List[str] = Field(default_factory=list, description="核心实体")
    key_relations: List[Dict[str, Any]] = Field(default_factory=list, description="关键关系三元组")
    decision_patterns: List[str] = Field(default_factory=list, description="可执行决策模式")
    contradiction_flags: List[str] = Field(default_factory=list, description="与其他晶体的冲突标记")

    # 向量指纹（轻量引用，实际存储在向量DB）
    vector_fingerprint: Optional[str] = None
    knowledge_graph_anchor: Dict[str, Any] = Field(default_factory=dict)

    # 元数据
    totem_affinity: Dict[str, float] = Field(default_factory=dict, description="与各路图腾的相关性分数")
    activation_triggers: List[str] = Field(default_factory=list)
    ttl_days: int = Field(default=365, description="生存周期，到期需重新蒸馏")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    causal_watermark: str = Field(default="✅ 标准处理")
    reviewed_by: Optional[str] = None
    narrative_cluster: str = Field(default="general", description="所属叙事簇")

    def to_graph_nodes(self) -> List[Dict]:
        """转换为图谱节点格式"""
        nodes = [{"id": self.crystal_id, "type": "Crystal", "properties": self.model_dump()}]
        for entity in self.primary_entities:
            nodes.append({"id": entity, "type": "Entity", "properties": {}})
        return nodes

    def to_graph_edges(self) -> List[Dict]:
        """转换为图谱边格式"""
        edges = []
        for rel in self.key_relations:
            edges.append({
                "source": rel.get("subject"),
                "target": rel.get("object"),
                "relation": rel.get("predicate"),
                "source_crystal": self.crystal_id
            })
        return edges


class TemporalCrystal(BaseModel):
    """
    时间晶体：记忆的事件源模型
    支持因果链追踪与叙事重构
    """
    event_id: str = Field(
        default_factory=lambda: f"TMP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:4]}"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    semantic_time: str = Field(default="未分类", description="认知时间标签，如'合伙人危机期'")

    # 内容
    event_type: Literal["perception", "decision", "action", "reflection", "contradiction", "evolution", "archive", "parliament_deliberation", "pressure_escalation", "hard_veto"] = "perception"
    content: str = ""
    crystal_refs: List[str] = Field(default_factory=list, description="引用的认知晶体ID")
    skill_refs: List[str] = Field(default_factory=list, description="激活的Skill")

    # 因果链
    causal_parents: List[str] = Field(default_factory=list, description="父事件ID")
    causal_children: List[str] = Field(default_factory=list, description="子事件ID")
    narrative_cluster: str = Field(default="general", description="所属叙事簇")

    # 动态属性
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="记忆强度")
    access_count: int = Field(default=0)
    last_accessed: Optional[datetime] = None

    def reinforce(self, delta: float = 0.1):
        """提取时强化记忆（Hebbian Learning模拟）"""
        self.strength = min(1.0, self.strength + delta)
        self.access_count += 1
        self.last_accessed = datetime.now()

    def decay(self, days: int = 1):
        """自然衰减（Ebbinghaus遗忘曲线简化模型）"""
        decay_rate = 0.05 * days
        self.strength = max(0.1, self.strength - decay_rate)


class AntagonisticArgument(BaseModel):
    """对抗议会中的论证结构"""
    argument_id: str
    totem: str
    target_proposal: str
    attack_vector: str = Field(default="", description="攻击角度：伦理/可行性/风险/关系/创新")
    severity: Literal["info", "warning", "critical", "blocking"] = "info"
    evidence: Dict[str, Any] = Field(default_factory=dict)
    suggested_mitigation: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
