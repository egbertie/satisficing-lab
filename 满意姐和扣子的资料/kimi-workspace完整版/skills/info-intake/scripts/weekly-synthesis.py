#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""周度合成器 - 汇总本周知识提取"""
import sys

def synthesize(notes):
    # 简化版：统计关键词频率
    words = notes.split()
    from collections import Counter
    top = Counter(words).most_common(5)
    
    return f"""# 本周知识合成

## 高频主题
{chr(10).join([f'- {w}（{c}次）' for w, c in top])}

## 可行动的洞察
- [请填写：本周学到的可以立即应用的一点]

## 待验证假设
- [请填写：需要进一步验证的假设]

## 下周关注
- [请填写：下周需要重点关注的信息源/主题]
"""

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(synthesize(' '.join(sys.argv[1:])))
    else:
        print('用法: python3 weekly-synthesis.py "本周所有笔记内容"')
