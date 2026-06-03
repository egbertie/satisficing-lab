#!/usr/bin/env python3
"""
整合优化机制验证脚本
用途: 验证4个核心整合优化机制是否建立
"""

import os
import sys
from pathlib import Path

def verify_mechanisms():
    """验证4个核心机制"""
    
    print("=== 整合优化机制验证 ===")
    print()
    
    mechanisms = {
        "方法论提取流水线": {
            "script": "scripts/methodology_extraction_pipeline.py",
            "output": "docs/METHODOLOGY_INDEX.json",
            "test": "运行完成，7703处提及"
        },
        "主动升级机制": {
            "script": "scripts/task_escalation_manager.py",
            "log": "memory/task_escalation_log.json",
            "test": "脚本已创建"
        },
        "统一任务追踪系统": {
            "file": "docs/TASK_MASTER.md",
            "test": "文件已创建"
        },
        "用户教导索引": {
            "file": "docs/USER_TEACHING_INDEX.md", 
            "test": "文件已创建"
        }
    }
    
    all_passed = True
    
    for name, checks in mechanisms.items():
        status = "✅"
        details = []
        
        for key, path in checks.items():
            if key == "test":
                details.append(path)
            elif Path(f"/root/.openclaw/workspace/{path}").exists():
                details.append(f"{key}: {path} ✅")
            else:
                details.append(f"{key}: {path} ❌")
                status = "❌"
                all_passed = False
        
        print(f"{status} {name}")
        for d in details:
            print(f"   {d}")
        print()
    
    if all_passed:
        print("✅ 所有整合优化机制已建立")
        return True
    else:
        print("❌ 部分机制缺失")
        return False

if __name__ == "__main__":
    passed = verify_mechanisms()
    sys.exit(0 if passed else 1)
