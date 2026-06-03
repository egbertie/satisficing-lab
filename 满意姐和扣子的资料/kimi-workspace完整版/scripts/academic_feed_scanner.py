#!/usr/bin/env python3
"""
academic_feed_scanner.py
Fetch arXiv cs.AI RSS weekly for decision-related papers.
Append matches to an internal queue for human review.
"""
import os
import re
import datetime
import urllib.request
import xml.etree.ElementTree as ET

WORKSPACE = "/root/.openclaw/workspace"
QUEUE = os.path.join(WORKSPACE, "memory", "academic_paper_queue.json")
REPORT_DIR = os.path.join(WORKSPACE, "A-manyige", "审计")
# arXiv cs.AI RSS
RSS_URL = "http://export.arxiv.org/rss/cs.AI"
DECISION_KEYWORDS = ["decision", "partner", "collaboration", "trust", "cognitive", "intuition", "negotiation", "founder"]


def fetch_rss():
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def extract_papers(xml_bytes):
    papers = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return papers
    # arXiv RSS items are usually under channel/item
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        summary = (item.findtext("description") or "").strip()
        link = (item.findtext("link") or "").strip()
        if title:
            papers.append({"title": title, "summary": summary, "link": link})
    return papers


def is_relevant(paper):
    text = (paper["title"] + " " + paper["summary"]).lower()
    return any(kw in text for kw in DECISION_KEYWORDS)


def load_queue():
    import json
    if not os.path.exists(QUEUE):
        return []
    with open(QUEUE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    import json
    with open(QUEUE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def write_report(new_papers):
    os.makedirs(REPORT_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = os.path.join(REPORT_DIR, f"academic_scan_report_{today}.md")
    lines = [
        f"# 学术饲料扫描报告 ({today})",
        f"\n本周新增决策相关论文: **{len(new_papers)}**\n"
    ]
    for i, p in enumerate(new_papers, 1):
        lines.append(f"{i}. **{p['title']}**")
        lines.append(f"   - 链接: {p['link']}")
        lines.append(f"   - 摘要: {p['summary'][:200]}...\n")
    lines.append("---\n**Action**:  review 后将有价值的论文融入知识库或TASK_MASTER。")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    try:
        xml = fetch_rss()
    except Exception as e:
        print(f"FETCH_FAILED: {e}")
        return
    papers = extract_papers(xml)
    relevant = [p for p in papers if is_relevant(p)]
    queue = load_queue()
    existing_titles = {q["title"] for q in queue}
    new_papers = [p for p in relevant if p["title"] not in existing_titles]
    if new_papers:
        queue.extend(new_papers)
        # keep last 100
        queue = queue[-100:]
        save_queue(queue)
        path = write_report(new_papers)
        print(f"FOUND: {len(new_papers)} new papers -> {path}")
    else:
        print("OK: No new relevant papers")


if __name__ == "__main__":
    main()
