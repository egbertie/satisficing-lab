#!/usr/bin/env python3
"""
Super Knowledge Ingest - 批处理脚本
执行7层标准化知识入库

用法:
    python3 batch_ingest.py --batch P0-C --files file1.md file2.md ...
    python3 batch_ingest.py --scan-all
    python3 batch_ingest.py --verify KNOW-P0-CORE-001
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置
WORKSPACE_ROOT = "/root/.openclaw/workspace"
KNOWLEDGE_DIR = f"{WORKSPACE_ROOT}/knowledge/P0-core"
INDEX_FILE = f"{WORKSPACE_ROOT}/knowledge/INDEX.md"
LOG_FILE = f"{WORKSPACE_ROOT}/diary/blue-army-super-ingest/BLUE-ARMY-SUPER-LOG.md"


def compute_sha256(filepath: str) -> str:
    """计算文件SHA256哈希"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_stats(filepath: str) -> Dict:
    """获取文件统计信息"""
    stat = os.stat(filepath)
    return {
        "line_count": sum(1 for _ in open(filepath, 'r', encoding='utf-8', errors='ignore')),
        "byte_count": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
    }


def generate_knowledge_id(batch: str, seq: int) -> str:
    """生成知识ID"""
    return f"KNOW-P0-CORE-{seq:03d}-v1.0"


def validate_s1(metadata: Dict) -> List[str]:
    """验证S1输入定义层"""
    errors = []
    required_fields = [
        "knowledge_id", "title", "original_filename", "source_path",
        "file_hash", "source_type", "created_at", "modified_at",
        "ingested_at", "version", "line_count", "byte_count"
    ]
    
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            errors.append(f"S1缺失: {field}")
    
    return errors


def validate_s3(metadata: Dict) -> List[str]:
    """验证S3知识结构化层"""
    errors = []
    required_fields = ["level1_category", "level2_category", "level3_category", "tags"]
    
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            errors.append(f"S3缺失: {field}")
    
    if "tags" in metadata and len(metadata["tags"]) < 3:
        errors.append("S3标签数量不足3个")
    
    return errors


def validate_s5(metadata: Dict) -> List[str]:
    """验证S5准确性验证层"""
    errors = []
    required_fields = ["quality_score", "validation_status", "validator"]
    
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            errors.append(f"S5缺失: {field}")
    
    return errors


def validate_s6(metadata: Dict) -> List[str]:
    """验证S6局限标注层"""
    errors = []
    required_fields = ["valid_until", "limitations", "confidence"]
    
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            errors.append(f"S6缺失: {field}")
    
    return errors


def validate_all_layers(metadata: Dict) -> Dict[str, List[str]]:
    """验证所有7层"""
    return {
        "S1": validate_s1(metadata),
        "S3": validate_s3(metadata),
        "S5": validate_s5(metadata),
        "S6": validate_s6(metadata),
        # S2, S4, S7 需要人工/蓝军验证
    }


def ingest_document(filepath: str, batch: str, seq: int) -> Dict:
    """
    执行单文档入库
    返回入库结果和元数据
    """
    result = {
        "success": False,
        "knowledge_id": None,
        "errors": [],
        "metadata": {}
    }
    
    # 检查文件存在
    if not os.path.exists(filepath):
        result["errors"].append(f"文件不存在: {filepath}")
        return result
    
    # S1: 输入定义
    filename = os.path.basename(filepath)
    knowledge_id = generate_knowledge_id(batch, seq)
    file_hash = compute_sha256(filepath)
    stats = get_file_stats(filepath)
    
    metadata = {
        "knowledge_id": knowledge_id,
        "title": filename.replace(".md", ""),
        "original_filename": filename,
        "source_path": filepath,
        "file_hash": f"sha256:{file_hash}",
        "source_type": "system_gen",
        "created_at": stats["created_at"],
        "modified_at": stats["modified_at"],
        "ingested_at": datetime.now().isoformat(),
        "version": "1.0.0",
        "line_count": stats["line_count"],
        "byte_count": stats["byte_count"],
        # S3 需要外部填充
        "level1_category": "",
        "level2_category": "",
        "level3_category": "",
        "tags": [],
        # S5 需要蓝军验证
        "quality_score": 0,
        "validation_status": "pending",
        "validator": "blue_army",
        # S6 需要外部填充
        "valid_until": "",
        "limitations": [],
        "dependencies": [],
        "confidence": "high",
        # S7
        "stress_test_scenarios": [],
        # 状态
        "status": "active",
        "access_level": "internal"
    }
    
    # 验证
    validation_results = validate_all_layers(metadata)
    all_errors = []
    for layer, errors in validation_results.items():
        all_errors.extend(errors)
    
    if all_errors:
        result["errors"] = all_errors
        result["metadata"] = metadata
        return result
    
    result["success"] = True
    result["knowledge_id"] = knowledge_id
    result["metadata"] = metadata
    
    return result


def batch_ingest(files: List[str], batch: str) -> Dict:
    """
    批量入库
    """
    results = {
        "batch": batch,
        "total": len(files),
        "success": 0,
        "failed": 0,
        "details": []
    }
    
    for seq, filepath in enumerate(files, 1):
        print(f"处理 {seq}/{len(files)}: {filepath}")
        result = ingest_document(filepath, batch, seq)
        results["details"].append(result)
        
        if result["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1
            print(f"  ❌ 失败: {result['errors']}")
    
    return results


def scan_uningested() -> List[str]:
    """
    扫描未入库的.md文件
    """
    # 这里简化实现，实际应检查knowledge/INDEX.md
    workspace_md = Path(WORKSPACE_ROOT).glob("*.md")
    return [str(f) for f in workspace_md]


def main():
    parser = argparse.ArgumentParser(description="Super Knowledge Ingest - 7层标准化入库")
    parser.add_argument("--batch", help="批次名称 (如: P0-C)")
    parser.add_argument("--files", nargs="+", help="要入库的文件列表")
    parser.add_argument("--scan-all", action="store_true", help="扫描所有未入库文件")
    parser.add_argument("--verify", help="验证指定知识ID")
    
    args = parser.parse_args()
    
    if args.scan_all:
        files = scan_uningested()
        print(f"扫描到 {len(files)} 个待入库文件")
        # 实际入库需要用户确认
        
    elif args.files and args.batch:
        results = batch_ingest(args.files, args.batch)
        print(f"\n批次 {args.batch} 完成:")
        print(f"  总计: {results['total']}")
        print(f"  成功: {results['success']}")
        print(f"  失败: {results['failed']}")
        
    elif args.verify:
        print(f"验证知识ID: {args.verify}")
        # 实现验证逻辑
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
