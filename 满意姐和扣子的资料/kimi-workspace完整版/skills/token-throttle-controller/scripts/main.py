#!/usr/bin/env python3
"""
token-throttle-controller - Token节流控制器
主入口

调用真正的实现: token_throttle_controller.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from token_throttle_controller import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
