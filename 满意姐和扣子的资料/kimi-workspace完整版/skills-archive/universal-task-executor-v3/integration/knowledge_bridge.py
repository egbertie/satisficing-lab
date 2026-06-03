"""
Knowledge Bridge - 知识入库桥接器
集成super-knowledge-ingest Skill到Universal Task Executor V3.0

职责：
1. 统一接口调用super-knowledge-ingest
2. 支持批量入库
3. 支持增量更新
4. Token优化（大任务分批入库）
5. Checkpoint支持（入库状态可恢复）
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# 添加super-knowledge-ingest路径
SKILL_PATH = Path(__file__).parent.parent.parent / "super-knowledge-ingest"
sys.path.insert(0, str(SKILL_PATH))

logger = logging.getLogger(__name__)


@dataclass
class IngestConfig:
    """入库配置"""
    # 路径配置
    skill_script_path: str = str(SKILL_PATH / "super_knowledge_ingest_v6.2.py")
    output_dir: str = "/root/.openclaw/workspace/knowledge/ingested-v6"
    index_file: str = "/root/.openclaw/workspace/knowledge/INDEX-v6.md"
    checkpoint_dir: str = "/root/.openclaw/workspace/memory/knowledge_checkpoints"
    
    # Token优化配置
    batch_size: int = 10  # 每批处理文件数
    max_tokens_per_batch: int = 50000  # 每批最大Token消耗
    token_efficiency_target: float = 0.85  # Token效率目标
    
    # 重试配置
    max_retries: int = 3
    retry_delay: int = 2  # 秒
    
    # 增量更新配置
    incremental_mode: bool = True  # 启用增量更新
    checksum_cache_file: str = "memory/knowledge_checksums.json"
    
    # 支持的文件类型
    supported_extensions: List[str] = field(default_factory=lambda: [
        '.md', '.py', '.json', '.sh', '.txt', 
        '.yaml', '.yml', '.html', '.svg', '.log'
    ])


@dataclass
class IngestResult:
    """入库结果"""
    success: bool
    file_path: str
    output_file: Optional[str] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None
    token_consumed: int = 0
    processing_time_ms: float = 0
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "file_path": self.file_path,
            "output_file": self.output_file,
            "metadata": self.metadata,
            "error": self.error,
            "token_consumed": self.token_consumed,
            "processing_time_ms": self.processing_time_ms,
            "checksum": self.checksum,
        }


@dataclass
class BatchIngestResult:
    """批量入库结果"""
    batch_id: str
    total_files: int
    success_count: int
    failed_count: int
    skipped_count: int  # 增量更新时跳过的文件
    results: List[IngestResult] = field(default_factory=list)
    token_consumed_total: int = 0
    processing_time_total_ms: float = 0
    checkpoint_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "total_files": self.total_files,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "token_consumed_total": self.token_consumed_total,
            "processing_time_total_ms": self.processing_time_total_ms,
            "checkpoint_id": self.checkpoint_id,
            "results": [r.to_dict() for r in self.results],
        }


class KnowledgeBridge:
    """
    知识入库桥接器
    
    统一封装super-knowledge-ingest Skill的调用，提供：
    - 单文件入库
    - 批量文件入库（带Token优化）
    - 增量更新支持
    - Checkpoint支持（可恢复）
    """
    
    def __init__(self, config: IngestConfig = None):
        self.config = config or IngestConfig()
        self._ensure_directories()
        self._checksum_cache: Dict[str, str] = {}
        self._load_checksum_cache()
        
    def _ensure_directories(self) -> None:
        """确保所需目录存在"""
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.checkpoint_dir).mkdir(parents=True, exist_ok=True)
        
    def _load_checksum_cache(self) -> None:
        """加载校验和缓存（用于增量更新）"""
        cache_file = Path(self.config.checksum_cache_file)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self._checksum_cache = json.load(f)
                logger.info(f"Loaded checksum cache: {len(self._checksum_cache)} entries")
            except Exception as e:
                logger.warning(f"Failed to load checksum cache: {e}")
                self._checksum_cache = {}
    
    def _save_checksum_cache(self) -> None:
        """保存校验和缓存"""
        cache_file = Path(self.config.checksum_cache_file)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._checksum_cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save checksum cache: {e}")
    
    def _compute_checksum(self, file_path: str) -> str:
        """计算文件MD5校验和"""
        import hashlib
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()[:16]
    
    def _should_process(self, file_path: str) -> bool:
        """检查文件是否需要处理（增量更新）"""
        if not self.config.incremental_mode:
            return True
        
        current_checksum = self._compute_checksum(file_path)
        cached_checksum = self._checksum_cache.get(file_path)
        
        if cached_checksum == current_checksum:
            logger.debug(f"Skipping unchanged file: {file_path}")
            return False
        
        return True
    
    def _update_checksum(self, file_path: str) -> None:
        """更新文件校验和缓存"""
        self._checksum_cache[file_path] = self._compute_checksum(file_path)
    
    def _validate_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        """验证文件是否可处理"""
        path = Path(file_path)
        
        # 检查文件是否存在
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        # 检查扩展名
        if path.suffix.lower() not in self.config.supported_extensions:
            return False, f"Unsupported file type: {path.suffix}"
        
        # 检查文件大小（10MB限制）
        max_size = 10 * 1024 * 1024  # 10MB
        if path.stat().st_size > max_size:
            return False, f"File too large: {path.stat().st_size} bytes (max 10MB)"
        
        return True, None
    
    def ingest_file(self, file_path: str, 
                    force: bool = False,
                    retry_count: int = 0) -> IngestResult:
        """
        单文件入库
        
        Args:
            file_path: 文件路径
            force: 是否强制处理（忽略增量更新）
            retry_count: 当前重试次数
            
        Returns:
            IngestResult: 入库结果
        """
        start_time = datetime.now()
        
        # 验证文件
        valid, error = self._validate_file(file_path)
        if not valid:
            return IngestResult(
                success=False,
                file_path=file_path,
                error=error,
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
        
        # 增量更新检查
        if not force and not self._should_process(file_path):
            return IngestResult(
                success=True,
                file_path=file_path,
                error=None,
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
        
        # 调用super-knowledge-ingest Skill
        try:
            result = self._call_skill(file_path)
            
            # 更新校验和缓存
            if result.success:
                self._update_checksum(file_path)
                result.checksum = self._checksum_cache.get(file_path)
            
            result.processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            return result
            
        except Exception as e:
            logger.error(f"Ingest failed for {file_path}: {e}")
            
            # 重试逻辑
            if retry_count < self.config.max_retries:
                logger.info(f"Retrying {file_path} (attempt {retry_count + 1})")
                import time
                time.sleep(self.config.retry_delay * (retry_count + 1))
                return self.ingest_file(file_path, force, retry_count + 1)
            
            return IngestResult(
                success=False,
                file_path=file_path,
                error=str(e),
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def _call_skill(self, file_path: str) -> IngestResult:
        """
        调用super-knowledge-ingest Skill
        
        注意：这是桥接层的核心，必须调用Skill而不是直接操作知识库
        """
        import tempfile
        
        # 使用临时文件捕获输出
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # 构建命令行调用
            cmd = [
                sys.executable,
                self.config.skill_script_path,
                file_path
            ]
            
            logger.debug(f"Calling skill: {' '.join(cmd)}")
            
            # 执行Skill
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # 检查输出文件是否生成
            path = Path(file_path)
            output_filename = f"{path.stem}_{path.suffix.lstrip('.')}_v6.json"
            output_path = Path(self.config.output_dir) / output_filename
            
            if output_path.exists():
                # 读取生成的元数据
                with open(output_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # 估算Token消耗
                token_estimate = self._estimate_tokens(file_path, metadata)
                
                return IngestResult(
                    success=True,
                    file_path=file_path,
                    output_file=str(output_path),
                    metadata=metadata,
                    token_consumed=token_estimate,
                )
            else:
                return IngestResult(
                    success=False,
                    file_path=file_path,
                    error=f"Skill did not generate output file. Stderr: {result.stderr}",
                )
                
        except subprocess.TimeoutExpired:
            return IngestResult(
                success=False,
                file_path=file_path,
                error="Skill execution timeout (300s)",
            )
        except Exception as e:
            return IngestResult(
                success=False,
                file_path=file_path,
                error=f"Skill execution error: {str(e)}",
            )
        finally:
            # 清理临时文件
            Path(tmp_path).unlink(missing_ok=True)
    
    def _estimate_tokens(self, file_path: str, metadata: Dict) -> int:
        """估算Token消耗"""
        path = Path(file_path)
        size_kb = path.stat().st_size / 1024
        
        # 基于文件大小的估算
        if size_kb < 10:
            return 300  # 小文件 ~300 tokens
        elif size_kb < 100:
            return 1000  # 中文件 ~1000 tokens
        elif size_kb < 1024:
            return 2500  # 大文件 ~2500 tokens
        else:
            return 4000  # 超大文件 ~4000 tokens
    
    async def ingest_batch(self, 
                          file_paths: List[str],
                          checkpoint_callback: Optional[Callable[[Dict], None]] = None,
                          progress_callback: Optional[Callable[[int, int], None]] = None) -> BatchIngestResult:
        """
        批量文件入库（带Token优化和Checkpoint支持）
        
        Args:
            file_paths: 文件路径列表
            checkpoint_callback: Checkpoint回调函数
            progress_callback: 进度回调函数(当前, 总数)
            
        Returns:
            BatchIngestResult: 批量入库结果
        """
        import uuid
        
        batch_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        results: List[IngestResult] = []
        success_count = 0
        failed_count = 0
        skipped_count = 0
        token_consumed_total = 0
        
        # 分批处理（Token优化）
        total_files = len(file_paths)
        batch_size = self.config.batch_size
        
        logger.info(f"Starting batch ingest: {total_files} files, batch_size={batch_size}")
        
        for i in range(0, total_files, batch_size):
            batch_files = file_paths[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_files + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches}: {len(batch_files)} files")
            
            # 检查Token预算
            if token_consumed_total > self.config.max_tokens_per_batch:
                logger.warning(f"Token budget reached: {token_consumed_total}, pausing batch")
                # 保存Checkpoint
                if checkpoint_callback:
                    checkpoint_callback({
                        "batch_id": batch_id,
                        "processed_count": len(results),
                        "total_count": total_files,
                        "token_consumed": token_consumed_total,
                        "pending_files": file_paths[i:],
                    })
                # 等待Token恢复或继续（这里简化处理）
                await asyncio.sleep(1)
            
            # 处理当前批次
            for file_path in batch_files:
                result = self.ingest_file(file_path)
                results.append(result)
                
                if result.success:
                    if result.output_file:  # 实际处理成功
                        success_count += 1
                    else:  # 增量更新跳过
                        skipped_count += 1
                    token_consumed_total += result.token_consumed
                else:
                    failed_count += 1
                
                # 进度回调
                if progress_callback:
                    progress_callback(len(results), total_files)
            
            # 每批次保存一次校验和缓存
            self._save_checksum_cache()
            
            # 小延迟避免过载
            await asyncio.sleep(0.1)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 保存最终Checkpoint
        checkpoint_id = None
        if checkpoint_callback:
            checkpoint_data = {
                "batch_id": batch_id,
                "processed_count": len(results),
                "total_count": total_files,
                "token_consumed": token_consumed_total,
                "completed": True,
            }
            checkpoint_callback(checkpoint_data)
            checkpoint_id = batch_id
        
        return BatchIngestResult(
            batch_id=batch_id,
            total_files=total_files,
            success_count=success_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            results=results,
            token_consumed_total=token_consumed_total,
            processing_time_total_ms=processing_time,
            checkpoint_id=checkpoint_id,
        )
    
    def ingest_task_output(self, task_id: str, output_files: List[str]) -> BatchIngestResult:
        """
        将任务输出文件入库（供auto_ingest调用）
        
        Args:
            task_id: 任务ID
            output_files: 输出文件路径列表
            
        Returns:
            BatchIngestResult: 入库结果
        """
        logger.info(f"Ingesting task output: task_id={task_id}, files={len(output_files)}")
        
        # 使用asyncio运行批量入库
        return asyncio.run(self.ingest_batch(output_files))
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "cached_files": len(self._checksum_cache),
            "output_dir": self.config.output_dir,
            "incremental_mode": self.config.incremental_mode,
            "batch_size": self.config.batch_size,
            "max_tokens_per_batch": self.config.max_tokens_per_batch,
        }
    
    def reset_cache(self) -> None:
        """重置校验和缓存（用于全量重新入库）"""
        self._checksum_cache = {}
        self._save_checksum_cache()
        logger.info("Checksum cache reset")


# 便捷函数
def create_bridge(config: Dict[str, Any] = None) -> KnowledgeBridge:
    """创建知识桥接器实例"""
    if config:
        return KnowledgeBridge(IngestConfig(**config))
    return KnowledgeBridge()


def quick_ingest(file_path: str) -> IngestResult:
    """快速单文件入库"""
    bridge = KnowledgeBridge()
    return bridge.ingest_file(file_path)


def quick_ingest_batch(file_paths: List[str]) -> BatchIngestResult:
    """快速批量入库"""
    bridge = KnowledgeBridge()
    return asyncio.run(bridge.ingest_batch(file_paths))
