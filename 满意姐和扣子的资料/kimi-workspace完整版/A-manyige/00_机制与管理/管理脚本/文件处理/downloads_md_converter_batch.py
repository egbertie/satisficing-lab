#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
downloads_md_converter_batch.py
.kimi/downloads/ 分批转化控制器
用于稳定处理大量文件，避免单批次超时或内存峰值
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace')
from downloads_md_converter import DownloadsMdConverter

WORKSPACE = Path("/root/.openclaw/workspace")
PROGRESS_FILE = WORKSPACE / "tmp" / "downloads_conversion_progress.json"


def run_batch(batch_size: int = 20, dry_run: bool = False, cleanup: bool = False):
    converter = DownloadsMdConverter(dry_run=dry_run)
    tasks = converter.scan_files()
    
    # 只处理 pending 的任务
    pending = [t for t in tasks if t.status == "pending" and t.file_type != "unknown"]
    already_done = [t for t in tasks if t.status == "skipped"]
    unsupported = [t for t in tasks if t.file_type == "unknown"]
    
    print(f"总文件: {len(tasks)} | 已处理: {len(already_done)} | 待处理: {len(pending)} | 不支持: {len(unsupported)}")
    
    batch = pending[:batch_size]
    if not batch:
        print("本批次无待处理文件。")
        return
    
    print(f"本批次处理: {len(batch)} 个文件")
    completed = 0
    failed = 0
    
    for i, task in enumerate(batch):
        print(f"[{i+1}/{len(batch)}] {task.source_path.name} ({task.file_type}) ... ", end="", flush=True)
        try:
            processed = converter._process_item(task)
            print(f"{processed.status} p={processed.paragraph_count} w={processed.word_count}")
            if processed.status == "completed":
                completed += 1
            else:
                failed += 1
                print(f"   ERROR: {processed.error_message}")
        except Exception as e:
            print(f"FAILED: {e}")
            failed += 1
    
    converter._save_progress()
    print(f"\n批次结果: 成功 {completed} | 失败 {failed}")
    
    # 只有最后一轮才清理
    remaining_after = len(pending) - len(batch)
    print(f"剩余待处理: {remaining_after}")
    
    if cleanup and remaining_after == 0 and not dry_run:
        all_tasks = converter.scan_files()
        cleaned = converter._cleanup_originals([asdict(t) for t in all_tasks if t.status == "completed"])
        print(f"已清理原始文件: {cleaned}")


if __name__ == "__main__":
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    dry_run = "--dry-run" in sys.argv
    cleanup = "--cleanup" in sys.argv
    run_batch(batch_size=batch_size, dry_run=dry_run, cleanup=cleanup)
