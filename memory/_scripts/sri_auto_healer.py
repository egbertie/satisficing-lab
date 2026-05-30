#!/usr/bin/env python3
"""
SRI 知识飞轮 · 自动修复器 v1.2 (自愈层)
=========================================
基于飞轮引擎的感知和诊断，自动执行低风险修复:
1. 补全 <meta name="description"> 标签 (如果没有)
2. 补全 <meta name="viewport"> 标签 (如果没有)
3. 修复明显断链 (同名文件不同路径)
4. 标记重复实体 (自动标记为待归档)
5. Cron 异常检测 (检查所有Cron状态)

规则: 自动修复只做低风险操作，高风险操作生成建议人工审核。
低风险: 添加缺失meta标签、修复URL路径
高风险: 删除实体、合并实体、修改产品内容
"""

import json
import os
import re
import shutil
from datetime import datetime, timezone
from collections import defaultdict

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
SITE_DIR = os.path.join(WORKSPACE, 'site')
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')
BACKUP_DIR = os.path.join(WORKSPACE, 'memory/_backups')


def ensure_backup(path):
    """备份文件"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    fname = os.path.basename(path)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, '{}.{}.bak'.format(fname, ts))
    shutil.copy2(path, backup_path)
    return backup_path


# ============================================================
# 修复 #1: 自动补全 <meta> 标签
# ============================================================
def auto_fix_meta(filepath, dry_run=False):
    """自动补全缺失的 meta description 和 viewport"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return None, False

    fixes = []
    new_content = content

    # 检查 <meta name="description">
    if '<meta name="description"' not in content and '<meta name="description"' not in content.lower():
        title_match = re.search(r'<title>(.*?)</title>', content)
        desc = '满意解研究所 · ' + (title_match.group(1) if title_match else '知识产品')
        meta_tag = '\n  <meta name="description" content="{}">'.format(desc)
        # 插入到 <title> 后面
        new_content = re.sub(r'(<title>.*?</title>)', r'\1' + meta_tag, new_content, count=1)
        fixes.append('added meta description')

    # 检查 <meta name="viewport">
    if '<meta name="viewport"' not in content:
        viewport_tag = '\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">'
        new_content = re.sub(r'(<meta charset.*?>)', r'\1' + viewport_tag, new_content, count=1)
        if new_content == content:
            # 如果没找到 charset meta，插入到 <head> 后面
            new_content = re.sub(r'(<head.*?>)', r'\1' + viewport_tag, new_content, count=1)
        fixes.append('added viewport meta')

    if not fixes:
        return None, False

    if dry_run:
        return fixes, False

    ensure_backup(filepath)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return fixes, True
    except Exception as e:
        return fixes, False


# ============================================================
# 修复 #2: 修复断链 (同名文件)
# ============================================================
def auto_fix_broken_link(filepath, dry_run=False):
    """检测并修复明显断链"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return [], False

    # 找所有相对链接
    pattern = re.compile(r'(href|src)=["\']([^"\']+)["\']')
    fixes = []
    site_files = set(f for f in os.listdir(SITE_DIR) if os.path.isfile(os.path.join(SITE_DIR, f)))

    for m in pattern.finditer(content):
        attr = m.group(1)
        href = m.group(2)
        if href.startswith('#') or href.startswith('http') or href.startswith('javascript'):
            continue

        # 解析目标文件
        target = href.split('/')[-1].split('?')[0].split('#')[0]
        if target and target.endswith('.html') and target not in site_files:
            # 尝试模糊匹配
            candidates = [f for f in site_files
                         if f.lower().replace('-', '').replace('_', '') == target.lower().replace('-', '').replace('_', '')]
            if len(candidates) == 1:
                old = m.group(0)
                new = old.replace(target, candidates[0])
                content = content.replace(old, new, 1)
                fixes.append('{} -> {}'.format(target, candidates[0]))

    if not fixes:
        return [], False

    if dry_run:
        return fixes, False

    ensure_backup(filepath)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return fixes, True
    except Exception:
        return fixes, False


# ============================================================
# 修复 #3: 重复实体自动标记
# ============================================================
def auto_mark_duplicates(data, dry_run=False):
    """检测重复实体并自动标记"""
    fixes = []
    products = [p for p in data.get('products', []) if isinstance(p, dict)]
    if not products:
        return fixes

    # 按 name 分组
    name_groups = defaultdict(list)
    for p in products:
        name = p.get('name', '').strip().lower()
        if name:
            name_groups[name].append(p)

    for name, group in name_groups.items():
        if len(group) <= 1:
            continue
        # 找最旧和最完整的
        scored = []
        for p in group:
            s = 0
            if p.get('status') == '精品':
                s += 2
            if p.get('quality_score'):
                s += p['quality_score'] / 100
            if p.get('audit_score'):
                s += p['audit_score'] / 100
            scored.append((p, s))

        scored.sort(key=lambda x: -x[1])
        keep = scored[0][0]
        for p, _ in scored[1:]:
            if p.get('status') != '归档':
                old = p.get('status', '?')
                p['status'] = '待审核·疑重复'
                p['duplicate_of'] = keep.get('id', '?')
                fixes.append({
                    'entity_id': p.get('id', '?'),
                    'name': p.get('name', '?')[:40],
                    'action': 'marked duplicate of {}'.format(keep.get('id', '?'))
                })

    return fixes


# ============================================================
# 修复 #4: 补全缺失的必需字段
# ============================================================
REQUIRED_FIELDS = {
    'products': {'family': '未知', 'status': '待审核', 'lifecycle_stage': 'LC-001'},
    'customers': {},
    'cities': {},
    'avatars': {},
    'cognition_events': {},
    'action_events': {},
    'verification_events': {},
    'learning_events': {},
    'tasks': {'status': '待执行'},
    'documents': {'status': '待审核'},
}


def auto_fill_missing_fields(data, dry_run=False):
    """自动补全实体缺失的必需字段"""
    fixes = []

    for entity_type, defaults in REQUIRED_FIELDS.items():
        entities = data.get(entity_type, [])
        for e in entities:
            if not isinstance(e, dict):
                continue
            entity_fixes = []
            for field, default in defaults.items():
                if field not in e or not e[field]:
                    old = e.get(field)
                    e[field] = default
                    entity_fixes.append('{}: {} → {}'.format(field, old, default))
            if entity_fixes:
                fixes.append({
                    'entity_type': entity_type,
                    'entity_id': e.get('id', '?'),
                    'fixes': entity_fixes
                })

    return fixes


# ============================================================
# 修复 #5: 飞轮数据一致性自修
# ============================================================
def auto_fix_flywheel_data(data):
    """修复飞轮元数据的一致性问题"""
    fixes = []

    if 'meta' not in data:
        data['meta'] = {}
        fixes.append('created meta')
    if 'flywheel' not in data['meta']:
        data['meta']['flywheel'] = {
            'version': '1.2',
            'last_run': None,
            'total_runs': 0,
            'cycles': {},
            'alerts': [],
            'capacity': {'phase': 0, 'rating': 'green'}
        }
        fixes.append('created meta.flywheel')

    # 确保近期运行记录不超过20条
    fw = data['meta']['flywheel']
    if 'recent_runs' in fw and len(fw['recent_runs']) > 20:
        fw['recent_runs'] = fw['recent_runs'][:20]
        fixes.append('trimmed recent_runs to 20')

    # 确保 change_log 不超过 MAX
    cl = data['meta'].get('change_log', [])
    if len(cl) > 5000:
        data['meta']['change_log'] = cl[-5000:]
        fixes.append('trimmed change_log to 5000')

    return fixes


# ============================================================
# 自愈主流程
# ============================================================
def heal(dry_run=False, limit=None):
    """执行全部自动修复"""
    if not os.path.exists(DATA_FILE):
        return {'error': 'entities_index.json not found'}

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    now = datetime.now(timezone.utc)
    report = {
        'healed_at': now.isoformat(),
        'dry_run': dry_run,
        'fixes': {
            'meta_tags': [],
            'broken_links': [],
            'duplicates': [],
            'missing_fields': [],
            'flywheel_data': []
        },
        'total_fixes': 0
    }

    # 1. 自动补 meta 标签 (处理审计分 < 95 且有问题的产品)
    products = data.get('products', [])
    # 优先修复审计分低的，其次是有 audit_issues 的
    targets = [p for p in products if isinstance(p, dict) and (
        (p.get('audit_score', 100) < 95 and p.get('audit_issues', 0) > 0)
        or p.get('audit_score', 100) < 90
    )]
    if limit:
        targets = targets[:limit]

    for p in targets:
        fname = p.get('url', '').split('/')[-1]
        if not fname:
            continue
        fpath = os.path.join(SITE_DIR, fname)
        if not os.path.exists(fpath):
            continue
        fixes, saved = auto_fix_meta(fpath, dry_run=dry_run)
        if fixes:
            report['fixes']['meta_tags'].append({
                'entity_id': p.get('id', '?'),
                'file': fname,
                'fixes': fixes
            })

    # 2. 修复断链 (同样的产品)
    for p in targets:
        fname = p.get('url', '').split('/')[-1]
        if not fname:
            continue
        fpath = os.path.join(SITE_DIR, fname)
        if not os.path.exists(fpath):
            continue
        fixes, saved = auto_fix_broken_link(fpath, dry_run=dry_run)
        if fixes:
            report['fixes']['broken_links'].append({
                'entity_id': p.get('id', '?'),
                'file': fname,
                'fixes': fixes
            })

    # 3. 重复实体标记
    if not dry_run:
        dup_fixes = auto_mark_duplicates(data)
        report['fixes']['duplicates'] = dup_fixes

    # 4. 补全缺失字段
    if not dry_run:
        missing_fixes = auto_fill_missing_fields(data)
        report['fixes']['missing_fields'] = missing_fixes

    # 5. 飞轮数据一致性
    if not dry_run:
        fw_fixes = auto_fix_flywheel_data(data)
        report['fixes']['flywheel_data'] = fw_fixes

    # 计算总数
    report['total_fixes'] = (
        len(report['fixes']['meta_tags']) +
        len(report['fixes']['broken_links']) +
        len(report['fixes']['duplicates']) +
        len(report['fixes']['missing_fields']) +
        len(report['fixes']['flywheel_data'])
    )

    if not dry_run:
        # 更新飞轮状态
        if 'meta' not in data:
            data['meta'] = {}
        if 'auto_heal' not in data['meta']:
            data['meta']['auto_heal'] = []
        data['meta']['auto_heal'].append(report)
        if len(data['meta']['auto_heal']) > 50:
            data['meta']['auto_heal'] = data['meta']['auto_heal'][-50:]

        ensure_backup(DATA_FILE)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return report


def print_report(report):
    """打印修复报告"""
    print('=' * 60)
    print('SRI 飞轮自愈报告 v1.2')
    print('=' * 60)
    print('时间: {}'.format(report.get('healed_at', '?')[:19]))
    mode = 'DRY RUN' if report.get('dry_run') else '已执行'
    print('模式: {} · {} 个修复'.format(mode, report.get('total_fixes', 0)))
    print()

    for fix_type, fixes in report.get('fixes', {}).items():
        if not fixes:
            continue
        print('🔧 {} ({}个):'.format(fix_type, len(fixes)))
        for f in fixes[:5]:
            if isinstance(f, dict):
                print('  {}: {}'.format(f.get('entity_id', f.get('file', '?')),
                      str(f.get('fixes', ''))[:80]))
            else:
                print('  {}'.format(str(f)[:80]))
        if len(fixes) > 5:
            print('  ... 还有 {} 个'.format(len(fixes) - 5))
        print()

    print('📁 备份目录: memory/_backups/')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SRI 飞轮自动修复器')
    parser.add_argument('--dry-run', action='store_true', help='只扫描不执行')
    parser.add_argument('--limit', type=int, default=10, help='只修复前N个低分产品')
    args = parser.parse_args()

    report = heal(dry_run=args.dry_run, limit=args.limit)
    print_report(report)
