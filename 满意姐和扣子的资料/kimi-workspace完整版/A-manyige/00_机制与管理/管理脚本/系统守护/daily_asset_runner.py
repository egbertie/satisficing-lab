"""
---
KIA-CODE: 知识入库代码级闭环
Asset: daily_asset_runner.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (功能定位确认)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 日常资产调度运行器
  - 关联: 五路图腾系统
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 观自在-流动智慧
  - 产品映射: SKU调度
  - 运营映射: 日常资产激活

---
"""

#!/usr/bin/env python3
"""
日常资产激活调度器 Daily Asset Runner
版本: 1.1 (蓝军整改后)
用途: 把workspace里"睡大觉"的系统资产真正用起来
规则: 每天早上由HEARTBEAT调用，激活监控/管理/收集类资产
更新: 2026-04-04 - 增加产出验证、差异化超时、dry-run支持
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent

WORKSPACE = '/root/.openclaw/workspace'
# 规则固化：供用户阅读的运行报告统一放 A-manyige/汇报/日报/
LOG_DIR = f'{WORKSPACE}/A-manyige/汇报/日报'
os.makedirs(LOG_DIR, exist_ok=True)

# 分类名称中文映射（用户可读）
CATEGORY_NAME_MAP = {
    'defense': '监控防御',
    'intelligence': '情报收集',
    'business': '业务系统',
    'management': '管理效能',
    'library': '基础库',
    'deprecated': '已废弃',
}

# 资产分类: 哪些需要日常激活，哪些是纯库
ASSET_REGISTRY = {
    # 监控防御类 - 每日运行
    'defense': [
        'unified_defense_system_v4.py',
        'skill_conditioning_v2.py',
        'decision_solidifier_v2.py',
        'repetition_inhibitor.py',
        'manual_approval_system.py',
    ],
    # 情报收集类 - 每日运行(轻量模式)
    'intelligence': [
        'intelligence_collection_system.py',
        'social_media_collector.py',
        'obsidian_sync.py',
    ],
    # 业务系统类 - 每周运行(或按需)
    'business': [
        'ai_decision_system.py',
        'partner_matcher.py',
        'satisficing_matcher.py',
        'simon_satisficing.py',
        'prospect_theory_scorer.py',
        'intuition_calibrator.py',
        'confucian_ethics_evaluator.py',
        'totem_multi_agent_council.py',
        'case_repository_system.py',
        # 4月6日 P0-系统类 + P0-核心类 新增资产
        'partner_mcda_selector.py',
        'hardtech_partner_risk_scanner.py',
        'xbotpark_synergy_evaluator.py',
        'confucian_ethics_assessor.py',
        'satisficing_decision_engine.py',
        'client_financial_impact_tracker.py',
        'competitive_effectiveness_evaluator.py',
        'perceptual_intelligence_evaluator.py',
        'totem_western_mapping.py',
        'perceptual_neuroscience_tracker.py',
        'hardtech_partner_conflict_window.py',
        'lizexiang_human_factor_analyzer.py',
        'lizexiang_synergy_strategy_v1.py',
        'project_operation_playbook.py',  # 2026-04-09 一堂复盘营项目运营方法论资产
        'yitang_methodology_kit.py',  # 2026-04-09 一堂方法论补充资料（129案例+AI加速包）
        'sri_asset_flywheel.py',  # 2026-04-09 满意解研究所底层操作系统：资产飞轮+经营指标
        'hardtech_partner_selection_casebook.py',
        'ai_partner_matching_landscape.py',
        'perceptual_decision_knowledge_graph.py',
        'hardtech_investment_policy_scanner.py',
        'dingyu_brand_prism.py',
        'partner_landmine_detector.py',
        'confucian_hardtech_case_index.py',
        'hardtech_equity_dispute_casebook.py',
        'xbotpark_evidence_validator.py',
        'simon_bibliography_index.py',
        'founder_first_meeting_script.py',
        'counterargument_playbook.py',
        'qpms_validation_framework.py',
        'dets_config_generator.py',
        'dr_fang_digital_twin.py',
        'dr_li_digital_twin.py',
        'confucian_business_philosophy_core.py',  # 2026-04-09 黎红雷儒商哲学内核资产
        'confucian_business_wisdom.py',  # 2026-04-09 黎红雷《儒家商道智慧》内化资产
        'pressure_test_72h_experimental.py',
        'emergence_matching_academic.py',
        'cka_knowledge_base_builder.py',
        'cka_meta_library_builder.py',
        'sku_a_assessment_orchestrator.py',  # 2026-04-09 Partner Matching SKU-A 评估编排器
        # 'technical_enforcement_suite.py',  # 路径在 skills/namespace-enforcement/，不在根目录
        # 'totem_agents.py',  # 路径在 cognitive_ecosystem/council/，不在根目录
        # 2026-04-08 外援深度优化方案落地（P1/P2缺口填补）
        'cognitive_firewall.py',
        'cognitive_immune_system.py',
        'temporal_consistency_engine.py',
        'cross_cultural_trust.py',
        'product_positioning_mvsr.py',
        'human_ai_symbiosis.py',
        'emergence_matching_system.py',
        'pressure_test_72h.py',
        'legal_as_code.py',
        'perceptual_tracker_proxy.py',
        # 2026-04-09 决策科学主题包
        'slow_think_fast_decide_toolkit.py',
        'kahneman_tversky_decision_archive.py',
        'honeybee_democracy_toolkit.py',
        'systems_thinking_primer.py',
        'integrative_decision_toolkit.py',
        # 2026-04-09 合伙人匹配咨询工具箱（实战级）
        'partner_match_consultation_kit.py',
        # 2026-04-09 专家矩阵数字替身补全
        'dr_luo_han_digital_twin.py',
        'dr_xie_bao_jian_digital_twin.py',
        'dr_xu_digital_twin.py',
        'dr_chen_guo_xiang_digital_twin.py',
        'dr_li_zexiang_digital_twin.py',
        # 2026-04-09 12场景条件反射矩阵实测基座
        'cognitive_organ_reflex_matrix.py',
    ],
    # 效率管理类 - 每日运行
    'management': [
        'efficiency_points_system.py',
        'efficiency_visualizer.py',
        'continual_learning_engine.py',
        'skill_governance_dashboard.py',
        'deprecated_reference_scanner.py',
        'claw_space_manager.py',
        'todo_ghost_hunter.py',  # 2026-04-09 待办幽灵猎人机制
        'skill_bloodization_guardian.py',  # 2026-04-09 技能血液化监控守护器
        'file_internalization_orchestrator.py',  # 2026-04-09 批量文件内化编排器
        'downloads_md_converter.py',  # 2026-04-09 .kimi/downloads/ → Markdown 转化流水线
    ],
    # 纯库/base类 - 不直接运行
    'library': [
        'defense_base_components.py',
        'report_template_system.py',
        'file7_processor_template.py',
        'context_persistence.py',
    ],
    # 旧版本 - 归档处理
    'deprecated': [
        'unified_defense_system.py',
        'unified_defense_system_v2.py',
        'unified_defense_system_v3.py',
        'skill_conditioning.py',
        'decision_solidifier.py',
        'totem_quantifier.py',
    ]
}

# 分类超时配置 (秒)
CATEGORY_TIMEOUT = {
    'defense': 30,
    'management': 30,
    'business': 60,
    'intelligence': 120,
}

# 产出验证规则 (按分类)
VALIDATION_RULES = {
    'defense': {
        'forbidden_patterns': [r'ERROR', r'Exception', r'Traceback'],
        'required_patterns': [],
        'min_output_length': 5,
    },
    'intelligence': {
        'forbidden_patterns': [r'暂无采集器', r'无数据', r'采集失败', r'ERROR'],
        'required_patterns': [],
        'min_output_length': 20,
    },
    'business': {
        'forbidden_patterns': [r'ERROR', r'Exception', r'Traceback'],
        'required_patterns': [],
        'min_output_length': 10,
    },
    'management': {
        'forbidden_patterns': [r'ERROR', r'Exception', r'Traceback', r'insufficient_data'],
        'required_patterns': [],
        'min_output_length': 10,
    },
}

# 特定资产额外规则
ASSET_VALIDATION = {
    'intelligence_collection_system.py': {
        # 必须真正产出至少1条情报（"采集完成: 共 N 条情报" 且 N > 0）
        'required_patterns': [r'采集完成:\s*共\s*[1-9]\d*\s*条情报'],
    },
    'continual_learning_engine.py': {
        # 样本数>0才算有产出
        'required_patterns': [r'学习样本数:\s*[1-9]\d*'],
    },
}

class DailyAssetRunner(BaseComponent):
    def __init__(self, dry_run=False):
        super().__init__('daily_asset_runner')
        self.dry_run = dry_run or os.environ.get('DAILY_RUNNER_DRY_RUN') == '1'
        self.report = {
            'timestamp': self.get_timestamp(),
            'activated': [],
            'validation_failed': [],
            'skipped': [],
            'errors': [],
            'deprecated_found': [],
            'summary': {}
        }
        self.history_file = f'{LOG_DIR}/activation_history.json'
        self.history = self.load_json(self.history_file, {})
    
    def _should_run(self, asset_name, category):
        """判断是否应该运行该资产"""
        if category in ['library', 'deprecated']:
            return False, 'category_excluded'
        
        last_run = self.history.get(asset_name, 0)
        last_dt = datetime.fromtimestamp(last_run) if last_run else None
        now = datetime.now()
        
        if category == 'business':
            if last_dt and (now - last_dt).days < 7:
                return False, f'last_run_{last_dt.strftime("%m-%d")}'
        else:
            if last_dt and last_dt.date() == now.date():
                return False, 'already_today'
        
        if not os.path.exists(f'{WORKSPACE}/{asset_name}'):
            return False, 'file_not_found'
        
        return True, 'ready'
    
    def _validate_output(self, asset_name, category, stdout, stderr):
        """验证产出是否有效"""
        output = (stdout or '') + '\n' + (stderr or '')
        
        # 获取规则（分类默认 + 资产特定覆盖）
        rules = dict(VALIDATION_RULES.get(category, {}))
        asset_override = ASSET_VALIDATION.get(asset_name, {})
        for key in ['forbidden_patterns', 'required_patterns', 'min_output_length']:
            if key in asset_override:
                rules[key] = asset_override[key]
        
        # 检查禁止模式
        for pattern in rules.get('forbidden_patterns', []):
            if re.search(pattern, output):
                return False, f"命中禁止模式: {pattern}"
        
        # 检查必须模式
        for pattern in rules.get('required_patterns', []):
            if not re.search(pattern, output):
                return False, f"未命中必须模式: {pattern}"
        
        # 检查最小长度
        min_len = rules.get('min_output_length', 0)
        if min_len and len(output.strip()) < min_len:
            return False, f"输出过短: {len(output.strip())} < {min_len}"
        
        return True, 'pass'
    
    def _run_asset(self, asset_name, category):
        """执行单个资产"""
        filepath = f'{WORKSPACE}/{asset_name}'
        timeout = CATEGORY_TIMEOUT.get(category, 30)
        
        if self.dry_run:
            return {
                'returncode': 0,
                'stdout': f'[DRY-RUN] 跳过执行: {asset_name}',
                'stderr': ''
            }
        
        try:
            result = subprocess.run(
                ['python3', filepath, '--daily'],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=WORKSPACE
            )
            return {
                'returncode': result.returncode,
                'stdout': result.stdout[:800] if result.stdout else '',
                'stderr': result.stderr[:400] if result.stderr else ''
            }
        except subprocess.TimeoutExpired:
            return {'returncode': -1, 'error': f'timeout ({timeout}s)'}
        except Exception as e:
            return {'returncode': -1, 'error': str(e)}
    
    def run(self):
        """执行每日资产激活"""
        now_ts = datetime.now().timestamp()
        
        for category, assets in ASSET_REGISTRY.items():
            for asset in assets:
                should_run, reason = self._should_run(asset, category)
                
                if category == 'deprecated':
                    if os.path.exists(f'{WORKSPACE}/{asset}'):
                        self.report['deprecated_found'].append(asset)
                    continue
                
                if not should_run:
                    self.report['skipped'].append({
                        'asset': asset,
                        'category': category,
                        'reason': reason
                    })
                    continue
                
                # 执行资产
                result = self._run_asset(asset, category)
                self.history[asset] = now_ts
                
                if result['returncode'] != 0:
                    self.report['errors'].append({
                        'asset': asset,
                        'category': category,
                        'error': result.get('error', result.get('stderr', 'unknown'))
                    })
                    continue
                
                # 产出验证
                valid, reason = self._validate_output(
                    asset, category,
                    result.get('stdout', ''),
                    result.get('stderr', '')
                )
                
                if not valid:
                    self.report['validation_failed'].append({
                        'asset': asset,
                        'category': category,
                        'reason': reason,
                        'output': result.get('stdout', '')[:200]
                    })
                    continue
                
                self.report['activated'].append({
                    'asset': asset,
                    'category': category,
                    'output': result.get('stdout', '')
                })
        
        # 保存历史
        self.save_json(self.history_file, self.history)
        
        # 生成报告
        self._generate_report()
        return self.report
    
    def _generate_report(self):
        """生成Markdown报告（全中文，用户可读）"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        report_file = f'{LOG_DIR}/日常资产激活报告-{date_str}.md'
        dry_run_text = "是（仅预览，未实际执行）" if self.dry_run else "否"
        
        def cat_name(category):
            return CATEGORY_NAME_MAP.get(category, category)
        
        lines = [
            '# 日常资产激活报告',
            '',
            f'**时间**: {self.get_timestamp()}',
            f'**调度器**: daily_asset_runner.py v1.1',
            f'**仅预览模式**: {dry_run_text}',
            '',
            '## 执行摘要',
            '',
            f'- ✅ 成功激活（含有效产出）: {len(self.report["activated"])} 个',
            f'- ⚠️ 运行通过但产出验证失败: {len(self.report["validation_failed"])} 个',
            f'- ⏭️ 跳过: {len(self.report["skipped"])} 个',
            f'- ❌ 运行失败: {len(self.report["errors"])} 个',
            f'- 🗃️ 待归档旧版本: {len(self.report["deprecated_found"])} 个',
            '',
            '## 成功激活',
            ''
        ]
        
        for item in self.report['activated']:
            lines.append(f"- `{item['asset']}`（{cat_name(item['category'])}）")
            if item.get('output'):
                lines.append(f"  - 输出: {item['output'][:200].replace(chr(10), ' ')}")
        
        if self.report['validation_failed']:
            lines.extend(['', '## 产出验证失败', ''])
            for item in self.report['validation_failed']:
                lines.append(f"- `{item['asset']}`（{cat_name(item['category'])}）→ {item['reason']}")
                lines.append(f"  - 输出片段: {item['output'][:150].replace(chr(10), ' ')}")
        
        if self.report['errors']:
            lines.extend(['', '## 运行失败', ''])
            for item in self.report['errors']:
                lines.append(f"- `{item['asset']}`（{cat_name(item['category'])}）→ {item['error'][:100]}")
        
        if self.report['deprecated_found']:
            lines.extend(['', '## 待归档旧版本', ''])
            for asset in self.report['deprecated_found']:
                lines.append(f"- `{asset}`")
            lines.append('')
            lines.append('> **建议**: 将旧版本移动到 `archive/deprecated/` 目录，避免混淆。')
        
        lines.extend(['', '## 资产状态总览', ''])
        lines.append('| 资产 | 分类 | 最后运行 |')
        lines.append('|------|------|----------|')
        
        all_assets = []
        for cat, assets in ASSET_REGISTRY.items():
            if cat == 'deprecated':
                continue
            for asset in assets:
                last = self.history.get(asset, 0)
                last_str = datetime.fromtimestamp(last).strftime('%m-%d %H:%M') if last else '从未'
                all_assets.append((asset, cat_name(cat), last_str))
        
        for asset, cat, last_str in sorted(all_assets):
            lines.append(f'| `{asset}` | {cat} | {last_str} |')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        self.report['report_file'] = report_file
        print(f"✅ 日常资产激活报告已生成: {report_file}")
        print(f"📍 报告位置: A-manyige/汇报/日报/日常资产激活报告-{date_str}.md")

if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    runner = DailyAssetRunner(dry_run=dry_run)
    runner.run()
# SKILL_LIFECYCLE_AUTO_INSERT_START
# 由 skill_lifecycle_manager.py 自动生成
SKILL_MATURITY_ASSETS = [
    "1001night-stories",
    "5standard-integration",
    "adi-decision-engine",
    "agent-deep-research",
    "agent-memory",
    "api-monitor",
    "auto-drive",
    "baidu-baike-data",
    "baseline-checker",
    "bazi-analysis",
    "buffett-analysis",
    "bun-runtime",
    "business-model-analyzer",
    "case-repository",
    "category6-full-task-processor",
    "cctv-news-fetcher",
    "ceo-advisor",
    "citation-consistency-auto-fix",
    "clawddocs",
    "cognitive-memory",
    "consensus-support-reply-guard",
    "consulting",
    "consulting-report-search",
    "conversation-researcher",
    "cos-vectors-skill",
    "cost-redlines",
    "counter-case-finder",
    "create-psychological-counselor",
    "creator-intel-v5",
    "cron",
    "cron-automation",
    "data-analyst",
    "data-quality-auditor",
    "decision-distiller",
    "decision-framework",
    "decision-maker",
    "deep-research-cli",
    "deepresearch-conversation",
    "deepthinklite",
    "defipoly",
    "destiny-fusion-pro",
    "dknowc-qa",
    "dormancy-protocol",
    "douyin-video-fetch",
    "edge-tts",
    "error-handler",
    "evolver",
    "executive-mentor",
    "feishu-docs",
    "feishu-docs-v2",
    "feishu-file-sender",
    "file-integrity",
    "finance-digitalization-product-manager",
    "first",
    "five-level-verification",
    "founder-coach-ai",
    "frontend-design-ultimate",
    "fundraising-advisor",
    "gemini-deep-research",
    "global-resource-arbitrage",
    "gosim7",
    "health-guide",
    "heartbeat-protocol",
    "honesty-tagging-protocol",
    "info-collection-quality",
    "info-quality-guardian",
    "intelligence-suite",
    "investment-committee",
    "kimi-usage-monitor",
    "knowledge-graph",
    "knowledge-graph-framework",
    "larry",
    "learning-system-skill",
    "legal-advisor",
    "legal-matter-intake-summarizer",
    "lexiang-mcp-skill",
    "lexiang-skill",
    "liang-tavily-search",
    "literature-search-workflow",
    "lm-studio-subagents",
    "local-data-ai",
    "local-file-rag-basic",
    "local-stt",
    "lygo-champion-omnisiren-silent-storm",
    "lygo-champion-volaris-prism-judgment",
    "maoxuan-maomethodology-skill",
    "markdown-convert",
    "market-research-reports",
    "mass-task-executor",
    "multi-viewpoint-debates",
    "mx-stocks-screener",
    "namespace-enforcement",
    "obsidian-ontology-sync",
    "ocr-local",
    "ollie-file-processor",
    "openclaw-anything",
    "openclaw-ultimate-suite",
    "partner-matching-engine",
    "pdf-ocr-layout",
    "perplexity-research",
    "personal-insight-engine",
    "playwright-scraper-skill",
    "product-manager-toolkit",
    "prompt-compress",
    "pymupdf-pdf-parser-clawdbot-skill",
    "quality-assessment",
    "quality-assurance",
    "quality-closure",
    "quality-gate-system",
    "qwen-image",
    "qwen-tts",
    "raglite",
    "reason",
    "repo-research",
    "research-orchestrator",
    "role-federation",
    "scry",
    "searxng",
    "second-brain",
    "self-improving-agent",
    "self-improving-agent-1-0-2",
    "skill-creator",
    "skill-finder-cn",
    "skill-usage-tracker",
    "startup-0-to-1-workflow",
    "stealth-browser",
    "super-knowledge-ingest",
    "survey-designer",
    "swarm",
    "system-commander",
    "task-manager",
    "tavily-tool",
    "taxation-expert",
    "team-collab-repo",
    "tencent-ads-assistant",
    "tencent-cos-skill",
    "tencent-news",
    "tencentcloud-cos",
    "testing-framework",
    "theory-miner",
    "thought-to-excalidraw",
    "tiangong-notebooklm-cli",
    "tiangong-wps-ppt-automation",
    "token-budget-enforcer",
    "token-management-satisficing",
    "token-optimizer",
    "token-throttle-controller",
    "token-weekly-monitor",
    "totem-avatar",
    "tushare-finance",
    "ui-ux-pro-max",
    "universal-checklist-enforcer",
    "valyu-search",
    "vendor-api-monitor",
    "video-image-file-analysis",
    "web-search",
    "web-search-pro",
    "wechat",
    "wechat-article-extractor-skill",
    "wechat-article-search",
    "wechat-article-spider",
    "wechat-miniprogram-automator",
    "wechat-mp-publisher",
    "wechat-publisher",
    "wechat-toolkit",
    "worry-list-manager",
    "wps-office",
    "xiaohongshu-tool",
    "youtube-full",
    "youtube-watcher",
    "zero-idle-enforcer",
    "zero-vacancy-executor",
    "ziwei-bazi-consulting",
    "ziwei-doushu",
]
# SKILL_LIFECYCLE_AUTO_INSERT_END