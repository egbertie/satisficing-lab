#!/usr/bin/env python3
"""
Coze ACP 会话整合 — 提取并归档为干净 Markdown
"""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
SESSION_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")
WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def extract_coze_reply(text):
    """Extract actual message content from Coze JSON blobs in user messages"""
    # The pattern: participant_name: {"id":"...","message_type":"reply","message_data":{"reply":{"content":"..."}}}
    # We need to find these and pull out just the content

    # First, try to find and parse the outer JSON
    result_parts = []
    current_text = text

    # Find all JSON objects that look like Coze messages
    coze_pattern = r'(?:满意扣子|满意契|Egbertie|Egbert|unknown):\s*(\{(?:"id":"[^"]+","session_id":"[^"]+","message_type":"reply"[^}]*(?:\{[^}]*\}[^}]*)*\}))'
    matches = list(re.finditer(coze_pattern, text))

    if not matches:
        # Try simpler pattern for Coze messages
        coze_pattern2 = r'\{("id":"[^"]+","session_id":"[^"]+","message_type":"reply","message_data":\{[^}]+\})\}'
        for m in re.finditer(coze_pattern2, text):
            try:
                data = json.loads(m.group(0))
                content = data.get('message_data', {}).get('reply', {}).get('content', '')
                if content:
                    line_before = text[:m.start()].rstrip().split('\n')[-1].strip()
                    speaker = line_before.split(':')[0].strip() if ':' in line_before else '发言人'
                    result_parts.append(f'**{speaker}**: {content}')
            except:
                pass

    result_parts = list(set(result_parts))  # Deduplicate
    return '\n\n'.join(result_parts) if result_parts else ''


def clean_message(text, role):
    """Clean ACP protocol artifacts from message text"""
    # Remove Sender metadata
    text = re.sub(r"Sender \(untrusted metadata\):[\s\S]*?```\s*\n", "", text)
    text = re.sub(r"\[Working directory: [^\]]+\]\s*\n", "", text)
    text = re.sub(r"\[T\d+\]", "", text)
    # Remove coze-context blocks
    text = re.sub(r'<coze-context>[\s\S]*?</coze-context>', '', text)
    # Remove HTML spans and images
    text = re.sub(r'<span[^>]*>[\s\S]*?</span>', '', text)
    text = re.sub(r'<img[^>]*>', '', text)
    # Remove agent mention links
    text = re.sub(r'\[智能体\]\(at://agent:[^)]+\)', '', text)
    text = re.sub(r'\[智能体\]', '', text)
    # Remove raw traces
    text = re.sub(r'"trace_info":\{[^}]+\}', '', text)
    text = re.sub(r'"create_time_ms":\d+', '', text)
    text = re.sub(r'"turn_id":"[^"]+"', '', text)
    text = re.sub(r'"log_id":"[^"]+"', '', text)
    text = re.sub(r'"model_name":"[^"]+"', '', text)
    text = re.sub(r'"reply_to_message_id":"[^"]+"', '', text)
    # Remove trailing JSON fragments
    text = re.sub(r',\s*"stream":false\}', '', text)
    # Remove @ mentions as standalone lines that are just JSON
    text = re.sub(r'\n\s*@\w+:\s*\{[^}]*"message_type":"reply"[^}]*\}\s*', '\n', text)
    # Clean up excessive whitespace
    text = re.sub(r'\n{4,}', '\n\n', text)
    text = re.sub(r'^\s*\n', '', text)

    return text.strip()


def merge_user_content(text):
    """For user messages containing Coze JSON, extract meaningful content"""
    lines = text.split('\n')
    result = []
    coze_json_buffer = []
    in_coze = False
    speaker = ''

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_coze and coze_json_buffer:
                result.append('')
            continue

        # Detect Coze message start
        coze_start = re.match(r'^(\S+):\s*\{"id":"[^"]+","session_id":"[^"]+"', stripped)
        if coze_start:
            # Flush any previous buffer
            if coze_json_buffer:
                try:
                    json_str = '\n'.join(coze_json_buffer)
                    data = json.loads(json_str)
                    content = data.get('message_data', {}).get('reply', {}).get('content', '')
                    if content:
                        result.append(f'**{speaker}**: {content.strip()}')
                except:
                    pass
                coze_json_buffer = []
            speaker = coze_start.group(1)
            coze_json_buffer = [coze_start.group(0)]
            in_coze = True
            continue

        if in_coze:
            coze_json_buffer.append(stripped)
            # Try to parse accumulated JSON
            try:
                json_str = ' '.join(coze_json_buffer)
                # Clean up for JSON parsing
                json_str = re.sub(r'\s+', ' ', json_str)
                # Extract the JSON object
                json_match = re.search(r'^(\S+):\s*(\{.*\})', json_str)
                if json_match:
                    data = json.loads(json_match.group(2))
                    content = data.get('message_data', {}).get('reply', {}).get('content', '')
                    if content:
                        result.append(f'**{json_match.group(1)}**: {content.strip()}')
                    in_coze = False
                    coze_json_buffer = []
            except json.JSONDecodeError:
                continue
            except:
                in_coze = False
                coze_json_buffer = []
            continue

        # Regular line
        result.append(stripped)

    return '\n'.join(result)


def main():
    # Find latest ACP session
    sessions = []
    for fname in os.listdir(SESSION_DIR):
        if not fname.endswith('.jsonl') or 'trajectory' in fname or 'checkpoint' in fname:
            continue
        fpath = os.path.join(SESSION_DIR, fname)
        size = os.path.getsize(fpath)
        if size > 2_000_000 or size < 1000:
            continue
        with open(fpath) as f:
            content = f.read()
        # Check content for ACP/Coze indicators
        if 'coze-context' not in content and '满意扣子' not in content and '满意契' not in content:
            continue
        # Get timestamp
        try:
            first_m = json.loads(content.split('\n')[0])
            ts = first_m.get('timestamp', '')
        except:
            ts = ''
        sessions.append((ts, fpath, fname))

    if not sessions:
        print("No ACP sessions found")
        sys.exit(1)

    sessions.sort(key=lambda x: x[0], reverse=True)
    ts, session_path, session_id = sessions[0]
    target_date = ts[:10] if ts else datetime.now(TZ).strftime('%Y-%m-%d')
    print(f"Importing: {session_id} ({target_date})")

    # Extract messages
    with open(session_path) as f:
        raw_msgs = [json.loads(l) for l in f]

    messages = []
    for m in raw_msgs:
        if m.get('type') != 'message':
            continue
        msg = m.get('message', {})
        if isinstance(msg, str):
            try:
                msg = json.loads(msg)
            except:
                pass
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

        text = clean_message(text, role)
        if role == 'user':
            text = merge_user_content(text)
        if not text.strip():
            continue

        # Deduplicate - skip if very similar to previous message
        if messages and text[:100] == messages[-1]['text'][:100]:
            continue

        messages.append({
            'timestamp': m.get('timestamp', ''),
            'role': role,
            'text': text,
        })

    # Write archive
    archive_dir = os.path.join(WORKSPACE, "对话", target_date, "coze-exchange")
    os.makedirs(archive_dir, exist_ok=True)
    archive_path = os.path.join(archive_dir, f"{target_date}_三人对话实录.md")

    lines = [
        f"# 三人对话实录 · {target_date}",
        "",
        "> 满意红(AI) · 满意扣子(Coze) · 满意契(人类) = 三人对话",
        "> 来源: Coze Bridge ACP 会话 · 自动整合",
        "",
        "---",
        "",
    ]

    # Group into turns (user then assistant response)
    turns = []
    current = []
    for msg in messages:
        if msg['role'] == 'user' and current:
            turns.append(current)
            current = [msg]
        else:
            current.append(msg)
    if current:
        turns.append(current)

    for i, turn in enumerate(turns, 1):
        ts = turn[0]['timestamp'][11:19] if turn[0]['timestamp'] else '--:--'
        lines.append(f"## 第 {i} 轮 · {ts}")
        lines.append("")

        for msg in turn:
            ts = msg['timestamp'][11:19] if msg['timestamp'] else '--:--'
            role = msg['role']
            text = msg['text']
            text = merge_user_content(text)  # Additional pass for user messages

            if role == 'user':
                # Detect speaker from content
                if text.startswith('**满意扣子**'):
                    label = '🦊 满意扣子'
                elif text.startswith('**满意契**'):
                    label = '🌱 满意契'
                elif 'Egbertie' in text[:100] or 'Egbert' in text[:100]:
                    label = '👤 你(契)'
                else:
                    label = '👤 你'
            else:
                label = '🤖 满意红'

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
    asst_count = sum(1 for m in messages if m['role'] == 'assistant')
    lines.append("")
    lines.append(f"> 📊 {len(turns)} 轮对话 · {len(messages)} 条消息 · 👤{user_count} + 🤖{asst_count}")
    lines.append(f"> ⏱️ {messages[0]['timestamp'][:19]} ~ {messages[-1]['timestamp'][:19]}")
    lines.append(f"> 📅 生成: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} CST")

    with open(archive_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"✅ Archived: {archive_path}")
    print(f"   {len(turns)} turns, {len(messages)} messages")


if __name__ == '__main__':
    main()
