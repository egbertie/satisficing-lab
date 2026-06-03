#!/usr/bin/env python3
"""
ReadGZH 每日领积分提醒机制
每天 09:00 生成提醒标记文件，AI 在当日首次会话时读取并提醒用户。
零 Token 成本的纯系统 cron。
"""
import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
FLAG_FILE = WORKSPACE / "memory" / ".readgzh_reminder_pending"


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "date": today,
        "created_at": datetime.now().isoformat(),
        "message": "今日 readgzh 免费积分尚未领取。请登录 https://readgzh.site/dashboard 领取 5 条免费文章额度。",
    }
    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FLAG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[{datetime.now().isoformat()}] readgzh reminder flag set for {today}")


if __name__ == "__main__":
    main()
