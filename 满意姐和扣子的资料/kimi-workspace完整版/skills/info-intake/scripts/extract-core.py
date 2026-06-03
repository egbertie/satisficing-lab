#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核心提取器 - 强制结构化输出"""
import sys

def extract(article_text):
    # 简化版：提取前3个句子作为核心内容
    sentences = article_text.split('。')[:3]
    core = '\n'.join([f"{i+1}. {s}。" for i, s in enumerate(sentences)])
    
    return f"""## 核心内容（3句话）
{core}

### 我的理解（1句话）
[请填写：这篇文章对我意味着什么]

### 关联知识
- [已有知识] → [关系]

### 待确认
- [不确定的点]

--- 写入时间: [YYYY-MM-DD HH:MM] ---"""

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(extract(' '.join(sys.argv[1:])))
    else:
        print('用法: python3 extract-core.py "文章内容"')
