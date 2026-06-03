#!/usr/bin/env python3
"""
会话归档脚本 - 解决"聊完就忘"

用法:
    python3 archive_session.py --topic "话题名" --key-decisions "决策1;决策2"
    python3 archive_session.py --topic "话题名" --file /path/to/content.md
    python3 archive_session.py --auto-extract  # 从上下文自动提取(需要配合OpenClaw)
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# 基础目录
BASE_DIR = Path(__file__).parent.parent.resolve()
MEMORY_DIR = BASE_DIR / "memory"


def ensure_dirs():
    """确保目录存在"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()[:50]  # 限制长度


def create_archive(topic: str, key_decisions: str = "", content: str = "", 
                   source_file: str = None) -> str:
    """
    创建归档文件
    
    Args:
        topic: 话题名称
        key_decisions: 关键决策点，用分号分隔
        content: 额外内容
        source_file: 源文件路径 (如果提供则读取其内容)
    
    Returns:
        归档文件路径
    """
    ensure_dirs()
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_topic = sanitize_filename(topic)
    filename = f"{date_str}_{safe_topic}.md"
    filepath = MEMORY_DIR / filename
    
    # 如果文件已存在，添加序号
    counter = 1
    original_filepath = filepath
    while filepath.exists():
        filename = f"{date_str}_{safe_topic}_{counter:02d}.md"
        filepath = MEMORY_DIR / filename
        counter += 1
    
    # 构建归档内容
    lines = [
        f"# {topic}",
        "",
        f"> 归档时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 归档类型: 会话归档",
        "",
        "## 关键决策点",
        "",
    ]
    
    if key_decisions:
        decisions = [d.strip() for d in key_decisions.split(';') if d.strip()]
        for i, decision in enumerate(decisions, 1):
            lines.append(f"{i}. {decision}")
    else:
        lines.append("(未记录关键决策)")
    
    lines.extend([
        "",
        "## 详细内容",
        "",
    ])
    
    if source_file and os.path.exists(source_file):
        with open(source_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        lines.append(file_content)
    elif content:
        lines.append(content)
    else:
        lines.append("(详细内容待补充)")
    
    lines.extend([
        "",
        "---",
        f"*归档ID: {filename.replace('.md', '')}*",
    ])
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(description='会话归档工具')
    parser.add_argument('--topic', '-t', required=True, help='话题名称')
    parser.add_argument('--key-decisions', '-k', default='', help='关键决策点，用分号分隔')
    parser.add_argument('--content', '-c', default='', help='额外内容')
    parser.add_argument('--file', '-f', help='源文件路径')
    parser.add_argument('--silent', '-s', action='store_true', help='静默模式')
    
    args = parser.parse_args()
    
    try:
        filepath = create_archive(
            topic=args.topic,
            key_decisions=args.key_decisions,
            content=args.content,
            source_file=args.file
        )
        if not args.silent:
            print(f"✅ 归档成功: {filepath}")
            print(f"   话题: {args.topic}")
            if args.key_decisions:
                decisions = [d.strip() for d in args.key_decisions.split(';') if d.strip()]
                print(f"   关键决策: {len(decisions)} 项")
    except Exception as e:
        print(f"❌ 归档失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
