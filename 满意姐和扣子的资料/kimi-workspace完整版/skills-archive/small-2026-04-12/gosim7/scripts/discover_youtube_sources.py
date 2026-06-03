#!/usr/bin/env python3
"""
Discover embedded YouTube videos from public web pages and emit candidate source
records that can be merged into source-manifest.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

try:
    from yt_dlp import YoutubeDL
except Exception:  # pragma: no cover - optional dependency
    YoutubeDL = None


YOUTUBE_ID_RE = re.compile(
    r"(?:youtube\.com/embed/|youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})"
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; MambaMentorDiscover/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def get_video_title(url: str) -> str | None:
    if YoutubeDL is None:
        return None
    ydl = YoutubeDL({"quiet": True, "skip_download": True})
    info = ydl.extract_info(url, download=False)
    return info.get("title")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+")
    parser.add_argument("--output", type=Path, default=Path("discovered-youtube.json"))
    args = parser.parse_args()

    records: list[dict] = []
    seen: set[str] = set()
    for page_url in args.urls:
        try:
            html = fetch_text(page_url)
        except urllib.error.URLError as exc:
            records.append(
                {
                    "id": f"page-error-{len(records)+1}",
                    "type": "discovery_error",
                    "url": page_url,
                    "error": str(exc),
                }
            )
            continue
        for video_id in sorted(set(YOUTUBE_ID_RE.findall(html))):
            if video_id in seen:
                continue
            seen.add(video_id)
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            record = {
                "id": f"youtube-{video_id.lower()}",
                "type": "youtube_transcript",
                "category": "interview",
                "title": get_video_title(youtube_url) or f"YouTube video {video_id}",
                "url": youtube_url,
                "video_id": video_id,
                "discovered_from": page_url,
            }
            records.append(record)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} discovered records to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
