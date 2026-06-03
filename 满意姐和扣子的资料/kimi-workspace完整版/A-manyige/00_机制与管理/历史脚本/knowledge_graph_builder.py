#!/usr/bin/env python3
"""
知识图谱构建脚本
将入库的2776个文件建立关联

质量建设：知识关联，非孤立存储
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple

# 配置
INGESTED_DIR = Path("/root/.openclaw/workspace/diary/knowledge-ingest/ingested")
OUTPUT_DIR = Path("/root/.openclaw/workspace/diary/knowledge-graph")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}  # 节点
        self.edges: List[Dict] = []  # 边（关系）
        self.file_index: Dict[str, Path] = {}  # 文件索引
    
    def scan_files(self):
        """扫描所有入库文件"""
        print("🔍 扫描入库文件...")
        
        count = 0
        for file_path in INGESTED_DIR.rglob("*"):
            if file_path.is_file():
                self.file_index[file_path.name] = file_path
                
                # 创建节点
                node_id = file_path.stem
                node_type = self._detect_type(file_path)
                
                self.nodes[node_id] = {
                    "id": node_id,
                    "name": file_path.name,
                    "type": node_type,
                    "path": str(file_path.relative_to(INGESTED_DIR)),
                    "size": file_path.stat().st_size,
                }
                count += 1
        
        print(f"   ✅ 扫描完成: {count} 个文件")
        return count
    
    def _detect_type(self, file_path: Path) -> str:
        """检测文件类型"""
        name = file_path.name.lower()
        
        if name.startswith("memory_"):
            return "conversation"
        elif name.startswith("skill_") or "skill" in name:
            return "skill"
        elif name.endswith(".md"):
            return "document"
        elif name.endswith(".py"):
            return "code"
        elif name.endswith(".json"):
            return "data"
        else:
            return "other"
    
    def extract_relationships(self):
        """提取文件间关系"""
        print("🔗 提取文件关系...")
        
        relationship_count = 0
        
        for node_id, node in self.nodes.items():
            file_path = INGESTED_DIR / node["path"]
            
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # 提取引用关系（简单模式：查找其他文件名）
                for other_id, other_node in self.nodes.items():
                    if other_id == node_id:
                        continue
                    
                    # 如果内容中提到其他文件名，建立引用关系
                    other_name = other_node["name"].replace(".md", "").replace(".py", "")
                    if other_name in content and len(other_name) > 5:
                        self.edges.append({
                            "source": node_id,
                            "target": other_id,
                            "type": "references",
                            "weight": content.count(other_name),
                        })
                        relationship_count += 1
                        
            except Exception as e:
                pass  # 忽略读取错误
        
        print(f"   ✅ 关系提取完成: {relationship_count} 个关系")
        return relationship_count
    
    def build_category_index(self):
        """构建分类索引"""
        print("📚 构建分类索引...")
        
        categories = {}
        
        for node_id, node in self.nodes.items():
            node_type = node["type"]
            
            if node_type not in categories:
                categories[node_type] = []
            
            categories[node_type].append(node_id)
        
        print(f"   ✅ 分类索引完成: {len(categories)} 个类别")
        for cat, items in categories.items():
            print(f"      - {cat}: {len(items)} 个")
        
        return categories
    
    def save_graph(self):
        """保存知识图谱"""
        print("💾 保存知识图谱...")
        
        graph_data = {
            "generated_at": datetime.now().isoformat(),
            "stats": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
            },
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
        }
        
        # 保存完整图谱
        graph_file = OUTPUT_DIR / "knowledge-graph.json"
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        # 保存索引
        index_file = OUTPUT_DIR / "file-index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump({k: str(v) for k, v in self.file_index.items()}, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 图谱已保存: {graph_file}")
        print(f"   ✅ 索引已保存: {index_file}")
    
    def generate_summary(self):
        """生成摘要"""
        print("\n📊 知识图谱摘要")
        print("═══════════════════════════════════════════════════════════")
        print(f"节点总数: {len(self.nodes)}")
        print(f"关系总数: {len(self.edges)}")
        
        # 按类型统计
        type_counts = {}
        for node in self.nodes.values():
            node_type = node["type"]
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        print("\n按类型分布:")
        for node_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  • {node_type}: {count} 个")
        
        print("═══════════════════════════════════════════════════════════")


def main():
    """主函数"""
    print("🚀 启动知识图谱构建...")
    print()
    
    builder = KnowledgeGraphBuilder()
    
    # 1. 扫描文件
    file_count = builder.scan_files()
    
    # 2. 提取关系
    if file_count > 0:
        builder.extract_relationships()
        
        # 3. 构建分类索引
        builder.build_category_index()
        
        # 4. 保存图谱
        builder.save_graph()
        
        # 5. 生成摘要
        builder.generate_summary()
    
    print()
    print("✅ 知识图谱构建完成")


if __name__ == "__main__":
    main()
