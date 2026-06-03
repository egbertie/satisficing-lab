#!/usr/bin/env python3
"""
info-quality-guardian - 信息采集质量控制体系
主入口

调用真正的实现: info_quality_guardian.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from info_quality_guardian import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
