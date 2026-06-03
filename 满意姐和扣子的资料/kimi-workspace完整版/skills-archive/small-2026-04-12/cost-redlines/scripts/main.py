#!/usr/bin/env python3
"""
cost-redlines - Token/成本红线监控系统
主入口

调用真正的实现: cost_redlines.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cost_redlines import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
