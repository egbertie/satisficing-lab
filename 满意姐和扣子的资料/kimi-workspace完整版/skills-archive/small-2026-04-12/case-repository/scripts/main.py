#!/usr/bin/env python3
"""
case-repository - 案例库管理系统
主入口

调用真正的实现: case_repository.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from case_repository import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
