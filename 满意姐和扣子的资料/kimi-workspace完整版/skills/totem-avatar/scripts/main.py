#!/usr/bin/env python3
"""Totem Avatar CLI入口"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from totem_avatar import cli

if __name__ == '__main__':
    cli()
