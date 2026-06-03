#!/usr/bin/env python3
"""
skill-usage-tracker - Skill使用追踪器
主入口

调用真正的实现: skill_usage_tracker.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from skill_usage_tracker import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
