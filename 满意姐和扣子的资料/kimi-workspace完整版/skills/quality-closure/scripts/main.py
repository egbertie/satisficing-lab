#!/usr/bin/env python3
"""
quality-closure - 质量闭环管理器
主入口

调用真正的实现: quality_closure.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from quality_closure import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
