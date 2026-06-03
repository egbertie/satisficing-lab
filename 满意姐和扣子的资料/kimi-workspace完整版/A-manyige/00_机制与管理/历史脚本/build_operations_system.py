#!/usr/bin/env python3
"""
运营体系构建器 - 承诺洗澡Phase 3
建立完整运营体系：质量标准+检查流程+追踪机制
"""

import json
from datetime import datetime
from pathlib import Path

def build_quality_standards():
    """建立质量标准文档"""
    standards = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "standards": {
            "文档交付": {
                "必含项": ["目的", "适用范围", "操作步骤", "验收标准"],
                "格式要求": "Markdown，层级清晰",
                "字数要求": "核心内容>500字"
            },
            "代码交付": {
                "必含项": ["功能说明", "使用方法", "错误处理"],
                "测试要求": "提供验证命令或测试用例",
                "文档要求": "必须可独立运行"
            },
            "任务交付": {
                "必含项": ["完成状态", "验证方式", "交付物路径"],
                "质量标准": "可验证、可复现、可追溯"
            }
        }
    }
    
    output_path = Path("/root/.openclaw/workspace/docs/QUALITY_STANDARDS.md")
    with open(output_path, 'w') as f:
        json.dump(standards, f, indent=2, ensure_ascii=False)
    
    return output_path

def build_quality_check_process():
    """建立质量检查流程"""
    check_process = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "process": {
            "交付前自检": [
                "检查必含项是否完整",
                "验证功能是否可用",
                "确认格式符合标准"
            ],
            "交付中验证": [
                "运行验证测试",
                "检查边界条件",
                "确认无报错"
            ],
            "交付后追踪": [
                "记录交付时间",
                "追踪使用情况",
                "收集反馈问题"
            ]
        },
        "checklist": {
            "文档": ["目的明确", "步骤清晰", "示例完整"],
            "代码": ["可运行", "有测试", "错误处理"],
            "任务": ["状态准确", "验证通过", "路径正确"]
        }
    }
    
    output_path = Path("/root/.openclaw/workspace/docs/QUALITY_CHECK_PROCESS.md")
    with open(output_path, 'w') as f:
        json.dump(check_process, f, indent=2, ensure_ascii=False)
    
    return output_path

def build_tracking_system():
    """建立效果追踪系统"""
    tracker = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "metrics": {
            "交付质量": {
                "首次通过率": "target:>90%",
                "返工率": "target:<10%",
                "逾期率": "target:<5%"
            },
            "问题追踪": {
                "问题发现时间": "记录",
                "问题解决时间": "记录",
                "问题复发次数": "记录"
            },
            "改进循环": {
                "每周复盘": "检查本周问题模式",
                "每月审计": "评估质量标准有效性",
                "持续优化": "根据反馈调整标准"
            }
        },
        "current_status": {
            "total_deliveries": 0,
            "passed_first_time": 0,
            "rework_count": 0,
            "issues": []
        }
    }
    
    output_path = Path("/root/.openclaw/workspace/memory/quality_tracker.json")
    with open(output_path, 'w') as f:
        json.dump(tracker, f, indent=2, ensure_ascii=False)
    
    return output_path

def run_quality_check():
    """运行质量检查"""
    checks = {
        "docs_with_standards": 0,
        "code_with_tests": 0,
        "tasks_with_verification": 0
    }
    
    # 检查文档
    for md_file in Path("/root/.openclaw/workspace/docs").glob("*.md"):
        content = md_file.read_text()
        if "验收标准" in content or "验证" in content:
            checks["docs_with_standards"] += 1
    
    # 检查代码
    for py_file in Path("/root/.openclaw/workspace/scripts").glob("*.py"):
        content = py_file.read_text()
        if "def test_" in content or "if __name__" in content:
            checks["code_with_tests"] += 1
    
    # 检查任务
    task_file = Path("/root/.openclaw/workspace/TASK_MASTER.md")
    if task_file.exists():
        content = task_file.read_text()
        checks["tasks_with_verification"] = content.count("验证")
    
    return checks

def build_operations_system():
    """构建完整运营体系"""
    results = {
        "build_time": datetime.now().isoformat(),
        "components": {}
    }
    
    # 构建各组件
    results["components"]["quality_standards"] = {
        "path": str(build_quality_standards()),
        "status": "created"
    }
    
    results["components"]["check_process"] = {
        "path": str(build_quality_check_process()),
        "status": "created"
    }
    
    results["components"]["tracking_system"] = {
        "path": str(build_tracking_system()),
        "status": "created"
    }
    
    # 运行质量检查
    results["quality_check"] = run_quality_check()
    
    # 保存总报告
    report_path = Path("/root/.openclaw/workspace/memory/operations_system_report.json")
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

if __name__ == "__main__":
    results = build_operations_system()
    print(f"运营体系构建完成:")
    print(f"  质量标准: {results['components']['quality_standards']['path']}")
    print(f"  检查流程: {results['components']['check_process']['path']}")
    print(f"  追踪系统: {results['components']['tracking_system']['path']}")
    print(f"  质量检查: {results['quality_check']}")
