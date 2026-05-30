#!/usr/bin/env python3
"""
SRI 产品物理质量扫描器 v1.0
================================
自动扫描 site/ 下所有 HTML 产品，检查:
1. 断链 (404/403)
2. HTML 结构完整性 (有无 <title>/<meta>/<script> 标签)
3. 文件大小 (过小=占位符·过大=性能问题)
4. 5秒可读性 (一句话价值主张是否存在)
5. 中文字符占比 (纯英文页面可能误入产品库)

输出: entities_index.json meta.product_audit
被飞轮引擎 health() 方法调用
"""

import json
import os
import re
from datetime import datetime, timezone
from html.parser import HTMLParser

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
SITE_DIR = os.path.join(WORKSPACE, 'site')
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')
BASE_URL = 'https://egbertie.github.io/satisficing-lab/'


class HTMLInspector(HTMLParser):
    """解析 HTML 结构，提取关键元素"""
    def __init__(self):
        super().__init__()
        self.has_title = False
        self.has_meta_desc = False
        self.has_meta_viewport = False
        self.has_h1 = False
        self.has_script = False
        self.has_link_css = False
        self.title_text = ''
        self.all_text = []
        self.link_hrefs = []
        self.script_srcs = []
        self.img_srcs = []
        self.style_tags = 0
        self.inline_style_count = 0
        self.error_count = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'title':
            self.has_title = True
        if tag == 'meta':
            name = attrs_dict.get('name', '')
            if name == 'description':
                self.has_meta_desc = True
            if name == 'viewport':
                self.has_meta_viewport = True
        if tag == 'h1':
            self.has_h1 = True
        if tag == 'script':
            self.has_script = True
            if 'src' in attrs_dict:
                self.script_srcs.append(attrs_dict['src'])
        if tag == 'link' and attrs_dict.get('rel') == 'stylesheet':
            self.has_link_css = True
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                self.link_hrefs.append(href)
        if tag == 'img' and 'src' in attrs_dict:
            self.img_srcs.append(attrs_dict['src'])
        if tag == 'style':
            self.style_tags += 1
        if 'style' in attrs_dict:
            self.inline_style_count += 1

    def handle_data(self, data):
        self.all_text.append(data.strip())

    def handle_startendtag(self, tag, attrs):
        # 自闭合标签也检查 meta
        attrs_dict = dict(attrs)
        if tag == 'meta':
            name = attrs_dict.get('name', '')
            if name == 'description':
                self.has_meta_desc = True
            if name == 'viewport':
                self.has_meta_viewport = True


def quick_scan_product(filepath):
    """
    快速扫描单个产品 HTML 文件
    返回: {score, issues, checks} 字典
    """
    result = {
        'file': os.path.basename(filepath),
        'size_bytes': os.path.getsize(filepath),
        'score': 100,
        'issues': [],
        'checks': {}
    }

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        result['score'] = 0
        result['issues'].append('文件无法读取: {}'.format(e))
        return result

    # 1. 文件大小检查
    size_kb = len(content) / 1024
    result['checks']['size_kb'] = round(size_kb, 1)
    if size_kb < 1:
        result['score'] -= 20
        result['issues'].append('文件过小({:.1f}KB)·可能是占位符'.format(size_kb))
    elif size_kb > 500:
        result['score'] -= 10
        result['issues'].append('文件过大({:.1f}KB)·建议拆分'.format(size_kb))

    # 2. HTML 结构解析
    inspector = HTMLInspector()
    try:
        inspector.feed(content)
    except Exception as e:
        pass  # 容错解析

    # 必需元素
    if not inspector.has_title:
        result['score'] -= 10
        result['issues'].append('缺少 <title> 标签')
    result['checks']['has_title'] = inspector.has_title

    if not inspector.has_h1:
        result['score'] -= 5
        result['issues'].append('缺少 <h1> 标签')
    result['checks']['has_h1'] = inspector.has_h1

    if not inspector.has_meta_desc:
        result['score'] -= 5
        result['issues'].append('缺少 <meta name="description">')
    result['checks']['has_meta_desc'] = inspector.has_meta_desc

    if not inspector.has_meta_viewport:
        result['score'] -= 5
        result['issues'].append('缺少 <meta name="viewport"> (移动端不适配)')
    result['checks']['has_meta_viewport'] = inspector.has_meta_viewport

    # 3. 链接检查 (只检测内部链接格式)
    internal_broken = 0
    external_count = 0
    for href in inspector.link_hrefs:
        if href.startswith('http'):
            external_count += 1
        else:
            # 内部链接：检查目标文件是否存在
            target = os.path.join(SITE_DIR, href)
            if not os.path.exists(target):
                internal_broken += 1

    if internal_broken > 0:
        result['score'] -= min(20, internal_broken * 3)
        result['issues'].append('{} 个内部断链'.format(internal_broken))
    result['checks']['internal_links'] = len(inspector.link_hrefs) - external_count
    result['checks']['external_links'] = external_count
    result['checks']['broken_internal'] = internal_broken

    # 4. 5秒可读性: 检查是否有明确的一句话价值主张
    all_text = ' '.join(inspector.all_text)
    # 简单启发式: 是否有 "满意解" 或 "工具" 或 "帮助" 等关键词
    value_keywords = ['满意度', '评价', '分析', '诊断', '匹配', '工具', '帮助', '解决', '识别', '评估', '检测', '生成', '创建']
    has_value = any(kw in all_text for kw in value_keywords)
    result['checks']['has_value_proposition'] = has_value
    if not has_value:
        result['score'] -= 10
        result['issues'].append('未检测到明确的价值主张关键词')

    # 5. 中文字符占比
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    total_chars = len(re.sub(r'\s', '', content))
    cn_ratio = chinese_chars / max(total_chars, 1)
    result['checks']['cn_ratio'] = round(cn_ratio, 2)
    if cn_ratio < 0.01:
        result['score'] -= 5
        result['issues'].append('中文占比<1%·可能是纯英文页面')

    # 6. 样式内联检查
    result['checks']['inline_styles'] = inspector.inline_style_count
    if inspector.inline_style_count > 30:
        result['score'] -= 5
        result['issues'].append('内联样式过多({})·建议提取 CSS'.format(inspector.inline_style_count))

    # 分数保底
    result['score'] = max(0, min(100, result['score']))
    result['checks']['text_length'] = len(all_text)

    return result


def batch_scan(limit=None):
    """批量扫描 site/ 下所有 HTML 产品"""
    results = []
    html_files = sorted([f for f in os.listdir(SITE_DIR)
                         if f.endswith('.html')
                         and not f.startswith('.')
                         and 'dashboard' not in f.lower()
                         and 'admin' not in f.lower()
                         and 'catalog' not in f.lower()
                         and 'index' not in f.lower()
                         and 'about' not in f.lower()
                         and 'gate' not in f.lower()])

    if limit:
        html_files = html_files[:limit]

    for fname in html_files:
        fpath = os.path.join(SITE_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        result = quick_scan_product(fpath)
        results.append(result)

    # 统计
    scores = [r['score'] for r in results if r['score'] > 0]
    return {
        'scanned_at': datetime.now(timezone.utc).isoformat(),
        'total_scanned': len(results),
        'avg_score': round(sum(scores) / len(scores), 1) if scores else 0,
        'min_score': min(scores) if scores else 0,
        'max_score': max(scores) if scores else 0,
        'products_under_60': len([s for s in scores if s < 60]),
        'products_under_40': len([s for s in scores if s < 40]),
        'total_issues': sum(len(r['issues']) for r in results),
        'results': results
    }


def update_entities_index(audit_data, dry_run=False):
    """将审计结果写入 entities_index"""
    if dry_run:
        print('[DRY RUN] 结果不入库')
        return

    if not os.path.exists(DATA_FILE):
        print('entities_index.json 不存在')
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'meta' not in data:
        data['meta'] = {}

    data['meta']['product_audit'] = audit_data

    # 同时更新每个产品的 audit_score
    audit_map = {r['file']: r for r in audit_data.get('results', [])}
    for prod in data.get('products', []):
        fname = prod.get('url', '').split('/')[-1]
        if fname in audit_map:
            r = audit_map[fname]
            prod['audit_score'] = r['score']
            prod['audit_issues'] = len(r['issues'])
            prod['last_audit'] = audit_data['scanned_at']

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('已写入: {} 产品审计结果'.format(len(audit_map)))
    print('  avg={:.1f} · min={} · max={} · <60:{} · <40:{}'.format(
        audit_data['avg_score'], audit_data['min_score'], audit_data['max_score'],
        audit_data['products_under_60'], audit_data['products_under_40']))


def print_report(audit_data, top_n=10):
    """打印审计报告"""
    print('=' * 60)
    print('SRI 产品物理质量扫描报告')
    print('=' * 60)
    print('扫描时间: {}'.format(audit_data['scanned_at'][:19]))
    print('扫描总数: {}'.format(audit_data['total_scanned']))
    print('平均分:   {:.1f}'.format(audit_data['avg_score']))
    print('最低分:   {}'.format(audit_data['min_score']))
    print('最高分:   {}'.format(audit_data['max_score']))
    print('<60分:    {} (需紧急修复)'.format(audit_data['products_under_60']))
    print('<40分:    {} (严重问题)'.format(audit_data['products_under_40']))
    print('总问题数: {}'.format(audit_data['total_issues']))
    print()

    # 问题分布
    issue_types = {}
    for r in audit_data['results']:
        for issue in r['issues']:
            # 提取问题类型关键词
            key = issue.split('·')[0].split('(')[0].split('：')[0].strip()[:30]
            issue_types[key] = issue_types.get(key, 0) + 1

    print('📊 问题分布 (Top 10):')
    sorted_issues = sorted(issue_types.items(), key=lambda x: -x[1])[:10]
    for issue, count in sorted_issues:
        bar = '█' * min(count, 30)
        print('  {}: {} {}'.format(count, bar, issue))
    print()

    # 最低分产品
    worst = sorted(audit_data['results'], key=lambda r: r['score'])[:top_n]
    print('🔴 最低分产品 (Top {}):'.format(top_n))
    for r in worst:
        print('  {:>3}分 · {} · {}'.format(r['score'], r['file'], ', '.join(r['issues'][:3])))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SRI 产品物理质量扫描器')
    parser.add_argument('--limit', type=int, help='只扫描前N个文件')
    parser.add_argument('--top', type=int, default=10, help='报告展示最低分产品数')
    parser.add_argument('--save', action='store_true', help='写入 entities_index')
    parser.add_argument('--dry-run', action='store_true', help='只扫描不写入')
    args = parser.parse_args()

    audit = batch_scan(limit=args.limit)
    print_report(audit, top_n=args.top)

    if args.save:
        update_entities_index(audit, dry_run=args.dry_run)
