#!/usr/bin/env python3
"""
Extract Python code blocks from the tencent_news_0408.txt research dump.
Heuristic: start at '# filename.py', end at next '# filename.py' or obvious heading.
"""
import re
import os

INPUT = '/tmp/tencent_news_0408.txt'
OUTPUT_DIR = '/root/.openclaw/workspace'

with open(INPUT, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all start markers
markers = []
for i, line in enumerate(lines):
    m = re.match(r'#\s+([A-Za-z0-9_]+\.py)(\s+[-–].*)?$', line.strip())
    if m:
        markers.append((i, m.group(1)))

print(f"Found {len(markers)} code blocks")

extracted = []
for idx, (start_line, fname) in enumerate(markers):
    end_line = len(lines)
    if idx + 1 < len(markers):
        end_line = markers[idx + 1][0]
    
    block = lines[start_line:end_line]
    
    # Trim trailing non-code lines (heuristic: lines that are Chinese explanations without code)
    while block:
        last = block[-1].strip()
        if last == '' or last.startswith('#') or any(c in last for c in ['import ', 'def ', 'class ', 'return ', 'print(', 'async ', 'await ', 'if ', 'elif ', 'else:', 'try:', 'except', 'for ', 'while ', 'with ', 'pass', 'continue', 'break', '=', '{', '}', '[', ']', '(', ')', ':', '\"', "'"]):
            break
        block.pop()
    
    code = ''.join(block)
    out_path = os.path.join(OUTPUT_DIR, fname)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(code)
    extracted.append((fname, len(block)))
    print(f"  Written {fname} ({len(block)} lines)")

print(f"\nTotal extracted: {len(extracted)} files")
