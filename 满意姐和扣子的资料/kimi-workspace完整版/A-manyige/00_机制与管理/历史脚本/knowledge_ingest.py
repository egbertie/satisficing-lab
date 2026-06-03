#!/usr/bin/env python3
"""
知识入库执行脚本
按重要性顺序处理文件入库

质量第一：逐文件验证，确保入库准确
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# 配置
INVENTORY_FILE = Path("~/.openclaw/workspace/diary/knowledge-ingest/inventory.json").expanduser()
OUTPUT_DIR = Path("~/.openclaw/workspace/diary/knowledge-ingest/ingested").expanduser()
WORKSPACE = Path("~/.openclaw/workspace").expanduser()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_inventory():
    """加载清单"""
    with open(INVENTORY_FILE, 'r') as f:
        return json.load(f)


def ingest_file(file_info: dict) -> dict:
    """
    入库单个文件
    
    Returns:
        入库记录
    """
    src_path = WORKSPACE / file_info["path"]
    
    if not src_path.exists():
        return {
            "path": file_info["path"],
            "status": "failed",
            "error": "源文件不存在",
            "timestamp": datetime.now().isoformat(),
        }
    
    # 复制到入库目录
    rel_path = Path(file_info["path"])
    dst_path = OUTPUT_DIR / rel_path.name
    
    # 避免覆盖，添加序号
    counter = 1
    original_dst = dst_path
    while dst_path.exists():
        dst_path = original_dst.with_suffix(f".{counter}{original_dst.suffix}")
        counter += 1
    
    try:
        shutil.copy2(src_path, dst_path)
        return {
            "path": file_info["path"],
            "status": "success",
            "ingested_path": str(dst_path.relative_to(OUTPUT_DIR)),
            "size": file_info["size"],
            "importance": file_info["importance"],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "path": file_info["path"],
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def ingest_by_importance(min_importance: int = 100):
    """
    按重要性入库
    
    Args:
        min_importance: 最小重要性分数
    """
    inventory = load_inventory()
    
    # 筛选符合条件的文件
    files_to_ingest = [
        f for f in inventory["files"]
        if f["importance"] >= min_importance
    ]
    
    results = []
    for file_info in files_to_ingest:
        result = ingest_file(file_info)
        results.append(result)
        
        status = "✅" if result["status"] == "success" else "❌"
        print(f"{status} {file_info['path']} (重要性: {file_info['importance']})")
    
    # 保存入库记录
    log_file = OUTPUT_DIR / f"ingest-log-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "min_importance": min_importance,
            "total": len(files_to_ingest),
            "success": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 入库完成: {len(results)} 个文件")
    print(f"   成功: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"   失败: {sum(1 for r in results if r['status'] == 'failed')}")
    print(f"   记录: {log_file}")


if __name__ == "__main__":
    import sys
    
    # 默认处理重要性100的文件
    min_imp = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    print(f"🚀 启动知识入库（重要性 ≥ {min_imp}）...\n")
    ingest_by_importance(min_imp)
