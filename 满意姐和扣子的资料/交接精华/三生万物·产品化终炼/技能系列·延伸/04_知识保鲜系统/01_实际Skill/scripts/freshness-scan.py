#!/usr/bin/env python3
"""知识保鲜扫描器 - 检测过期知识"""
import sys, os, re
from pathlib import Path
from datetime import datetime, timedelta
import json

SHELF_LIFE = {
    '技术': 180,    # 6个月
    '市场': 90,     # 3个月
    '法规': 30,     # 1个月
    '方法论': 365,  # 12个月
    '案例': 180,    # 6个月
    '默认': 90
}

def scan_freshness(knowledge_dir, older_than_days=90):
    now = datetime.now()
    expired = []
    
    for md_file in Path(knowledge_dir).rglob('*.md'):
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
        age_days = (now - mtime).days
        
        if age_days > older_than_days:
            # 尝试识别类型
            text = md_file.read_text(encoding='utf-8', errors='ignore')
            ktype = '默认'
            for t in SHELF_LIFE:
                if t in text[:500]:
                    ktype = t
                    break
            
            expired.append({
                'file': str(md_file),
                'age_days': age_days,
                'type': ktype,
                'shelf_life': SHELF_LIFE.get(ktype, 90),
                'expired': age_days > SHELF_LIFE.get(ktype, 90)
            })
    
    report = {
        'scan_time': now.isoformat(),
        'total_scanned': len(list(Path(knowledge_dir).rglob('*.md'))),
        'expired_count': len(expired),
        'expired_items': expired[:20]  # 前20个
    }
    
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '/root/.openclaw/workspace'
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    scan_freshness(path, days)
