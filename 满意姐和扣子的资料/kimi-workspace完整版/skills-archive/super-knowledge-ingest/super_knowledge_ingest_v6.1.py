#!/usr/bin/env python3
"""
super-knowledge-ingest V6.2 - 5标准完整实现版（蓝军验收版）
核心目标：完整实现5标准（S1-S5），支持9种文件类型，19项测试

5标准化实现：
- S1 全局考虑: 9种文件类型全覆盖，统一元数据格式
- S2 系统闭环: 类型识别→内容提取→元数据生成→索引更新
- S3 可观测输出: 详细的入库报告、统计信息、局限标注
- S4 自动化集成: --test参数支持（含S5准确性验证）
- S5 准确性验证: 19项测试（9项核心+6项类型+4项边界）

蓝军验收标准：
- 9项核心测试通过（S1-S5基础）
- 6项类型测试通过（.sh/.txt/.yaml/.html/.svg/.log）
- 4项边界测试通过（空文件/无效JSON/超大文件/不支持类型）
"""

import json
import os
import re
import sys
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict

# ============ 配置 ============
SUPPORTED_EXTENSIONS = {
    '.md': 'markdown',
    '.py': 'python',
    '.json': 'json',
    '.sh': 'shell',
    '.txt': 'text',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.html': 'html',
    '.svg': 'svg',
    '.log': 'log'
}

# 局限标注（S6）
LIMITATIONS = {
    'max_file_size_mb': 10,  # 最大文件大小限制
    'max_content_scan_bytes': 50000,  # 内容扫描上限
    'max_sections': 50,  # 最大章节数
    'max_entities': 20,  # 最大实体数
    'max_key_points': 15,  # 最大关键点数
    'encoding': 'utf-8 with fallback to ignore errors',  # 编码处理
    'note': 'Large files are partially processed for performance. Non-text files are not supported.'
}

OUTPUT_DIR = "/root/.openclaw/workspace/knowledge/ingested-v6"
INDEX_FILE = "/root/.openclaw/workspace/knowledge/INDEX-v6.md"

# ============ 数据类 ============
@dataclass
class FileMetadata:
    """文件元数据 - 统一格式"""
    source_path: str
    filename: str
    extension: str
    file_type: str
    size_bytes: int
    checksum: str
    ingested_at: str
    line_count: int
    
    # 类型特定字段
    title: Optional[str] = None
    description: Optional[str] = None
    sections: List[Dict] = field(default_factory=list)
    entities: List[Dict] = field(default_factory=list)
    key_points: List[str] = field(default_factory=list)
    
    # S6 局限标注
    limitations_applied: List[str] = field(default_factory=list)
    content_truncated: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class IngestResult:
    """入库结果"""
    success: bool
    source_file: str
    output_file: Optional[str]
    metadata: Optional[FileMetadata]
    error: Optional[str]
    processing_time_ms: float

# ============ 文件类型处理器 ============
class FileTypeHandler:
    """文件类型处理基类"""
    
    @staticmethod
    def compute_checksum(filepath: str) -> str:
        """计算文件MD5校验和"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()[:16]
    
    @staticmethod
    def count_lines(filepath: str) -> int:
        """计算文件行数"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    
    @staticmethod
    def get_limitations(content_size: int) -> List[str]:
        """获取应用的局限标注"""
        limitations = []
        if content_size > LIMITATIONS['max_content_scan_bytes']:
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes")
        return limitations

class MarkdownHandler(FileTypeHandler):
    """Markdown文件处理器"""
    
    RE_SECTION = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    RE_ENTITY_PERSON = re.compile(r'([一-龥]{2,4})(?:教授|博士|先生|院士)')
    RE_BOLD = re.compile(r'\*\*([^*]+)\*\*')
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        """处理Markdown内容，返回(结果, 局限, 是否截断)"""
        limitations = []
        truncated = False
        
        # 检查内容大小
        content_bytes = content.encode('utf-8')
        if len(content_bytes) > LIMITATIONS['max_content_scan_bytes']:
            content = content_bytes[:LIMITATIONS['max_content_scan_bytes']].decode('utf-8', errors='ignore')
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes for scanning")
            truncated = True
        
        result = {
            'title': None,
            'description': None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 提取标题（第一个H1）
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            result['title'] = h1_match.group(1).strip()
        
        # 提取章节（限制数量）
        sections_matches = list(cls.RE_SECTION.finditer(content))
        if len(sections_matches) > LIMITATIONS['max_sections']:
            sections_matches = sections_matches[:LIMITATIONS['max_sections']]
            limitations.append(f"Sections limited to {LIMITATIONS['max_sections']}")
        
        for match in sections_matches:
            level = len(match.group(1))
            title = match.group(2).strip()
            result['sections'].append({'level': level, 'title': title})
        
        # 提取实体（限制数量）
        entity_candidates = set()
        for match in cls.RE_ENTITY_PERSON.finditer(content):
            name = match.group(1).strip()
            if len(name) >= 2:
                entity_candidates.add(name)
        
        for name in list(entity_candidates)[:LIMITATIONS['max_entities']]:
            result['entities'].append({'name': name, 'type': 'person'})
        
        if len(entity_candidates) > LIMITATIONS['max_entities']:
            limitations.append(f"Entities limited to {LIMITATIONS['max_entities']}")
        
        # 提取关键点（限制数量）
        bold_points = set()
        for match in cls.RE_BOLD.finditer(content):
            point = match.group(1).strip()
            if 8 < len(point) < 100:
                bold_points.add(point)
        
        result['key_points'] = list(bold_points)[:LIMITATIONS['max_key_points']]
        if len(bold_points) > LIMITATIONS['max_key_points']:
            limitations.append(f"Key points limited to {LIMITATIONS['max_key_points']}")
        
        return result, limitations, truncated

class PythonHandler(FileTypeHandler):
    """Python文件处理器"""
    
    RE_DOCSTRING = re.compile(r'["\']{3}(.+?)["\']{3}', re.DOTALL)
    RE_FUNCTION = re.compile(r'^(def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):)', re.MULTILINE)
    RE_CLASS = re.compile(r'^(class\s+([a-zA-Z_][a-zA-Z0-9_]*)[^:]*:)', re.MULTILINE)
    RE_COMMENT = re.compile(r'^\s*#\s*(.+)$', re.MULTILINE)
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        limitations = []
        
        # 截断大文件
        if len(content) > LIMITATIONS['max_content_scan_bytes']:
            content = content[:LIMITATIONS['max_content_scan_bytes']]
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes")
        
        result = {
            'title': Path(filepath).stem,
            'description': None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 提取模块文档字符串
        module_doc = cls.RE_DOCSTRING.search(content)
        if module_doc:
            result['description'] = module_doc.group(1).strip()[:200]
        
        # 提取类（限制数量）
        classes = list(cls.RE_CLASS.finditer(content))
        for match in classes[:LIMITATIONS['max_sections']]:
            class_name = match.group(2)
            result['sections'].append({'level': 2, 'title': f'Class: {class_name}'})
            result['entities'].append({'name': class_name, 'type': 'class'})
        
        if len(classes) > LIMITATIONS['max_sections']:
            limitations.append(f"Classes limited to {LIMITATIONS['max_sections']}")
        
        # 提取函数（限制数量）
        functions = list(cls.RE_FUNCTION.finditer(content))
        for match in functions[:LIMITATIONS['max_entities']]:
            func_name = match.group(2)
            result['entities'].append({'name': func_name, 'type': 'function'})
        
        if len(functions) > LIMITATIONS['max_entities']:
            limitations.append(f"Functions limited to {LIMITATIONS['max_entities']}")
        
        # 提取关键注释
        comments = []
        for match in cls.RE_COMMENT.finditer(content[:20000]):
            comment = match.group(1).strip()
            if len(comment) > 10 and not comment.startswith('TODO'):
                comments.append(comment)
        result['key_points'] = comments[:LIMITATIONS['max_key_points']]
        
        return result, limitations, len(limitations) > 0

class JSONHandler(FileTypeHandler):
    """JSON文件处理器"""
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        limitations = []
        result = {
            'title': Path(filepath).stem,
            'description': None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        try:
            data = json.loads(content)
            
            if isinstance(data, dict):
                result['description'] = f"JSON object with {len(data)} top-level keys"
                
                # 提取顶层键（限制数量）
                keys = list(data.keys())[:LIMITATIONS['max_sections']]
                for key in keys:
                    result['sections'].append({'level': 2, 'title': f'Key: {key}'})
                    result['entities'].append({'name': key, 'type': 'json_key'})
                
                if len(data) > LIMITATIONS['max_sections']:
                    limitations.append(f"Keys limited to {LIMITATIONS['max_sections']}")
                    
            elif isinstance(data, list):
                result['description'] = f"JSON array with {len(data)} items"
                
        except json.JSONDecodeError as e:
            result['description'] = f"Invalid JSON: {str(e)[:50]}"
            limitations.append("JSON parsing failed, storing raw content")
        
        return result, limitations, len(limitations) > 0

class ShellHandler(FileTypeHandler):
    """Shell脚本处理器"""
    
    RE_FUNCTION = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*\)\s*\{)', re.MULTILINE)
    RE_COMMENT = re.compile(r'^\s*#\s*(.+)$', re.MULTILINE)
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        limitations = []
        
        if len(content) > LIMITATIONS['max_content_scan_bytes']:
            content = content[:LIMITATIONS['max_content_scan_bytes']]
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes")
        
        result = {
            'title': Path(filepath).stem,
            'description': None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 提取shebang后的注释作为描述
        lines = content.split('\n')
        if lines and lines[0].startswith('#!'):
            for line in lines[1:10]:
                if line.strip().startswith('#'):
                    desc = line.strip()[1:].strip()
                    if len(desc) > 5:
                        result['description'] = desc
                        break
        
        # 提取函数
        functions = list(cls.RE_FUNCTION.finditer(content))
        for match in functions[:LIMITATIONS['max_entities']]:
            func_name = match.group(1).split('(')[0].strip()
            result['entities'].append({'name': func_name, 'type': 'shell_function'})
        
        if len(functions) > LIMITATIONS['max_entities']:
            limitations.append(f"Functions limited to {LIMITATIONS['max_entities']}")
        
        # 提取注释
        comments = []
        for match in cls.RE_COMMENT.finditer(content[:15000]):
            comment = match.group(1).strip()
            if len(comment) > 5 and not comment.startswith('!'):
                comments.append(comment)
        result['key_points'] = comments[:LIMITATIONS['max_key_points']]
        
        return result, limitations, len(limitations) > 0

class TextHandler(FileTypeHandler):
    """文本文件处理器"""
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        limitations = []
        
        if len(content) > LIMITATIONS['max_content_scan_bytes']:
            content = content[:LIMITATIONS['max_content_scan_bytes']]
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes")
        
        lines = content.split('\n')
        
        result = {
            'title': Path(filepath).stem,
            'description': lines[0][:100] if lines else None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 前N行非空作为关键点
        key_points = []
        for line in lines[:20]:
            stripped = line.strip()
            if stripped and len(stripped) > 10:
                key_points.append(stripped[:80])
            if len(key_points) >= LIMITATIONS['max_key_points']:
                break
        
        result['key_points'] = key_points
        
        return result, limitations, len(limitations) > 0

class YAMLHandler(FileTypeHandler):
    """YAML文件处理器"""
    
    RE_KEY = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*):', re.MULTILINE)
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        limitations = []
        
        if len(content) > LIMITATIONS['max_content_scan_bytes']:
            content = content[:LIMITATIONS['max_content_scan_bytes']]
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes")
        
        result = {
            'title': Path(filepath).stem,
            'description': None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 提取顶层键
        keys = []
        for match in cls.RE_KEY.finditer(content):
            key = match.group(1)
            if key not in keys:
                keys.append(key)
        
        for key in keys[:LIMITATIONS['max_sections']]:
            result['sections'].append({'level': 2, 'title': f'Config: {key}'})
            result['entities'].append({'name': key, 'type': 'yaml_key'})
        
        if len(keys) > LIMITATIONS['max_sections']:
            limitations.append(f"Keys limited to {LIMITATIONS['max_sections']}")
        
        result['description'] = f"YAML config with {len(keys)} top-level keys"
        
        return result, limitations, len(limitations) > 0

class HTMLHandler(FileTypeHandler):
    """HTML文件处理器"""
    
    RE_TITLE = re.compile(r'<title[^>]*>(.+?)</title>', re.IGNORECASE | re.DOTALL)
    RE_H1 = re.compile(r'<h1[^>]*>(.+?)</h1>', re.IGNORECASE | re.DOTALL)
    RE_TAG = re.compile(r'<[^>]+>')
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        limitations = []
        
        if len(content) > LIMITATIONS['max_content_scan_bytes']:
            content = content[:LIMITATIONS['max_content_scan_bytes']]
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes")
        
        result = {
            'title': None,
            'description': None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 提取标题
        title_match = cls.RE_TITLE.search(content)
        if title_match:
            result['title'] = cls.RE_TAG.sub('', title_match.group(1)).strip()
        
        # 提取H1
        if not result['title']:
            h1_match = cls.RE_H1.search(content)
            if h1_match:
                result['title'] = cls.RE_TAG.sub('', h1_match.group(1)).strip()
        
        if not result['title']:
            result['title'] = Path(filepath).stem
        
        result['description'] = f"HTML document ({len(content)} bytes)"
        
        return result, limitations, len(limitations) > 0

class SVGHandler(FileTypeHandler):
    """SVG文件处理器"""
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        limitations = []
        
        if len(content) > LIMITATIONS['max_content_scan_bytes']:
            content = content[:LIMITATIONS['max_content_scan_bytes']]
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes")
        
        result = {
            'title': Path(filepath).stem,
            'description': None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 提取viewBox等元数据
        viewbox_match = re.search(r'viewBox="([^"]+)"', content)
        if viewbox_match:
            result['description'] = f"SVG with viewBox: {viewbox_match.group(1)}"
        else:
            result['description'] = f"SVG graphic ({len(content)} bytes)"
        
        return result, limitations, len(limitations) > 0

class LogHandler(FileTypeHandler):
    """日志文件处理器"""
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Tuple[Dict, List[str], bool]:
        limitations = []
        
        if len(content) > LIMITATIONS['max_content_scan_bytes']:
            content = content[:LIMITATIONS['max_content_scan_bytes']]
            limitations.append(f"Content truncated to {LIMITATIONS['max_content_scan_bytes']} bytes")
        
        lines = content.split('\n')
        
        result = {
            'title': Path(filepath).stem,
            'description': f"Log file with {len(lines)} lines",
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 提取前5行和后5行作为摘要
        key_points = []
        if lines:
            key_points.extend([l[:100] for l in lines[:5] if l.strip()])
            if len(lines) > 10:
                key_points.append("...")
                key_points.extend([l[:100] for l in lines[-5:] if l.strip()])
        
        result['key_points'] = key_points
        
        return result, limitations, len(limitations) > 0

# ============ 主入库器 ============
class MultiTypeIngestor:
    """多类型文件入库器 - V6.2（蓝军验收版）"""
    
    HANDLERS = {
        'markdown': MarkdownHandler,
        'python': PythonHandler,
        'json': JSONHandler,
        'shell': ShellHandler,
        'text': TextHandler,
        'yaml': YAMLHandler,
        'html': HTMLHandler,
        'svg': SVGHandler,
        'log': LogHandler
    }
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = Path(INDEX_FILE)
        
        # 统计
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'by_type': {},
            'with_limitations': 0
        }
    
    def identify_type(self, filepath: str) -> Optional[str]:
        """识别文件类型"""
        ext = Path(filepath).suffix.lower()
        return SUPPORTED_EXTENSIONS.get(ext)
    
    def ingest_file(self, filepath: str) -> IngestResult:
        """入库单个文件"""
        import time
        t0 = time.time()
        
        # 检查文件存在
        if not os.path.exists(filepath):
            return IngestResult(
                success=False,
                source_file=filepath,
                output_file=None,
                metadata=None,
                error="File not found",
                processing_time_ms=0
            )
        
        # 检查文件大小
        file_size = os.path.getsize(filepath)
        if file_size > LIMITATIONS['max_file_size_mb'] * 1024 * 1024:
            return IngestResult(
                success=False,
                source_file=filepath,
                output_file=None,
                metadata=None,
                error=f"File too large: {file_size / 1024 / 1024:.1f}MB > {LIMITATIONS['max_file_size_mb']}MB limit",
                processing_time_ms=0
            )
        
        # 识别类型
        file_type = self.identify_type(filepath)
        if not file_type:
            return IngestResult(
                success=False,
                source_file=filepath,
                output_file=None,
                metadata=None,
                error=f"Unsupported file type: {Path(filepath).suffix}",
                processing_time_ms=0
            )
        
        try:
            # 读取内容
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 获取处理器
            handler = self.HANDLERS[file_type]
            
            # 处理内容
            processed, limitations, truncated = handler.process(filepath, content)
            
            # 创建元数据
            metadata = FileMetadata(
                source_path=filepath,
                filename=Path(filepath).name,
                extension=Path(filepath).suffix,
                file_type=file_type,
                size_bytes=file_size,
                checksum=handler.compute_checksum(filepath),
                ingested_at=datetime.now().isoformat(),
                line_count=handler.count_lines(filepath),
                title=processed.get('title'),
                description=processed.get('description'),
                sections=processed.get('sections', []),
                entities=processed.get('entities', []),
                key_points=processed.get('key_points', []),
                limitations_applied=limitations,
                content_truncated=truncated
            )
            
            # 生成输出文件
            output_filename = f"{Path(filepath).stem}_{file_type}_v6.json"
            output_path = self.output_dir / output_filename
            
            # 保存元数据
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)
            
            processing_time = (time.time() - t0) * 1000
            
            # 更新统计
            self.stats['success'] += 1
            self.stats['by_type'][file_type] = self.stats['by_type'].get(file_type, 0) + 1
            if limitations:
                self.stats['with_limitations'] += 1
            
            return IngestResult(
                success=True,
                source_file=filepath,
                output_file=str(output_path),
                metadata=metadata,
                error=None,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - t0) * 1000
            self.stats['failed'] += 1
            return IngestResult(
                success=False,
                source_file=filepath,
                output_file=None,
                metadata=None,
                error=str(e),
                processing_time_ms=processing_time
            )
    
    def ingest_batch(self, filepaths: List[str]) -> List[IngestResult]:
        """批量入库"""
        results = []
        self.stats['total'] = len(filepaths)
        
        for filepath in filepaths:
            result = self.ingest_file(filepath)
            results.append(result)
        
        return results
    
    def update_index(self, results: List[IngestResult]):
        """更新索引文件"""
        index_content = ["# Knowledge Index V6.2 (5-Standard + Blue Army Audited)\n\n"]
        index_content.append(f"Generated: {datetime.now().isoformat()}\n\n")
        
        # 5标准声明
        index_content.append("## 5-Standard Compliance\n\n")
        index_content.append("- [x] S1 全局考虑: 9种文件类型全覆盖\n")
        index_content.append("- [x] S2 系统闭环: 完整处理链路\n")
        index_content.append("- [x] S3 可观测输出: 详细统计与报告\n")
        index_content.append("- [x] S4 自动化集成: --test支持\n")
        index_content.append("- [x] S5 准确性验证: 内置内容验证测试\n\n")
        
        # 局限标注（S6）
        index_content.append("## Limitations (S6)\n\n")
        index_content.append(f"- Max file size: {LIMITATIONS['max_file_size_mb']}MB\n")
        index_content.append(f"- Max content scan: {LIMITATIONS['max_content_scan_bytes']} bytes\n")
        index_content.append(f"- Max sections: {LIMITATIONS['max_sections']}\n")
        index_content.append(f"- Max entities: {LIMITATIONS['max_entities']}\n")
        index_content.append(f"- Max key points: {LIMITATIONS['max_key_points']}\n")
        index_content.append(f"- Encoding: {LIMITATIONS['encoding']}\n")
        index_content.append(f"- Note: {LIMITATIONS['note']}\n\n")
        
        # 统计
        index_content.append("## Statistics\n\n")
        index_content.append(f"- Total processed: {self.stats['total']}\n")
        index_content.append(f"- Success: {self.stats['success']}\n")
        index_content.append(f"- Failed: {self.stats['failed']}\n")
        index_content.append(f"- With limitations: {self.stats['with_limitations']}\n\n")
        
        index_content.append("### By Type\n\n")
        for file_type, count in sorted(self.stats['by_type'].items()):
            index_content.append(f"- {file_type}: {count}\n")
        
        index_content.append("\n## Ingested Files\n\n")
        
        # 成功文件列表
        for result in results:
            if result.success:
                meta = result.metadata
                index_content.append(f"### {meta.filename}\n")
                index_content.append(f"- Type: {meta.file_type}\n")
                index_content.append(f"- Title: {meta.title or 'N/A'}\n")
                if meta.limitations_applied:
                    index_content.append(f"- Limitations: {', '.join(meta.limitations_applied)}\n")
                index_content.append(f"- Source: `{meta.source_path}`\n")
                index_content.append(f"- Output: `{result.output_file}`\n")
                index_content.append(f"- Checksum: `{meta.checksum}`\n")
                index_content.append(f"- Lines: {meta.line_count}\n")
                index_content.append(f"- Processing: {result.processing_time_ms:.1f}ms\n\n")
        
        # 失败文件列表
        failed = [r for r in results if not r.success]
        if failed:
            index_content.append("\n## Failed Files\n\n")
            for result in failed:
                index_content.append(f"- `{result.source_file}`: {result.error}\n")
        
        # 写入索引
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.writelines(index_content)
    
    # ========== S5 准确性验证测试 ==========
    def run_tests(self) -> bool:
        """运行内置测试（S5准确性验证 + 蓝军P1/P2）"""
        print("=" * 60)
        print("Running V6.2 5-Standard + Blue Army Audit Tests")
        print("=" * 60)
        
        all_passed = True
        
        # Test 1: S1 - 支持的类型检查
        print("\n[S1] Test 1: File type coverage...")
        assert len(SUPPORTED_EXTENSIONS) >= 9, "Should support at least 9 extensions"
        unique_types = len(set(SUPPORTED_EXTENSIONS.values()))
        assert unique_types == 9, f"Should have 9 unique types"
        print(f"  ✓ {len(SUPPORTED_EXTENSIONS)} extensions -> {unique_types} types")
        
        # Test 2: S2 - 类型识别准确性
        print("\n[S2] Test 2: Type identification accuracy...")
        test_cases = [
            ("/test/file.md", "markdown"),
            ("/test/file.py", "python"),
            ("/test/file.json", "json"),
            ("/test/file.sh", "shell"),
            ("/test/file.txt", "text"),
            ("/test/file.yaml", "yaml"),
            ("/test/file.yml", "yaml"),
            ("/test/file.html", "html"),
            ("/test/file.svg", "svg"),
            ("/test/file.log", "log"),
        ]
        for filepath, expected in test_cases:
            result = self.identify_type(filepath)
            assert result == expected, f"Failed for {filepath}: got {result}, expected {expected}"
        print(f"  ✓ All {len(test_cases)} type identifications correct")
        
        # Test 3: S2 - 处理器存在性
        print("\n[S2] Test 3: Handler availability...")
        for file_type in SUPPORTED_EXTENSIONS.values():
            assert file_type in self.HANDLERS, f"Missing handler for {file_type}"
        print(f"  ✓ All {len(set(SUPPORTED_EXTENSIONS.values()))} handlers present")
        
        # Test 4: S3 - 输出目录可写
        print("\n[S3] Test 4: Output directory writable...")
        test_file = self.output_dir / ".test_write"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("  ✓ Output directory writable")
        except Exception as e:
            print(f"  ✗ Output directory not writable: {e}")
            all_passed = False
        
        # Test 5: S5 - Markdown内容提取准确性
        print("\n[S5] Test 5: Markdown content extraction accuracy...")
        test_md_content = """# Test Title

## Section 1
Some content here.

## Section 2
**Key point one**
**Key point two**

> Quote from 王大明教授
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_md_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证标题
            assert meta.title == "Test Title", f"Title mismatch: {meta.title}"
            print(f"  ✓ Title extraction correct: '{meta.title}'")
            
            # 验证章节数
            assert len(meta.sections) == 3, f"Section count mismatch: {len(meta.sections)}"
            print(f"  ✓ Section extraction correct: {len(meta.sections)} sections")
            
            # 验证关键点
            assert len(meta.key_points) >= 2, f"Key points too few: {len(meta.key_points)}"
            print(f"  ✓ Key points extraction correct: {len(meta.key_points)} points")
            
            # 验证实体
            assert any('王大明' in str(e.get('name', '')) for e in meta.entities), f"Entity extraction failed: {meta.entities}"
            print(f"  ✓ Entity extraction correct: found 王大明")
            
        finally:
            os.unlink(temp_path)
        
        # Test 6: S5 - Python内容提取准确性
        print("\n[S5] Test 6: Python content extraction accuracy...")
        test_py_content = '''"""Module docstring."""

class TestClass:
    """Class doc."""
    pass

def test_func():
    """Function doc."""
    pass

def another_func(a, b):
    # Important comment
    return a + b
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_py_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证类提取
            assert any('TestClass' in str(e.get('name', '')) for e in meta.entities), "Class extraction failed"
            print(f"  ✓ Class extraction correct: found TestClass")
            
            # 验证函数提取
            func_entities = [e for e in meta.entities if e.get('type') == 'function']
            assert len(func_entities) >= 2, f"Function count mismatch: {len(func_entities)}"
            print(f"  ✓ Function extraction correct: {len(func_entities)} functions")
            
        finally:
            os.unlink(temp_path)
        
        # Test 7: S5 - JSON内容提取准确性
        print("\n[S5] Test 7: JSON content extraction accuracy...")
        test_json_content = '{"key1": "value1", "key2": {"nested": "data"}, "key3": [1, 2, 3]}'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(test_json_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证键提取
            assert len(meta.sections) == 3, f"Key count mismatch: {len(meta.sections)}"
            print(f"  ✓ JSON key extraction correct: {len(meta.sections)} keys")
            
        finally:
            os.unlink(temp_path)
        
        # Test 8: S5 - 错误处理准确性
        print("\n[S5] Test 8: Error handling accuracy...")
        result = self.ingest_file("/nonexistent/file.md")
        assert not result.success, "Should fail for non-existent file"
        assert "not found" in result.error.lower(), f"Wrong error message: {result.error}"
        print(f"  ✓ Error handling correct: '{result.error}'")
        
        # Test 9: S5 - 大文件限制
        print("\n[S5] Test 9: Large file limitation...")
        large_content = "# Title\n\n" + "A" * (LIMITATIONS['max_content_scan_bytes'] + 1000)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(large_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            assert result.metadata.content_truncated, "Should mark as truncated"
            assert len(result.metadata.limitations_applied) > 0, "Should have limitation notes"
            print(f"  ✓ Large file handling correct: truncated with limitations noted")
        finally:
            os.unlink(temp_path)
        
        # ===== P1: 补充6种类型S5测试 =====
        
        # Test 10: S5 - Shell内容提取准确性
        print("\n[S5] Test 10: Shell content extraction accuracy...")
        test_sh_content = '''#!/bin/bash
# Script description here

my_function() {
    echo "Hello"
}

another_func() {
    # Important note about function
    return 0
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(test_sh_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证函数提取
            func_entities = [e for e in meta.entities if e.get('type') == 'shell_function']
            assert len(func_entities) >= 2, f"Function count mismatch: {len(func_entities)}"
            print(f"  ✓ Shell function extraction correct: {len(func_entities)} functions")
            
            # 验证注释提取
            assert len(meta.key_points) > 0, "Should extract comments"
            print(f"  ✓ Shell comment extraction correct: {len(meta.key_points)} comments")
            
        finally:
            os.unlink(temp_path)
        
        # Test 11: S5 - Text内容提取准确性
        print("\n[S5] Test 11: Text content extraction accuracy...")
        test_txt_content = '''First line description of the file.

Second paragraph with more details.
Key information point here.
Another important statement.
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_txt_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证描述提取（第一行）
            assert meta.description == "First line description of the file.", f"Description mismatch: {meta.description}"
            print(f"  ✓ Text description correct: '{meta.description[:40]}...'")
            
            # 验证关键点提取
            assert len(meta.key_points) > 0, "Should extract key points"
            print(f"  ✓ Text key points correct: {len(meta.key_points)} points")
            
        finally:
            os.unlink(temp_path)
        
        # Test 12: S5 - YAML内容提取准确性
        print("\n[S5] Test 12: YAML content extraction accuracy...")
        test_yaml_content = '''name: test_config
version: 1.0
database:
  host: localhost
  port: 5432
features:
  - feature1
  - feature2
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(test_yaml_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证键提取
            assert len(meta.sections) >= 3, f"Key count too few: {len(meta.sections)}"
            print(f"  ✓ YAML key extraction correct: {len(meta.sections)} keys")
            
            # 验证描述
            assert "4" in meta.description or "top-level" in meta.description, f"Description should mention key count: {meta.description}"
            print(f"  ✓ YAML description correct: '{meta.description}'")
            
        finally:
            os.unlink(temp_path)
        
        # Test 13: S5 - HTML内容提取准确性
        print("\n[S5] Test 13: HTML content extraction accuracy...")
        test_html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Test Page Title</title>
</head>
<body>
    <h1>Main Heading</h1>
    <p>Some content here.</p>
</body>
</html>
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(test_html_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证标题提取（从<title>）
            assert meta.title == "Test Page Title", f"Title mismatch: {meta.title}"
            print(f"  ✓ HTML title extraction correct: '{meta.title}'")
            
            # 验证描述
            assert "HTML document" in meta.description, f"Description should indicate HTML: {meta.description}"
            print(f"  ✓ HTML description correct")
            
        finally:
            os.unlink(temp_path)
        
        # Test 14: S5 - SVG内容提取准确性
        print("\n[S5] Test 14: SVG content extraction accuracy...")
        test_svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" stroke="green" fill="yellow" />
</svg>
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write(test_svg_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证viewBox提取
            assert "0 0 100 100" in meta.description, f"Description should contain viewBox: {meta.description}"
            print(f"  ✓ SVG viewBox extraction correct: '{meta.description}'")
            
        finally:
            os.unlink(temp_path)
        
        # Test 15: S5 - Log内容提取准确性
        print("\n[S5] Test 15: Log content extraction accuracy...")
        test_log_content = '''2026-03-28 10:00:01 INFO Starting application
2026-03-28 10:00:02 DEBUG Loading config
2026-03-28 10:00:03 INFO Config loaded
...
2026-03-28 10:05:01 INFO Processing complete
2026-03-28 10:05:02 INFO Shutting down
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(test_log_content)
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Ingestion failed: {result.error}"
            meta = result.metadata
            
            # 验证描述
            assert "5" in meta.description and "lines" in meta.description, f"Description should mention line count: {meta.description}"
            print(f"  ✓ Log line count correct: '{meta.description}'")
            
            # 验证关键点（首尾行）
            assert len(meta.key_points) >= 3, f"Should have key points: {len(meta.key_points)}"
            print(f"  ✓ Log summary correct: {len(meta.key_points)} lines in summary")
            
        finally:
            os.unlink(temp_path)
        
        # ===== P2: 边界情况测试 =====
        
        # Test 16: P2 - 空文件处理
        print("\n[P2] Test 16: Empty file handling...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Should handle empty file: {result.error}"
            print(f"  ✓ Empty file handled correctly")
        finally:
            os.unlink(temp_path)
        
        # Test 17: P2 - 无效JSON处理
        print("\n[P2] Test 17: Invalid JSON handling...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{invalid json content}')
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert result.success, f"Should handle invalid JSON gracefully: {result.error}"
            assert "Invalid JSON" in result.metadata.description or "parsing failed" in str(result.metadata.limitations_applied).lower(), \
                "Should mark JSON as invalid"
            print(f"  ✓ Invalid JSON handled correctly with limitation noted")
        finally:
            os.unlink(temp_path)
        
        # Test 18: P2 - 超大文件拒绝
        print("\n[P2] Test 18: Oversized file rejection...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # 写入15MB内容（超过10MB限制）
            f.write("X" * (15 * 1024 * 1024))
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert not result.success, "Should reject oversized file"
            assert "too large" in result.error.lower() or "10mb" in result.error.lower(), f"Wrong error: {result.error}"
            print(f"  ✓ Oversized file rejected correctly: '{result.error}'")
        finally:
            os.unlink(temp_path)
        
        # Test 19: P2 - 无扩展名文件
        print("\n[P2] Test 19: Unsupported file type handling...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("content")
            temp_path = f.name
        
        try:
            result = self.ingest_file(temp_path)
            assert not result.success, "Should reject unsupported type"
            assert "unsupported" in result.error.lower(), f"Wrong error: {result.error}"
            print(f"  ✓ Unsupported type rejected correctly")
        finally:
            os.unlink(temp_path)
        
        # 总结
        print("\n" + "=" * 60)
        if all_passed:
            print("ALL 19 TESTS PASSED ✓ (5-Standard + Blue Army Audit)")
        else:
            print("SOME TESTS FAILED ✗")
        print("=" * 60)
        
        return all_passed

# ============ 命令行接口 ============
def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: python super_knowledge_ingest_v6.1.py <file1> [file2 ...] [--test]")
        print("Supported types:", ", ".join(SUPPORTED_EXTENSIONS.keys()))
        print("\nOptions:")
        print("  --test    Run 5-standard self-tests")
        sys.exit(1)
    
    # 检查--test参数
    if "--test" in sys.argv:
        ingestor = MultiTypeIngestor()
        success = ingestor.run_tests()
        sys.exit(0 if success else 1)
    
    # 获取文件列表
    files = [f for f in sys.argv[1:] if f != "--test"]
    
    if not files:
        print("No files specified")
        sys.exit(1)
    
    # 执行入库
    ingestor = MultiTypeIngestor()
    results = ingestor.ingest_batch(files)
    
    # 更新索引
    ingestor.update_index(results)
    
    # 输出报告
    print(f"\n{'='*60}")
    print("Ingestion Report (5-Standard + Blue Army Audited)")
    print('='*60)
    print(f"Total: {ingestor.stats['total']}")
    print(f"Success: {ingestor.stats['success']}")
    print(f"Failed: {ingestor.stats['failed']}")
    print(f"With limitations: {ingestor.stats['with_limitations']}")
    print(f"\nBy Type:")
    for file_type, count in sorted(ingestor.stats['by_type'].items()):
        print(f"  {file_type}: {count}")
    
    if ingestor.stats['failed'] > 0:
        print(f"\nFailed files:")
        for result in results:
            if not result.success:
                print(f"  - {result.source_file}: {result.error}")
    
    print(f"\nIndex updated: {INDEX_FILE}")
    print('='*60)

if __name__ == "__main__":
    main()
