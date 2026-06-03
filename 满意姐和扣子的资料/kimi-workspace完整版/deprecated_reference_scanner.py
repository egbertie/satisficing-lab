#!/usr/bin/env python3
"""
deprecated_reference_scanner.py
全 workspace 已归档旧版本引用自动扫描脚本
版本: 1.0
用途: 扫描 workspace 中是否仍有对 archive/deprecated/ 内旧版本文件的引用
"""

import os
import sys
import re
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent

WORKSPACE = Path('/root/.openclaw/workspace')
DEPRECATED_DIR = WORKSPACE / 'archive' / 'deprecated'

# 扫描时需要忽略的路径
IGNORE_PATTERNS = [
    r'archive/deprecated/',
    r'\.git/',
    r'__pycache__/',
    r'\.pyc$',
    r'OLD-ARCHIVE-2026/',
    r'A-manyige/',
    r'diary/honesty-audit/',
    r'memory/asset-activation/',
]

# 明确允许引用旧版本文件的白名单文件（这些文件本身就是管理旧版本的）
WHITELIST_FILES = {
    'daily_asset_runner.py',
    'deprecated_reference_scanner.py',
}

# 需要扫描的文件扩展名
SCAN_EXTENSIONS = {'.py', '.md', '.json', '.sh', '.txt', '.yaml', '.yml'}

DEPRECATED_FILES = [
    'skill_conditioning.py',
    'decision_solidifier.py',
    'unified_defense_system.py',
    'unified_defense_system_v2.py',
    'unified_defense_system_v3.py',
    'totem_quantifier.py',
]


class DeprecatedReferenceScanner(BaseComponent):
    def __init__(self):
        super().__init__('deprecated_scanner')
    
    def _should_ignore(self, path: Path) -> bool:
        rel = str(path.relative_to(WORKSPACE))
        for pattern in IGNORE_PATTERNS:
            if re.search(pattern, rel):
                return True
        if path.name in WHITELIST_FILES:
            return True
        return False
    
    def _scan_md_content(self, content: str, deprecated: str):
        """
        对 .md 文件进行两层扫描：
        1. 全局扫描 import/from 语句（因为 import 不一定在代码块里）
        2. 仅对 ```bash / ```sh / ```shell / ```python 代码块内扫描 python3 运行命令
        """
        import_patterns = [
            rf'from\s+{re.escape(deprecated).replace("\\.py", "")}\b',
            rf'import\s+{re.escape(deprecated).replace("\\.py", "")}\b',
        ]
        for p in import_patterns:
            if re.search(p, content):
                return True

        # 提取代码块并扫描运行命令
        code_block_pattern = re.compile(
            r'```(?:bash|sh|shell|python)\n(.*?)\n```',
            re.DOTALL | re.IGNORECASE
        )
        run_pattern = rf'python3\s+{re.escape(deprecated)}'
        for block in code_block_pattern.finditer(content):
            if re.search(run_pattern, block.group(1)):
                return True
        return False

    def scan(self):
        violations = []
        scanned = 0
        
        for filepath in WORKSPACE.rglob('*'):
            if not filepath.is_file():
                continue
            if filepath.suffix not in SCAN_EXTENSIONS:
                continue
            if self._should_ignore(filepath):
                continue
            
            scanned += 1
            try:
                content = filepath.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            
            for deprecated in DEPRECATED_FILES:
                # 排除archive/deprecated/README.md中的合法引用
                if 'README.md' in str(filepath) and 'archive/deprecated' in str(filepath):
                    continue

                if filepath.suffix == '.md':
                    if self._scan_md_content(content, deprecated):
                        violations.append({
                            'file': str(filepath.relative_to(WORKSPACE)),
                            'deprecated': deprecated,
                            'pattern': 'md_codeblock_or_import',
                            'line': None,
                        })
                        break
                else:
                    patterns = [
                        rf'python3\s+{re.escape(deprecated)}',
                        rf'from\s+{re.escape(deprecated).replace("\\.py", "")}\b',
                        rf'import\s+{re.escape(deprecated).replace("\\.py", "")}\b',
                        rf'{re.escape(deprecated)}',
                    ]
                    for pattern in patterns:
                        if re.search(pattern, content):
                            violations.append({
                                'file': str(filepath.relative_to(WORKSPACE)),
                                'deprecated': deprecated,
                                'pattern': pattern,
                                'line': None,
                            })
                            break
        
        return {
            'scanned_files': scanned,
            'violations': violations,
            'clean': len(violations) == 0
        }
    
    def run(self):
        print("=" * 60)
        print("🔍 已归档旧版本引用扫描")
        print("=" * 60)
        
        result = self.scan()
        print(f"\n扫描文件数: {result['scanned_files']}")
        print(f"违规引用数: {len(result['violations'])}")
        
        if result['clean']:
            print("\n✅ 扫描通过: 未发现对旧版本文件的违规引用")
            return 0
        else:
            print("\n❌ 发现违规引用:")
            for v in result['violations']:
                print(f"   - {v['file']} → {v['deprecated']}")
            return 1


if __name__ == '__main__':
    scanner = DeprecatedReferenceScanner()
    sys.exit(scanner.run())
