#!/usr/bin/env python3
"""批量重新格式化从docx提取的单行Python文件"""
import ast
import sys
from pathlib import Path

FILES = [
    'antifragile_system.py',
    'temporal_consistency_engine.py',
    'value_alignment_quantizer.py',
    'cognitive_resonance_network.py',
    'cognitive_debt_manager.py',
    'edge_cognition_container.py',
    'meta_cognitive_orchestrator.py',
    'legal_as_code.py',
    'perceptual_tracker_proxy.py',
    'system_thermodynamics.py',
    'satisficing_ecosystem_v2.py',
    'module_rescue_pipeline.py',
    'knowledge_extraction_pipeline.py',
    'five_totem_engine.py',
]

def reformat_file(filename):
    path = Path('/root/.openclaw/workspace') / filename
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 去掉我手动添加的shebang和空行（ast会重新生成）
    lines = content.split('\n')
    while lines and (lines[0].startswith('#!') or lines[0].strip() == ''):
        lines.pop(0)
    code = '\n'.join(lines)
    try:
        tree = ast.parse(code)
        formatted = ast.unparse(tree)
        with open(path, 'w', encoding='utf-8') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write(formatted)
            f.write("\n")
        print(f"✓ {filename}: reformatted")
        return True
    except SyntaxError as e:
        print(f"✗ {filename}: syntax error - {e}")
        return False

if __name__ == "__main__":
    ok = 0
    for f in FILES:
        if reformat_file(f):
            ok += 1
    print(f"\nDone: {ok}/{len(FILES)} files reformatted")
    sys.exit(0 if ok == len(FILES) else 1)
