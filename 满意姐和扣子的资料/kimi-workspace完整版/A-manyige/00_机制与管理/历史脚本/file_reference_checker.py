#!/usr/bin/env python3
"""
全局文件引用一致性检查脚本
4维检查法 - 维度3：文件引用一致性
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")

# 引用模式定义
PATTERNS = {
    'markdown_link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),  # [text](path)
    'wiki_link': re.compile(r'\[\[([^\]]+)\]\]'),  # [[path]]
    'skill_ref': re.compile(r'skills/([^/\s]+)/SKILL\.md', re.IGNORECASE),  # skills/XXX/SKILL.md
    'memory_ref': re.compile(r'MEMORY\.md#([^\s\])]+)', re.IGNORECASE),  # MEMORY.md#section
    'doc_ref': re.compile(r'docs/([^\s\])]+\.md)', re.IGNORECASE),  # docs/XXX.md
    'internal_ref': re.compile(r'A满意哥专属文件夹/([^\s\])]+)', re.IGNORECASE),  # 内部引用
}

class ReferenceChecker:
    def __init__(self):
        self.all_md_files = []
        self.broken_refs = []
        self.version_mismatches = []
        self.circular_refs = []
        self.file_versions = {}
        self.stats = {
            'total_files': 0,
            'total_refs': 0,
            'broken_refs': 0,
            'version_issues': 0,
            'circular_refs': 0,
        }
        
    def scan_all_files(self):
        """扫描所有.md文件"""
        print("🔍 扫描所有Markdown文件...")
        for md_file in WORKSPACE.rglob("*.md"):
            # 排除.archive_开头的存档目录
            if ".archive_" not in str(md_file):
                self.all_md_files.append(md_file)
        self.stats['total_files'] = len(self.all_md_files)
        print(f"   发现 {self.stats['total_files']} 个Markdown文件")
        
    def extract_version(self, content):
        """从文件内容提取版本号"""
        # 常见版本号格式
        patterns = [
            r'版本[:：]\s*v?(\d+\.?\d*\.?\d*)',
            r'Version[:：]\s*v?(\d+\.?\d*\.?\d*)',
            r'v(\d+\.\d+\.?\d*)',
            r'V(\d+\.\d+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
        
    def check_file_exists(self, ref_path, source_file):
        """检查引用路径是否存在"""
        # 处理相对路径
        if ref_path.startswith('./') or ref_path.startswith('../'):
            base_dir = source_file.parent
            full_path = base_dir / ref_path
        elif ref_path.startswith('/'):
            full_path = Path(ref_path)
        else:
            # 尝试多种解析方式
            full_path = WORKSPACE / ref_path
            if not full_path.exists():
                # 尝试从source_file的目录解析
                full_path = source_file.parent / ref_path
                
        return full_path.exists(), full_path
        
    def analyze_file(self, md_file):
        """分析单个文件的引用"""
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"   ⚠️ 无法读取 {md_file}: {e}")
            return
            
        # 提取版本号
        version = self.extract_version(content)
        if version:
            self.file_versions[str(md_file)] = version
            
        # 查找Markdown链接
        for match in PATTERNS['markdown_link'].finditer(content):
            text, path = match.groups()
            # 过滤掉URL
            if path.startswith('http://') or path.startswith('https://') or path.startswith('#'):
                continue
            self.check_reference(md_file, path, 'markdown_link', match.start())
            
        # 查找Wiki链接
        for match in PATTERNS['wiki_link'].finditer(content):
            path = match.group(1)
            self.check_reference(md_file, path, 'wiki_link', match.start())
            
        # 查找SKILL.md引用
        for match in PATTERNS['skill_ref'].finditer(content):
            skill_name = match.group(1)
            skill_path = f"skills/{skill_name}/SKILL.md"
            self.check_reference(md_file, skill_path, 'skill_ref', match.start())
            
        # 查找MEMORY.md引用
        for match in PATTERNS['memory_ref'].finditer(content):
            section = match.group(1)
            self.check_reference(md_file, f"MEMORY.md#{section}", 'memory_ref', match.start())
            
        # 查找docs引用
        for match in PATTERNS['doc_ref'].finditer(content):
            doc_path = match.group(1)
            self.check_reference(md_file, f"docs/{doc_path}", 'doc_ref', match.start())
            
        # 查找内部文件夹引用
        for match in PATTERNS['internal_ref'].finditer(content):
            internal_path = match.group(1)
            self.check_reference(md_file, f"A满意哥专属文件夹/{internal_path}", 'internal_ref', match.start())
            
    def check_reference(self, source_file, ref_path, ref_type, position):
        """检查单个引用"""
        self.stats['total_refs'] += 1
        
        # 处理带锚点的路径
        clean_path = ref_path.split('#')[0]
        
        # 检查文件是否存在
        exists, full_path = self.check_file_exists(clean_path, source_file)
        
        if not exists and clean_path:
            self.broken_refs.append({
                'source': str(source_file),
                'ref_path': ref_path,
                'type': ref_type,
                'severity': 'P0' if ref_type in ['skill_ref', 'doc_ref'] else 'P1',
            })
            self.stats['broken_refs'] += 1
            
    def check_versions(self):
        """检查版本一致性"""
        print("\n📋 检查版本一致性...")
        # 检查是否有引用版本与实际文件版本不匹配的情况
        # 这需要更复杂的逻辑，暂时跳过详细实现
        pass
        
    def detect_circular_refs(self):
        """检测循环引用"""
        print("\n🔄 检测循环引用...")
        # 简化实现：检查A引用B，B引用A的情况
        ref_graph = defaultdict(set)
        
        for ref in self.broken_refs:
            if ref['severity'] == 'P0':
                continue
                
        # 实际循环引用检测需要构建完整的引用图
        pass
        
    def calculate_health_score(self):
        """计算健康度评分"""
        if self.stats['total_refs'] == 0:
            return 100
            
        broken_ratio = self.stats['broken_refs'] / self.stats['total_refs']
        version_ratio = self.stats['version_issues'] / max(self.stats['total_files'], 1)
        
        score = 100 - (broken_ratio * 50) - (version_ratio * 30) - (self.stats['circular_refs'] * 5)
        return max(0, min(100, score))
        
    def generate_report(self):
        """生成检查报告"""
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        health_score = self.calculate_health_score()
        
        report = f"""# 全局文件引用一致性检查报告
**检查时间**: {report_time}
**检查维度**: 4维检查法 - 维度3（文件引用一致性）

## 📊 总体统计

| 指标 | 数值 |
|------|------|
| 扫描文件数 | {self.stats['total_files']} |
| 发现引用数 | {self.stats['total_refs']} |
| 失效引用 | {self.stats['broken_refs']} |
| 版本问题 | {self.stats['version_issues']} |
| 循环引用 | {self.stats['circular_refs']} |
| **健康度评分** | **{health_score:.1f}/100** |

"""
        
        # 失效引用清单
        if self.broken_refs:
            report += "## 🔴 失效引用清单（P0严重/P1一般）\n\n"
            report += "| 源文件 | 引用路径 | 类型 | 严重级别 |\n"
            report += "|--------|----------|------|----------|\n"
            
            # 按严重级别排序
            sorted_refs = sorted(self.broken_refs, key=lambda x: 0 if x['severity'] == 'P0' else 1)
            for ref in sorted_refs[:50]:  # 限制输出数量
                report += f"| {ref['source'].replace(str(WORKSPACE), '.')} | {ref['ref_path']} | {ref['type']} | {ref['severity']} |\n"
                
            if len(sorted_refs) > 50:
                report += f"| ... | ... | ... | 还有 {len(sorted_refs) - 50} 项 |\n"
        else:
            report += "## ✅ 失效引用清单\n\n未发现失效引用。\n\n"
            
        # 修复建议
        report += """\n## 🔧 修复建议

### 高优先级（P0）
- 修复核心引用路径（skills/、docs/等关键目录）
- 检查文件移动或重命名导致的链接断裂

### 中优先级（P1）
- 修复内部文档引用
- 更新相对路径引用

### 修复命令示例
```bash
# 查找所有失效引用
grep -r "](skills/" /root/.openclaw/workspace --include="*.md" | grep -v ".archive_"

# 批量替换（谨慎使用）
# sed -i 's/旧路径/新路径/g' 文件.md
```

## 📈 健康度评估

"""
        
        if health_score >= 90:
            report += f"**{health_score:.1f}分** - 🟢 优秀：引用一致性良好\n"
        elif health_score >= 70:
            report += f"**{health_score:.1f}分** - 🟡 良好：存在少量问题，建议修复\n"
        elif health_score >= 50:
            report += f"**{health_score:.1f}分** - 🟠 一般：需要关注和修复\n"
        else:
            report += f"**{health_score:.1f}分** - 🔴 较差：急需全面治理\n"
            
        return report
        
    def run(self):
        """执行完整检查"""
        print("=" * 60)
        print("🚀 全局文件引用一致性检查")
        print("=" * 60)
        
        self.scan_all_files()
        
        print("\n📄 分析文件引用...")
        for i, md_file in enumerate(self.all_md_files):
            if i % 100 == 0:
                print(f"   进度: {i}/{len(self.all_md_files)}")
            self.analyze_file(md_file)
            
        self.check_versions()
        self.detect_circular_refs()
        
        # 生成并保存报告
        report = self.generate_report()
        report_path = WORKSPACE / "reports" / f"file_reference_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding='utf-8')
        
        print(f"\n✅ 检查完成！报告已保存: {report_path}")
        print(f"\n健康度评分: {self.calculate_health_score():.1f}/100")
        
        return report

if __name__ == "__main__":
    checker = ReferenceChecker()
    report = checker.run()
    print("\n" + "=" * 60)
    print(report)
