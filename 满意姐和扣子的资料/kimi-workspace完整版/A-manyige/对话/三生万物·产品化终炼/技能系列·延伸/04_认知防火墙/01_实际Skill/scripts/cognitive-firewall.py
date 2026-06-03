#!/usr/bin/env python3
"""认知防火墙 - 新知识入库前的认知安检"""
import sys, re, json
from pathlib import Path
from datetime import datetime

BIAS_PATTERNS = {
    '确认偏误': [r'显然', r'毫无疑问', r'明显', r'当然'],
    '锚定效应': [r'最初', r'一开始', r'首先', r'起点'],
    '幸存者偏差': [r'成功案例', r'赢家', r'胜利者', r'脱颖而出'],
    '因果混淆': [r'导致', r'造成', r'引起', r'因此'],
    '基底率忽视': [r'大部分', r'绝大多数', r'通常', r'一般'],
    '光环效应': [r'顶级', r'一流', r'卓越', r'杰出'],
    '近因效应': [r'最近', r'最新', r'不久前', r'刚刚'],
    '可得性启发': [r'众所周知', r'大家都知道', r'常识'],
    '框架效应': [r'换句话说', r'换个说法', r'换言之'],
    '沉没成本': [r'已经投入', r'不能浪费', r'继续投入'],
    '群体思维': [r'大家都', r'主流', r'普遍', r'公认'],
    '过度自信': [r'一定', r'绝对', r'必然', r'肯定']
}

def scan_bias(text):
    findings = []
    for bias_name, patterns in BIAS_PATTERNS.items():
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        if count > 0:
            findings.append({
                'bias': bias_name,
                'count': count,
                'severity': 'high' if count >= 3 else 'medium' if count >= 1 else 'low'
            })
    return findings

def main():
    if len(sys.argv) < 2:
        print("用法: python3 cognitive-firewall.py <文件路径>")
        return
    
    file_path = Path(sys.argv[1])
    text = file_path.read_text(encoding='utf-8', errors='ignore')
    
    findings = scan_bias(text)
    
    # 生成报告
    report = {
        'scanned_at': datetime.now().isoformat(),
        'file': str(file_path),
        'total_findings': len(findings),
        'findings': findings,
        'verdict': 'PASS' if not findings else 'WARN' if all(f['severity'] != 'high' for f in findings) else 'FAIL'
    }
    
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
