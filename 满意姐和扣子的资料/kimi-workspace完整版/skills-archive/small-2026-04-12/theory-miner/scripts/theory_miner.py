#!/usr/bin/env python3
"""
theory-miner - 理论挖掘器
真正实现版本

功能:
- 从文档中提取理论框架
- 识别核心概念和关系
- 构建知识图谱
- 支持理论溯源和引用
- 生成理论摘要

作者: 满意妞
版本: 1.0.0-real
日期: 2026-04-03
"""

import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
import hashlib


class TheoryType(Enum):
    """理论类型"""
    DECISION_MODEL = "decision_model"      # 决策模型
    FRAMEWORK = "framework"                # 分析框架
    PRINCIPLE = "principle"                # 原则/原理
    METHODOLOGY = "methodology"            # 方法论
    CONCEPT = "concept"                    # 核心概念
    CASE_PATTERN = "case_pattern"          # 案例模式


class SourceType(Enum):
    """来源类型"""
    ACADEMIC = "academic"                  # 学术论文
    BOOK = "book"                          # 书籍
    ARTICLE = "article"                    # 文章/报告
    CASE = "case"                          # 案例研究
    EXPERT = "expert"                      # 专家观点
    INTERNAL = "internal"                  # 内部研究


@dataclass
class Concept:
    """概念定义"""
    name: str
    definition: str
    aliases: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)


@dataclass
class Source:
    """理论来源"""
    title: str
    author: str
    source_type: str
    year: Optional[int] = None
    url: str = ""
    citation: str = ""


@dataclass
class TheoryNode:
    """理论节点"""
    theory_id: str
    name: str
    theory_type: str
    description: str
    core_concepts: List[Concept]
    source: Source
    tags: List[str] = field(default_factory=list)
    related_theories: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass
class TheoryRelation:
    """理论关系"""
    from_theory: str
    to_theory: str
    relation_type: str           # extends/depends_on/conflicts_with/similar_to
    description: str = ""


@dataclass
class ExtractionResult:
    """提取结果"""
    document_id: str
    theories_found: List[TheoryNode]
    concepts_found: List[Concept]
    relations_found: List[TheoryRelation]
    confidence_score: float
    extraction_notes: List[str]


class TheoryMiner:
    """理论挖掘器"""
    
    # 理论类型关键词映射
    THEORY_PATTERNS = {
        TheoryType.DECISION_MODEL: [
            r"决策模型|决策框架|decision model|decision framework",
            r"满意解|最优解|satisficing|optimizing",
            r"前景理论|prospect theory",
            r"双系统|system 1.*system 2"
        ],
        TheoryType.FRAMEWORK: [
            r"分析框架|framework|模型|model",
            r"五维|四象限|SWOT|PEST|Porter",
            r"方法论|methodology|approach"
        ],
        TheoryType.PRINCIPLE: [
            r"原则|principle|原理|axiom",
            r"第一性原理|first principles",
            r"知行合一|长期主义"
        ],
        TheoryType.METHODOLOGY: [
            r"方法|method|流程|process",
            r"SOP|标准作业|best practice",
            r"敏捷|agile|精益|lean"
        ],
        TheoryType.CONCEPT: [
            r"概念|concept|定义|definition",
            r"核心|core|关键|key"
        ],
        TheoryType.CASE_PATTERN: [
            r"模式|pattern|规律|regularity",
            r"典型案例|标杆|benchmark",
            r"成功因素|失败原因"
        ]
    }
    
    # 核心概念提取模式
    CONCEPT_PATTERNS = [
        r"【([^】]+)】([^\n]+)",                    # 【概念名】定义
        r"\*\*([^*]+)\*\*[:：]\s*([^\n]+)",       # **概念**: 定义
        r"`([^`]+)`[:：]\s*([^\n]+)",             # `概念`: 定义
        r"(?:^|\n)([^\n:]+)[:：]\s*([^\n]{10,})", # 概念: 长定义
    ]
    
    def __init__(self, data_dir: Optional[str] = None):
        """初始化"""
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.theories_file = self.data_dir / "theories.json"
        self.relations_file = self.data_dir / "theory_relations.json"
        
        self.theories: Dict[str, TheoryNode] = self._load_theories()
        self.relations: List[TheoryRelation] = self._load_relations()
    
    def _load_theories(self) -> Dict[str, TheoryNode]:
        """加载理论库"""
        if not self.theories_file.exists():
            return {}
        
        with open(self.theories_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {tid: self._dict_to_theory(t) for tid, t in data.items()}
    
    def _save_theories(self):
        """保存理论库"""
        with open(self.theories_file, 'w', encoding='utf-8') as f:
            data = {tid: self._theory_to_dict(t) for tid, t in self.theories.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_relations(self) -> List[TheoryRelation]:
        """加载关系"""
        if not self.relations_file.exists():
            return []
        
        with open(self.relations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [TheoryRelation(**r) for r in data]
    
    def _save_relations(self):
        """保存关系"""
        with open(self.relations_file, 'w', encoding='utf-8') as f:
            data = [{'from_theory': r.from_theory, 'to_theory': r.to_theory,
                    'relation_type': r.relation_type, 'description': r.description}
                   for r in self.relations]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _theory_to_dict(self, theory: TheoryNode) -> Dict:
        """理论转字典"""
        return {
            'theory_id': theory.theory_id,
            'name': theory.name,
            'theory_type': theory.theory_type,
            'description': theory.description,
            'core_concepts': [{'name': c.name, 'definition': c.definition,
                              'aliases': c.aliases, 'related_concepts': c.related_concepts}
                             for c in theory.core_concepts],
            'source': {'title': theory.source.title, 'author': theory.source.author,
                      'source_type': theory.source.source_type, 'year': theory.source.year,
                      'url': theory.source.url, 'citation': theory.source.citation},
            'tags': theory.tags,
            'related_theories': theory.related_theories,
            'applications': theory.applications,
            'created_at': theory.created_at,
            'updated_at': theory.updated_at
        }
    
    def _dict_to_theory(self, data: Dict) -> TheoryNode:
        """字典转理论"""
        return TheoryNode(
            theory_id=data['theory_id'],
            name=data['name'],
            theory_type=data['theory_type'],
            description=data['description'],
            core_concepts=[Concept(**c) for c in data.get('core_concepts', [])],
            source=Source(**data.get('source', {})),
            tags=data.get('tags', []),
            related_theories=data.get('related_theories', []),
            applications=data.get('applications', []),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )
    
    def _generate_id(self, name: str) -> str:
        """生成理论ID"""
        hash_obj = hashlib.md5(name.encode())
        return f"THEORY-{hash_obj.hexdigest()[:8].upper()}"
    
    def extract_from_document(self, document_path: str, 
                             source: Optional[Source] = None) -> ExtractionResult:
        """从文档提取理论"""
        doc_path = Path(document_path)
        if not doc_path.exists():
            raise FileNotFoundError(f"文档不存在: {document_path}")
        
        # 读取文档
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成文档ID
        doc_id = hashlib.md5(content.encode()).hexdigest()[:12]
        
        # 提取理论
        theories = []
        concepts = []
        notes = []
        
        # 1. 识别理论类型和名称
        theory_candidates = self._identify_theories(content)
        
        # 2. 提取概念定义
        concept_candidates = self._extract_concepts(content)
        concepts.extend(concept_candidates)
        
        # 3. 构建理论节点
        for theory_name, theory_type, description in theory_candidates:
            theory_id = self._generate_id(theory_name)
            
            # 查找相关概念
            related_concepts = [c for c in concept_candidates 
                              if c.name in description or c.name in theory_name]
            
            # 查找应用场景
            applications = self._extract_applications(content, theory_name)
            
            theory = TheoryNode(
                theory_id=theory_id,
                name=theory_name,
                theory_type=theory_type,
                description=description,
                core_concepts=related_concepts[:5],  # 最多5个核心概念
                source=source or Source(
                    title=doc_path.name,
                    author="Unknown",
                    source_type=SourceType.INTERNAL.value
                ),
                tags=self._extract_tags(content, theory_name),
                applications=applications,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            theories.append(theory)
            self.theories[theory_id] = theory
        
        # 4. 提取理论关系
        relations = self._extract_relations(content, theories)
        
        # 5. 计算置信度
        confidence = self._calculate_confidence(theories, concepts, content)
        
        # 保存
        self._save_theories()
        self._save_relations()
        
        return ExtractionResult(
            document_id=doc_id,
            theories_found=theories,
            concepts_found=concepts,
            relations_found=relations,
            confidence_score=confidence,
            extraction_notes=notes
        )
    
    def _identify_theories(self, content: str) -> List[Tuple[str, str, str]]:
        """识别理论候选"""
        theories = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 匹配标题模式
            for theory_type, patterns in self.THEORY_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # 提取理论名称（通常是前一行或当前行）
                        name = self._extract_theory_name(line, lines, i)
                        description = self._extract_description(lines, i)
                        
                        if name and len(description) > 20:
                            theories.append((name, theory_type.value, description))
                        break
        
        # 去重
        seen = set()
        unique = []
        for t in theories:
            if t[0] not in seen:
                seen.add(t[0])
                unique.append(t)
        
        return unique[:10]  # 最多10个理论
    
    def _extract_theory_name(self, line: str, lines: List[str], idx: int) -> str:
        """提取理论名称"""
        # 如果当前行是标题，直接使用
        if line.strip().startswith('#') or line.strip().startswith('##'):
            return re.sub(r'^#+\s*', '', line).strip()
        
        # 否则看前一行
        if idx > 0:
            prev = lines[idx-1].strip()
            if prev and not prev.startswith('-') and not prev.startswith('*'):
                return prev[:50]
        
        return line.strip()[:50]
    
    def _extract_description(self, lines: List[str], start_idx: int) -> str:
        """提取描述"""
        description = []
        for i in range(start_idx, min(start_idx + 5, len(lines))):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                description.append(line)
        return ' '.join(description)[:200]
    
    def _extract_concepts(self, content: str) -> List[Concept]:
        """提取概念"""
        concepts = []
        seen = set()
        
        for pattern in self.CONCEPT_PATTERNS:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    name, definition = match[0].strip(), match[1].strip()
                    
                    # 过滤无效概念
                    if (len(name) < 2 or len(name) > 20 or 
                        len(definition) < 10 or name in seen):
                        continue
                    
                    seen.add(name)
                    concepts.append(Concept(
                        name=name,
                        definition=definition[:200],
                        aliases=[],
                        related_concepts=[]
                    ))
        
        return concepts[:20]  # 最多20个概念
    
    def _extract_applications(self, content: str, theory_name: str) -> List[str]:
        """提取应用场景"""
        applications = []
        
        # 查找理论名称附近的内容
        idx = content.find(theory_name)
        if idx >= 0:
            context = content[idx:idx+500]
            
            # 匹配应用场景
            patterns = [
                r"适用[:：]\s*([^\n]+)",
                r"应用[:：]\s*([^\n]+)",
                r"场景[:：]\s*([^\n]+)",
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, context)
                applications.extend(matches)
        
        return applications[:3]
    
    def _extract_tags(self, content: str, theory_name: str) -> List[str]:
        """提取标签"""
        tags = []
        
        # 从内容中提取关键词作为标签
        keywords = [
            "决策", "匹配", "合伙人", "融资", "股权",
            "硬科技", "芯片", "生物医药", "AI",
            "满意解", "最优解", "直觉", "理性"
        ]
        
        for keyword in keywords:
            if keyword in content or keyword in theory_name:
                tags.append(keyword)
        
        return tags[:5]
    
    def _extract_relations(self, content: str, theories: List[TheoryNode]) -> List[TheoryRelation]:
        """提取理论关系"""
        relations = []
        theory_names = [t.name for t in theories]
        
        # 简单的共现关系
        for i, t1 in enumerate(theories):
            for t2 in theories[i+1:]:
                # 检查两个理论是否在相近位置出现
                idx1 = content.find(t1.name)
                idx2 = content.find(t2.name)
                
                if abs(idx1 - idx2) < 500:  # 500字符内
                    relations.append(TheoryRelation(
                        from_theory=t1.theory_id,
                        to_theory=t2.theory_id,
                        relation_type="related_to",
                        description="在同一上下文中提及"
                    ))
        
        return relations
    
    def _calculate_confidence(self, theories: List[TheoryNode], 
                             concepts: List[Concept], content: str) -> float:
        """计算提取置信度"""
        if not theories:
            return 0.0
        
        # 基于多个因素计算
        scores = []
        
        # 1. 理论数量合理性
        if 1 <= len(theories) <= 10:
            scores.append(0.3)
        
        # 2. 概念数量合理性
        if 3 <= len(concepts) <= 30:
            scores.append(0.3)
        
        # 3. 内容长度
        if len(content) > 500:
            scores.append(0.2)
        
        # 4. 理论有描述
        theories_with_desc = sum(1 for t in theories if len(t.description) > 50)
        if theories_with_desc >= len(theories) * 0.5:
            scores.append(0.2)
        
        return sum(scores)
    
    def get_theory(self, theory_id: str) -> Optional[TheoryNode]:
        """获取理论"""
        return self.theories.get(theory_id)
    
    def search_theories(self, query: str, theory_type: Optional[str] = None) -> List[Tuple[TheoryNode, float]]:
        """搜索理论"""
        results = []
        query_lower = query.lower()
        
        for theory in self.theories.values():
            # 类型过滤
            if theory_type and theory.theory_type != theory_type:
                continue
            
            # 计算匹配度
            score = 0.0
            
            # 名称匹配
            if query_lower in theory.name.lower():
                score += 0.4
            
            # 描述匹配
            if query_lower in theory.description.lower():
                score += 0.3
            
            # 标签匹配
            for tag in theory.tags:
                if query_lower in tag.lower():
                    score += 0.2
                    break
            
            # 概念匹配
            for concept in theory.core_concepts:
                if query_lower in concept.name.lower():
                    score += 0.1
                    break
            
            if score > 0:
                results.append((theory, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_related_theories(self, theory_id: str) -> List[TheoryNode]:
        """获取相关理论"""
        theory = self.get_theory(theory_id)
        if not theory:
            return []
        
        related = []
        for rid in theory.related_theories:
            t = self.get_theory(rid)
            if t:
                related.append(t)
        
        return related
    
    def generate_theory_map(self, tag: Optional[str] = None) -> str:
        """生成理论图谱（Markdown格式）"""
        theories = list(self.theories.values())
        
        if tag:
            theories = [t for t in theories if tag in t.tags]
        
        lines = ["# 理论图谱\n"]
        
        # 按类型分组
        by_type = {}
        for t in theories:
            by_type.setdefault(t.theory_type, []).append(t)
        
        for ttype, tlist in by_type.items():
            lines.append(f"\n## {ttype}\n")
            for t in tlist:
                lines.append(f"- **{t.name}**: {t.description[:100]}...")
        
        return '\n'.join(lines)
    
    def export_theory_summary(self, theory_id: str) -> str:
        """导出理论摘要"""
        theory = self.get_theory(theory_id)
        if not theory:
            return "理论不存在"
        
        lines = [
            f"# {theory.name}",
            "",
            f"**类型**: {theory.theory_type}",
            f"**来源**: {theory.source.title} ({theory.source.author})",
            "",
            "## 描述",
            theory.description,
            "",
            "## 核心概念"
        ]
        
        for concept in theory.core_concepts[:5]:
            lines.append(f"- **{concept.name}**: {concept.definition[:100]}")
        
        if theory.applications:
            lines.extend(["", "## 应用场景"])
            for app in theory.applications:
                lines.append(f"- {app}")
        
        return '\n'.join(lines)
    
    def get_statistics(self) -> Dict:
        """获取统计"""
        return {
            'total_theories': len(self.theories),
            'total_concepts': sum(len(t.core_concepts) for t in self.theories.values()),
            'total_relations': len(self.relations),
            'by_type': {
                ttype.value: len([t for t in self.theories.values() if t.theory_type == ttype.value])
                for ttype in TheoryType
            }
        }


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Theory Miner - 理论挖掘器')
    parser.add_argument('--extract', metavar='FILE',
                       help='从文档提取理论')
    parser.add_argument('--source-title', default='',
                       help='来源标题')
    parser.add_argument('--source-author', default='',
                       help='来源作者')
    parser.add_argument('--search', metavar='QUERY',
                       help='搜索理论')
    parser.add_argument('--type', choices=[t.value for t in TheoryType],
                       help='理论类型筛选')
    parser.add_argument('--get', metavar='THEORY_ID',
                       help='获取理论详情')
    parser.add_argument('--map', action='store_true',
                       help='生成理论图谱')
    parser.add_argument('--tag', help='按标签筛选')
    parser.add_argument('--stats', action='store_true',
                       help='查看统计')
    parser.add_argument('--data-dir', help='数据目录')
    
    args = parser.parse_args()
    
    try:
        miner = TheoryMiner(args.data_dir)
        
        if args.extract:
            source = None
            if args.source_title:
                source = Source(
                    title=args.source_title,
                    author=args.source_author or "Unknown",
                    source_type=SourceType.INTERNAL.value
                )
            
            result = miner.extract_from_document(args.extract, source)
            print(f"✅ 提取完成")
            print(f"   发现理论: {len(result.theories_found)}")
            print(f"   发现概念: {len(result.concepts_found)}")
            print(f"   置信度: {result.confidence_score:.1%}")
            
            for t in result.theories_found:
                print(f"\n   • [{t.theory_id}] {t.name} ({t.theory_type})")
        
        elif args.search:
            results = miner.search_theories(args.search, args.type)
            if not results:
                print(f"未找到匹配'{args.search}'的理论")
            else:
                print(f"找到 {len(results)} 个相关理论:")
                for theory, score in results[:10]:
                    print(f"  [{theory.theory_id}] {theory.name} (匹配度: {score:.2%})")
        
        elif args.get:
            summary = miner.export_theory_summary(args.get)
            print(summary)
        
        elif args.map:
            map_md = miner.generate_theory_map(args.tag)
            print(map_md)
        
        elif args.stats:
            stats = miner.get_statistics()
            print("=" * 50)
            print("理论库统计")
            print("=" * 50)
            print(f"总理论数: {stats['total_theories']}")
            print(f"总概念数: {stats['total_concepts']}")
            print(f"总关系数: {stats['total_relations']}")
            print("\n按类型分布:")
            for ttype, count in stats['by_type'].items():
                if count > 0:
                    print(f"  {ttype}: {count}")
        
        else:
            stats = miner.get_statistics()
            print(f"理论库: {stats['total_theories']} 个理论, {stats['total_concepts']} 个概念")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
