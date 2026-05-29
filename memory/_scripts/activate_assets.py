#!/usr/bin/env python3
"""
满意解研究所 · 历史资产激活管道 V1.0
对标: RAG + Knowledge Graph + Content Audit Pipeline
目标: 自动扫描全部文件→提取元数据→打标签→连接驾驶舱
"""
import os, json, time, re, hashlib
from collections import defaultdict

WORKSPACE = "/Users/egbertielau/.openclaw/workspace"
ASSETS_FILE = f"{WORKSPACE}/satisficing-lab/assets_index.json"
SKIP_DIRS = {'.git','node_modules','__pycache__','.dreams','_data','_archive','Archives','历史版本','历史','归档','OLD-ARCHIVE'}

# 产品关键词分类体系
TAG_SYSTEM = {
    "产品设计": ["产品","工具","测评","诊断","卡牌","剧场","模拟","温度计","计算器","章程","指南","工作坊"],
    "方法论": ["五维","五路图腾","满意解","Simon","司马贺","时间轴","可行域","身心流","信义观","直觉阈"],
    "案例与数据": ["案例","84","大疆","云鲸","比锐","海柔","固高","68Entry","张雪","Zipcar"],
    "运营管理": ["驾驶舱","cron","自动化","脚本","SQLite","localStorage","飞轮","同步","日志"],
    "品牌与设计": ["VI","配色","#C23B22","赭石红","设计系统","WCAG","sri-design"],
    "增长与获客": ["获客","转化","NPS","K-factor","转介绍","Aha Moment","Growth Loop","公开课","路演"],
    "标准与质量": ["QM-","审核","Peer Review","APA","ICF","ISO","HBR","标准","规范"],
    "知识与培训": ["教程","课程","培训","翻书","Wasserman","Gottman","Duke","Feld","Lencioni","Moyer"],
    "AI与系统": ["满意姐","扣子","满意红","蓝军","Skeptor","代理","Session","子人格"],
    "法律与合同": ["商标","合同","协议","协议","条款","CC","著作权","MIT"],
}

def scan_and_tag(root):
    """扫描文件并自动打标签"""
    results = []
    total = 0
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        
        for fname in filenames:
            if fname.startswith('.'): continue
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, root)
            total += 1
            
            try:
                stat = os.stat(full)
                ext = os.path.splitext(fname)[1].lower()
                size = stat.st_size
                if size > 5000000: continue  # skip >5MB
                
                # 快速内容标签扫描（仅读前10KB）
                content_sample = ""
                if ext in ['.md','.py','.html','.js','.css','.txt','.json']:
                    try:
                        with open(full,'r',encoding='utf-8',errors='ignore') as fh:
                            content_sample = fh.read(10240)
                    except:
                        pass
                
                # 自动打标签
                tags = set()
                for category, keywords in TAG_SYSTEM.items():
                    for kw in keywords:
                        if kw in fname or kw in content_sample:
                            tags.add(category)
                            break
                
                # 价值分计算
                value_score = min(100,
                    len(tags) * 10 +  # 标签越多越有价值
                    (20 if ext == '.md' else 0) +  # MD文档额外加分
                    (10 if '标准' in rel or '规范' in rel else 0) +
                    (10 if rel.startswith('记忆') else 0)
                )
                
                results.append({
                    "name": fname,
                    "path": rel,
                    "size": size,
                    "type": ext.replace('.','') if ext else 'file',
                    "modified": time.strftime('%Y-%m-%d',time.localtime(stat.st_mtime)),
                    "tags": list(tags),
                    "value": value_score,
                    "active": value_score >= 30  # 自动激活门槛
                })
                
            except:
                pass
            
            if total % 2000 == 0:
                print(f"  扫描中... {total} 文件")
    
    return results, total

def build_index():
    print("历史资产激活管道 · 对标 RAG + Knowledge Graph")
    print("=" * 60)
    
    # 1. 扫描所有文件
    print("\n📥 阶段1: 扫描与标签...")
    assets, total = scan_and_tag(WORKSPACE)
    
    # 2. 统计
    active = [a for a in assets if a['active']]
    dormant = [a for a in assets if not a['active']]
    
    # 3. 按标签分类汇总
    tag_summary = defaultdict(lambda: {"count": 0, "active": 0})
    for a in assets:
        for t in a.get('tags', []):
            tag_summary[t]["count"] += 1
            if a['active']:
                tag_summary[t]["active"] += 1
    
    # 4. 输出
    print(f"\n📊 扫描结果:")
    print(f"  总文件: {total}")
    print(f"  有效资产: {len(assets)}")
    print(f"  自动激活: {len(active)} (score≥30)")
    print(f"  休眠资产: {len(dormant)} (score<30)")
    print(f"  激活率: {len(active)/max(len(assets),1)*100:.0f}%")
    
    print(f"\n🏷️ 标签分类:")
    for tag, info in sorted(tag_summary.items(), key=lambda x: x[1]["count"], reverse=True):
        pct = info["active"] / max(info["count"], 1) * 100
        print(f"  {tag}: {info['count']}文件 · 激活{pct:.0f}%")
    
    # 5. 保存
    with open(ASSETS_FILE,'w') as f:
        json.dump({
            "scanned": time.strftime('%Y-%m-%d %H:%M'),
            "total": total,
            "assets": len(assets),
            "active": len(active),
            "dormant": len(dormant),
            "tagSummary": {k: v for k, v in tag_summary.items()},
            "files": [a for a in sorted(assets, key=lambda x: x["value"], reverse=True)[:500]]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 资产索引已保存: {ASSETS_FILE}")
    return assets, tag_summary

if __name__ == "__main__":
    build_index()
