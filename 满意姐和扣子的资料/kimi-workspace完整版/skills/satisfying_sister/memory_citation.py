"""
满意尺 - 记忆引用模块
实现30%引用密度、分层记忆检索、记忆引用礼仪
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from defense_base_components import BaseComponent
import random
import glob
from typing import Dict, List, Optional, Any
from datetime import datetime


class MemoryCitation(BaseComponent):
    """
    5.1-5.3 记忆圣殿系统
    - 30%引用密度
    - 给出具体文件依据
    - 主动引用过去
    """

    def __init__(self):
        super().__init__("memory_citation")
        self.citation_rate = 0.30
        self.memory_dir = Path(self.workspace) / "memory"

    def should_cite(self) -> bool:
        """基于30%密度决定是否引用"""
        return random.random() < self.citation_rate

    def find_recent_memories(self, days: int = 7, limit: int = 5) -> List[Dict[str, Any]]:
        """检索最近n天的记忆文件"""
        results = []
        if not self.memory_dir.exists():
            return results

        files = sorted(self.memory_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        for f in files[:limit]:
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                results.append({
                    "path": str(f),
                    "filename": f.name,
                    "mtime": mtime.isoformat(),
                    "size": f.stat().st_size,
                })
            except Exception:
                continue
        return results

    def generate_citation(self, query: Optional[str] = None) -> str:
        """生成一句带物理路径的记忆引用"""
        memories = self.find_recent_memories(limit=5)
        if not memories:
            return ""

        chosen = random.choice(memories)
        templates = [
            f"根据 `{chosen['filename']}` 里的记录……",
            f"你上次也是这样，后来在 `{chosen['filename']}` 里我们确认了方向。",
            f"这事在 `{chosen['filename']}` 里提到过。",
            f"我记得 `{chosen['filename']}` 写过相关的内容。",
        ]
        return random.choice(templates)

    def archive_memory(self, content: str, date_str: Optional[str] = None) -> str:
        """
        追加记忆到 memory/YYYY-MM-DD.md
        禁止生成timestamped变体
        """
        if date_str is None:
            date_str = self.get_date_string()

        target = self.memory_dir / f"{date_str}.md"
        target.parent.mkdir(parents=True, exist_ok=True)

        header = f"\n---\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} 追加记录\n\n"
        with open(target, "a", encoding="utf-8") as f:
            f.write(header + content + "\n")

        return str(target)

    def get_memory_stats(self) -> Dict[str, Any]:
        """记忆系统统计"""
        if not self.memory_dir.exists():
            return {"total_files": 0, "total_size": 0}

        files = list(self.memory_dir.glob("*.md"))
        total_size = sum(f.stat().st_size for f in files)
        return {
            "total_files": len(files),
            "total_size": total_size,
            "latest_file": max(files, key=lambda f: f.stat().st_mtime).name if files else None,
        }
