#!/usr/bin/env python3
"""
Partner Matching Engine - CLI入口
"""

import sys
import os

# 将scripts目录添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from partner_matching import cli

if __name__ == '__main__':
    cli()
