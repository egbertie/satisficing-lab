#!/usr/bin/env python3
"""
五层深挖验证脚本
用途: 自动检查洞察是否完成L5
规则: 只到L2=检查，不是洞察；必须到L5
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path

def validate_five_layers(file_path):
    """验证五层深挖是否到L5"""
    
    print(f"=== 五层深挖验证: {file_path} ===")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 错误: 无法读取文件 - {e}")
        return False
    
    # 检查5层
    layers = {
        "L1": bool(re.search(r"L1|发现了什么|表面现象", content)),
        "L2": bool(re.search(r"L2|共同模式|规律", content)),
        "L3": bool(re.search(r"L3|为什么|根因|认知偏差", content)),
        "L4": bool(re.search(r"L4|系统关联|负熵构造体", content)),
        "L5": bool(re.search(r"L5|未来指导|原则.*标准.*验证", content))
    }
    
    all_found = True
    for layer, found in layers.items():
        status = "✅" if found else "❌"
        print(f"{status} {layer}: {'找到' if found else '未找到'}")
        if not found:
            all_found = False
    
    if all_found:
        print("✅ 验证通过 - 五层深挖完整到L5")
    else:
        print("❌ 验证失败 - 未完整到L5")
    
    return all_found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 validate_five_layers.py <insight_file>")
        sys.exit(1)
    
    passed = validate_five_layers(sys.argv[1])
    sys.exit(0 if passed else 1)
