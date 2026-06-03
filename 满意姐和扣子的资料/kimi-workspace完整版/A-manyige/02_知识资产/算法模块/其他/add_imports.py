#!/usr/bin/env python3
import os
import re

OUTPUT_DIR = '/root/.openclaw/workspace'
files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.py') and f.startswith(('claw_', 'skill_'))]

TYPING_SYMBOLS = ['Dict', 'List', 'Optional', 'Any', 'Union', 'Tuple', 'Callable']

for fname in files:
    path = os.path.join(OUTPUT_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines(keepends=True)
    
    # Check if __future__ annotations already exists
    has_future = any('from __future__ import annotations' in line for line in lines)
    
    # Determine typing symbols used
    used_types = [sym for sym in TYPING_SYMBOLS if re.search(r'\b' + sym + r'\b', content)]
    has_typing_import = any('from typing import' in line for line in lines) or any('import typing' in line for line in lines)
    
    insertions = []
    if not has_future:
        insertions.append('from __future__ import annotations\n')
    if used_types and not has_typing_import:
        insertions.append(f"from typing import {', '.join(used_types)}\n")
    
    if insertions:
        # Find insertion point: after shebang/comments at top, before first code line
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                insert_idx = i
                break
            insert_idx = i + 1
        
        # If there is already a blank line before code, insert there
        new_lines = lines[:insert_idx] + insertions + lines[insert_idx:]
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Updated {fname}: {' + '.join(insertions).strip()}")
    else:
        print(f"Skipped {fname}")
