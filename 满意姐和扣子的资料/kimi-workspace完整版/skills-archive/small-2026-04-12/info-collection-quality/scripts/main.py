#!/usr/bin/env python3
"""
info-collection-quality - Main execution script
信息采集与质量控制体系 V2.0 - 5-Standard Skill

本文件提供简化的入口点，主要逻辑在 info-collection-quality-runner.py
"""

import sys
from pathlib import Path

# 添加scripts目录到路径
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from info_collection_quality_runner import main as runner_main
    
    if __name__ == '__main__':
        sys.exit(runner_main())
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保 info-collection-quality-runner.py 存在于 scripts/ 目录")
    sys.exit(1)
