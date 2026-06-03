#!/usr/bin/env python3
"""
知识入库准备脚本
整理394文件清单，按重要性排序
"""

import json
from pathlib import Path
from datetime import datetime

# 知识库目录
KNOWLEDGE_DIRS = [
    "~/.openclaw/workspace/memory",
    "~/.openclaw/workspace/docs", 
    "~/.openclaw/workspace/diary",
    "~/.openclaw/workspace/skills",
]

# 重要性评分规则
IMPORTANCE_RULES = {
    "SOUL.md": 100,
    "USER.md": 100,
    "AGENTS.md": 95,
    "MEMORY.md": 95,
    "HEARTBEAT.md": 90,
    "SUPER_RED_LINES.md": 90,
    "IDENTITY.md": 85,
    "SKILL.md": 80,
    "execution": 75,
    "errors": 70,
    "audit": 70,
    ".md": 50,  # 默认markdown文件
    ".json": 40,
    ".py": 30,
    ".txt": 20,
}


def calculate_importance(file_path: Path) -> int:
    """计算文件重要性分数"""
    name = file_path.name
    
    # 直接匹配
    if name in IMPORTANCE_RULES:
        return IMPORTANCE_RULES[name]
    
    # 父目录匹配
    for parent in file_path.parents:
        if parent.name in IMPORTANCE_RULES:
            return IMPORTANCE_RULES[parent.name]
    
    # 后缀匹配
    suffix = file_path.suffix
    if suffix in IMPORTANCE_RULES:
        return IMPORTANCE_RULES[suffix]
    
    return 10  # 默认最低


def scan_knowledge_files():
    """扫描所有知识文件"""
    files = []
    
    for dir_path in KNOWLEDGE_DIRS:
        path = Path(dir_path).expanduser()
        if not path.exists():
            continue
        
        for file_path in path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                importance = calculate_importance(file_path)
                files.append({
                    "path": str(file_path.relative_to(Path("~/.openclaw/workspace").expanduser())),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "importance": importance,
                })
    
    # 按重要性排序
    files.sort(key=lambda x: (-x["importance"], x["path"]))
    return files


def generate_inventory():
    """生成清单"""
    files = scan_knowledge_files()
    
    inventory = {
        "generated_at": datetime.now().isoformat(),
        "total_files": len(files),
        "by_importance": {},
        "files": files[:100],  # 前100个
    }
    
    # 按重要性分组统计
    for imp in [100, 95, 90, 85, 80, 75, 70, 50, 40, 30, 20, 10]:
        count = sum(1 for f in files if f["importance"] == imp)
        if count > 0:
            inventory["by_importance"][imp] = count
    
    # 保存清单
    output_dir = Path("~/.openclaw/workspace/diary/knowledge-ingest").expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "inventory.json", "w") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    return inventory


if __name__ == "__main__":
    inv = generate_inventory()
    print(f"📚 知识文件清单生成完成")
    print(f"   总数: {inv['total_files']} 个文件")
    print(f"   前100个重要文件已记录")
    
    print("\n按重要性分布:")
    for imp, count in sorted(inv["by_importance"].items(), reverse=True):
        print(f"   重要性 {imp}: {count} 个文件")
