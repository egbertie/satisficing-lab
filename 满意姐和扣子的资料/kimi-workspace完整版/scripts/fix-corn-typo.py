#!/usr/bin/env python3
"""
fix-cron-typo.py - 全局修正corn拼写错误
"""
import os
import re
from pathlib import Path

def fix_typo_in_file(filepath):
    """修正单个文件中的corn为cron"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 统计corn出现次数（排除正常单词如corn本身）
        pattern = r'\bcorn\b'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        if matches:
            # 替换（保留大小写）
            new_content = re.sub(r'\bcorn\b', 'cron', content, flags=re.IGNORECASE)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return len(matches)
        return 0
    except Exception as e:
        print(f"  跳过 {filepath}: {e}")
        return 0

def main():
    workspace = Path('/root/.openclaw/workspace')
    fixed_files = []
    total_fixes = 0
    
    # 扫描文件类型
    extensions = ['.md', '.py', '.sh', '.txt', '.json']
    
    for ext in extensions:
        for filepath in workspace.rglob(f'*{ext}'):
            # 跳过二进制和隐藏文件
            if '.git' in str(filepath) or '__pycache__' in str(filepath):
                continue
            
            count = fix_typo_in_file(filepath)
            if count > 0:
                fixed_files.append(str(filepath.relative_to(workspace)))
                total_fixes += count
                print(f"✅ 已修正 {count} 处: {filepath.name}")
    
    # 生成报告
    report = {
        'timestamp': '2026-04-15T14:05:00',
        'total_files': len(fixed_files),
        'total_fixes': total_fixes,
        'fixed_files': fixed_files[:20]  # 最多记录20个
    }
    
    print(f"\n📝 修正完成: {total_fixes} 处拼写错误，涉及 {len(fixed_files)} 个文件")
    return report

if __name__ == '__main__':
    main()
