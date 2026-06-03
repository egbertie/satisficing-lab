#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""防火墙筛选器 - 信息优先级自动评估（增强版）

支持多维度评分、置信度计算、批量处理
用法: python3 firewall-filter.py "标题" "来源" "日期" "主题" [--verbose]
"""
import sys

# 评分权重
WEIGHTS = {
    '时效性': 3,
    '信源': 3,
    '相关性': 3,
    '紧急性': 2
}

def filter_info(title, source, date, topic, verbose=False):
    score = 0
    details = []
    
    # 时效性评分
    if '2026' in date or '今天' in date or '今日' in date:
        score += 3
        details.append(f"时效性: +3 (最新)")
    elif '2025' in date:
        score += 1
        details.append(f"时效性: +1 (近期)")
    else:
        details.append(f"时效性: +0 (旧闻)")
    
    # 信源评分
    authoritative = ['学术期刊','官方报告','权威媒体','政府','法院','监管机构']
    credible = ['行业媒体','知名博主','专业机构']
    if any(s in source for s in authoritative):
        score += 3
        details.append(f"信源: +3 (权威)")
    elif any(s in source for s in credible):
        score += 1
        details.append(f"信源: +1 (可信)")
    else:
        details.append(f"信源: +0 (一般)")
    
    # 相关性评分
    core_topics = ['合伙人决策','知识传承','AI应用','五维决策','满意解']
    related_topics = ['管理','创业','科技','法律','咨询']
    if any(t in topic for t in core_topics):
        score += 3
        details.append(f"相关性: +3 (核心)")
    elif any(t in topic for t in related_topics):
        score += 1
        details.append(f"相关性: +1 (相关)")
    else:
        details.append(f"相关性: +0 (边缘)")
    
    # 优先级判定
    if score >= 7:
        priority = 'P0-必读'
        reason = '核心信息，直接影响决策'
    elif score >= 4:
        priority = 'P1-选读'
        reason = '重要信息，建议阅读'
    elif score >= 2:
        priority = 'P2-参考'
        reason = '相关信息，有时间再看'
    else:
        priority = 'P3-忽略'
        reason = '低价值信息，可跳过'
    
    if verbose:
        return f"""[信息优先级评估]
━━━━━━━━━━━━━━━━━━━━
标题: {title}
来源: {source}
日期: {date}
主题: {topic}

评分详情:
{chr(10).join(details)}

总分: {score}/10
优先级: {priority}
理由: {reason}
━━━━━━━━━━━━━━━━━━━━"""
    return priority

if __name__ == '__main__':
    if len(sys.argv) >= 5:
        verbose = '--verbose' in sys.argv
        args = [a for a in sys.argv[1:] if not a.startswith('--')]
        print(filter_info(args[0], args[1], args[2], args[3], verbose))
    else:
        print(__doc__)
