#!/usr/bin/env python3
"""决策挖掘器 - 从契晋纪历史文档中提取决策点"""
import sys, re, json
from pathlib import Path
from datetime import datetime

DECISION_PATTERNS = [
    r'(?:决定|决策|选择|选定|确定)[：:]\s*(.+)',
    r'(?:采用|选用|使用|执行)[：:]\s*(.+)',
    r'(?:放弃|否决|不采用)[：:]\s*(.+)',
    r'(?:最终|最后|结论)[：:]\s*(.+)',
    r'(?:拍板|定案|落定)[：:]\s*(.+)',
]

def excavate_decisions(text, source_path=""):
    decisions = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for pattern in DECISION_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # 提取上下文（前后5行）
                context_start = max(0, i-5)
                context_end = min(len(lines), i+6)
                context = '\n'.join(lines[context_start:context_end])
                decisions.append({
                    'source': source_path,
                    'line': i+1,
                    'decision_text': match.group(1).strip(),
                    'context': context,
                    'confidence': 'medium'
                })
    return decisions

def main():
    if len(sys.argv) < 2:
        print("用法: python3 decision-excavator.py <文件或目录>")
        return
    
    target = Path(sys.argv[1])
    all_decisions = []
    
    if target.is_file():
        text = target.read_text(encoding='utf-8', errors='ignore')
        all_decisions = excavate_decisions(text, str(target))
    elif target.is_dir():
        for md_file in target.rglob('*.md'):
            text = md_file.read_text(encoding='utf-8', errors='ignore')
            decisions = excavate_decisions(text, str(md_file))
            all_decisions.extend(decisions)
    
    # 输出JSON
    output = {
        'excavated_at': datetime.now().isoformat(),
        'total_decisions': len(all_decisions),
        'decisions': all_decisions[:50]  # 限制前50个
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
