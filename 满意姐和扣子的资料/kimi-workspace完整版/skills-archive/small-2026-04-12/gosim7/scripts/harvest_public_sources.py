#!/usr/bin/env python3
"""
Unified corpus harvester for the laoda-skill project.

Supports:
- public HTML pages
- YouTube transcripts via youtube-transcript-api
- fallback YouTube subtitle/text extraction via yt-dlp metadata
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except Exception:  # pragma: no cover - optional dependency
    YouTubeTranscriptApi = None

try:
    from yt_dlp import YoutubeDL
except Exception:  # pragma: no cover - optional dependency
    YoutubeDL = None


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if text:
            self.parts.append(text)


def clean_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    text = "\n".join(parser.parts)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_url(url: str, timeout: float) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; MambaMentorCollector/2.0)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def iter_sources(manifest_path: Path) -> Iterable[dict]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Manifest must contain a JSON array.")
    for item in data:
        if not isinstance(item, dict) or "id" not in item or "url" not in item:
            raise ValueError("Each source must be an object with at least id and url.")
        yield item


def extract_video_id(source: dict) -> str | None:
    if source.get("video_id"):
        return str(source["video_id"])
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", source["url"])
    if match:
        return match.group(1)
    return None


def fetch_youtube_transcript(video_id: str) -> str:
    if YouTubeTranscriptApi is not None:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=["en"])
        return "\n".join(snippet.text for snippet in transcript)
    raise RuntimeError("youtube-transcript-api is not installed.")


def fetch_youtube_metadata(url: str) -> dict:
    if YoutubeDL is None:
        raise RuntimeError("yt-dlp is not installed.")
    ydl = YoutubeDL({"quiet": True, "skip_download": True})
    info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title"),
        "channel": info.get("channel"),
        "description": info.get("description"),
        "duration": info.get("duration"),
    }


def harvest_source(source: dict, timeout: float) -> dict:
    record = dict(source)
    source_type = source.get("type", "web")

    if source_type == "youtube_transcript":
        video_id = extract_video_id(source)
        if not video_id:
            raise ValueError(f"Could not derive video ID for {source['id']}")
        record["video_id"] = video_id
        record["text"] = fetch_youtube_transcript(video_id)
        try:
            record["metadata"] = fetch_youtube_metadata(source["url"])
        except Exception as exc:  # pragma: no cover - best effort only
            record["metadata_error"] = str(exc)
        return record

    html = fetch_url(source["url"], timeout=timeout)
    record["text"] = clean_text(html)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("collected-sources.json"),
        help="JSON output path",
    )
    parser.add_argument(
        "--timeout", type=float, default=20.0, help="Per-request timeout in seconds"
    )
    args = parser.parse_args()

    results: list[dict] = []
    for item in iter_sources(args.manifest):
        record = dict(item)
        try:
            harvested = harvest_source(item, timeout=args.timeout)
            record.update(harvested)
            record["status"] = "ok"
        except (urllib.error.URLError, ValueError, RuntimeError) as exc:
            record["status"] = "error"
            record["error"] = str(exc)
        results.append(record)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    ok_count = sum(1 for record in results if record["status"] == "ok")
    print(f"Wrote {len(results)} records to {args.output} ({ok_count} fetched successfully).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
