#!/usr/bin/env python3
"""
抖音视频下载器（无水印）- 改造版
支持真实工具链（yt-dlp / you-get）或 Demo 模式
"""
from __future__ import annotations
import re
import os
import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Union

class DouyinDownloader:
    """
    抖音视频下载器（无水印）
    优先尝试真实下载工具 yt-dlp / you-get；不存在则回退 Demo 模式
    """

    def __init__(self, api_endpoint: str = ""):
        # 外部虚构 API 已废弃；若传入真实 endpoint 可保留兼容
        self.api_endpoint = api_endpoint or os.environ.get("DOUYIN_API_ENDPOINT", "")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self._backend = self._detect_backend()

    def _detect_backend(self) -> str:
        if shutil.which("yt-dlp"):
            return "yt-dlp"
        if shutil.which("you-get"):
            return "you-get"
        return "demo"

    async def download(self, share_url: str, extract_audio: bool = False) -> Union[str, Dict]:
        """
        下载抖音视频（无水印）
        Demo 模式下返回可执行的命令提示，不真正下载
        """
        if self._backend == "demo":
            return {
                "status": "demo",
                "message": "当前环境缺少 yt-dlp / you-get，进入演示模式。",
                "install_hint": "pip install yt-dlp 或 pip install you-get",
                " example_command": f"yt-dlp '{share_url}' -o /tmp/douyin_%(id)s.%(ext)s",
                "share_url": share_url,
                "extract_audio": extract_audio
            }

        video_id = await self._parse_share_url(share_url)
        local_path = f"/tmp/douyin_{video_id}.mp4"

        if self._backend == "yt-dlp":
            cmd = [
                "yt-dlp", share_url,
                "-o", local_path,
                "--no-warnings",
                "--quiet"
            ]
        else:
            cmd = [
                "you-get", "-o", "/tmp", "-O", f"douyin_{video_id}", share_url
            ]
            local_path = f"/tmp/douyin_{video_id}.mp4"

        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.communicate()

        if not Path(local_path).exists():
            return {"status": "failed", "error": f"下载失败: {share_url}"}

        if extract_audio:
            audio_path = await self._extract_audio(local_path)
            return {"video": local_path, "audio": audio_path, "status": "success"}

        return local_path

    async def _parse_share_url(self, share_url: str) -> str:
        """解析短链接获取真实视频ID"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(share_url, headers=self.headers, allow_redirects=True) as resp:
                final_url = str(resp.url)
                match = re.search(r'/video/(\d+)', final_url)
                if match:
                    return match.group(1)
                # 尝试匹配其他格式
                match2 = re.search(r'modal_id=(\d+)', final_url)
                if match2:
                    return match2.group(1)
                raise ValueError("无法解析视频ID")

    async def _extract_audio(self, video_path: str) -> str:
        """使用 ffmpeg 提取音频"""
        audio_path = video_path.replace(".mp4", "_audio.mp3")
        cmd = [
            "ffmpeg", "-i", video_path, "-vn", "-acodec", "libmp3lame",
            "-q:a", "2", audio_path, "-y"
        ]
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.communicate()
        return audio_path


async def _demo():
    dd = DouyinDownloader()
    # 使用一个公共示例链接（不保证长期有效，仅用于演示解析逻辑）
    test_url = "https://v.douyin.com/i5M5uQ2H/"
    result = await dd.download(test_url, extract_audio=False)
    print(result)

if __name__ == '__main__':
    asyncio.run(_demo())
