#!/usr/bin/env python3
"""深研·静流 - 六阶段研究流水线"""
import sys, json, re
from pathlib import Path
from datetime import datetime

RESEARCH_TEMPLATE = """
# 研究任务书
**主题**: {topic}
**模式**: {mode}
**时间**: {timestamp}
**边界**: [用户补充]
**目标读者**: [用户补充]
**预期产出**: [报告/摘要/清单]

---

## 六阶段流水线

### 阶段1: 理解 (10min)
- [ ] 明确核心问题
- [ ] 确定研究边界
- [ ] 识别目标读者
- [ ] 设定预期产出

### 阶段2: 搜索 (15min)
- [ ] 学术来源
- [ ] 政策/法规来源
- [ ] 行业/新闻来源
- [ ] 专家/访谈来源

### 阶段3: 验证 (10min)
- [ ] 交叉验证关键事实
- [ ] 标注信源可靠性
- [ ] 识别信息缺口

### 阶段4: 架构 (10min)
- [ ] 确定叙述逻辑
- [ ] 设计内容结构
- [ ] 分配篇幅权重

### 阶段5: 写作 (30min)
- [ ] 按架构填充内容
- [ ] 保持客观中立
- [ ] 引用标注

### 阶段6: 交付 (5min)
- [ ] 格式化输出
- [ ] 生成摘要
- [ ] 交付最终包

---

*模板版本: V1.0*
"""

def generate_research_task(topic, mode="standard"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return RESEARCH_TEMPLATE.format(topic=topic, mode=mode, timestamp=timestamp)

def estimate_time(mode):
    times = {
        'quick': 30,
        'standard': 80,
        'deep': 180
    }
    return times.get(mode, 80)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 deep-research.py --topic '主题' [--mode quick|standard|deep]")
        return
    
    # 简单解析参数
    topic = ""
    mode = "standard"
    for i, arg in enumerate(sys.argv):
        if arg == '--topic' and i+1 < len(sys.argv):
            topic = sys.argv[i+1]
        if arg == '--mode' and i+1 < len(sys.argv):
            mode = sys.argv[i+1]
    
    if not topic:
        print("错误: 必须指定 --topic")
        return
    
    task = generate_research_task(topic, mode)
    minutes = estimate_time(mode)
    
    # 输出JSON
    output = {
        'skill': 'deep-research',
        'version': '1.0',
        'topic': topic,
        'mode': mode,
        'estimated_minutes': minutes,
        'task_book': task,
        'stages': [
            {'name': '理解', 'duration': 10, 'order': 1},
            {'name': '搜索', 'duration': 15, 'order': 2},
            {'name': '验证', 'duration': 10, 'order': 3},
            {'name': '架构', 'duration': 10, 'order': 4},
            {'name': '写作', 'duration': 30, 'order': 5},
            {'name': '交付', 'duration': 5, 'order': 6}
        ] if mode == 'standard' else [
            {'name': '理解', 'duration': 5, 'order': 1},
            {'name': '搜索', 'duration': 15, 'order': 2},
            {'name': '交付', 'duration': 10, 'order': 3}
        ] if mode == 'quick' else [
            {'name': '理解', 'duration': 20, 'order': 1},
            {'name': '搜索', 'duration': 40, 'order': 2},
            {'name': '验证', 'duration': 30, 'order': 3},
            {'name': '架构', 'duration': 20, 'order': 4},
            {'name': '写作', 'duration': 50, 'order': 5},
            {'name': '交付', 'duration': 20, 'order': 6}
        ]
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
