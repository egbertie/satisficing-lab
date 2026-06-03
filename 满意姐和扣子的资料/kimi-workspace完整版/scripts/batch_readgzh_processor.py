#!/usr/bin/env python3
"""
Batch readgzh processor for 105 WeChat article URLs.
Processes in batches of 21 with 30s rest between.
Saves content and generates index.
"""
import json
import os
import time
import urllib.parse
import urllib.request
import ssl
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

KEY = "sk_live_ojMsROfhGepeWlaC6VfMMuz94uiM9Iu7NIFAWaAH"
URLS_FILE = "/tmp/wechat_urls.txt"
OUT_DIR = Path("/root/.openclaw/workspace/A-manyige/知识库/readgzh_2026-04-11")
INDEX_FILE = OUT_DIR / "index.json"
MASTER_MD = OUT_DIR / "微信学术快报_全文汇总_2026-04-11.md"

OUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch(url):
    q = urllib.parse.urlencode({"url": url, "format": "text", "key": KEY})
    api_url = f"https://api.readgzh.site/rd?{q}"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (compatible; OpenClaw)"})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
            elapsed = time.time() - start
            title = ""
            desc = ""
            if "<title>" in data and "</title>" in data:
                title = data.split("<title>")[1].split("</title>")[0].strip()
            # meta description
            if '<meta name="description" content="' in data:
                desc = data.split('<meta name="description" content="')[1].split('"')[0].strip()
            return {
                "ok": True,
                "url": url,
                "title": title,
                "description": desc,
                "size": len(data),
                "time": round(elapsed, 2),
                "cost": resp.headers.get("x-credit-cost", "?"),
                "cache": resp.headers.get("x-cache", "?"),
                "content": data,
            }
    except Exception as e:
        return {
            "ok": False,
            "url": url,
            "error": f"{type(e).__name__}: {e}",
            "time": round(time.time() - start, 2),
        }

def main():
    with open(URLS_FILE) as f:
        urls = [u.strip() for u in f if u.strip()]
    
    batch_size = 21
    results = []
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"\n=== Processing Batch {batch_num}/{(len(urls)-1)//batch_size + 1} ({len(batch)} items) ===")
        for url in batch:
            r = fetch(url)
            results.append(r)
            status = "✅" if r["ok"] else "❌"
            title = r.get("title", "")[:30]
            print(f"  {status} {title}... | {r.get('size', 0)} bytes | cost={r.get('cost', '?')} | cache={r.get('cache', '?')}")
        
        if i + batch_size < len(urls):
            print("  [Resting 30s...]")
            time.sleep(30)
    
    # Save individual files
    for idx, r in enumerate(results, 1):
        if r["ok"]:
            safe_title = "".join(c for c in r["title"] if c.isalnum() or c in " _-")[:40] or f"article_{idx}"
            fname = OUT_DIR / f"{idx:03d}_{safe_title}.html"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(r["content"])
    
    # Save index JSON
    index = []
    for idx, r in enumerate(results, 1):
        entry = {
            "idx": idx,
            "url": r["url"],
            "ok": r["ok"],
        }
        if r["ok"]:
            entry.update({
                "title": r["title"],
                "description": r["description"],
                "size": r["size"],
                "time": r["time"],
                "cost": r["cost"],
                "cache": r["cache"],
                "file": f"{idx:03d}_{''.join(c for c in r['title'] if c.isalnum() or c in ' _-')[:40] or f'article_{idx}'}.html",
            })
        else:
            entry["error"] = r["error"]
        index.append(entry)
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    # Generate master markdown
    lines = [
        "# 微信学术快报 · readgzh 全文汇总",
        "",
        f"> **来源**：微信公众号「爱可可爱生活」  ",
        f"> **采集时间**：2026-04-11  ",
        f"> **链接总数**：{len(urls)} 条  ",
        f"> **成功解析**：{sum(1 for r in results if r['ok'])} 条  ",
        f"> **失败**：{sum(1 for r in results if not r['ok'])} 条  ",
        f"> **总积分消耗**：{sum(int(r['cost']) for r in results if r['ok'] and r['cost'] != '?')} credits  ",
        "",
        "---",
        "",
        "## 文章索引",
        "",
        "| 编号 | 标题 | 缓存 | 积分 | 字数/大小 |",
        "|:-:|:-----|:----:|:----:|:---------:|",
    ]
    
    for entry in index:
        if entry["ok"]:
            size_kb = round(entry["size"] / 1024, 1)
            lines.append(f"| {entry['idx']} | {entry['title']} | {entry['cache']} | {entry['cost']} | {size_kb} KB |")
        else:
            lines.append(f"| {entry['idx']} | ❌ {entry['error'][:30]}... | - | - | - |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 全文内容")
    lines.append("")
    
    for idx, r in enumerate(results, 1):
        if r["ok"]:
            lines.append(f"### [{idx}] {r['title']}")
            lines.append(f"- **URL**: {r['url']}")
            lines.append(f"- **Cache**: {r['cache']} | **Cost**: {r['cost']} | **Size**: {r['size']} bytes")
            lines.append("")
            # Include raw HTML content
            lines.append("```html")
            # Truncate extremely long content to avoid markdown bloat? No, keep all.
            lines.append(r["content"])
            lines.append("```")
            lines.append("")
            lines.append("---")
            lines.append("")
    
    with open(MASTER_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    # Summary stats
    ok_count = sum(1 for r in results if r["ok"])
    total_cost = sum(int(r["cost"]) for r in results if r["ok"] and r["cost"] != "?")
    hit_count = sum(1 for r in results if r["ok"] and r["cache"] == "HIT")
    print(f"\n=== DONE ===")
    print(f"Total URLs: {len(urls)}")
    print(f"Success: {ok_count}")
    print(f"Cache HIT: {hit_count}")
    print(f"Total Credits: {total_cost}")
    print(f"Output: {OUT_DIR}")

if __name__ == "__main__":
    main()
