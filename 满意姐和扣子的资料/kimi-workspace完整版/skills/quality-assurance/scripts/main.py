#!/usr/bin/env python3
"""
quality-assurance - 质量保证框架
主入口

调用真正的实现: quality_assurance.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from quality_assurance import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
