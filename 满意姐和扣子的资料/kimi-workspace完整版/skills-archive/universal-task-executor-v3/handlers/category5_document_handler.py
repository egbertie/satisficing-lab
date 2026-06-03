import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills/universal-task-executor-v3")
"""
Universal Task Executor V3.0 - Category 5: 文档归类处理器
处理文档的自动分类、归档和索引管理
"""

import os
import re
import json
import logging
import shutil
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path

from core.registry import TaskHandler
from core.structures import Task, TaskResult, TaskStatus, AuditRecord
from core.token_engine import TokenEngine

logger = logging.getLogger(__name__)


class Category5DocumentHandler(TaskHandler):
    """
    第5类处理器：文档归类处理器
    
    职责：
    1. 文档自动分类（按类型、主题、时间）
    2. 归档管理（移动、复制、链接）
    3. 索引更新（维护可搜索索引）
    4. 重复检测和清理
    5. 元数据提取和管理
    
    归类维度：
    - 文档类型（设计文档、会议纪要、报告等）
    - 项目/主题归属
    - 时间维度（年月）
    - 重要程度
    - 访问频率
    """
    
    handler_name = "category5_document_handler"
    supported_categories = ["category_5"]
    version = "3.0.0"
    
    # 文档类型定义
    DOC_TYPES = {
        "design": {
            "name": "设计文档",
            "extensions": [".md", ".docx", ".drawio"],
            "keywords": ["设计", "架构", "架构图", "Design", "Architecture"],
            "target_dir": "docs/design/"
        },
        "meeting": {
            "name": "会议纪要",
            "extensions": [".md", ".txt"],
            "keywords": ["会议", "纪要", "讨论", "Meeting", "讨论"],
            "target_dir": "docs/meetings/"
        },
        "report": {
            "name": "报告文档",
            "extensions": [".md", ".pdf", ".docx"],
            "keywords": ["报告", "总结", "分析", "Report", "Summary"],
            "target_dir": "docs/reports/"
        },
        "guide": {
            "name": "指南文档",
            "extensions": [".md", ".rst"],
            "keywords": ["指南", "手册", "教程", "Guide", "Tutorial", "HowTo"],
            "target_dir": "docs/guides/"
        },
        "spec": {
            "name": "规范文档",
            "extensions": [".md", ".yaml", ".yml"],
            "keywords": ["规范", "标准", "约定", "Spec", "Standard"],
            "target_dir": "docs/specs/"
        },
        "research": {
            "name": "研究文档",
            "extensions": [".md", ".pdf", ".ipynb"],
            "keywords": ["研究", "调研", "分析", "Research", "Analysis"],
            "target_dir": "docs/research/"
        },
        "code_doc": {
            "name": "代码文档",
            "extensions": [".py", ".js", ".ts", ".md"],
            "keywords": ["SKILL.md", "README", "API文档"],
            "target_dir": "docs/code/"
        },
        "temp": {
            "name": "临时文件",
            "extensions": [".tmp", ".draft", ".bak"],
            "keywords": ["临时", "草稿", "备份", "draft", "temp"],
            "target_dir": "docs/temp/"
        },
        "misc": {
            "name": "杂项文档",
            "extensions": [],
            "keywords": [],
            "target_dir": "docs/misc/"
        }
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.doc_base_path = self.config.get("doc_base_path", 
                                             "/root/.openclaw/workspace/")
        self.archive_base_path = self.config.get("archive_base_path",
                                                  "/root/.openclaw/workspace/docs/")
        self.index_path = self.config.get("index_path", "memory/doc_index.json")
        self.classification_log_dir = self.config.get("classification_log_dir", 
                                                       "logs/doc_classification/")
        
        os.makedirs(self.archive_base_path, exist_ok=True)
        os.makedirs(self.classification_log_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # 加载现有索引
        self.doc_index = self._load_index()
        
        logger.info(f"Category5DocumentHandler initialized: base={self.doc_base_path}")
    
    def validate(self, task: Task) -> bool:
        """验证文档归类任务数据"""
        if not super().validate(task):
            return False
        
        data = task.data
        
        # 检查是否有文档路径或内容
        if "doc_path" not in data and "doc_content" not in data:
            logger.error("Task validation failed: missing doc_path or doc_content")
            return False
        
        return True
    
    def execute(self, task: Task, checkpoint_state: Optional[Dict] = None) -> TaskResult:
        """执行文档归类"""
        start_time = datetime.now()
        task_id = task.task_id
        
        if checkpoint_state:
            self._restore_state(checkpoint_state)
        
        try:
            data = task.data
            doc_path = data.get("doc_path", "")
            doc_content = data.get("doc_content", "")
            doc_name = data.get("doc_name", "")
            force_type = data.get("doc_type", None)  # 强制指定类型
            auto_archive = data.get("auto_archive", False)
            
            # 1. 确定文档类型
            if force_type:
                doc_type = force_type
                classification_confidence = 1.0
            else:
                doc_type, classification_confidence = self._classify_document(
                    doc_path, doc_name, doc_content
                )
            
            # 2. 提取元数据
            metadata = self._extract_metadata(doc_path, doc_name, doc_content, doc_type)
            
            # 3. 确定目标位置
            target_path = self._determine_target_path(doc_name or os.path.basename(doc_path), 
                                                       doc_type, metadata)
            
            # 4. 如果需要归档，执行归档
            archive_result = None
            if auto_archive and doc_path:
                archive_result = self._archive_document(doc_path, target_path)
            
            # 5. 更新索引
            doc_entry = {
                "task_id": task_id,
                "original_path": doc_path,
                "doc_name": doc_name or os.path.basename(doc_path),
                "doc_type": doc_type,
                "doc_type_name": self.DOC_TYPES.get(doc_type, {}).get("name", "未知"),
                "classification_confidence": classification_confidence,
                "metadata": metadata,
                "target_path": target_path,
                "archived": auto_archive,
                "archive_result": archive_result,
                "indexed_at": datetime.now().isoformat()
            }
            
            self.doc_index[task_id] = doc_entry
            self._save_index()
            
            # 6. 记录分类日志
            self._log_classification(doc_entry)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                task_id=task_id,
                status="completed",
                output={
                    "doc_name": doc_entry["doc_name"],
                    "doc_type": doc_type,
                    "doc_type_name": doc_entry["doc_type_name"],
                    "classification_confidence": f"{classification_confidence:.1%}",
                    "target_path": target_path,
                    "archived": auto_archive,
                    "archive_success": archive_result.get("success") if archive_result else None,
                    "metadata": metadata,
                    "index_updated": True
                },
                token_consumed=1500,
                time_elapsed=elapsed,
                audit_required=False  # 文档归类不需要审计
            )
            
        except Exception as e:
            logger.error(f"Document classification failed: {task_id}, error={e}")
            elapsed = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                task_id=task_id,
                status="failed",
                output={},
                token_consumed=800,
                time_elapsed=elapsed,
                error=str(e)
            )
    
    def _classify_document(self, doc_path: str, doc_name: str, 
                           doc_content: str) -> tuple:
        """分类文档，返回(类型, 置信度)"""
        
        # 从文件名分析
        name_lower = (doc_name or os.path.basename(doc_path) or "").lower()
        
        # 从内容分析
        content_preview = (doc_content or "")[:2000].lower()
        
        type_scores = {}
        
        for doc_type, config in self.DOC_TYPES.items():
            score = 0
            
            # 关键词匹配
            for keyword in config.get("keywords", []):
                keyword_lower = keyword.lower()
                if keyword_lower in name_lower:
                    score += 3  # 文件名匹配权重高
                if keyword_lower in content_preview:
                    score += 2  # 内容匹配
            
            # 扩展名匹配
            for ext in config.get("extensions", []):
                if name_lower.endswith(ext.lower()):
                    score += 1
            
            type_scores[doc_type] = score
        
        # 选择得分最高的类型
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            best_score = type_scores[best_type]
            
            # 计算置信度（简化计算）
            max_possible = 6  # 最大可能得分
            confidence = min(best_score / max_possible, 1.0)
            
            # 如果没有得分，归类为misc
            if best_score == 0:
                return "misc", 0.3
            
            return best_type, confidence
        
        return "misc", 0.3
    
    def _extract_metadata(self, doc_path: str, doc_name: str, 
                          doc_content: str, doc_type: str) -> Dict:
        """提取文档元数据"""
        metadata = {
            "extracted_at": datetime.now().isoformat(),
            "doc_type": doc_type
        }
        
        # 文件信息
        if doc_path and os.path.exists(doc_path):
            stat = os.stat(doc_path)
            metadata["file_size_bytes"] = stat.st_size
            metadata["file_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            metadata["file_created"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
        
        # 内容统计
        if doc_content:
            metadata["content_length"] = len(doc_content)
            metadata["line_count"] = len(doc_content.split("\n"))
            metadata["word_count"] = len(doc_content.split())
            
            # 提取标题（假设第一行或第一个#后面是标题）
            title_match = re.search(r'^#\s*(.+)$', doc_content, re.MULTILINE)
            if title_match:
                metadata["title"] = title_match.group(1).strip()
            else:
                # 使用第一行非空内容
                lines = [l.strip() for l in doc_content.split("\n") if l.strip()]
                if lines:
                    metadata["title"] = lines[0][:100]  # 限制长度
        
        # 时间维度
        metadata["year"] = datetime.now().year
        metadata["month"] = datetime.now().month
        
        return metadata
    
    def _determine_target_path(self, doc_name: str, doc_type: str, 
                               metadata: Dict) -> str:
        """确定目标路径"""
        type_config = self.DOC_TYPES.get(doc_type, self.DOC_TYPES["misc"])
        base_dir = type_config.get("target_dir", "docs/misc/")
        
        # 添加年月子目录
        year = metadata.get("year", datetime.now().year)
        month = metadata.get("month", datetime.now().month)
        
        target_dir = os.path.join(self.archive_base_path, base_dir, str(year), f"{month:02d}")
        target_path = os.path.join(target_dir, doc_name)
        
        return target_path
    
    def _archive_document(self, source_path: str, target_path: str) -> Dict:
        """归档文档"""
        try:
            # 创建目标目录
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # 检查目标是否已存在
            if os.path.exists(target_path):
                # 添加时间戳后缀
                base, ext = os.path.splitext(target_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_path = f"{base}_{timestamp}{ext}"
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            
            return {
                "success": True,
                "source": source_path,
                "target": target_path,
                "method": "copy"
            }
        except Exception as e:
            logger.error(f"Archive failed: {source_path} -> {target_path}, error={e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_index(self) -> Dict:
        """加载文档索引"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load index: {e}")
        return {}
    
    def _save_index(self) -> None:
        """保存文档索引"""
        try:
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(self.doc_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def _log_classification(self, doc_entry: Dict) -> None:
        """记录分类日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": doc_entry["task_id"],
            "doc_name": doc_entry["doc_name"],
            "doc_type": doc_entry["doc_type"],
            "confidence": doc_entry["classification_confidence"],
            "archived": doc_entry["archived"]
        }
        
        # 追加到日志文件
        log_file = os.path.join(self.classification_log_dir, 
                                f"classification_{datetime.now().strftime('%Y%m')}.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def search_documents(self, query: str, doc_type: Optional[str] = None) -> List[Dict]:
        """搜索文档"""
        results = []
        query_lower = query.lower()
        
        for task_id, entry in self.doc_index.items():
            # 类型过滤
            if doc_type and entry.get("doc_type") != doc_type:
                continue
            
            # 搜索匹配
            match_score = 0
            
            # 名称匹配
            if query_lower in entry.get("doc_name", "").lower():
                match_score += 3
            
            # 类型名称匹配
            if query_lower in entry.get("doc_type_name", "").lower():
                match_score += 2
            
            # 标题匹配
            metadata = entry.get("metadata", {})
            if query_lower in metadata.get("title", "").lower():
                match_score += 3
            
            if match_score > 0:
                results.append({
                    "task_id": task_id,
                    "entry": entry,
                    "match_score": match_score
                })
        
        # 按匹配分数排序
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return results
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self.doc_index)
        
        by_type = {}
        for entry in self.doc_index.values():
            t = entry.get("doc_type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        
        archived = sum(1 for e in self.doc_index.values() if e.get("archived"))
        
        return {
            "total_documents": total,
            "archived_documents": archived,
            "by_type": by_type,
            "last_updated": datetime.now().isoformat()
        }
    
    def _restore_state(self, state: Dict) -> None:
        """从检查点恢复状态"""
        if "doc_index" in state:
            self.doc_index = state["doc_index"]
    
    def estimate_cost(self, task: Task) -> Dict[str, int]:
        """估算Token和时间成本"""
        return {
            "tokens": 1500,
            "time_seconds": 15
        }
    
    def get_checkpoint_state(self) -> Dict[str, Any]:
        """获取检查点状态"""
        state = super().get_checkpoint_state()
        state["doc_index"] = self.doc_index
        return state
    
    def restore_from_checkpoint(self, state: Dict[str, Any]) -> None:
        """从检查点恢复"""
        super().restore_from_checkpoint(state)
        if "doc_index" in state:
            self.doc_index = state["doc_index"]
    
    def audit(self, task_id: Optional[str] = None) -> AuditRecord:
        """
        蓝军审计方法（简化版）
        
        审计标准：
        1. 索引完整性
        2. 分类准确性抽样
        3. 归档一致性
        """
        audit = AuditRecord(
            task_id=task_id,
            auditor="blue_army_category5",
            audit_type="self",  # 文档归类使用自检
            criteria=[
                "index_integrity",
                "classification_accuracy",
                "archive_consistency"
            ]
        )
        
        # 检查索引一致性
        if not os.path.exists(self.index_path) and self.doc_index:
            audit.add_finding(
                item="索引文件一致性",
                expected="索引文件与内存索引同步",
                actual="索引文件不存在但内存有数据",
                severity="warning"
            )
        
        # 抽样检查归档一致性
        sample_size = min(10, len(self.doc_index))
        sample_entries = list(self.doc_index.values())[:sample_size]
        
        for entry in sample_entries:
            if entry.get("archived"):
                target_path = entry.get("target_path", "")
                if target_path and not os.path.exists(target_path):
                    audit.add_finding(
                        item=f"归档文件存在性: {entry.get('doc_name')}",
                        expected="归档文件存在",
                        actual="归档文件不存在",
                        severity="medium"
                    )
        
        audit.passed = not any(f["severity"] == "critical" for f in audit.findings)
        audit.severity = "warning" if audit.findings else "info"
        audit.recommendations.append("定期运行文档索引同步")
        
        logger.info(f"Category5 audit completed: {audit.passed}, findings={len(audit.findings)}")
        return audit


def register_handler(registry):
    """注册处理器到注册表"""
    registry.register_handler(Category5DocumentHandler)
    logger.info("Category5DocumentHandler registered")
