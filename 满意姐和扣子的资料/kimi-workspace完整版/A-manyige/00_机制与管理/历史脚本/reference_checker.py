#!/usr/bin/env python3
"""
全局文件引用一致性检查脚本
4维检查法 - 维度3: 引用一致性
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

WORKSPACE = "/root/.openclaw/workspace"

# 引用模式定义
REFERENCE_PATTERNS = {
    'markdown_link': r'\[([^\]]+)\]\(([^)]+)\)',  # [text](path)
    'wiki_link': r'\[\[([^\]]+)\]\]',  # [[path]]
    'md_ref': r'`([^`]*\.md)[^`]*`',  # `path.md`
    'memory_ref': r'MEMORY\.md#([\w-]+)',  # MEMORY.md#section
    'skill_ref': r'skills/([\w-]+)/SKILL\.md',  # skills/xxx/SKILL.md
    'version_in_ref': r'v(\d+\.?\d*)',  # v1.0, v2, etc.
}

class ReferenceChecker:
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.issues = {
            'broken_refs': [],
            'version_mismatch': [],
            'circular_refs': [],
            'suspicious_refs': []
        }
        self.stats = {
            'total_files': 0,
            'total_refs': 0,
            'valid_refs': 0,
            'broken_refs': 0,
        }
        self.file_versions = {}
        
    def scan_all_md_files(self):
        """扫描所有md文件"""
        md_files = list(self.workspace.rglob("*.md"))
        self.stats['total_files'] = len(md_files)
        return md_files
    
    def extract_file_version(self, file_path):
        """提取文件中的版本号"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            # 查找版本声明
            version_patterns = [
                r'版本[:：]\s*v?(\d+\.?\d*)',
                r'Version[:：]\s*v?(\d+\.?\d*)',
                r'v(\d+\.\d+\.?\d*)',  # v1.0.0
                r'##?\s*版本.*\n.*?(\d+\.?\d*)',
            ]
            for pattern in version_patterns:
                match = re.search(pattern, content[:5000], re.IGNORECASE)
                if match:
                    return match.group(1)
        except Exception as e:
            pass
        return None
    
    def resolve_reference(self, ref_path, source_file):
        """解析引用路径"""
        # 处理绝对路径（相对于workspace）
        if ref_path.startswith('/'):
            resolved = self.workspace / ref_path.lstrip('/')
        # 处理相对路径
        elif ref_path.startswith('./') or ref_path.startswith('../') or not ref_path.startswith('/'):
            resolved = source_file.parent / ref_path
        else:
            resolved = self.workspace / ref_path
        
        return resolved.resolve() if resolved.exists() else resolved
    
    def check_references_in_file(self, file_path):
        """检查单个文件中的所有引用"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return
        
        relative_path = file_path.relative_to(self.workspace)
        
        # 检查Markdown链接 [text](path)
        for match in re.finditer(REFERENCE_PATTERNS['markdown_link'], content):
            text, path = match.groups()
            # 跳过URL和锚点
            if path.startswith('http') or path.startswith('#'):
                continue
            
            self.stats['total_refs'] += 1
            resolved = self.resolve_reference(path, file_path)
            
            if not resolved.exists():
                self.issues['broken_refs'].append({
                    'source': str(relative_path),
                    'ref_type': 'markdown_link',
                    'ref_text': text,
                    'ref_path': path,
                    'line': content[:match.start()].count('\n') + 1,
                    'severity': 'P1' if 'SKILL.md' in path or 'MEMORY.md' in path else 'P2'
                })
                self.stats['broken_refs'] += 1
            else:
                self.stats['valid_refs'] += 1
        
        # 检查SKILL.md引用
        for match in re.finditer(REFERENCE_PATTERNS['skill_ref'], content):
            skill_name = match.group(1)
            self.stats['total_refs'] += 1
            
            skill_path = self.workspace / 'skills' / skill_name / 'SKILL.md'
            if not skill_path.exists():
                self.issues['broken_refs'].append({
                    'source': str(relative_path),
                    'ref_type': 'skill_ref',
                    'ref_path': f'skills/{skill_name}/SKILL.md',
                    'line': content[:match.start()].count('\n') + 1,
                    'severity': 'P0'
                })
                self.stats['broken_refs'] += 1
            else:
                self.stats['valid_refs'] += 1
        
        # 检查MEMORY.md引用
        for match in re.finditer(REFERENCE_PATTERNS['memory_ref'], content):
            section = match.group(1)
            self.stats['total_refs'] += 1
            
            memory_path = self.workspace / 'MEMORY.md'
            if memory_path.exists():
                self.stats['valid_refs'] += 1
            else:
                self.issues['broken_refs'].append({
                    'source': str(relative_path),
                    'ref_type': 'memory_ref',
                    'ref_path': f'MEMORY.md#{section}',
                    'line': content[:match.start()].count('\n') + 1,
                    'severity': 'P1'
                })
                self.stats['broken_refs'] += 1
    
    def check_skills_directory(self):
        """专门检查skills目录的引用一致性"""
        skills_dir = self.workspace / 'skills'
        if not skills_dir.exists():
            return
        
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir():
                skill_md = skill_path / 'SKILL.md'
                if not skill_md.exists():
                    self.issues['suspicious_refs'].append({
                        'type': 'missing_skill_md',
                        'path': str(skill_path.relative_to(self.workspace)),
                        'severity': 'P2'
                    })
    
    def generate_report(self):
        """生成检查报告"""
        # 计算健康度
        if self.stats['total_refs'] > 0:
            health_score = (self.stats['valid_refs'] / self.stats['total_refs']) * 100
        else:
            health_score = 100
        
        # 按严重级别分类
        p0_issues = [i for i in self.issues['broken_refs'] if i.get('severity') == 'P0']
        p1_issues = [i for i in self.issues['broken_refs'] if i.get('severity') == 'P1']
        p2_issues = [i for i in self.issues['broken_refs'] if i.get('severity') == 'P2']
        
        report = {
            'timestamp': '2026-03-21T10:11:00+08:00',
            'check_type': '全局文件引用一致性检查',
            'stats': self.stats,
            'health_score': round(health_score, 2),
            'issues_summary': {
                'P0_critical': len(p0_issues),
                'P1_high': len(p1_issues),
                'P2_medium': len(p2_issues),
                'suspicious': len(self.issues['suspicious_refs'])
            },
            'broken_refs_by_severity': {
                'P0': p0_issues,
                'P1': p1_issues,
                'P2': p2_issues
            },
            'suspicious_refs': self.issues['suspicious_refs']
        }
        
        return report
    
    def run(self):
        """执行完整检查"""
        print("🔍 开始全局文件引用一致性检查...")
        print(f"📁 工作空间: {self.workspace}")
        
        # 扫描所有文件
        print("\n📄 扫描Markdown文件...")
        md_files = self.scan_all_md_files()
        print(f"   发现 {len(md_files)} 个Markdown文件")
        
        # 检查每个文件
        print("\n🔎 检查文件引用...")
        for i, file_path in enumerate(md_files):
            if i % 200 == 0:
                print(f"   进度: {i}/{len(md_files)}")
            self.check_references_in_file(file_path)
        
        # 检查skills目录
        print("\n🛠️  检查Skills目录...")
        self.check_skills_directory()
        
        # 生成报告
        print("\n📊 生成报告...")
        report = self.generate_report()
        
        return report

if __name__ == '__main__':
    checker = ReferenceChecker(WORKSPACE)
    report = checker.run()
    
    # 输出JSON报告
    print("\n" + "="*60)
    print(json.dumps(report, indent=2, ensure_ascii=False))
