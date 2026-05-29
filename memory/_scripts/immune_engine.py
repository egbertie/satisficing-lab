#!/usr/bin/env python3
"""
满意红 · 基线快照 + 免疫记忆引擎 V1.0
L0 (自身耐受) — 建立核心文件的 MD5 基线
L4 (免疫记忆) — 记录和召回已知威胁的修复方案
"""

import os, json, hashlib
from datetime import datetime
from pathlib import Path

WORKSPACE = "/Users/egbertielau/.openclaw/workspace"
SITE_DIR = f"{WORKSPACE}/site"
DATA_DIR = f"{WORKSPACE}/memory/_data"

os.makedirs(DATA_DIR, exist_ok=True)

# === L0 自身耐受: 核心文件定义 ===
CRITICAL_FILES = [
    "index.html", "about.html", "assessment.html", "checklist.html",
    "cases.html", "gate.html", "decision-theatre.html", "product-catalog.html",
    "dashboard.html", "go.html", "chemical-report.html", "fulldiag.html",
    "match.html", "knights.html", "thermometer.html", "radar.html",
    "cards-play.html", "crisis-sim.html", "pre0.html", "workshop.html",
    "exit-guide.html", "flywheel.html", "stars.html", "roots.html",
    "creation.html", "wizard.html", "go-gallery.html", "guide.html",
    "certification.html", "quotes.html", "rps.html", "slicing-pie.html",
    "metapartner.html", "account.html", "privacy.html", "terms.html",
    "symbols.html", "report-demo.html", "deep-gottman.html"
]

DEV_FILES = [
    "dashboard-kozi-debug.html", "dashboard-min.html", "dashboard-v2.html",
    "dashboard-local.html", "dashboard-vfy.html", "dashboard-test.html",
    "dashboard-clean.html", "admin.html"
]

ARCHIVE_PATTERNS = ["blood-", "fw-", "sk-", "wx-", "dialogue-", "game-", 
                    "media-", "ops-", "track-", "prod-", "skill-", "case-",
                    "deep-", "test-", "kouyan-", "maps-", "quotes-",
                    "54days.html", "bigrich.html", "account.html", 
                    "access_classification.json", "assets_index.json"]

def build_baseline():
    """建立核心文件的 MD5 基线"""
    baseline = {
        'created_at': datetime.now().isoformat(),
        'description': '核心产品页面 MD5 基线。任何偏差意味着文件被修改。',
        'files': {}
    }
    
    for fname in os.listdir(SITE_DIR):
        if not fname.endswith('.html'):
            continue
        
        fpath = os.path.join(SITE_DIR, fname)
        
        # 分类
        if fname in CRITICAL_FILES:
            tier = 'critical'
        elif fname in DEV_FILES:
            tier = 'dev'
        elif any(fname.startswith(p) for p in ARCHIVE_PATTERNS):
            tier = 'archive'
        else:
            tier = 'other'
        
        try:
            with open(fpath, 'rb') as f:
                content = f.read()
            md5 = hashlib.md5(content).hexdigest()
            size = len(content)
            
            baseline['files'][fname] = {
                'md5': md5,
                'size': size,
                'tier': tier
            }
        except:
            pass
    
    with open(f'{DATA_DIR}/baseline_snapshot.json', 'w') as f:
        json.dump(baseline, f, ensure_ascii=False, indent=2)
    
    return baseline

def check_baseline():
    """对比当前状态与基线，发现变更"""
    if not os.path.exists(f'{DATA_DIR}/baseline_snapshot.json'):
        return {'status': 'no_baseline', 'changes': []}
    
    with open(f'{DATA_DIR}/baseline_snapshot.json') as f:
        baseline = json.load(f)
    
    changes = []
    for fname, info in baseline['files'].items():
        fpath = os.path.join(SITE_DIR, fname)
        if not os.path.exists(fpath):
            changes.append({
                'file': fname,
                'type': 'deleted',
                'tier': info['tier'],
                'severity': 'critical' if info['tier'] == 'critical' else 'low'
            })
            continue
        
        with open(fpath, 'rb') as f:
            new_md5 = hashlib.md5(f.read()).hexdigest()
        
        if new_md5 != info['md5']:
            changes.append({
                'file': fname,
                'type': 'modified',
                'tier': info['tier'],
                'old_md5': info['md5'],
                'new_md5': new_md5,
                'severity': 'high' if info['tier'] == 'critical' else 'low'
            })
    
    return {
        'status': 'ok',
        'checked_at': datetime.now().isoformat(),
        'total': len(baseline['files']),
        'changes': changes,
        'change_count': len(changes)
    }

def build_immune_memory():
    """建立免疫记忆库"""
    memory = {
        'updated_at': datetime.now().isoformat(),
        'incidents': [
            {
                'incident_id': 'INC-001',
                'date': '2026-05-28',
                'threat': 'event.target 全局变量在现代浏览器中不可靠',
                'symptoms': 'onclick 绑定的函数点击无任何反应，console 无报错',
                'root_cause': 'Chrome/Safari 现代版本在严格模式下不再支持 event 隐式全局变量',
                'fix': '将 onclick="func()" 改为 onclick="func(args, this)"，函数签名加 btn 参数',
                'auto_fix_pattern': {
                    'search': r'onclick="(\w+)\(([^)]*)\)"(?!.*this)',
                    'replace': r'onclick="\\1(\\2, this)"'
                },
                'detection_time': '2天',
                'repair_time': '30分钟（诊断页验证通过后）',
                'lesson': '用极简诊断页逐层隔离测试。当代码看起来正确但不工作时——怀疑 HTML 环境而非代码逻辑。',
                'preventive_measure': [
                    'pre-commit hook: grep event\\.target',
                    '免疫扫描 L2: 每小时检查',
                    '新页面模板强制用 product-catalog 模式'
                ],
                'severity': 'critical',
                'category': 'browser_compatibility'
            },
            {
                'incident_id': 'INC-002',
                'date': '2026-05-29',
                'threat': 'crypto.subtle.digest(SHA-256) 在 GitHub Pages 静默失败',
                'symptoms': '密码输入正确但验证失败，无报错，无异常',
                'root_cause': 'Web Crypto API 在 GitHub Pages 的某些 HTTPS + 文件协议组合中静默失败',
                'fix': '内部工具改用明文密码比对。外部密码用简化纯 JS SHA-256',
                'auto_fix_pattern': None,
                'detection_time': '8小时',
                'repair_time': '5分钟（移除 crypto.subtle，改用明文）',
                'lesson': '跨浏览器兼容性 > 加密复杂度。内部工具不需要与外部工具同等级别的密码安全。',
                'preventive_measure': [
                    '所有新增密码验证必须先测试 Chrome + Safari + 隐身模式',
                    '内部工具统一用 sessionStorage + 明文'
                ],
                'severity': 'critical',
                'category': 'browser_compatibility'
            },
            {
                'incident_id': 'INC-003',
                'date': '2026-05-29',
                'threat': 'Safari 内容拦截器阻断 sessionStorage/localStorage',
                'symptoms': '密码门可以输入但验证后页面不跳转。换了 Chrome 就正常。',
                'root_cause': 'Safari 的内容拦截器（Content Blockers）阻断了 Web Storage API',
                'fix': '启动时检测 sessionStorage 可用性，不可用时显示降级提示',
                'auto_fix_pattern': {
                    'detect': 'sessionStorage.setItem("_t","1") in try/catch',
                    'response': 'show HTML warning message'
                },
                'detection_time': '1小时',
                'repair_time': '10分钟（加探测+降级提示）',
                'lesson': '永远假设最保守的浏览器环境。核心功能（如存储）需要降级方案。',
                'preventive_measure': [
                    '所有依赖 Web Storage 的页面启动时探测可用性',
                    '降级提示文案模板化'
                ],
                'severity': 'medium',
                'category': 'browser_compatibility'
            },
            {
                'incident_id': 'INC-004',
                'date': '2026-05-29',
                'threat': '字体全局替换破坏驾驶舱布局',
                'symptoms': '改完字体后，驾驶舱的 KPI 卡片全部错位',
                'root_cause': '.replace("font-size:9px","font-size:12px") 全局替换——把布局 CSS 中的 9px 也改了',
                'fix': '用精确 CSS 选择器（如 .tbl td, .tg）替换，不碰布局 CSS',
                'auto_fix_pattern': None,
                'detection_time': '即时（视觉检查）',
                'repair_time': '5分钟（git revert）',
                'lesson': '全局文本替换在 CSS 中是危险的。必须用选择器级别的精确修改。改完立即浏览器验证。',
                'preventive_measure': [
                    'CSS 修改前先分析哪些选择器是布局相关的（position/display/flex/grid）',
                    'style 修改只在精确选择器范围内',
                    '修改后立即在浏览器验证（不是依赖 CI）'
                ],
                'severity': 'medium',
                'category': 'code_quality'
            }
        ],
        'threat_patterns': [
            {
                'id': 'TP-001',
                'pattern': 'event\\.target',
                'detection': 'grep -rn',
                'auto_fix': True,
                'auto_fix_script': 'event_target_fix.py',
                'severity': 'critical',
                'incident_ref': 'INC-001'
            },
            {
                'id': 'TP-002',
                'pattern': 'crypto\\.subtle|SHA-256',
                'detection': 'grep -rn',
                'auto_fix': False,
                'severity': 'critical',
                'incident_ref': 'INC-002'
            },
            {
                'id': 'TP-003',
                'pattern': 'sessionStorage.*setItem|localStorage.*setItem',
                'detection': '无可用性探测的存储调用',
                'auto_fix': False,
                'severity': 'medium',
                'incident_ref': 'INC-003'
            },
            {
                'id': 'TP-004',
                'pattern': '\\.replace\\(.*font-size.*\\)',
                'detection': '全局 font-size 替换',
                'auto_fix': False,
                'severity': 'low',
                'incident_ref': 'INC-004'
            }
        ]
    }
    
    with open(f'{DATA_DIR}/immune_memory.json', 'w') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
    
    return memory

def main():
    print("🧬 满意红 · 基线快照 + 免疫记忆引擎")
    print()
    
    # L0: 建立基线
    print("📸 L0 · 自身耐受: 建立 MD5 基线...")
    baseline = build_baseline()
    critical = sum(1 for v in baseline['files'].values() if v['tier'] == 'critical')
    dev = sum(1 for v in baseline['files'].values() if v['tier'] == 'dev')
    archive = sum(1 for v in baseline['files'].values() if v['tier'] == 'archive')
    print(f"   关键文件: {critical}")
    print(f"   开发文件: {dev}")
    print(f"   归档文件: {archive}")
    print(f"   ✅ baseline_snapshot.json")
    
    # 检查是否偏离
    print("\n🔍 基线偏离检查...")
    result = check_baseline()
    if result['changes']:
        print(f"   ⚠️ 发现 {len(result['changes'])} 个变更:")
        for c in result['changes']:
            print(f"      [{c['severity']}] {c['file']}: {c['type']}")
    else:
        print("   ✅ 无偏离")
    
    # L4: 免疫记忆
    print("\n🧠 L4 · 适应性免疫: 建立免疫记忆库...")
    memory = build_immune_memory()
    print(f"   已知事件: {len(memory['incidents'])}")
    print(f"   威胁模式: {len(memory['threat_patterns'])}")
    for inc in memory['incidents']:
        print(f"   INC-{inc['incident_id'].split('-')[1]}: {inc['threat'][:50]}...")
    print(f"   ✅ immune_memory.json")

if __name__ == '__main__':
    main()
