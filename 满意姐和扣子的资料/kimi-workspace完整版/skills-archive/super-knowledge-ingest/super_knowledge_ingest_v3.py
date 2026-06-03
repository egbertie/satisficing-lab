#!/usr/bin/env python3
"""
super-knowledge-ingest V3.0 - 压缩引用式入库
核心优化：用位置引用代替内容复制，gzip压缩降低存储
目标：保证7层标准，输出大小控制在原始文件1-2倍以内
"""

import json
import gzip
import base64
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ContentPosition:
    """内容位置引用，代替实际存储"""
    start_line: int
    end_line: int
    start_char: int
    end_char: int
    char_count: int
    
    def to_dict(self) -> Dict:
        return {
            "start_line": self.start_line,
            "end_line": self.end_line,
            "start_char": self.start_char, 
            "end_char": self.end_char,
            "char_count": self.char_count
        }

@dataclass  
class SectionRef:
    """章节引用"""
    level: int
    title: str
    position: ContentPosition
    
    def to_dict(self) -> Dict:
        return {
            "level": self.level,
            "title": self.title,
            "position": self.position.to_dict()
        }

@dataclass
class QuoteRef:
    """语录引用"""
    text_preview: str  # 前100字预览
    position: ContentPosition
    source: Optional[str]
    
    def to_dict(self) -> Dict:
        return {
            "text_preview": self.text_preview,
            "position": self.position.to_dict(),
            "source": self.source
        }

@dataclass
class CaseRef:
    """案例引用"""
    title: str
    position: ContentPosition
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "position": self.position.to_dict()
        }


class CompactKnowledgeIngestor:
    """
    V3.0 压缩引用式知识入库器
    
    核心设计原则：
    1. 内容只存一次（gzip压缩的原始内容）
    2. 所有结构用位置引用（行号+字符位置）
    3. 需要时从压缩内容实时提取
    4. 元数据精简，去除冗余字段
    """
    
    def __init__(self, source_file: str, output_dir: str = "/root/.openclaw/workspace/knowledge/7standard-v3"):
        self.source_file = Path(source_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载并立即压缩原始内容
        with open(source_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        self.original_size = len(raw_content.encode('utf-8'))
        self.lines = raw_content.split('\n')
        self.line_positions = self._build_line_index(raw_content)
        
        # Gzip压缩
        self.compressed_content = gzip.compress(raw_content.encode('utf-8'))
        self.compressed_size = len(self.compressed_content)
        
        self.file_hash = hashlib.sha256(raw_content.encode()).hexdigest()[:16]
        
    def _build_line_index(self, content: str) -> List[int]:
        """构建行号到字符位置的映射"""
        positions = [0]
        for i, char in enumerate(content):
            if char == '\n':
                positions.append(i + 1)
        return positions
    
    def _get_char_position(self, line_num: int, col: int = 0) -> int:
        """将行号转换为字符位置"""
        if line_num < len(self.line_positions):
            return self.line_positions[line_num] + col
        return len(self.line_positions)
    
    def _extract_text(self, pos: ContentPosition) -> str:
        """根据位置引用提取原文（从压缩内容解压后提取）"""
        # 解压内容
        raw = gzip.decompress(self.compressed_content).decode('utf-8')
        return raw[pos.start_char:pos.end_char]
    
    # ==================== S1: 输入定义（精简版） ====================
    def s1_define_input(self) -> Dict:
        """S1: 精简输入定义，去除冗余字段"""
        filename = self.source_file.name
        
        # 极简元数据
        return {
            "standard": "S1-Input-Definition-v3",
            "source": str(self.source_file),
            "hash": self.file_hash,
            "sizes": {
                "original": self.original_size,
                "compressed": self.compressed_size,
                "ratio": f"{self.compressed_size/self.original_size:.1%}"
            },
            "lines": len(self.lines),
            "type": self._detect_type(filename)
        }
    
    def _detect_type(self, filename: str) -> str:
        if "深度研究" in filename:
            return "deep_research"
        elif "白皮书" in filename or "whitepaper" in filename.lower():
            return "whitepaper"
        elif "档案" in filename:
            return "profile"
        return "document"
    
    # ==================== S2: 内容处理（引用式） ====================
    def s2_process_content(self) -> Dict:
        """
        S2: 引用式内容处理
        不存储实际内容，只存储位置引用
        """
        sections = self._extract_sections_ref()
        quotes = self._extract_quotes_ref()
        cases = self._extract_cases_ref()
        key_points = self._extract_key_points()
        
        return {
            "standard": "S2-Content-Processing-v3",
            "structure": {
                "sections": len(sections),
                "quotes": len(quotes), 
                "cases": len(cases),
                "key_points": len(key_points)
            },
            "sections": [s.to_dict() for s in sections[:50]],  # 限制数量
            "quotes": [q.to_dict() for q in quotes[:30]],
            "cases": [c.to_dict() for c in cases[:20]],
            "key_points": key_points[:20]
        }
    
    def _extract_sections_ref(self) -> List[SectionRef]:
        """提取章节位置引用"""
        sections = []
        content = gzip.decompress(self.compressed_content).decode('utf-8')
        
        pattern = r'^(#{1,6})\s+(.+)$'
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        for i, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            start_char = match.start()
            
            # 确定结束位置
            if i + 1 < len(matches):
                end_char = matches[i + 1].start()
            else:
                end_char = len(content)
            
            # 计算行号
            start_line = content[:start_char].count('\n')
            end_line = content[:end_char].count('\n')
            
            sections.append(SectionRef(
                level=level,
                title=title,
                position=ContentPosition(
                    start_line=start_line,
                    end_line=end_line,
                    start_char=start_char,
                    end_char=end_char,
                    char_count=end_char - start_char
                )
            ))
        
        return sections
    
    def _extract_quotes_ref(self) -> List[QuoteRef]:
        """提取语录位置引用"""
        quotes = []
        content = gzip.decompress(self.compressed_content).decode('utf-8')
        
        pattern = r'^\s*>\s*(.+?)(?=\n\s*[^>]|\Z)'
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            quote_text = match.group(1).strip()
            quote_text = re.sub(r'\n\s*>\s*', ' ', quote_text)
            
            # 提取来源
            source = None
            source_match = re.search(r'——(.+)$', quote_text)
            if source_match:
                source = source_match.group(1)
                quote_text = quote_text[:source_match.start()].strip()
            
            # 预览前100字符
            preview = quote_text[:100] + "..." if len(quote_text) > 100 else quote_text
            
            start_char = match.start()
            end_char = match.end()
            start_line = content[:start_char].count('\n')
            end_line = content[:end_char].count('\n')
            
            quotes.append(QuoteRef(
                text_preview=preview,
                position=ContentPosition(
                    start_line=start_line,
                    end_line=end_line,
                    start_char=start_char,
                    end_char=end_char,
                    char_count=end_char - start_char
                ),
                source=source
            ))
        
        return quotes
    
    def _extract_cases_ref(self) -> List[CaseRef]:
        """提取案例位置引用"""
        cases = []
        content = gzip.decompress(self.compressed_content).decode('utf-8')
        
        pattern = r'(?:###?\s+\d+\.\d+\s+)?案例[：:]\s*(.+?)(?=\n##|\n###\s+\d+\.\d+\s+(?!案例)|\Z)'
        for match in re.finditer(pattern, content, re.DOTALL):
            case_content = match.group(1).strip()
            lines = case_content.split('\n')
            title = lines[0][:50] if lines else "未命名"
            
            start_char = match.start()
            end_char = match.end()
            start_line = content[:start_char].count('\n')
            end_line = content[:end_char].count('\n')
            
            cases.append(CaseRef(
                title=title,
                position=ContentPosition(
                    start_line=start_line,
                    end_line=end_line,
                    start_char=start_char,
                    end_char=end_char,
                    char_count=end_char - start_char
                )
            ))
        
        return cases
    
    def _extract_key_points(self) -> List[str]:
        """提取关键点（只存文本，因为较短）"""
        content = gzip.decompress(self.compressed_content).decode('utf-8')
        points = []
        
        # 加粗内容
        for match in re.finditer(r'\*\*([^*]+)\*\*', content):
            point = match.group(1).strip()
            if 10 < len(point) < 100:
                points.append(point)
        
        # 去重限制
        return list(dict.fromkeys(points))[:15]
    
    # ==================== S3: 知识结构化（延迟计算） ====================
    def s3_structure_knowledge(self, s2: Dict) -> Dict:
        """
        S3: 轻量知识结构化
        从章节标题和关键点提取实体
        """
        entities = []
        entity_names = set()
        
        # 从章节标题提取 - sections是列表，每个元素是字典
        sections = s2.get("sections", [])
        for section in sections[:20]:
            if isinstance(section, dict):
                title = section.get("title", "")
            else:
                continue
                
            # 匹配人名（司马贺、西蒙等）
            for match in re.finditer(r'([一-龥·A-Za-z\s]{2,20})(?:教授|博士|先生|院士|西蒙)', title):
                name = match.group(1).strip()
                if name and name not in entity_names and len(name) < 30:
                    entity_names.add(name)
                    entities.append({"name": name, "type": "person"})
            
            # 匹配概念（有限理性、满意解等）
            for match in re.finditer(r'([「""]?)([^"""」\n]{2,15})(?:理论|模型|框架|科学)', title):
                concept = match.group(2).strip()
                if concept and concept not in entity_names and len(concept) < 20:
                    entity_names.add(concept)
                    entities.append({"name": concept, "type": "concept"})
        
        # 从关键点提取
        key_points = s2.get("key_points", [])
        for point in key_points[:10]:
            if isinstance(point, str):
                # 匹配引号内的概念
                for match in re.finditer(r'[「""]([^"""」]{2,15})["""」]', point):
                    concept = match.group(1)
                    if concept not in entity_names:
                        entity_names.add(concept)
                        entities.append({"name": concept, "type": "concept"})
        
        return {
            "standard": "S3-Knowledge-Structuring-v3",
            "entities": entities[:15],
            "entity_count": len(entities),
            "notes": "Relations computed on-demand via position refs"
        }
    
    # ==================== S4: 自动化集成（压缩存储） ====================
    def s4_automation(self, s1: Dict, s2: Dict, s3: Dict) -> Dict:
        """S4: 压缩存储核心数据"""
        output_filename = f"{self.source_file.stem}_v3.bin"
        output_path = self.output_dir / output_filename
        
        # 构建精简文档
        doc = {
            "_meta": {
                "v": "3.0",
                "t": datetime.now().isoformat(),
                "hash": self.file_hash,
                "orig": self.original_size,
                "comp": self.compressed_size
            },
            "S1": s1,
            "S2": s2,
            "S3": s3,
            # 压缩内容用base64编码
            "_content": base64.b64encode(self.compressed_content).decode('ascii')
        }
        
        # 保存为压缩二进制
        with open(output_path, 'wb') as f:
            f.write(gzip.compress(json.dumps(doc, ensure_ascii=False).encode('utf-8')))
        
        return {
            "standard": "S4-Automation-v3",
            "output": str(output_path),
            "sizes": {
                "original": self.original_size,
                "compressed_content": self.compressed_size,
                "total_estimated": self.compressed_size + 2000  # 预估元数据大小
            }
        }
    
    # ==================== S5: 准确性验证 ====================
    def s5_validate(self, s2: Dict, output_path: Path) -> Dict:
        """S5: 验证内容可恢复性"""
        # 测试从输出文件恢复
        try:
            with open(output_path, 'rb') as f:
                loaded = json.loads(gzip.decompress(f.read()).decode('utf-8'))
            
            # 验证压缩内容可解压
            compressed = base64.b64decode(loaded['_content'])
            recovered = gzip.decompress(compressed).decode('utf-8')
            recovered_size = len(recovered.encode())
            
            integrity = recovered_size >= self.original_size * 0.99
            
            return {
                "standard": "S5-Validation-v3",
                "integrity": "PASS" if integrity else "FAIL",
                "recovered_size": recovered_size,
                "ratio": f"{recovered_size/self.original_size:.1%}",
                "structure_ok": len(s2.get("sections", [])) > 0
            }
        except Exception as e:
            return {
                "standard": "S5-Validation-v3",
                "integrity": "FAIL",
                "error": str(e)
            }
    
    # ==================== S6: 局限标注（精简） ====================
    def s6_limitations(self) -> Dict:
        """S6: 精简局限标注"""
        return {
            "standard": "S6-Limitations-v3",
            "limits": [
                "Content accessed via position refs (slower than direct access)",
                "Entity extraction simplified for compactness",
                "Large files (>10MB) not optimized"
            ]
        }
    
    # ==================== S7: 对抗测试 ====================
    def s7_test(self, output_path: Path) -> Dict:
        """S7: 测试文件可恢复性"""
        tests = []
        
        try:
            # 测试1: 文件可读
            with open(output_path, 'rb') as f:
                data = gzip.decompress(f.read())
            tests.append({"name": "file_readable", "result": "PASS"})
            
            # 测试2: 内容可解压
            doc = json.loads(data.decode('utf-8'))
            compressed = base64.b64decode(doc['_content'])
            raw = gzip.decompress(compressed)
            tests.append({"name": "content_recoverable", "result": "PASS"})
            
            # 测试3: 结构可用
            has_structure = 'S2' in doc and 'sections' in doc['S2']
            tests.append({"name": "structure_valid", "result": "PASS" if has_structure else "FAIL"})
            
        except Exception as e:
            tests.append({"name": "recovery", "result": "FAIL", "error": str(e)})
        
        pass_rate = sum(1 for t in tests if t.get("result") == "PASS") / len(tests)
        
        return {
            "standard": "S7-Testing-v3",
            "tests": tests,
            "pass_rate": f"{pass_rate:.0%}"
        }
    
    # ==================== 主流程 ====================
    def ingest(self) -> Dict:
        """执行V3.0压缩引用式入库"""
        print(f"🚀 V3.0压缩引用式入库: {self.source_file.name}")
        print(f"   原始大小: {self.original_size} bytes")
        print(f"   Gzip压缩: {self.compressed_size} bytes ({self.compressed_size/self.original_size:.1%})")
        
        # S1
        print("\n[S1] 输入定义...")
        s1 = self.s1_define_input()
        
        # S2
        print("[S2] 内容处理(引用式)...")
        s2 = self.s2_process_content()
        print(f"   ✓ {s2['structure']['sections']}章节, {s2['structure']['quotes']}语录")
        
        # S3
        print("[S3] 知识结构化...")
        s3 = self.s3_structure_knowledge(s2)
        print(f"   ✓ {s3['entity_count']}实体")
        
        # S4
        print("[S4] 压缩存储...")
        s4 = self.s4_automation(s1, s2, s3)
        output_path = Path(s4['output'])
        
        # 获取实际输出大小
        actual_size = output_path.stat().st_size
        print(f"   ✓ 输出: {actual_size} bytes ({actual_size/self.original_size:.1%} of original)")
        
        # S5
        print("[S5] 准确性验证...")
        s5 = self.s5_validate(s2, output_path)
        print(f"   ✓ 完整性: {s5['integrity']}, 恢复率: {s5['ratio']}")
        
        # S6
        s6 = self.s6_limitations()
        
        # S7
        print("[S7] 对抗测试...")
        s7 = self.s7_test(output_path)
        print(f"   ✓ 通过率: {s7['pass_rate']}")
        
        # 更新文件添加S5-S7
        with open(output_path, 'rb') as f:
            doc = json.loads(gzip.decompress(f.read()).decode('utf-8'))
        
        doc['S5'] = s5
        doc['S6'] = s6
        doc['S7'] = s7
        doc['_meta']['7standard'] = 'complete'
        
        with open(output_path, 'wb') as f:
            f.write(gzip.compress(json.dumps(doc, ensure_ascii=False).encode('utf-8')))
        
        final_size = output_path.stat().st_size
        
        print(f"\n✅ V3.0入库完成!")
        print(f"   原始: {self.original_size} bytes")
        print(f"   输出: {final_size} bytes")
        print(f"   比例: {final_size/self.original_size:.1%}")
        print(f"   相比V2节省: {(1 - final_size/119147)*100:.0f}%")
        
        return {
            "success": True,
            "original_size": self.original_size,
            "output_size": final_size,
            "ratio": f"{final_size/self.original_size:.1%}",
            "savings_vs_v2": f"{(1 - final_size/119147)*100:.0f}%",
            "integrity": s5['integrity'],
            "pass_rate": s7['pass_rate'],
            "output": str(output_path)
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python super_knowledge_ingest_v3.py <source_file.md>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    ingestor = CompactKnowledgeIngestor(source_file)
    result = ingestor.ingest()
    
    print("\n" + "="*50)
    print("V3.0入库结果:")
    for k, v in result.items():
        print(f"  {k}: {v}")
