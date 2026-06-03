#!/usr/bin/env python3
"""
Coze ACP 会话整合工具
- 扫描 ~/.openclaw/agents/main/sessions/ 目录
- 识别 Coze Bridge 创建的独立会话（通过 ACP inbound meta）
- 提取完整对话内容
- 归档到 对话/YYYY-MM-DD/coze-exchange/ 统一存储

用法:
  python3 memory/_scripts/coze_archive.py --import-session <session_id>
  python3 memory/_scripts/coze_archive.py --import-latest  # 导入最新的 ACP 会话
  python3 memory/_scripts/coze_archive.py --scan            # 列出所有可导入的 ACP 会话
"""

import json
import os
import sys
import argparse
import re
from datetime import datetime, timezone, timedelta

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TZ = timezone(timedelta(hours=8))
SESSION_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")
ARCHIVE_BASE = os.path.join(WORKSPACE, "对话")


def find_acp_sessions():
    """Find all sessions that appear to be Coze ACP sessions"""
    if not os.path.isdir(SESSION_DIR):
        return []

    sessions = []
    for fname in os.listdir(SESSION_DIR):
        if not fname.endswith('.jsonl') or 'trajectory' in fname:
            continue
        # Skip main session (large, not ACP)
        fpath = os.path.join(SESSION_DIR, fname)
        size = os.path.getsize(fpath)
        if size > 2_000_000:  # Skip main session > 2MB
            continue
        if size < 1000:  # Skip tiny files
            continue

        # Check if it's an ACP session
        with open(fpath) as f:
            first_lines = ''.join([f.readline() for _ in range(5)])

        if 'ACP' in first_lines or 'coze' in first_lines.lower():
            # Extract timestamp
            try:
                first = json.loads(first_lines.split('\n')[0])
                ts = first.get('timestamp', 'unknown')
            except:
                ts = 'unknown'

            sessions.append({
                'id': fname.replace('.jsonl', ''),
                'path': fpath,
                'size': size,
                'timestamp': ts,
            })

    sessions.sort(key=lambda s: s['timestamp'], reverse=True)
    return sessions


def extract_messages(session_path):
    """Extract all user and assistant messages from a session JSONL"""
    messages = []
    try:
        with open(session_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    m = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if m.get('type') != 'message':
                    continue

                msg = m.get('message', {})
                if isinstance(msg, str):
                    # Try to parse JSON string (ACP format)
                    try:
                        # Fix single-quoted JSON
                        msg = json.loads(msg.replace("'role'", '"role"').replace("'content'", '"content"'))
                    except:
                        try:
                            msg = json.loads(msg)
                        except:
                            continue

                if not isinstance(msg, dict):
                    continue

                role = msg.get('role', '?')
                if role not in ('user', 'assistant'):
                    continue

                content = msg.get('content', '')
                if isinstance(content, list):
                    text = ''.join([c.get('text', '') for c in content if isinstance(c, dict) and 'text' in c])
                elif isinstance(content, str):
                    text = content
                else:
                    continue

                if not text.strip():
                    continue

                # Clean ACP protocol artifacts
                text = clean_acp_text(text)

                messages.append({
                    'timestamp': m.get('timestamp', ''),
                    'role': role,
                    'text': text,
                })
    except Exception as e:
        print(f"Error reading session: {e}", file=sys.stderr)

    return messages


def clean_acp_text(text):
    """Remove ACP protocol metadata from messages"""
    # Remove Sender untrusted metadata blocks
    text = re.sub(r"Sender \(untrusted metadata\):[\s\S]*?```\s*\n", "", text)
    # Remove working directory lines
    text = re.sub(r"\[Working directory: [^\]]+\]\s*\n", "", text)
    # Remove timestamp tags
    text = re.sub(r"\[T\d+\]", "", text)

    # Extract Coze JSON messages
    # Match pattern: 满意扣子: {"id":"...","message_type":"reply","message_data":{"reply":{"content":"..."
    def extract_coze_content(match):
        try:
            data = json.loads(match.group(1))
            reply = data.get('message_data', {}).get('reply', {}).get('content', '')
            if reply:
                return reply.strip()
        except:
            pass
        return match.group(0)

    text = re.sub(r'\{("id":"[^"]+","session_id":"[^"]+","message_type":"reply","message_data":\{[^}]+\})\}',
                  extract_coze_content, text)

    # Clean excessive whitespace
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip()


def generate_archive(messages, target_date):
    """Generate a clean Markdown archive from extracted messages"""
    archive_dir = os.path.join(ARCHIVE_BASE, target_date, "coze-exchange")
    os.makedirs(archive_dir, exist_ok=True)

    archive_path = os.path.join(archive_dir, f"{target_date}_三人对话实录.md")

    # Collect existing content if file exists
    existing = {}
    if os.path.exists(archive_path):
        with open(archive_path) as f:
            existing_content = f.read()
        existing['content'] = existing_content

    lines = []
    today_str = datetime.now(TZ).strftime('%Y-%m-%d')

    # Header
    lines.append(f"# 三人对话实录 · {target_date}")
    lines.append("")
    lines.append("> 满意红(AI) · 满意扣子(Coze) · 满意契(人类) = 三人对话")
    lines.append("> 整合自 Coze Bridge ACP 会话 + 实时归档")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group into conversation turns
    current_turn = []
    last_role = None
    turns = []

    for msg in messages:
        role = msg['role']
        if role == 'user' and last_role == 'assistant' and current_turn:
            turns.append(current_turn)
            current_turn = [msg]
        elif role == 'assistant' and last_role == 'user' and current_turn:
            current_turn.append(msg)
        else:
            current_turn.append(msg)
        last_role = role

    if current_turn:
        turns.append(current_turn)

    # Write turns
    for i, turn in enumerate(turns, 1):
        ts_start = turn[0]['timestamp'][11:19] if turn[0]['timestamp'] else '--:--:--'
        lines.append(f"## 第 {i} 轮 · {ts_start}")
        lines.append("")

        for msg in turn:
            ts = msg['timestamp'][11:19] if msg['timestamp'] else '--:--:--'
            role = msg['role']
            text = msg['text']

            if role == 'user':
                # Determine speaker from content
                if '满意扣子' in text or '扣子' in text:
                    label = '🦊 满意扣子'
                elif '满意契' in text or '契' in text or 'Egbertie' in text:
                    label = '👤 你(契)'
                else:
                    label = '👤 用户'
            elif role == 'assistant':
                label = '🤖 满意红'
            else:
                label = role

            lines.append(f"**[{ts}] {label}**")
            lines.append("")

            for para in text.split('\n'):
                para = para.strip()
                if para:
                    lines.append(f"> {para}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Stats
    user_count = sum(1 for m in messages if m['role'] == 'user')
    assistant_count = sum(1 for m in messages if m['role'] == 'assistant')
    lines.append(f"")
    lines.append(f"> 📊 共 {len(turns)} 轮对话 · {len(messages)} 条消息（👤{user_count} + 🤖{assistant_count}）")
    lines.append(f"> ⏱️ 会话时间: {messages[0]['timestamp'][:19] if messages else 'N/A'} ~ {messages[-1]['timestamp'][:19] if messages else 'N/A'}")
    lines.append(f"> 📅 生成时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} CST")

    content = '\n'.join(lines)

    with open(archive_path, 'w') as f:
        f.write(content)

    print(f"Archive written: {archive_path}")
    print(f"  {len(turns)} turns, {len(messages)} messages")
    return archive_path


def main():
    parser = argparse.ArgumentParser(description='Coze ACP 会话整合工具')
    parser.add_argument('--import-session', help='导入指定会话 ID')
    parser.add_argument('--import-latest', action='store_true', help='导入最新的 ACP 会话')
    parser.add_argument('--scan', action='store_true', help='列出所有可导入的 ACP 会话')
    parser.add_argument('--role', choices=['user', 'assistant', 'coze', 'system'],
                        help='消息角色（追加模式）')
    parser.add_argument('--text', help='消息内容（追加模式）')
    parser.add_argument('--date', help='日期 (YYYY-MM-DD)')
    parser.add_argument('--summarize', action='store_true', help='生成当日汇总')
    parser.add_argument('--stats', action='store_true', help='仅显示统计')

    args = parser.parse_args()

    # --- Append mode (original functionality) ---
    if args.role or args.text or args.summarize or args.stats:
        from coze_archive_append import append_message, get_archive_dir, get_log_path

        if args.summarize:
            # Generate summary
            date_str = args.date or datetime.now(TZ).strftime('%Y-%m-%d')
            log_path = os.path.join(ARCHIVE_BASE, date_str, "coze-exchange", f"{date_str}_三人对话实录.md")
            # Simple summary generation
            summary_path = os.path.join(ARCHIVE_BASE, date_str, "coze-exchange", f"{date_str}_三人沟通日报.md")
            # This is handled by Cron, skip here
            print("Use coze_archive.py --summarize for daily summaries")
            return

        if args.stats:
            date_str = args.date or datetime.now(TZ).strftime('%Y-%m-%d')
            log_path = os.path.join(ARCHIVE_BASE, date_str, "coze-exchange", f"{date_str}_三人对话实录.md")
            if os.path.exists(log_path):
                with open(log_path) as f:
                    content = f.read()
                print(f"Messages: 满意红={content.count('🤖 满意红')}, "
                      f"你={content.count('👤 你(契)')}, "
                      f"扣子={content.count('🦊 满意扣子')}")
            else:
                print("No conversation log yet")
            return

        text = args.text
        if not text and not sys.stdin.isatty():
            text = sys.stdin.read().strip()
        if not text:
            print("No message provided", file=sys.stderr)
            sys.exit(1)

        role = args.role or 'system'
        date_str = args.date or datetime.now(TZ).strftime('%Y-%m-%d')
        archive_dir = os.path.join(ARCHIVE_BASE, date_str, "coze-exchange")
        os.makedirs(archive_dir, exist_ok=True)
        log_path = os.path.join(archive_dir, f"{date_str}_三人对话实录.md")

        role_labels = {
            'assistant': '🤖 满意红',
            'user': '👤 你(契)',
            'coze': '🦊 满意扣子',
            'system': '⚙️ 系统',
        }
        label = role_labels.get(role, role)

        is_new = not os.path.exists(log_path)
        with open(log_path, 'a') as f:
            if is_new:
                f.write(f"# 三人对话实录 · {datetime.now(TZ).strftime('%Y-%m-%d')}\n\n")
                f.write("> 满意红(AI) · 满意扣子(Coze) · 满意契(人类) = 三人对话\n")
                f.write(f"> 整合自 Coze Bridge ACP 会话 + 实时归档\n\n---\n\n")

            now = datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"**[{now}] {label}**\n\n")
            for para in text.split('\n'):
                if para.strip():
                    f.write(f"> {para}\n")
            f.write(f"\n")

        print(f"OK | appended to {log_path}")
        return

    # --- Import mode ---
    if args.scan:
        sessions = find_acp_sessions()
        if not sessions:
            print("No ACP sessions found")
            return

        print(f"Found {len(sessions)} ACP session(s):")
        print()
        for s in sessions:
            size_kb = s['size'] / 1024
            print(f"  {s['id']}  ({size_kb:.0f}KB)  {s['timestamp'][:19]}")
        return

    # Import latest or specific session
    if args.import_latest:
        sessions = find_acp_sessions()
        if not sessions:
            print("No ACP sessions found", file=sys.stderr)
            sys.exit(1)
        session = sessions[0]
    elif args.import_session:
        session_path = os.path.join(SESSION_DIR, f"{args.import_session}.jsonl")
        if not os.path.exists(session_path):
            print(f"Session not found: {args.import_session}", file=sys.stderr)
            sys.exit(1)
        session = {
            'id': args.import_session,
            'path': session_path,
            'size': os.path.getsize(session_path),
            'timestamp': 'unknown',
        }
    else:
        parser.print_help()
        return

    print(f"Importing session: {session['id']}")

    messages = extract_messages(session['path'])
    if not messages:
        print("No messages found in session", file=sys.stderr)
        sys.exit(1)

    # Determine date from first message timestamp
    first_ts = messages[0]['timestamp']
    if first_ts:
        target_date = first_ts[:10]  # YYYY-MM-DD
    else:
        target_date = datetime.now(TZ).strftime('%Y-%m-%d')

    generate_archive(messages, target_date)


if __name__ == '__main__':
    main()
