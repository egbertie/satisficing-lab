#!/usr/bin/env python3
"""
quality-assessment - 质量评估工具
主入口

调用真正的实现: quality_assessment.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from quality_assessment import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
