#!/usr/bin/env python3
"""
爱可可情报矿脉即时处理脚本
用途: 当用户转发/粘贴一篇爱可可文章时，自动结构化分析并存档
"""

import sys
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/root/.openclaw/workspace/A-manyige/汇报/专项报告/爱可可情报矿脉")

TEMPLATE = """# 爱可可情报矿脉 · {date}

## 文章元信息
- **来源**: 爱可可爱生活（微信公众号）
- **接收时间**: {received_at}
- **文章标题**: {title}
- **文章链接**: {url}

## 一句话摘要
{summary}

## 领域分类
{classification}

## 与满意解研究所有关的洞察
{insight}

## 可引用的金句/数据
{quotes}

## 建议行动
{action}

---
*由爱可可信息流处理脚本自动生成*
"""


def classify(title: str, content: str) -> str:
    """基于标题和内容的领域分类"""
    keywords = {
        "AI / LLM": ["大模型", "GPT", "LLM", "transformer", "prompt", "agent"],
        "认知科学 / 神经": ["认知", "神经", "大脑", "直觉", "决策", "心理学", "量子认知"],
        "创业 / 合伙人": ["创业", "合伙人", "创始人", "股权", "融资", "退出"],
        "硬科技 / 转化": ["硬科技", "技术转化", "TRL", "产学研", "科学家创业"],
        "工具 / 效率": ["工具", "效率", "workflow", "自动化", "开源"],
    }
    text = (title + " " + content).lower()
    matched = []
    for domain, kws in keywords.items():
        if any(kw in text for kw in kws):
            matched.append(domain)
    return "、".join(matched) if matched else "待进一步判断"


def main():
    if len(sys.argv) < 2:
        print("用法: python3 process_aibot.py '文章标题\n文章内容'")
        sys.exit(1)
    
    raw = sys.argv[1]
    lines = raw.strip().split("\n")
    title = lines[0] if lines else "未识别标题"
    content = "\n".join(lines[1:])
    
    # 提取 URL
    urls = re.findall(r'https?://[^\s\)]+', raw)
    url = urls[0] if urls else "未提供"
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M")
    
    report = TEMPLATE.format(
        date=date_str,
        received_at=time_str,
        title=title,
        url=url,
        summary="（待填入：用 1-2 句话总结文章核心发现）",
        classification=classify(title, content),
        insight="（待填入：这篇文章对满意解的方法论、客户痛点、或服务能力有什么启发？）",
        quotes="（待填入：可直接引用到白皮书/课堂/公众号文章中的句子或数据）",
        action="（待填入：是否值得转发给客户？是否值得进一步深挖？是否需要写进案例库？）"
    )
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"爱可可矿脉-{date_str}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"处理完成，报告已保存: {out_path}")


if __name__ == "__main__":
    main()
