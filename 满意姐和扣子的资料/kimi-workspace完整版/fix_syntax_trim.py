#!/usr/bin/env python3
import os

FILES = [
    'claw_agent_optimizer.py','benchmark_token_saver.py','claw_lab_modes.py',
    'claw_cloud_storage.py','skill_digital_human.py','claw_guide_assistant.py',
    'claw_invoice_management_demo.py','claw_inspiration_capture.py','skill_clawpilot.py',
    'skill_graphify.py','skill_ai_native_dev.py','skill_openspec_installer.py',
    'skill_pua.py','claw_skill_discovery_creator.py'
]

chinese_punct = set('（），。！？“”‘’：；')

for fname in FILES:
    path = os.path.join('/root/.openclaw/workspace', fname)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_count = len(lines)
    # Trim from end
    while lines:
        line = lines[-1]
        stripped = line.strip()
        if not stripped:
            lines.pop()
            continue
        # If line contains full-width Chinese punctuation, it's likely narrative text
        if any(c in stripped for c in chinese_punct):
            lines.pop()
            continue
        break
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Trimmed {fname}: {original_count} -> {len(lines)} lines")
