#!/usr/bin/env python3
"""
quality-gate-system - 质量门禁系统
主入口

调用真正的实现: quality_gate_system.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from quality_gate_system import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
