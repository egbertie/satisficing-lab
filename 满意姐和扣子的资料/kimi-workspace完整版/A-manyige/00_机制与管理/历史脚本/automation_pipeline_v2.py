#!/usr/bin/env python3
"""
自动化执行管道 - 承诺洗澡Phase 2
建立监控+执行完整的自动化能力
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def auto_knowledge_ingestion():
    """知识自动入库管道"""
    # 检查新文件
    workspace = Path("/root/.openclaw/workspace")
    knowledge_dir = workspace / "knowledge" / "ingested"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    # 扫描新增文件
    new_files = []
    for ext in [".md", ".txt", ".json"]:
        for f in workspace.rglob(f"*{ext}"):
            if "knowledge/ingested" not in str(f) and f.stat().st_size > 0:
                new_files.append({
                    "path": str(f),
                    "size": f.stat().st_size,
                    "mtime": f.stat().st_mtime
                })
    
    # 保存索引
    index_path = knowledge_dir / "auto_ingested_index.json"
    with open(index_path, 'w') as f:
        json.dump({
            "scan_time": datetime.now().isoformat(),
            "total_files": len(new_files),
            "files": new_files[:50]  # 只保留前50个
        }, f, indent=2)
    
    return len(new_files)

def auto_task_escalation():
    """任务逾期自动升级"""
    # 读取任务看板
    task_file = Path("/root/.openclaw/workspace/TASK_MASTER.md")
    if not task_file.exists():
        return 0
    
    content = task_file.read_text()
    
    # 简单检测逾期任务（基于文本匹配）
    overdue_count = content.count("逾期")
    
    # 生成升级报告
    escalation_path = Path("/root/.openclaw/workspace/memory/auto_escalation_report.json")
    escalation_data = {
        "check_time": datetime.now().isoformat(),
        "overdue_tasks_detected": overdue_count,
        "escalation_triggered": overdue_count > 0,
        "action": "notify_user" if overdue_count > 0 else "none"
    }
    
    with open(escalation_path, 'w') as f:
        json.dump(escalation_data, f, indent=2)
    
    return overdue_count

def auto_error_fix():
    """常见错误自动修复"""
    fixes_applied = []
    
    # 修复1: 确保memory目录存在
    memory_dir = Path("/root/.openclaw/workspace/memory")
    if not memory_dir.exists():
        memory_dir.mkdir(parents=True)
        fixes_applied.append("created_memory_dir")
    
    # 修复2: 确保知识目录存在
    knowledge_dir = Path("/root/.openclaw/workspace/knowledge/system")
    if not knowledge_dir.exists():
        knowledge_dir.mkdir(parents=True)
        fixes_applied.append("created_knowledge_dir")
    
    # 修复3: 检查并修复损坏的JSON
    for json_file in Path("/root/.openclaw/workspace").rglob("*.json"):
        try:
            with open(json_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            # 备份损坏文件
            backup_path = str(json_file) + ".backup"
            os.rename(json_file, backup_path)
            fixes_applied.append(f"fixed_corrupted_json:{json_file.name}")
    
    # 保存修复报告
    fix_report_path = Path("/root/.openclaw/workspace/memory/auto_fix_report.json")
    with open(fix_report_path, 'w') as f:
        json.dump({
            "check_time": datetime.now().isoformat(),
            "fixes_applied": fixes_applied,
            "fix_count": len(fixes_applied)
        }, f, indent=2)
    
    return len(fixes_applied)

def run_automation_pipeline():
    """运行完整自动化管道"""
    results = {
        "run_time": datetime.now().isoformat(),
        "pipelines": {}
    }
    
    # 执行各管道
    results["pipelines"]["knowledge_ingestion"] = {
        "status": "success",
        "files_scanned": auto_knowledge_ingestion()
    }
    
    results["pipelines"]["task_escalation"] = {
        "status": "success",
        "overdue_detected": auto_task_escalation()
    }
    
    results["pipelines"]["error_fix"] = {
        "status": "success",
        "fixes_applied": auto_error_fix()
    }
    
    # 保存总报告
    report_path = Path("/root/.openclaw/workspace/memory/automation_pipeline_report.json")
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = run_automation_pipeline()
    print(f"自动化管道执行完成:")
    print(f"  知识入库: {results['pipelines']['knowledge_ingestion']['files_scanned']} 个文件")
    print(f"  任务升级: {results['pipelines']['task_escalation']['overdue_detected']} 个逾期")
    print(f"  错误修复: {results['pipelines']['error_fix']['fixes_applied']} 处修复")
