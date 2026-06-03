#!/usr/bin/env python3
import ast
import os

FILES = [
    'claw_agent_optimizer.py','benchmark_token_saver.py','claw_lab_modes.py',
    'claw_cloud_storage.py','skill_digital_human.py','claw_guide_assistant.py',
    'claw_invoice_management_demo.py','claw_inspiration_capture.py','skill_clawpilot.py',
    'skill_graphify.py','skill_ai_native_dev.py','skill_openspec_installer.py',
    'skill_pua.py','claw_skill_discovery_creator.py'
]

for fname in FILES:
    path = os.path.join('/root/.openclaw/workspace', fname)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Start with full file, trim from end until it parses
    trim_idx = len(lines)
    parsed = False
    while trim_idx > 0:
        snippet = ''.join(lines[:trim_idx])
        # skip empty snippet
        if not snippet.strip():
            trim_idx -= 1
            continue
        try:
            ast.parse(snippet)
            parsed = True
            break
        except SyntaxError:
            trim_idx -= 1
    
    if parsed and trim_idx < len(lines):
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines[:trim_idx])
        print(f"Trimmed {fname}: {len(lines)} -> {trim_idx} lines")
    else:
        print(f"No trim needed or unable to parse {fname}")
