#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冲突裁决器 - 当蓝军和满意姐意见冲突时（增强版）

支持三种裁决策略：
  safety: 安全/质量优先（蓝军优先）
  efficiency: 效率/流程优先（满意姐优先）
  default: 提交用户裁决

用法: python3 conflict-resolver.py "蓝军意见" "满意姐意见" [safety/efficiency/default] [--verbose]
"""
import sys

def analyze_conflict(blue, satisfaction):
    """分析冲突性质"""
    blue_lower = blue.lower()
    sat_lower = satisfaction.lower()
    
    # 安全相关关键词
    safety_keywords = ['风险','安全','红线','危险','崩溃','损失','失败','错误']
    # 效率相关关键词
    efficiency_keywords = ['效率','速度','时间','成本','资源','进度','交付']
    
    blue_safety = sum(1 for k in safety_keywords if k in blue_lower)
    sat_safety = sum(1 for k in safety_keywords if k in sat_lower)
    blue_eff = sum(1 for k in efficiency_keywords if k in blue_lower)
    sat_eff = sum(1 for k in efficiency_keywords if k in sat_lower)
    
    return {
        'blue_safety_score': blue_safety,
        'sat_safety_score': sat_safety,
        'blue_eff_score': blue_eff,
        'sat_eff_score': sat_eff,
        'conflict_type': 'safety' if blue_safety > 0 else 'efficiency' if sat_eff > 0 else 'general'
    }

def resolve(blue, satisfaction, criteria='default', verbose=False):
    analysis = analyze_conflict(blue, satisfaction)
    
    if criteria == 'safety' or analysis['conflict_type'] == 'safety':
        result = f"""[裁决: 蓝军优先 — 安全/质量相关]
━━━━━━━━━━━━━━━━━━━━
采纳: {blue}
理由: 涉及安全/质量/风险，蓝军判断优先
记录: {satisfaction}（作为后续优化建议）
行动: 按蓝军意见执行，满意姐建议纳入下周期改进"""
    elif criteria == 'efficiency' or analysis['conflict_type'] == 'efficiency':
        result = f"""[裁决: 满意姐优先 — 效率/流程相关]
━━━━━━━━━━━━━━━━━━━━
采纳: {satisfaction}
理由: 涉及效率/进度/资源，满意姐判断优先
备注: {blue}（作为风险监控点）
行动: 按满意姐意见执行，蓝军关注的风险点持续监控"""
    else:
        result = f"""[冲突点分析]
━━━━━━━━━━━━━━━━━━━━
蓝军: {blue}
满意姐: {satisfaction}

[冲突性质]
安全相关度: 蓝军{analysis['blue_safety_score']} vs 满意姐{analysis['sat_safety_score']}
效率相关度: 蓝军{analysis['blue_eff_score']} vs 满意姐{analysis['sat_eff_score']}

[裁决: 提交Egbertie]
请裁定:
A) 采纳蓝军（安全/质量优先）
B) 采纳满意姐（效率/流程优先）
C) 折中方案（请描述具体方案）

[建议]
如30分钟内无法裁决，默认采纳蓝军意见（安全优先）"""
    
    if verbose:
        result += f"""
━━━━━━━━━━━━━━━━━━━━
[裁决参数]
策略: {criteria}
冲突类型: {analysis['conflict_type']}
时间戳: {__import__('datetime').datetime.now().isoformat()}
状态: {'已裁决' if criteria != 'default' else '待用户裁决'}"""
    
    return result

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        verbose = '--verbose' in sys.argv
        args = [a for a in sys.argv[1:] if not a.startswith('--')]
        blue_opinion = args[0]
        sat_opinion = args[1]
        criteria = args[2] if len(args) > 2 else 'default'
        print(resolve(blue_opinion, sat_opinion, criteria, verbose))
    else:
        print(__doc__)
