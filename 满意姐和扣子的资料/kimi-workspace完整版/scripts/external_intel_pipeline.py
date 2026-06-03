#!/usr/bin/env python3
"""
external_intel_pipeline.py
Minimal weekly pipeline that checks an RSS feed for external intelligence
and appends to a backlog. 血液化外部信息监控机制。
"""
import os
import json
import datetime
import urllib.request
import xml.etree.ElementTree as ET

WORKSPACE = "/root/.openclaw/workspace"
BACKLOG = os.path.join(WORKSPACE, "memory", "external_intel_backlog.json")
REPORT_DIR = os.path.join(WORKSPACE, "A-manyige", "审计")
# Using a tech/business feed; can be swapped for any RSS
RSS_URL = "http://feeds.feedburner.com/TechCrunch/startups"
TARGET_KEYWORDS = ["partner", "co-founder", "founder", "startup", "decision", "venture", "capital"]


def fetch_feed():
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_items(xml_bytes):
    items = []
    try:
        root = ET.fromstring(xml_bytes)
    except Exception:
        return items
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        if title:
            items.append({"title": title, "link": link, "desc": desc})
    return items


def is_relevant(item):
    text = (item["title"] + " " + item["desc"]).lower()
    return any(kw in text for kw in TARGET_KEYWORDS)


def load_backlog():
    if not os.path.exists(BACKLOG):
        return []
    with open(BACKLOG, "r", encoding="utf-8") as f:
        return json.load(f)


def save_backlog(data):
    with open(BACKLOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_report(new_items):
    os.makedirs(REPORT_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = os.path.join(REPORT_DIR, f"external_intel_report_{today}.md")
    lines = [
        f"# 外部情报流水线报告 ({today})",
        f"\n本周新增相关情报: **{len(new_items)}**\n"
    ]
    for i, it in enumerate(new_items, 1):
        lines.append(f"{i}. **{it['title']}**")
        lines.append(f"   - {it['link']}\n")
    lines.append("---\n**Action**: 阅读后将有价值的情报转化为 TASK_MASTER 任务或洞察。")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    try:
        xml = fetch_feed()
    except Exception as e:
        print(f"FETCH_FAILED: {e}")
        return
    items = parse_items(xml)
    relevant = [it for it in items if is_relevant(it)]
    backlog = load_backlog()
    seen = {b["title"] for b in backlog}
    new_items = [it for it in relevant if it["title"] not in seen]
    if new_items:
        backlog.extend(new_items)
        backlog = backlog[-100:]
        save_backlog(backlog)
        path = write_report(new_items)
        print(f"FOUND: {len(new_items)} intel items -> {path}")
    else:
        print("OK: No new intel")


if __name__ == "__main__":
    main()
