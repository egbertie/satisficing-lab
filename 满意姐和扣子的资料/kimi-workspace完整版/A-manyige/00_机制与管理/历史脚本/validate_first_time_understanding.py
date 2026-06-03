#!/usr/bin/env python3
"""
第一次理解检查验证脚本
用途: 自动检查是否完成5层理解
规则: 没过5层就执行 = 违规
"""

import sys
import re

def validate_first_time_understanding(file_path):
    """验证第一次理解检查是否完成5层"""
    
    print(f"=== 第一次理解检查验证: {file_path} ===")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 错误: 无法读取文件 - {e}")
        return False
    
    # 检查5层
    checks = {
        "表面意思": bool(re.search(r"表面意思|字面意思", content)),
        "深层意图": bool(re.search(r"深层意图|为什么要", content)),
        "执行方式": bool(re.search(r"执行方式|立即完成|分批次", content)),
        "潜在要求": bool(re.search(r"潜在要求|隐含", content)),
        "我的错误": bool(re.search(r"我的错误|过去.*犯错", content))
    }
    
    all_found = True
    for check, found in checks.items():
        status = "✅" if found else "❌"
        print(f"{status} {check}: {'找到' if found else '未找到'}")
        if not found:
            all_found = False
    
    if all_found:
        print("✅ 验证通过 - 5层理解检查完整")
    else:
        print("❌ 验证失败 - 未完整到5层")
    
    return all_found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 validate_first_time_understanding.py <file>")
        sys.exit(1)
    
    passed = validate_first_time_understanding(sys.argv[1])
    sys.exit(0 if passed else 1)
