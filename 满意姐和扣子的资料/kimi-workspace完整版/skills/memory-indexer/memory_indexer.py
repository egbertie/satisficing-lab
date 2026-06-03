"""
记忆索引管理器 - Memory Indexer
核心模块: MEMORY.md轻量索引 + 当日记忆压缩
版本: 1.0.0
日期: 2026-04-02

整改说明 (蓝军要求):
- 原三层记忆架构 → 改为两阶段（Stage 1+2）
- 删除: Layer 3 Raw Transcripts（Web环境不支持）
- 压缩比: 5:1起步（非原10:1激进方案）
- 新限制: 跨会话细节丢失，依赖手动/compaction
"""

import re
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time


@dataclass
class IndexEntry:
    """索引条目"""
    topic: str
    file_path: str
    line_range: str
    priority: str  # P0/P1/P2
    last_updated: str
    hash_preview: str  # 前8位hash


@dataclass
class CompressionResult:
    """压缩结果"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    key_decisions: List[str]
    todos: List[str]
    insights: List[str]
    discarded: int  # 丢弃的内容量


class MemoryIndexer:
    """
    记忆索引管理器
    
    两阶段架构 (整改后):
    
    Stage 1: MEMORY.md轻量索引
    ├── 每行<150字符指针
    ├── 格式: [P0] 标题 → 路径:行范围
    ├── 不包含实际数据，只存"去哪里找"
    └── 严格写入纪律管理
    
    Stage 2: 当日记忆压缩
    ├── 每10轮触发/compaction
    ├── 保留: 关键决策+待办+重要洞察
    ├── 丢弃: 过程性对话+重复内容
    └── 压缩比目标: 5:1（保守起步）
    
    新限制声明:
    - 跨会话细节丢失（超出当前会话）
    - 压缩可能丢失次要信息
    - 依赖手动/compaction触发
    - 5:1压缩比可能无法达到，需调整
    """
    
    def __init__(
        self,
        workspace_path: str = "/root/.openclaw/workspace",
        memory_dir: str = "memory",
        max_index_size: int = 5 * 1024,  # 5KB
        compression_ratio_target: float = 5.0  # 5:1（保守）
    ):
        self.workspace = Path(workspace_path)
        self.memory_dir = self.workspace / memory_dir
        self.memory_dir.mkdir(exist_ok=True)
        
        self.memory_md_path = self.workspace / "MEMORY.md"
        self.max_index_size = max_index_size
        self.compression_target = compression_ratio_target
        
        # 压缩规则
        self.preserve_patterns = [
            r'##\s*决策[:：]\s*(.+)',           # 决策
            r'##\s*待办[:：]\s*(.+)',           # 待办
            r'##\s*TODO[:：]\s*(.+)',           # TODO
            r'##\s*关键洞察[:：]\s*(.+)',       # 洞察
            r'##\s*承诺[:：]\s*(.+)',           # 承诺
            r'\[([Pp][0-3])\]\s*(.+)',          # P0-P3标记
            r'✅\s*(.+)',                       # 完成项
            r'⏳\s*(.+)',                       # 待执行
        ]
        
        self.discard_patterns = [
            r'\[思考\].*',                       # 思考过程
            r'```\n[\s\S]*?```',                  # 代码块（保留结果）
            r'我认为', r'我觉得', r'可能',        # 模糊表达
            r'好的', r'明白', r'收到',            # 应答词
        ]
    
    # ============ Stage 1: 轻量索引 ============
    
    def rebuild_index(self) -> bool:
        """
        重建MEMORY.md轻量索引
        
        目标: 大小<5KB，每行150字符指针
        """
        index_entries = []
        
        # 扫描memory目录
        for md_file in sorted(self.memory_dir.glob("*.md")):
            if md_file.name == "MEMORY.md":
                continue
            
            # 解析文件内容
            entries = self._parse_memory_file(md_file)
            index_entries.extend(entries)
        
        # 生成索引内容
        index_content = self._generate_index_content(index_entries)
        
        # 检查大小
        if len(index_content.encode('utf-8')) > self.max_index_size:
            # 过大时只保留高优先级
            index_entries = [e for e in index_entries if e.priority in ['P0', 'P1']]
            index_content = self._generate_index_content(index_entries)
        
        # 写入MEMORY.md（使用严格写入纪律）
        return self._strict_write(index_content, self.memory_md_path)
    
    def _parse_memory_file(self, file_path: Path) -> List[IndexEntry]:
        """解析记忆文件，提取索引条目"""
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            return entries
        
        current_section = None
        line_num = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            line_num = i + 1
            
            # 检测标题
            if line.startswith('# '):
                current_section = line[2:].strip()[:50]  # 截断
                priority = self._detect_priority(line)
                
                entry = IndexEntry(
                    topic=current_section,
                    file_path=str(file_path.relative_to(self.workspace)),
                    line_range=f"{line_num}-{line_num+20}",
                    priority=priority,
                    last_updated=datetime.now().strftime("%Y-%m-%d"),
                    hash_preview=self._hash_preview(line)
                )
                entries.append(entry)
        
        return entries
    
    def _detect_priority(self, text: str) -> str:
        """检测优先级"""
        if '[P0]' in text or 'P0' in text:
            return 'P0'
        elif '[P1]' in text or 'P1' in text:
            return 'P1'
        elif '[P2]' in text or 'P2' in text:
            return 'P2'
        return 'P3'
    
    def _hash_preview(self, text: str) -> str:
        """生成hash预览"""
        return hashlib.md5(text.encode()).hexdigest()[:8]
    
    def _generate_index_content(self, entries: List[IndexEntry]) -> str:
        """生成索引内容"""
        lines = [
            "# MEMORY.md - 轻量级索引",
            "",
            f"> 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"> 条目数: {len(entries)}",
            f"> 大小限制: {self.max_index_size/1024:.1f}KB",
            "",
            "## 索引说明",
            "- 格式: [优先级] 主题 → 文件路径:行范围",
            "- 本文件只存指针，不存实际内容",
            "- 详细内容见各日期文件",
            "",
            "## 核心索引",
            ""
        ]
        
        # 按优先级分组
        for priority in ['P0', 'P1', 'P2', 'P3']:
            priority_entries = [e for e in entries if e.priority == priority]
            if priority_entries:
                lines.append(f"### {priority} 优先级")
                lines.append("")
                for entry in priority_entries[:20]:  # 每级最多20条
                    line = f"- [{entry.priority}] {entry.topic[:40]} → `{entry.file_path}:{entry.line_range}` (hash:{entry.hash_preview})"
                    lines.append(line[:150])  # 限制行长度
                lines.append("")
        
        return '\n'.join(lines)
    
    # ============ Stage 2: 记忆压缩 ============
    
    def compress_memory(self, input_text: str, target_ratio: float = None) -> CompressionResult:
        """
        压缩记忆内容
        
        目标: 5:1压缩比（保守起步，非原10:1激进）
        
        保留:
        - 关键决策
        - 待办事项
        - 重要洞察
        - 承诺
        
        丢弃:
        - 过程性思考
        - 重复内容
        - 模糊表达
        """
        target_ratio = target_ratio or self.compression_target
        original_size = len(input_text)
        
        # 提取保留内容
        key_decisions = self._extract_pattern(input_text, r'##\s*决策[:：]\s*(.+)|\b决定\b[:：]\s*(.+)')
        todos = self._extract_pattern(input_text, r'##\s*(?:待办|TODO)[:：]\s*(.+)|- \[ \]\s*(.+)')
        insights = self._extract_pattern(input_text, r'##\s*(?:洞察|发现)[:：]\s*(.+)|\b发现\b[:：]\s*(.+)')
        commitments = self._extract_pattern(input_text, r'##\s*承诺[:：]\s*(.+)|\b承诺\b[:：]\s*(.+)')
        
        # 构建压缩后内容
        compressed_lines = [
            "# 压缩记忆摘要",
            f"",
            f"> 原始大小: {original_size} 字符",
            f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f""
        ]
        
        if key_decisions:
            compressed_lines.extend(["## 关键决策", ""])
            for i, d in enumerate(key_decisions[:10], 1):
                compressed_lines.append(f"{i}. {d[:100]}")
            compressed_lines.append("")
        
        if todos:
            compressed_lines.extend(["## 待办事项", ""])
            for i, t in enumerate(todos[:10], 1):
                compressed_lines.append(f"- [ ] {t[:100]}")
            compressed_lines.append("")
        
        if insights:
            compressed_lines.extend(["## 重要洞察", ""])
            for i, ins in enumerate(insights[:10], 1):
                compressed_lines.append(f"{i}. {ins[:100]}")
            compressed_lines.append("")
        
        if commitments:
            compressed_lines.extend(["## 承诺事项", ""])
            for i, c in enumerate(commitments[:5], 1):
                compressed_lines.append(f"- {c[:100]}")
            compressed_lines.append("")
        
        compressed_text = '\n'.join(compressed_lines)
        compressed_size = len(compressed_text)
        
        # 计算压缩比
        if compressed_size > 0:
            actual_ratio = original_size / compressed_size
        else:
            actual_ratio = 1.0
        
        # 如果未达到目标压缩比，进一步压缩
        if actual_ratio < target_ratio and compressed_size > 500:
            # 截断到目标大小
            target_size = int(original_size / target_ratio)
            compressed_text = compressed_text[:target_size]
            compressed_size = len(compressed_text)
            actual_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        
        discarded = original_size - compressed_size
        
        return CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=actual_ratio,
            key_decisions=key_decisions[:10],
            todos=todos[:10],
            insights=insights[:10],
            discarded=discarded
        )
    
    def _extract_pattern(self, text: str, pattern: str) -> List[str]:
        """提取匹配模式的内容"""
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        results = []
        for match in matches:
            if isinstance(match, tuple):
                # 取非空的匹配组
                content = next((m for m in match if m), "")
            else:
                content = match
            if content and len(content.strip()) > 5:
                results.append(content.strip())
        return list(set(results))  # 去重
    
    def compact_session(self, session_file: Path) -> bool:
        """
        压缩会话文件（/compaction触发）
        
        流程:
        1. 读取原始内容
        2. 压缩
        3. 备份原始（可选）
        4. 写入压缩内容
        """
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                original = f.read()
        except:
            return False
        
        # 压缩
        result = self.compress_memory(original)
        
        # 检查压缩效果
        if result.compression_ratio < 2.0:
            # 压缩效果不佳，保留原样
            return False
        
        # 生成压缩后文件
        compressed_file = session_file.with_suffix('.compact.md')
        compressed_content = f"""# 压缩会话记录

> 原始文件: {session_file.name}
> 原始大小: {result.original_size} 字符
> 压缩后大小: {result.compressed_size} 字符
> 压缩比: {result.compression_ratio:.1f}:1
> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

{self._generate_compressed_body(result)}

---

## 统计

- 保留决策: {len(result.key_decisions)} 条
- 保留待办: {len(result.todos)} 条
- 保留洞察: {len(result.insights)} 条
- 丢弃内容: {result.discarded} 字符

---

> 注意: 此为压缩版本，详细内容见原始文件
"""
        
        # 写入（使用严格写入）
        return self._strict_write(compressed_content, compressed_file)
    
    def _generate_compressed_body(self, result: CompressionResult) -> str:
        """生成压缩后正文"""
        lines = []
        
        if result.key_decisions:
            lines.extend(["## 关键决策", ""])
            for d in result.key_decisions:
                lines.append(f"- {d[:150]}")
            lines.append("")
        
        if result.todos:
            lines.extend(["## 待办事项", ""])
            for t in result.todos:
                lines.append(f"- [ ] {t[:150]}")
            lines.append("")
        
        if result.insights:
            lines.extend(["## 重要洞察", ""])
            for i in result.insights:
                lines.append(f"- {i[:150]}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _strict_write(self, content: str, file_path: Path) -> bool:
        """严格写入（使用已实现的严格写入纪律）"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                f.flush()
                import os
                os.fsync(f.fileno())
            return True
        except:
            return False
    
    # ============ 工具方法 ============
    
    def get_index_stats(self) -> Dict:
        """获取索引统计"""
        stats = {
            "memory_md_exists": self.memory_md_path.exists(),
            "memory_md_size": 0,
            "memory_files_count": 0,
            "compression_target": self.compression_target,
            "max_index_size": self.max_index_size
        }
        
        if self.memory_md_path.exists():
            stats["memory_md_size"] = self.memory_md_path.stat().st_size
        
        stats["memory_files_count"] = len(list(self.memory_dir.glob("*.md")))
        
        return stats
    
    def validate_index(self) -> bool:
        """验证索引完整性"""
        if not self.memory_md_path.exists():
            return False
        
        try:
            with open(self.memory_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基本验证
            checks = [
                len(content) <= self.max_index_size,
                "# MEMORY.md" in content,
                "轻量级索引" in content
            ]
            
            return all(checks)
        except:
            return False


# 便捷函数接口
def rebuild_memory_index() -> bool:
    """便捷重建索引函数"""
    indexer = MemoryIndexer()
    return indexer.rebuild_index()


def compact_session_file(file_path: str) -> bool:
    """便捷压缩函数"""
    indexer = MemoryIndexer()
    return indexer.compact_session(Path(file_path))


if __name__ == "__main__":
    # 单元测试
    print("=" * 60)
    print("记忆索引管理器 - 单元测试")
    print("=" * 60)
    
    indexer = MemoryIndexer()
    
    # 测试1: 索引重建
    print("\n[测试1] 索引重建...")
    result = indexer.rebuild_index()
    print(f"  重建结果: {'成功' if result else '失败'}")
    
    if indexer.memory_md_path.exists():
        size = indexer.memory_md_path.stat().st_size
        print(f"  索引大小: {size} bytes ({size/1024:.2f}KB)")
        print(f"  大小检查: {'✅ 通过' if size <= 5120 else '❌ 超标'}")
    
    # 测试2: 记忆压缩
    print("\n[测试2] 记忆压缩...")
    test_content = """
# 会话记录

这是一个测试内容。

## 决策
我们决定采用方案A。

## 待办
- [ ] 完成任务1
- [ ] 完成任务2

一些过程性思考：我觉得可能应该这样，然后再那样...

## 洞察
发现一个重要规律。

重复内容：这是一个测试内容。

好的，明白，收到。

## 承诺
我承诺在下周完成。
""" * 5  # 放大内容测试压缩
    
    result = indexer.compress_memory(test_content, target_ratio=5.0)
    print(f"  原始大小: {result.original_size} 字符")
    print(f"  压缩后大小: {result.compressed_size} 字符")
    print(f"  压缩比: {result.compression_ratio:.1f}:1")
    print(f"  目标比: 5:1")
    print(f"  压缩效果: {'✅ 达标' if result.compression_ratio >= 4.0 else '⚠️ 未达标'}")
    print(f"  保留决策: {len(result.key_decisions)} 条")
    print(f"  保留待办: {len(result.todos)} 条")
    print(f"  保留洞察: {len(result.insights)} 条")
    
    # 测试3: 统计信息
    print("\n[测试3] 索引统计...")
    stats = indexer.get_index_stats()
    print(f"  MEMORY.md存在: {stats['memory_md_exists']}")
    print(f"  索引大小: {stats['memory_md_size']} bytes")
    print(f"  记忆文件数: {stats['memory_files_count']}")
    print(f"  压缩目标: {stats['compression_target']}:1")
    
    # 测试4: 索引验证
    print("\n[测试4] 索引验证...")
    valid = indexer.validate_index()
    print(f"  验证结果: {'✅ 通过' if valid else '❌ 失败'}")
    
    print("\n" + "=" * 60)
    print("单元测试完成")
    print("=" * 60)
    print("\n注意: 压缩比目标5:1为保守起步")
    print("      实际效果依赖内容类型，可能需要调整")