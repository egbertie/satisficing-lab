#!/usr/bin/env python3
"""
深度洞察验证脚本
用途: 自动检查洞察报告是否包含全部10个方法论
规则: 少一个方法论 = 验证失败
时间: 2026-03-30
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path

# 10方法论关键词定义
METHODOLOGY_KEYWORDS = {
    "first_principles": ["第一性原理", "物理本质", "拆解"],
    "satisficing": ["满意解", "最优解陷阱", "分批次"],
    "antifragile": ["反脆弱", "从失败中获益", "失败→学习→机制"],
    "skeptor7": ["Skeptor-7", "7问", "我遗漏了什么"],
    "time_asymmetry": ["时间不对称", "现在省", "未来付", "净收益"],
    "five_totems": ["五图腾", "LIU", "SIMON", "GUANYIN", "CONFUCIUS", "HUINENG"],
    "five_layers": ["五层深挖", "L1", "L2", "L3", "L4", "L5", "原则+标准+验证"],
    "negentropy": ["负熵", "熵增", "熵减", "混乱"],
    "identity": ["身份验证", "负熵构造体", "守护型", "操心老妈子"],
    "blue_army": ["蓝军", "Skeptor-7", "审计", "质疑"]
}

def check_methodology(content, methodology_name, keywords):
    """检查是否包含特定方法论"""
    for keyword in keywords:
        if keyword in content:
            return True, keyword
    return False, None

def validate_insight_report(file_path):
    """验证洞察报告"""
    
    print(f"=== 深度洞察验证: {file_path} ===")
    print(f"时间: {datetime.now().isoformat()}")
    print()
    
    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 错误: 无法读取文件 - {e}")
        return False
    
    # 检查10方法论
    results = {}
    missing = []
    
    for method_name, keywords in METHODOLOGY_KEYWORDS.items():
        found, matched_keyword = check_methodology(content, method_name, keywords)
        results[method_name] = {
            "found": found,
            "keyword": matched_keyword
        }
        
        status = "✅" if found else "❌"
        print(f"{status} {method_name}: {'找到 - ' + matched_keyword if found else '未找到'}")
        
        if not found:
            missing.append(method_name)
    
    print()
    
    # 检查L5
    l5_pattern = r"(原则|标准|验证).*[：:]|L5.*(原则|标准|验证)"
    l5_found = bool(re.search(l5_pattern, content))
    l5_status = "✅" if l5_found else "❌"
    print(f"{l5_status} L5未来指导: {'找到' if l5_found else '未找到'}")
    
    if not l5_found:
        missing.append("L5未来指导")
    
    # 检查物理化
    physical_pattern = r"(物理化|写入|创建).*\.(md|json|py|sh)"
    physical_found = bool(re.search(physical_pattern, content))
    physical_status = "✅" if physical_found else "❌"
    print(f"{physical_status} 物理化: {'找到' if physical_found else '未找到'}")
    
    if not physical_found:
        missing.append("物理化")
    
    print()
    
    # 最终结果
    if missing:
        print(f"❌ 验证失败 - 缺失: {', '.join(missing)}")
        return False
    else:
        print("✅ 验证通过 - 10方法论完整，L5到位，已物理化")
        return True

def log_execution(task_name, methodologies_used, l5_reached, physicalized, passed):
    """记录执行日志"""
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task_name,
        "methodologies_used": methodologies_used,
        "methodologies_count": len(methodologies_used),
        "l5_reached": l5_reached,
        "physicalized": physicalized,
        "blue_army_approved": passed,
        "status": "PASS" if passed else "FAIL"
    }
    
    log_file = Path("/root/.openclaw/workspace/memory/deep_insight_execution_log.json")
    
    # 读取现有日志
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    else:
        logs = []
    
    # 添加新记录
    logs.append(log_entry)
    
    # 写入日志
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 执行日志已记录: {log_file}")

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("用法: python3 deep_insight_validator.py <insight_report_file>")
        print("示例: python3 deep_insight_validator.py diary/my_insight.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # 验证报告
    passed = validate_insight_report(file_path)
    
    # 记录日志
    log_execution(
        task_name=file_path,
        methodologies_used=list(METHODOLOGY_KEYWORDS.keys()) if passed else [],
        l5_reached=passed,
        physicalized=passed,
        passed=passed
    )
    
    # 返回状态码
    sys.exit(0 if passed else 1)
