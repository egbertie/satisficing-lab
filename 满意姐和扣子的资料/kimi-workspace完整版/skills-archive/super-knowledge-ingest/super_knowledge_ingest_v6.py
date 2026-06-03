#!/usr/bin/env python3
"""
super-knowledge-ingest V6.0 - 多类型文件支持版
核心目标：支持9种文件类型，达到满意解和4标准化
设计理念：稳定可靠 > 极致性能，满意解 > 最优解

支持的文件类型：
- .md - Markdown文档（原文处理）
- .py - Python脚本（提取注释、函数、类）
- .json - JSON配置（结构化存储）
- .sh - Shell脚本（提取注释、函数）
- .txt - 文本文件（原文存储）
- .yaml/.yml - YAML配置（结构化存储）
- .html - HTML文档（提取文本内容）
- .svg - SVG图形（元数据提取）
- .log - 日志文件（摘要存储）

4标准化实现：
- S1 全局考虑：9种文件类型全覆盖，统一元数据格式
- S2 系统闭环：类型识别→内容提取→元数据生成→索引更新
- S3 可观测输出：详细的入库报告和统计
- S4 自动化集成：--test参数支持，批量处理，索引自动更新
"""

import json
import os
import re
import sys
import hashlib
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

class MarkdownHandler(FileTypeHandler):
    """Markdown文件处理器"""
    
    RE_SECTION = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    RE_ENTITY_PERSON = re.compile(r'([一-龥·A-Za-z\s]{2,20})(?:教授|博士|先生|院士)')
    RE_BOLD = re.compile(r'\*\*([^*]+)\*\*')
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理Markdown内容"""
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
        
        # 提取章节
        for match in cls.RE_SECTION.finditer(content[:50000]):  # 限制前50KB
            level = len(match.group(1))
            title = match.group(2).strip()
            result['sections'].append({
                'level': level,
                'title': title
            })
        
        # 提取实体
        for match in cls.RE_ENTITY_PERSON.finditer(content):
            name = match.group(1).strip()
            if len(name) >= 2:
                result['entities'].append({
                    'name': name,
                    'type': 'person'
                })
        
        # 提取关键点（加粗文本）
        bold_points = set()
        for match in cls.RE_BOLD.finditer(content[:30000]):
            point = match.group(1).strip()
            if 8 < len(point) < 100:
                bold_points.add(point)
        result['key_points'] = list(bold_points)[:15]
        
        return result

class PythonHandler(FileTypeHandler):
    """Python文件处理器"""
    
    RE_DOCSTRING = re.compile(r'["\']{3}(.+?)["\']{3}', re.DOTALL)
    RE_FUNCTION = re.compile(r'^(def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):)', re.MULTILINE)
    RE_CLASS = re.compile(r'^(class\s+([a-zA-Z_][a-zA-Z0-9_]*)[^:]*:)', re.MULTILINE)
    RE_COMMENT = re.compile(r'^\s*#\s*(.+)$', re.MULTILINE)
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理Python内容"""
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
        
        # 提取类
        for match in cls.RE_CLASS.finditer(content):
            class_def = match.group(1)
            class_name = match.group(2)
            result['sections'].append({
                'level': 2,
                'title': f'Class: {class_name}'
            })
            result['entities'].append({
                'name': class_name,
                'type': 'class'
            })
        
        # 提取函数
        for match in cls.RE_FUNCTION.finditer(content):
            func_name = match.group(2)
            result['entities'].append({
                'name': func_name,
                'type': 'function'
            })
        
        # 提取关键注释
        comments = []
        for match in cls.RE_COMMENT.finditer(content[:20000]):
            comment = match.group(1).strip()
            if len(comment) > 10 and not comment.startswith('TODO'):
                comments.append(comment)
        result['key_points'] = comments[:10]
        
        return result

class JSONHandler(FileTypeHandler):
    """JSON文件处理器"""
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理JSON内容"""
        result = {
            'title': Path(filepath).stem,
            'description': None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        try:
            data = json.loads(content)
            
            # 描述
            if isinstance(data, dict):
                result['description'] = f"JSON object with {len(data)} top-level keys"
                
                # 提取顶层键作为sections
                for key in list(data.keys())[:20]:
                    result['sections'].append({
                        'level': 2,
                        'title': f'Key: {key}'
                    })
                    result['entities'].append({
                        'name': key,
                        'type': 'json_key'
                    })
            elif isinstance(data, list):
                result['description'] = f"JSON array with {len(data)} items"
        except json.JSONDecodeError:
            result['description'] = "Invalid JSON"
        
        return result

class ShellHandler(FileTypeHandler):
    """Shell脚本处理器"""
    
    RE_FUNCTION = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*\)\s*\{)', re.MULTILINE)
    RE_COMMENT = re.compile(r'^\s*#\s*(.+)$', re.MULTILINE)
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理Shell内容"""
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
        for match in cls.RE_FUNCTION.finditer(content):
            func_name = match.group(1).split('(')[0].strip()
            result['entities'].append({
                'name': func_name,
                'type': 'shell_function'
            })
        
        # 提取注释
        comments = []
        for match in cls.RE_COMMENT.finditer(content[:15000]):
            comment = match.group(1).strip()
            if len(comment) > 5 and not comment.startswith('!'):
                comments.append(comment)
        result['key_points'] = comments[:10]
        
        return result

class TextHandler(FileTypeHandler):
    """文本文件处理器"""
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理文本内容"""
        lines = content.split('\n')
        
        result = {
            'title': Path(filepath).stem,
            'description': lines[0][:100] if lines else None,
            'sections': [],
            'entities': [],
            'key_points': []
        }
        
        # 前10行非空作为关键点
        key_points = []
        for line in lines[:20]:
            stripped = line.strip()
            if stripped and len(stripped) > 10:
                key_points.append(stripped[:80])
            if len(key_points) >= 5:
                break
        result['key_points'] = key_points
        
        return result

class YAMLHandler(FileTypeHandler):
    """YAML文件处理器"""
    
    RE_KEY = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*):', re.MULTILINE)
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理YAML内容"""
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
                result['sections'].append({
                    'level': 2,
                    'title': f'Config: {key}'
                })
                result['entities'].append({
                    'name': key,
                    'type': 'yaml_key'
                })
        
        result['description'] = f"YAML config with {len(keys)} top-level keys"
        
        return result

class HTMLHandler(FileTypeHandler):
    """HTML文件处理器"""
    
    RE_TITLE = re.compile(r'<title[^>]*>(.+?)</title>', re.IGNORECASE | re.DOTALL)
    RE_H1 = re.compile(r'<h1[^>]*>(.+?)</h1>', re.IGNORECASE | re.DOTALL)
    RE_TAG = re.compile(r'<[^>]+>')
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理HTML内容"""
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
        
        # 如果没有找到标题，使用文件名
        if not result['title']:
            result['title'] = Path(filepath).stem
        
        result['description'] = f"HTML document ({len(content)} bytes)"
        
        return result

class SVGHandler(FileTypeHandler):
    """SVG文件处理器"""
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理SVG内容"""
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
        
        return result

class LogHandler(FileTypeHandler):
    """日志文件处理器"""
    
    @classmethod
    def process(cls, filepath: str, content: str) -> Dict:
        """处理日志内容"""
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
        
        return result

# ============ 主入库器 ============
class MultiTypeIngestor:
    """多类型文件入库器 - V6.0"""
    
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
            'by_type': {}
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
            processed = handler.process(filepath, content)
            
            # 创建元数据
            metadata = FileMetadata(
                source_path=filepath,
                filename=Path(filepath).name,
                extension=Path(filepath).suffix,
                file_type=file_type,
                size_bytes=os.path.getsize(filepath),
                checksum=handler.compute_checksum(filepath),
                ingested_at=datetime.now().isoformat(),
                line_count=handler.count_lines(filepath),
                title=processed.get('title'),
                description=processed.get('description'),
                sections=processed.get('sections', []),
                entities=processed.get('entities', []),
                key_points=processed.get('key_points', [])
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
        index_content = ["# Knowledge Index V6.0\n"]
        index_content.append(f"Generated: {datetime.now().isoformat()}\n\n")
        
        # 统计
        index_content.append("## Statistics\n\n")
        index_content.append(f"- Total processed: {self.stats['total']}\n")
        index_content.append(f"- Success: {self.stats['success']}\n")
        index_content.append(f"- Failed: {self.stats['failed']}\n\n")
        
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
    
    def run_tests(self) -> bool:
        """运行内置测试"""
        print("Running V6.0 self-tests...")
        
        # 测试1: 支持的类型
        print("Test 1: Checking supported file types...")
        # 注意: .yaml和.yml映射到同一类型
        assert len(SUPPORTED_EXTENSIONS) >= 9, f"Should support at least 9 file extensions"
        unique_types = len(set(SUPPORTED_EXTENSIONS.values()))
        assert unique_types == 9, f"Should have 9 unique types, got {unique_types}"
        print(f"  ✓ {len(SUPPORTED_EXTENSIONS)} extensions -> {unique_types} types supported")
        
        # 测试2: 类型识别
        print("Test 2: Testing type identification...")
        test_cases = [
            ("/test/file.md", "markdown"),
            ("/test/file.py", "python"),
            ("/test/file.json", "json"),
            ("/test/file.yaml", "yaml"),
            ("/test/file.yml", "yaml"),
        ]
        for filepath, expected in test_cases:
            result = self.identify_type(filepath)
            assert result == expected, f"Failed for {filepath}: got {result}, expected {expected}"
        print("  ✓ Type identification working")
        
        # 测试3: 处理器存在
        print("Test 3: Checking handlers...")
        for file_type in SUPPORTED_EXTENSIONS.values():
            assert file_type in self.HANDLERS, f"Missing handler for {file_type}"
        print("  ✓ All handlers present")
        
        # 测试4: 输出目录可写
        print("Test 4: Checking output directory...")
        test_file = self.output_dir / ".test_write"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("  ✓ Output directory writable")
        except Exception as e:
            print(f"  ✗ Output directory not writable: {e}")
            return False
        
        print("\nAll tests passed! ✓")
        return True

# ============ 命令行接口 ============
def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: python super_knowledge_ingest_v6.py <file1> [file2 ...] [--test]")
        print("Supported types:", ", ".join(SUPPORTED_EXTENSIONS.keys()))
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
    print(f"\n=== Ingestion Report ===")
    print(f"Total: {ingestor.stats['total']}")
    print(f"Success: {ingestor.stats['success']}")
    print(f"Failed: {ingestor.stats['failed']}")
    print(f"\nBy Type:")
    for file_type, count in sorted(ingestor.stats['by_type'].items()):
        print(f"  {file_type}: {count}")
    
    if ingestor.stats['failed'] > 0:
        print(f"\nFailed files:")
        for result in results:
            if not result.success:
                print(f"  - {result.source_file}: {result.error}")
    
    print(f"\nIndex updated: {INDEX_FILE}")

if __name__ == "__main__":
    main()
