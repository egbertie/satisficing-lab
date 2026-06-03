#!/usr/bin/env python3
"""快速研究 - 30分钟压缩版"""
import sys, json
from datetime import datetime

def quick_research(topic):
    return {
        'skill': 'quick-research',
        'version': '1.0',
        'topic': topic,
        'mode': 'quick',
        'estimated_minutes': 30,
        'pipeline': [
            {'stage': '理解', 'duration': 5, 'action': '明确1个核心问题'},
            {'stage': '搜索', 'duration': 15, 'action': '收集3-5个关键来源'},
            {'stage': '交付', 'duration': 10, 'action': '输出1页核心结论'}
        ],
        'quality_threshold': {
            'min_sources': 3,
            'max_length': 1000,
            'must_have': ['核心结论', '关键来源', '适用边界']
        },
        'timestamp': datetime.now().isoformat()
    }

def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else "未指定主题"
    result = quick_research(topic)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
