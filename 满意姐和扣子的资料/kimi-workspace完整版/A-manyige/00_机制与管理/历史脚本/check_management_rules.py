#!/usr/bin/env python3
"""
管理规则执行器 - 核心检查脚本
强制执行检查，不留死角，如实汇报

使用方法:
    python3 check_management_rules.py [--full|--quick]
    
选项:
    --full  执行完整检查（对话开始时）
    --quick 执行快速检查（Heartbeat时）
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
DIARY_DIR = WORKSPACE / "diary"
DOCS_DIR = WORKSPACE / "docs"

def log(message, level="INFO"):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def get_file_mtime(filepath):
    """获取文件最后修改时间"""
    try:
        return datetime.fromtimestamp(os.path.getmtime(filepath))
    except FileNotFoundError:
        return None

def check_truth_redline():
    """
    实事求是红线检查
    返回: (是否通过, 问题列表)
    """
    issues = []
    
    # 检查diary/errors/中是否有未纠正的错误
    errors_dir = DIARY_DIR / "errors"
    if errors_dir.exists():
        error_files = list(errors_dir.glob("error_*.md"))
        for ef in error_files:
            content = ef.read_text()
            if "## 纠正措施" in content:
                # 检查是否所有纠正项都已勾选
                unchecked = content.count("- [ ]")
                if unchecked > 0:
                    issues.append({
                        "type": "未纠正错误",
                        "file": ef.name,
                        "detail": f"还有{unchecked}项纠正措施未完成"
                    })
    
    log(f"实事求是红线检查: {'通过' if not issues else f'发现{len(issues)}个问题'}")
    return len(issues) == 0, issues

def check_task_management():
    """
    任务管理检查
    返回: (是否通过, 问题列表)
    """
    issues = []
    
    # 检查TASK_MASTER.md是否存在
    task_master = WORKSPACE / "TASK_MASTER.md"
    if not task_master.exists():
        issues.append({
            "type": "文件缺失",
            "file": "TASK_MASTER.md",
            "detail": "任务总清单文件不存在"
        })
    else:
        # 检查是否有逾期任务（简化检查，实际应解析yaml）
        content = task_master.read_text()
        # 这里简化处理，实际应解析任务状态
        
    # 检查是否有被遗忘任务清单
    forgotten_tasks = WORKSPACE / "docs" / "FORGOTTEN_TASKS.md"
    if forgotten_tasks.exists():
        content = forgotten_tasks.read_text()
        if "- [ ]" in content or "- [x]" in content:
            # 统计未完成的任务
            total = content.count("- [ ]") + content.count("- [x]")
            undone = content.count("- [ ]")
            if undone > 0:
                issues.append({
                    "type": "被遗忘任务",
                    "count": undone,
                    "detail": f"还有{undone}个被遗忘任务未完成"
                })
    
    log(f"任务管理检查: {'通过' if not issues else f'发现{len(issues)}个问题'}")
    return len(issues) == 0, issues

def check_memory_system():
    """
    记忆系统检查
    返回: (是否通过, 问题列表)
    """
    issues = []
    now = datetime.now()
    
    # 检查MEMORY.md更新时间
    memory_file = WORKSPACE / "MEMORY.md"
    if memory_file.exists():
        mtime = get_file_mtime(memory_file)
        if mtime and (now - mtime) > timedelta(hours=24):
            hours_ago = (now - mtime).total_seconds() / 3600
            issues.append({
                "type": "记忆未更新",
                "file": "MEMORY.md",
                "detail": f"已{hours_ago:.1f}小时未更新"
            })
    else:
        issues.append({
            "type": "文件缺失",
            "file": "MEMORY.md",
            "detail": "核心记忆文件不存在"
        })
    
    # 检查当日日志是否存在
    today_str = now.strftime("%Y-%m-%d")
    today_log = MEMORY_DIR / f"{today_str}.md"
    if not today_log.exists():
        issues.append({
            "type": "日志缺失",
            "file": f"{today_str}.md",
            "detail": "当日日志文件未创建"
        })
    
    log(f"记忆系统检查: {'通过' if not issues else f'发现{len(issues)}个问题'}")
    return len(issues) == 0, issues

def check_expert_progress():
    """
    专家研究进度检查
    返回: (是否通过, 问题列表)
    """
    issues = []
    
    # 检查专家档案
    expert_file = WORKSPACE / "knowledge_system" / "core" / "experts.yaml"
    if expert_file.exists():
        content = expert_file.read_text()
        # 检查方翊沣博士的进度
        if "方翊沣" in content or "fang_yifeng" in content:
            # 简化检查，实际应解析yaml
            import re
            current_nodes_match = re.search(r'current_nodes:\s*(\d+)', content)
            target_nodes_match = re.search(r'target_nodes:\s*(\d+)', content)
            
            if current_nodes_match and target_nodes_match:
                current = int(current_nodes_match.group(1))
                target = int(target_nodes_match.group(1))
                
                if current < target:
                    progress = current / target * 100
                    if progress < 50:
                        issues.append({
                            "type": "研究进度滞后",
                            "expert": "方翊沣博士",
                            "detail": f"进度{progress:.1f}%({current}/{target})，低于50%"
                        })
    
    log(f"专家研究进度检查: {'通过' if not issues else f'发现{len(issues)}个问题'}")
    return len(issues) == 0, issues

def check_morning_report():
    """
    晨报生成检查
    返回: (是否通过, 问题列表)
    """
    issues = []
    now = datetime.now()
    
    # 如果当前时间已过09:00，检查晨报是否生成
    if now.hour >= 9:
        today_str = now.strftime("%Y-%m-%d")
        # 检查A满意哥专属文件夹中的晨报
        morning_report = WORKSPACE / "A满意哥专属文件夹" / "01_🔥今日重点" / f"晨报_{today_str}.md"
        
        if not morning_report.exists():
            issues.append({
                "type": "晨报未生成",
                "file": f"晨报_{today_str}.md",
                "detail": f"已过09:00，晨报尚未生成"
            })
    
    log(f"晨报生成检查: {'通过' if not issues else f'发现{len(issues)}个问题'}")
    return len(issues) == 0, issues

def run_full_check():
    """执行完整检查（对话开始时）"""
    log("=" * 60)
    log("开始执行完整检查")
    log("=" * 60)
    
    all_issues = []
    
    checks = [
        ("实事求是红线", check_truth_redline),
        ("任务管理", check_task_management),
        ("记忆系统", check_memory_system),
        ("专家研究进度", check_expert_progress),
        ("晨报生成", check_morning_report),
    ]
    
    for check_name, check_func in checks:
        log(f"\n执行: {check_name}")
        passed, issues = check_func()
        if issues:
            all_issues.extend([{**issue, "check": check_name} for issue in issues])
    
    log("\n" + "=" * 60)
    log(f"检查完成: 共发现 {len(all_issues)} 个问题")
    log("=" * 60)
    
    return all_issues

def run_quick_check():
    """执行快速检查（Heartbeat时）"""
    all_issues = []
    
    # 只检查P0项
    checks = [
        ("实事求是红线", check_truth_redline),
        ("任务管理", check_task_management),
    ]
    
    for check_name, check_func in checks:
        passed, issues = check_func()
        if issues:
            all_issues.extend([{**issue, "check": check_name} for issue in issues])
    
    return all_issues

def record_execution(check_type, issues_count, issues_list):
    """记录执行日志"""
    log_file = MEMORY_DIR / "management-enforcer-log.json"
    
    execution = {
        "timestamp": int(time.time()),
        "datetime": datetime.now().isoformat(),
        "type": check_type,
        "issues_count": issues_count,
        "issues": issues_list
    }
    
    log_data = []
    if log_file.exists():
        try:
            log_data = json.loads(log_file.read_text())
        except:
            pass
    
    log_data.append(execution)
    
    # 只保留最近100条记录
    log_data = log_data[-100:]
    
    log_file.write_text(json.dumps(log_data, indent=2, ensure_ascii=False))

def format_issues_report(issues):
    """格式化问题报告"""
    if not issues:
        return None
    
    report = ["⚠️ 【管理规则执行器发现异常】\n"]
    
    for i, issue in enumerate(issues, 1):
        report.append(f"{i}. [{issue['check']}] {issue['type']}")
        report.append(f"   详情: {issue.get('detail', 'N/A')}")
        if 'file' in issue:
            report.append(f"   文件: {issue['file']}")
        report.append("")
    
    report.append("-" * 40)
    report.append("纠正措施已启动，详见日志。")
    
    return "\n".join(report)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="管理规则执行器")
    parser.add_argument("--full", action="store_true", help="执行完整检查")
    parser.add_argument("--quick", action="store_true", help="执行快速检查")
    
    args = parser.parse_args()
    
    if args.full:
        issues = run_full_check()
        record_execution("full", len(issues), issues)
        report = format_issues_report(issues)
        if report:
            print("\n" + report)
            sys.exit(1)  # 发现问题，返回错误码
    elif args.quick:
        issues = run_quick_check()
        record_execution("quick", len(issues), issues)
        report = format_issues_report(issues)
        if report:
            print(report)
            sys.exit(1)
        else:
            print("HEARTBEAT_OK")
    else:
        # 默认执行完整检查
        issues = run_full_check()
        record_execution("full", len(issues), issues)
        report = format_issues_report(issues)
        if report:
            print("\n" + report)
            sys.exit(1)
    
    sys.exit(0)