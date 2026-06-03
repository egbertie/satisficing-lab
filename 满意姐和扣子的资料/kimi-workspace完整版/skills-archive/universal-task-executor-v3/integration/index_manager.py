"""
Index Manager - 索引管理器
集成super-knowledge-ingest Skill到Universal Task Executor V3.0

职责：
1. 维护任务→知识库的索引
2. 支持快速检索
3. 支持版本管理
4. 与Checkpoint系统集成
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class IndexVersionStatus(Enum):
    """索引版本状态"""
    ACTIVE = "active"         # 当前活跃版本
    ARCHIVED = "archived"     # 已归档
    PENDING = "pending"       # 待处理
    CORRUPTED = "corrupted"   # 已损坏


@dataclass
class KnowledgeEntry:
    """知识库条目"""
    # 基础信息
    entry_id: str = field(default_factory=lambda: f"k_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]}")
    source_file: str = ""  # 源文件路径
    source_task_id: Optional[str] = None  # 来源任务ID
    
    # 元数据文件
    metadata_file: Optional[str] = None  # 元数据JSON文件路径
    
    # 内容摘要
    file_type: str = ""  # 文件类型
    title: Optional[str] = None
    description: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    
    # 时间戳
    ingested_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # 版本
    version: int = 1
    checksum: Optional[str] = None  # 文件校验和
    
    # 标签和分类
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None  # 分类
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "source_file": self.source_file,
            "source_task_id": self.source_task_id,
            "metadata_file": self.metadata_file,
            "file_type": self.file_type,
            "title": self.title,
            "description": self.description,
            "key_points": self.key_points,
            "ingested_at": self.ingested_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
            "checksum": self.checksum,
            "tags": self.tags,
            "category": self.category,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeEntry":
        return cls(
            entry_id=data.get("entry_id", ""),
            source_file=data.get("source_file", ""),
            source_task_id=data.get("source_task_id"),
            metadata_file=data.get("metadata_file"),
            file_type=data.get("file_type", ""),
            title=data.get("title"),
            description=data.get("description"),
            key_points=data.get("key_points", []),
            ingested_at=datetime.fromisoformat(data["ingested_at"]) if data.get("ingested_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            version=data.get("version", 1),
            checksum=data.get("checksum"),
            tags=data.get("tags", []),
            category=data.get("category"),
        )


@dataclass
class IndexVersion:
    """索引版本"""
    version_id: str = field(default_factory=lambda: f"v_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)
    status: IndexVersionStatus = IndexVersionStatus.ACTIVE
    
    # 统计
    entry_count: int = 0
    task_count: int = 0
    
    # 版本说明
    description: Optional[str] = None
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "entry_count": self.entry_count,
            "task_count": self.task_count,
            "description": self.description,
            "created_by": self.created_by,
        }


@dataclass
class TaskKnowledgeMapping:
    """任务知识映射"""
    task_id: str
    entry_ids: List[str] = field(default_factory=list)
    ingested_at: datetime = field(default_factory=datetime.now)
    total_entries: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "entry_ids": self.entry_ids,
            "ingested_at": self.ingested_at.isoformat(),
            "total_entries": len(self.entry_ids),
        }


class IndexManager:
    """
    索引管理器
    
    管理任务与知识库的映射关系，提供：
    - 任务→知识条目索引
    - 快速检索能力
    - 版本管理
    - Checkpoint集成
    """
    
    def __init__(self, 
                 index_dir: str = "memory/knowledge_index",
                 knowledge_dir: str = "/root/.openclaw/workspace/knowledge/ingested-v6"):
        self.index_dir = Path(index_dir)
        self.knowledge_dir = Path(knowledge_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # 索引文件
        self._entries_file = self.index_dir / "entries.json"
        self._task_mapping_file = self.index_dir / "task_mappings.json"
        self._versions_file = self.index_dir / "versions.json"
        self._checkpoint_file = self.index_dir / "index_checkpoint.json"
        
        # 内存索引
        self._entries: Dict[str, KnowledgeEntry] = {}  # entry_id -> entry
        self._file_to_entry: Dict[str, str] = {}  # source_file -> entry_id
        self._task_mappings: Dict[str, TaskKnowledgeMapping] = {}  # task_id -> mapping
        self._versions: List[IndexVersion] = []
        
        # 当前版本
        self._current_version: Optional[IndexVersion] = None
        
        # 加载索引
        self._load_index()
    
    def _load_index(self) -> None:
        """加载索引数据"""
        # 加载知识条目
        if self._entries_file.exists():
            try:
                with open(self._entries_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry_data in data.get("entries", []):
                        entry = KnowledgeEntry.from_dict(entry_data)
                        self._entries[entry.entry_id] = entry
                        self._file_to_entry[entry.source_file] = entry.entry_id
                logger.info(f"Loaded {len(self._entries)} knowledge entries")
            except Exception as e:
                logger.warning(f"Failed to load entries: {e}")
        
        # 加载任务映射
        if self._task_mapping_file.exists():
            try:
                with open(self._task_mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for mapping_data in data.get("mappings", []):
                        mapping = TaskKnowledgeMapping(
                            task_id=mapping_data["task_id"],
                            entry_ids=mapping_data.get("entry_ids", []),
                            ingested_at=datetime.fromisoformat(mapping_data["ingested_at"]) if mapping_data.get("ingested_at") else datetime.now(),
                        )
                        self._task_mappings[mapping.task_id] = mapping
                logger.info(f"Loaded {len(self._task_mappings)} task mappings")
            except Exception as e:
                logger.warning(f"Failed to load task mappings: {e}")
        
        # 加载版本
        if self._versions_file.exists():
            try:
                with open(self._versions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for version_data in data.get("versions", []):
                        version = IndexVersion(
                            version_id=version_data["version_id"],
                            created_at=datetime.fromisoformat(version_data["created_at"]),
                            status=IndexVersionStatus(version_data.get("status", "active")),
                            entry_count=version_data.get("entry_count", 0),
                            task_count=version_data.get("task_count", 0),
                            description=version_data.get("description"),
                            created_by=version_data.get("created_by", "system"),
                        )
                        self._versions.append(version)
                
                # 找到活跃版本
                active_versions = [v for v in self._versions if v.status == IndexVersionStatus.ACTIVE]
                if active_versions:
                    self._current_version = active_versions[-1]
                    logger.info(f"Current index version: {self._current_version.version_id}")
            except Exception as e:
                logger.warning(f"Failed to load versions: {e}")
        
        # 如果没有版本，创建一个
        if not self._current_version:
            self.create_version("Initial index version")
    
    def _save_index(self) -> None:
        """保存索引数据"""
        # 保存知识条目
        try:
            with open(self._entries_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "entries": [e.to_dict() for e in self._entries.values()],
                    "version": self._current_version.version_id if self._current_version else None,
                    "updated_at": datetime.now().isoformat(),
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save entries: {e}")
        
        # 保存任务映射
        try:
            with open(self._task_mapping_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "mappings": [m.to_dict() for m in self._task_mappings.values()],
                    "updated_at": datetime.now().isoformat(),
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save task mappings: {e}")
        
        # 保存版本
        try:
            with open(self._versions_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "versions": [v.to_dict() for v in self._versions],
                    "updated_at": datetime.now().isoformat(),
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save versions: {e}")
    
    def create_version(self, description: str = None) -> IndexVersion:
        """创建新版本"""
        # 归档当前版本
        if self._current_version:
            self._current_version.status = IndexVersionStatus.ARCHIVED
        
        # 创建新版本
        version = IndexVersion(
            description=description,
            entry_count=len(self._entries),
            task_count=len(self._task_mappings),
        )
        
        self._versions.append(version)
        self._current_version = version
        
        self._save_index()
        logger.info(f"Created new index version: {version.version_id}")
        
        return version
    
    def add_entry(self, 
                  source_file: str,
                  metadata_file: str,
                  task_id: Optional[str] = None,
                  checksum: Optional[str] = None) -> KnowledgeEntry:
        """
        添加知识条目
        
        Args:
            source_file: 源文件路径
            metadata_file: 元数据文件路径
            task_id: 来源任务ID
            checksum: 文件校验和
            
        Returns:
            KnowledgeEntry: 创建的知识条目
        """
        # 检查是否已存在
        if source_file in self._file_to_entry:
            entry_id = self._file_to_entry[source_file]
            entry = self._entries[entry_id]
            
            # 更新版本
            entry.version += 1
            entry.updated_at = datetime.now()
            entry.metadata_file = metadata_file
            if checksum:
                entry.checksum = checksum
            
            logger.debug(f"Updated knowledge entry: {entry_id} (v{entry.version})")
        else:
            # 创建新条目
            entry = KnowledgeEntry(
                source_file=source_file,
                metadata_file=metadata_file,
                source_task_id=task_id,
                checksum=checksum,
            )
            
            # 尝试读取元数据
            self._enrich_from_metadata(entry, metadata_file)
            
            self._entries[entry.entry_id] = entry
            self._file_to_entry[source_file] = entry.entry_id
            
            logger.debug(f"Created knowledge entry: {entry.entry_id}")
        
        # 更新任务映射
        if task_id:
            self._update_task_mapping(task_id, entry.entry_id)
        
        # 更新版本统计
        if self._current_version:
            self._current_version.entry_count = len(self._entries)
        
        self._save_index()
        
        return entry
    
    def _enrich_from_metadata(self, entry: KnowledgeEntry, metadata_file: str) -> None:
        """从元数据文件丰富条目信息"""
        try:
            if Path(metadata_file).exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                entry.file_type = metadata.get("file_type", "")
                entry.title = metadata.get("title")
                entry.description = metadata.get("description")
                entry.key_points = metadata.get("key_points", [])
                
                # 从源路径推断分类
                path = Path(entry.source_file)
                if "skills" in str(path):
                    entry.category = "skill"
                elif "memory" in str(path):
                    entry.category = "memory"
                elif "docs" in str(path):
                    entry.category = "document"
                elif "scripts" in str(path):
                    entry.category = "script"
                else:
                    entry.category = "general"
        except Exception as e:
            logger.warning(f"Failed to enrich from metadata: {e}")
    
    def _update_task_mapping(self, task_id: str, entry_id: str) -> None:
        """更新任务映射"""
        if task_id not in self._task_mappings:
            self._task_mappings[task_id] = TaskKnowledgeMapping(task_id=task_id)
        
        mapping = self._task_mappings[task_id]
        if entry_id not in mapping.entry_ids:
            mapping.entry_ids.append(entry_id)
            mapping.total_entries = len(mapping.entry_ids)
        
        # 更新版本统计
        if self._current_version:
            self._current_version.task_count = len(self._task_mappings)
    
    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """通过ID获取知识条目"""
        return self._entries.get(entry_id)
    
    def get_entry_by_file(self, source_file: str) -> Optional[KnowledgeEntry]:
        """通过源文件路径获取知识条目"""
        entry_id = self._file_to_entry.get(source_file)
        if entry_id:
            return self._entries.get(entry_id)
        return None
    
    def get_entries_by_task(self, task_id: str) -> List[KnowledgeEntry]:
        """获取任务关联的所有知识条目"""
        mapping = self._task_mappings.get(task_id)
        if not mapping:
            return []
        
        entries = []
        for entry_id in mapping.entry_ids:
            entry = self._entries.get(entry_id)
            if entry:
                entries.append(entry)
        
        return entries
    
    def search(self, 
               query: str = None,
               file_type: str = None,
               category: str = None,
               tags: List[str] = None,
               task_id: str = None) -> List[KnowledgeEntry]:
        """
        搜索知识条目
        
        Args:
            query: 搜索关键词（匹配标题、描述、关键点）
            file_type: 文件类型过滤
            category: 分类过滤
            tags: 标签过滤
            task_id: 任务ID过滤
            
        Returns:
            List[KnowledgeEntry]: 匹配的知识条目
        """
        results = list(self._entries.values())
        
        # 按任务过滤
        if task_id:
            mapping = self._task_mappings.get(task_id)
            if mapping:
                entry_ids = set(mapping.entry_ids)
                results = [e for e in results if e.entry_id in entry_ids]
            else:
                return []
        
        # 按文件类型过滤
        if file_type:
            results = [e for e in results if e.file_type == file_type]
        
        # 按分类过滤
        if category:
            results = [e for e in results if e.category == category]
        
        # 按标签过滤
        if tags:
            tag_set = set(tags)
            results = [e for e in results if tag_set.intersection(set(e.tags))]
        
        # 按关键词搜索
        if query:
            query_lower = query.lower()
            filtered = []
            for entry in results:
                # 搜索标题
                if entry.title and query_lower in entry.title.lower():
                    filtered.append(entry)
                    continue
                
                # 搜索描述
                if entry.description and query_lower in entry.description.lower():
                    filtered.append(entry)
                    continue
                
                # 搜索关键点
                for point in entry.key_points:
                    if query_lower in point.lower():
                        filtered.append(entry)
                        break
            
            results = filtered
        
        # 按时间倒序排序
        results.sort(key=lambda e: e.ingested_at, reverse=True)
        
        return results
    
    def create_checkpoint(self) -> str:
        """
        创建索引Checkpoint（用于恢复）
        
        Returns:
            str: Checkpoint ID
        """
        checkpoint_id = f"idx_cp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "version_id": self._current_version.version_id if self._current_version else None,
            "entries_count": len(self._entries),
            "mappings_count": len(self._task_mappings),
            "entries_snapshot": {k: v.to_dict() for k, v in list(self._entries.items())[:100]},  # 只保存前100条
        }
        
        try:
            with open(self._checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
            logger.info(f"Index checkpoint created: {checkpoint_id}")
            return checkpoint_id
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return ""
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> bool:
        """
        从Checkpoint恢复索引
        
        Args:
            checkpoint_id: Checkpoint ID
            
        Returns:
            bool: 是否成功
        """
        if not self._checkpoint_file.exists():
            logger.warning("No checkpoint file found")
            return False
        
        try:
            with open(self._checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            if checkpoint_data.get("checkpoint_id") != checkpoint_id:
                logger.warning(f"Checkpoint ID mismatch: {checkpoint_id}")
                return False
            
            # 重新加载索引
            self._load_index()
            
            logger.info(f"Index restored from checkpoint: {checkpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from checkpoint: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        # 按类型统计
        type_counts: Dict[str, int] = {}
        category_counts: Dict[str, int] = {}
        
        for entry in self._entries.values():
            type_counts[entry.file_type] = type_counts.get(entry.file_type, 0) + 1
            if entry.category:
                category_counts[entry.category] = category_counts.get(entry.category, 0) + 1
        
        return {
            "total_entries": len(self._entries),
            "total_tasks": len(self._task_mappings),
            "current_version": self._current_version.version_id if self._current_version else None,
            "version_count": len(self._versions),
            "type_distribution": type_counts,
            "category_distribution": category_counts,
            "index_dir": str(self.index_dir),
            "knowledge_dir": str(self.knowledge_dir),
        }
    
    def get_task_knowledge_summary(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务知识摘要"""
        mapping = self._task_mappings.get(task_id)
        if not mapping:
            return None
        
        entries = self.get_entries_by_task(task_id)
        
        return {
            "task_id": task_id,
            "total_entries": len(entries),
            "ingested_at": mapping.ingested_at.isoformat(),
            "entries": [e.to_dict() for e in entries],
        }
    
    def list_versions(self) -> List[IndexVersion]:
        """列出所有版本"""
        return sorted(self._versions, key=lambda v: v.created_at, reverse=True)
    
    def switch_version(self, version_id: str) -> bool:
        """切换到指定版本"""
        for version in self._versions:
            if version.version_id == version_id:
                if self._current_version:
                    self._current_version.status = IndexVersionStatus.ARCHIVED
                version.status = IndexVersionStatus.ACTIVE
                self._current_version = version
                self._save_index()
                logger.info(f"Switched to index version: {version_id}")
                return True
        
        return False
    
    def rebuild_index(self) -> int:
        """
        重建索引（扫描知识库目录）
        
        Returns:
            int: 重建的条目数
        """
        if not self.knowledge_dir.exists():
            logger.warning(f"Knowledge directory not found: {self.knowledge_dir}")
            return 0
        
        # 创建新版本
        self.create_version("Index rebuild")
        
        # 清空当前索引
        self._entries.clear()
        self._file_to_entry.clear()
        self._task_mappings.clear()
        
        # 扫描知识库目录
        count = 0
        for json_file in self.knowledge_dir.glob("*_v6.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                source_file = metadata.get("source_path", "")
                if source_file:
                    entry = KnowledgeEntry(
                        source_file=source_file,
                        metadata_file=str(json_file),
                        file_type=metadata.get("file_type", ""),
                        title=metadata.get("title"),
                        description=metadata.get("description"),
                        key_points=metadata.get("key_points", []),
                        ingested_at=datetime.fromisoformat(metadata.get("ingested_at")) if metadata.get("ingested_at") else datetime.now(),
                        checksum=metadata.get("checksum"),
                    )
                    
                    self._entries[entry.entry_id] = entry
                    self._file_to_entry[source_file] = entry.entry_id
                    count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to process {json_file}: {e}")
        
        # 更新版本统计
        if self._current_version:
            self._current_version.entry_count = count
        
        self._save_index()
        logger.info(f"Index rebuilt: {count} entries")
        
        return count


# 便捷函数
def create_index_manager(index_dir: str = None, knowledge_dir: str = None) -> IndexManager:
    """创建索引管理器"""
    kwargs = {}
    if index_dir:
        kwargs["index_dir"] = index_dir
    if knowledge_dir:
        kwargs["knowledge_dir"] = knowledge_dir
    
    return IndexManager(**kwargs)
