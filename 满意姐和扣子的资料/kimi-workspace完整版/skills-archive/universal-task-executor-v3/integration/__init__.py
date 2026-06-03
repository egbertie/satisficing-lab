"""
Universal Task Executor V3.0 - Knowledge Integration Module
知识集成模块

集成super-knowledge-ingest Skill到Task Executor，提供：
- KnowledgeBridge: 知识入库桥接器
- AutoIngestor: 自动入库触发器
- IndexManager: 索引管理器
"""

from .knowledge_bridge import (
    KnowledgeBridge,
    IngestConfig,
    IngestResult,
    BatchIngestResult,
    create_bridge,
    quick_ingest,
    quick_ingest_batch,
)

from .auto_ingest import (
    AutoIngestor,
    IngestPolicy,
    IngestRecord,
    IngestTrigger,
    IngestStrategy,
    create_auto_ingestor,
)

from .index_manager import (
    IndexManager,
    KnowledgeEntry,
    IndexVersion,
    TaskKnowledgeMapping,
    IndexVersionStatus,
    create_index_manager,
)

__all__ = [
    # Knowledge Bridge
    "KnowledgeBridge",
    "IngestConfig",
    "IngestResult",
    "BatchIngestResult",
    "create_bridge",
    "quick_ingest",
    "quick_ingest_batch",
    
    # Auto Ingest
    "AutoIngestor",
    "IngestPolicy",
    "IngestRecord",
    "IngestTrigger",
    "IngestStrategy",
    "create_auto_ingestor",
    
    # Index Manager
    "IndexManager",
    "KnowledgeEntry",
    "IndexVersion",
    "TaskKnowledgeMapping",
    "IndexVersionStatus",
    "create_index_manager",
]

__version__ = "3.0.0"
