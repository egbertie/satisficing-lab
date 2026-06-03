#!/usr/bin/env python3
"""分类根目录.py脚本到A-manyige对应目录"""
import os, shutil, re

base = '/root/.openclaw/workspace'
target_base = '/root/.openclaw/workspace/A-manyige'

# 分类规则
rules = {
    '06_项目版本/算法模块/合伙人匹配': [
        'partner_matcher', 'partner_matching', 'partner_match', 'partner_mcda',
        'partner_landmine', 'partner_conflict', 'emergence_matching',
        'hardtech_partner', 'partner_selection', 'partner_'
    ],
    '06_项目版本/算法模块/决策引擎': [
        'ai_decision', 'satisficing_decision', 'satisficing_matcher',
        'prospect_theory', 'decision_style', 'decision_solidifier',
        'integrative_decision', 'slow_think_fast', 'kahneman'
    ],
    '06_项目版本/算法模块/评估系统': [
        'sku_a_assessment', 'assessment_orchestrator', 'maturity_scoring',
        'perceptual_intelligence', 'perceptual_tracker', 'perceptual_neuro',
        'perceptual_decision', 'piq', 'pressure_test', 'landmine_detector'
    ],
    '00_机制与管理/管理脚本/Token治理': [
        'token_benefit', 'token_circuit', 'token_monitor', 'token_tracker',
        'token_economic', 'token_fuse', 'token_optimizer', 'token_saver',
        'token_throttle', 'token_weekly', 'benchmark_token', 'token_budget',
        'token_zero', 'token_'
    ],
    '00_机制与管理/管理脚本/系统守护': [
        'system_guardian', 'daily_asset', 'unified_defense', 'unified_nurse',
        'cognitive_firewall', 'cognitive_immune', 'hibernation', 'circuit_breaker',
        'deadline_watchdog', 'bootstrap_guard', 'session_startup'
    ],
    '00_机制与管理/管理脚本/审计监控': [
        'blue_team', 'audit', 'auditor', 'sentinel', 'inspector',
        'file_presence', 'code_asset', 'todo_ghost', 'quality_gate',
        'efficiency_points', 'effectiveness', 'competitive_effectiveness'
    ],
    '02_知识资产/算法模块/儒商哲学': [
        'confucian', 'ru_shang', 'rishang', 'confucius', 'ethics_assessor',
        'ethics_evaluator', 'dingyu', '鼎玉'
    ],
    '02_知识资产/算法模块/五维图腾': [
        'totem', 'five_totem', 'totem_western', 'totem_quantifier', 'totem_multi',
        'pentad_extractor'
    ],
    '02_知识资产/算法模块/认知框架': [
        'cognitive_ecosystem', 'cognitive_organ', 'cognitive_workload',
        'cognitive_debt', 'cognitive_resonance', 'meta_cognitive',
        'systems_thinking', 'tool_first_cognitive', 'temporal_consistency',
        'context_persistence'
    ],
    '02_知识资产/算法模块/情报采集': [
        'intelligence_collection', 'social_media', 'academic_collector',
        'itjuzi', 'kr36', 'external_intel', 'info_collection'
    ],
    '02_知识资产/算法模块/方法论工具': [
        'yitang', 'methodology', 'skill_methodology', 'simon_satisficing',
        'simon_bibliography', 'first_principles', 'anticipatory_framework',
        'emergence_matching', 'honeybee', 'human_ai'
    ],
    '02_知识资产/算法模块/知识图谱': [
        'perceptual_decision_knowledge', 'knowledge_graph', 'knowledge_extraction',
        'cka_knowledge', 'cka_meta', 'file_structured_knowledge'
    ],
    '06_项目版本/算法模块/技能管理': [
        'skill_lifecycle', 'skill_execution', 'skill_bloodization',
        'skill_workflow', 'skill_conditioning', 'skill_methodology_extractor',
        'generate_skill_scene', 'skill_ai_native', 'skill_slimming',
        'claw_skill', 'skill_'
    ],
    '06_项目版本/算法模块/案例库': [
        'case_repo', 'case_repository', 'case_acquisition', 'hardtech_equity',
        'hardtech_investment', 'confucian_hardtech', 'xbotpark'
    ],
    '06_项目版本/算法模块/资产飞轮': [
        'sri_asset', 'assets_flywheel', 'asset_flywheel', 'client_financial',
        'value_alignment', 'product_positioning'
    ],
    '06_项目版本/算法模块/专家替身': [
        'dr_li', 'dr_fang', 'dr_xu', 'dr_xie', 'dr_luo', 'dr_chen',
        'digital_twin', 'expert_digital', 'lizexiang'
    ],
    '06_项目版本/算法模块/自动化工作流': [
        'automated_diligence', 'trigger_pipeline', 'workflow_cli',
        'start_workflow', 'claw_auto_injector', 'process_aibot'
    ],
    '00_机制与管理/管理脚本/文件处理': [
        'file_deep', 'file_internalization', 'downloads_md', 'extract_docx',
        'extract_code', 'reformat', 'fix_syntax', 'ast_trim',
        'downloads_md_converter', 'file7_processor', 'file_'
    ],
    '02_知识资产/算法模块/神经科学': [
        'neuroscience', 'neuro_feedback', 'perceptual_neuroscience',
        'intuition_calibrator'
    ],
    '02_知识资产/算法模块/反脆弱': [
        'antifragile', 'taleb', 'counterargument', 'defense_base'
    ],
}

# 收集根目录.py文件
py_files = [f for f in os.listdir(base) if f.endswith('.py') and not f.startswith('.')]

# 执行分类
categorized = {k: [] for k in rules.keys()}
categorized['02_知识资产/算法模块/其他'] = []

for fname in py_files:
    matched = False
    for category, keywords in rules.items():
        stem = fname.lower().replace('.py', '')
        for kw in keywords:
            if kw.lower() in stem:
                categorized[category].append(fname)
                matched = True
                break
        if matched:
            break
    if not matched:
        categorized['02_知识资产/算法模块/其他'].append(fname)

# 创建目录并移动
for cat, files in categorized.items():
    if not files:
        continue
    dest = os.path.join(target_base, cat)
    os.makedirs(dest, exist_ok=True)
    for f in files:
        src = os.path.join(base, f)
        dst = os.path.join(dest, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)

# 输出报告
print("=" * 60)
print("ROOT-LEVEL .PY SCRIPT CLASSIFICATION REPORT")
print("=" * 60)
total = 0
for cat, files in sorted(categorized.items()):
    if files:
        print(f"\n[{cat}] {len(files)} files:")
        for f in files[:5]:
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  ... ({len(files)-5} more)")
        total += len(files)
print(f"\n{'='*60}")
print(f"TOTAL: {total} scripts categorized")
print(f"{'='*60}")
