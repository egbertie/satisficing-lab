#!/usr/bin/env python3
"""
token-weekly-monitor - Token周度监控器
主入口

调用真正的实现: token_weekly_monitor.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from token_weekly_monitor import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
