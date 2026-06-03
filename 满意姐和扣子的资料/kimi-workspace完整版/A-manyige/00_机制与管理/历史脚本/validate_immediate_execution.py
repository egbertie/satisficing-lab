#!/usr/bin/env python3
"""
立即执行文化验证脚本
用途: 验证任务是否立即执行，没有拖延
"""

import sys
import re

def validate_immediate_execution(file_path):
    """验证立即执行文化"""
    
    print(f"=== 立即执行文化验证: {file_path} ===")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 错误: 无法读取文件 - {e}")
        return False
    
    # 检查立即执行指标
    checks = {
        "立即开始": bool(re.search(r"立即开始|立即执行", content)),
        "分批次": bool(re.search(r"分批次|P0|P1|P2", content)),
        "不等待": bool(re.search(r"不等待|批次间.*不等待", content)),
        "非明天": not bool(re.search(r"明天再做|等有时间", content))
    }
    
    all_found = True
    for check, found in checks.items():
        status = "✅" if found else "❌"
        print(f"{status} {check}: {'找到' if found else '未找到'}")
        if not found:
            all_found = False
    
    if all_found:
        print("✅ 验证通过 - 立即执行文化符合")
    else:
        print("❌ 验证失败 - 存在拖延信号")
    
    return all_found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 validate_immediate_execution.py <file>")
        sys.exit(1)
    
    passed = validate_immediate_execution(sys.argv[1])
    sys.exit(0 if passed else 1)
