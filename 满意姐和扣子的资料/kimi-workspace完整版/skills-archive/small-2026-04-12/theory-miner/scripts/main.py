#!/usr/bin/env python3
"""
theory-miner - 理论挖掘器
主入口

调用真正的实现: theory_miner.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from theory_miner import main as real_main

if __name__ == '__main__':
    sys.exit(real_main())
