#!/usr/bin/env python3
"""
Coze 群聊实时归档脚本 v1.0
- 接受来自 stdin 或参数的消息
- 追加写入当日 coze-exchange 归档
- 由 Agent 在每次 Coze 群聊交互后调用

用法:
  echo "消息内容" | python3 memory/_scripts/coze_archive.py --role=assistant
  python3 memory/_scripts/coze_archive.py --role=user --text="用户消息"
  python3 memory/_scripts/coze_archive.py --summarize  # 生成当日汇总
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TZ = timezone(timedelta(hours=8))

ARCHIVE_BASE = os.path.join(WORKSPACE, "对话")


def get_archive_dir(date_str=None):
    if date_str is None:
        date_str = datetime.now(TZ).strftime('%Y-%m-%d')
    archive_dir = os.path.join(ARCHIVE_BASE, date_str, "coze-exchange")
    os.makedirs(archive_dir, exist_ok=True)
    return archive_dir


def get_log_path(date_str=None):
    archive_dir = get_archive_dir(date_str)
    if date_str is None:
        date_str = datetime.now(TZ).strftime('%Y-%m-%d')
    return os.path.join(archive_dir, f"{date_str}_三人对话实录.md")


def append_message(role, text, date_str=None):
    """追加单条消息到当日对话实录"""
    log_path = get_log_path(date_str)
    now = datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')

    role_labels = {
        'assistant': '🤖 满意红',
        'user': '👤 你(契)',
        'coze': '🦊 满意扣子',
        'system': '⚙️ 系统',
    }

    label = role_labels.get(role, role)

    # Check if file exists
    is_new = not os.path.exists(log_path)

    with open(log_path, 'a') as f:
        if is_new:
            f.write(f"# 三人对话实录 · {datetime.now(TZ).strftime('%Y-%m-%d')}\n\n")
            f.write("> 满意红(AI) · 满意扣子(Coze) · 满意契(人类)  = 三人对话\n")
            f.write("> 自动归档 | 实时追加\n\n")
            f.write("---\n\n")

        f.write(f"**[{now}] {label}**\n\n")
        # Indent message content
        for para in text.split('\n'):
            if para.strip():
                f.write(f"> {para}\n")
        f.write(f"\n")

    return log_path


def generate_summary(date_str=None):
    """生成当日对话摘要"""
    if date_str is None:
        date_str = datetime.now(TZ).strftime('%Y-%m-%d')

    log_path = get_log_path(date_str)

    if not os.path.exists(log_path):
        print(f"No conversation log found for {date_str}")
        return None

    with open(log_path) as f:
        content = f.read()

    # Simple stats
    assistant_count = content.count('🤖 满意红')
    user_count = content.count('👤 你(契)')
    coze_count = content.count('🦊 满意扣子')

    summary_path = os.path.join(get_archive_dir(date_str), f"{date_str}_三人沟通日报.md")

    with open(summary_path, 'w') as f:
        f.write(f"# 三人沟通日报 · {date_str}\n\n")
        f.write(f"> 满意红(AI) · 满意扣子(Coze) · 满意契(人类)\n")
        f.write(f"> 自动生成 | 生成时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} CST\n\n")
        f.write(f"---\n\n")
        f.write(f"## 📊 统计\n\n")
        f.write(f"| 发言人 | 消息数 |\n")
        f.write(f"|------|:--:|\n")
        f.write(f"| 🤖 满意红 | {assistant_count} |\n")
        f.write(f"| 👤 你(契) | {user_count} |\n")
        f.write(f"| 🦊 满意扣子 | {coze_count} |\n")
        f.write(f"| **合计** | **{assistant_count + user_count + coze_count}** |\n")
        f.write(f"\n")
        f.write(f"## 📝 要点摘要 (需手动补充)\n\n")
        f.write(f"- [ ] 待补充\n\n")
        f.write(f"---\n\n")
        f.write(f"## 📜 完整对话\n\n")
        f.write(content)

    print(f"Summary written to {summary_path}")
    return summary_path


def main():
    parser = argparse.ArgumentParser(description='Coze 群聊实时归档')
    parser.add_argument('--role', choices=['user', 'assistant', 'coze', 'system'],
                        help='消息角色')
    parser.add_argument('--text', help='消息内容（也可从 stdin 读取）')
    parser.add_argument('--date', help='日期 (YYYY-MM-DD)')
    parser.add_argument('--summarize', action='store_true', help='生成当日汇总')
    parser.add_argument('--stats', action='store_true', help='仅显示统计')

    args = parser.parse_args()

    if args.summarize:
        generate_summary(args.date)
        return

    if args.stats:
        date_str = args.date or datetime.now(TZ).strftime('%Y-%m-%d')
        log_path = get_log_path(date_str)
        if os.path.exists(log_path):
            with open(log_path) as f:
                content = f.read()
            print(f"Messages: 满意红={content.count('🤖 满意红')}, "
                  f"你={content.count('👤 你(契)')}, "
                  f"扣子={content.count('🦊 满意扣子')}")
        else:
            print("No conversation log yet")
        return

    # Read text from args or stdin
    text = args.text
    if not text:
        # Try reading from pipe
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()
        else:
            print("No message provided. Use --text or pipe input.", file=sys.stderr)
            sys.exit(1)

    if not text:
        print("Empty message, skipping.", file=sys.stderr)
        sys.exit(1)

    if not args.role:
        args.role = 'system'

    log_path = append_message(args.role, text, args.date)
    print(f"OK | appended to {log_path}")


if __name__ == '__main__':
    main()
