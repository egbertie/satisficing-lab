#!/usr/bin/env python3
"""
全量工程静默执行脚本
自动执行Skill修复、审计，记录结果
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

SKILLS_DIR = "/root/.openclaw/workspace/skills"
REPORT_FILE = "/root/.openclaw/workspace/reports/MASTER_EXECUTION_REPORT.json"
LOG_FILE = "/root/.openclaw/workspace/reports/execution_log.txt"

# 执行列表（优先级排序）
EXECUTION_QUEUE = [
    # 阶段1: 核心Skill修复
    {'skill': 'blue-army-interceptor', 'action': 'fix_and_audit'},
    {'skill': 'hibernation-protocol', 'action': 'fix_and_audit'},
    {'skill': 'tiered-output', 'action': 'fix_and_audit'},
    
    # 阶段2: 10超级系统SOP审计
    {'skill': 'knowledge-suite', 'action': 'audit_only'},
    {'skill': 'automation-suite', 'action': 'audit_only'},
    {'skill': 'file-suite', 'action': 'audit_only'},
    {'skill': 'quality-suite', 'action': 'audit_only'},
    {'skill': 'backup-suite', 'action': 'audit_only'},
    {'skill': 'token-suite', 'action': 'audit_only'},
    {'skill': 'content-suite', 'action': 'audit_only'},
    {'skill': 'expert-suite', 'action': 'audit_only'},
    {'skill': 'feishu-suite', 'action': 'audit_only'},
    {'skill': 'governance-suite', 'action': 'audit_only'},
]

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + '\n')

def audit_skill(skill_name):
    """审计Skill"""
    skill_path = Path(SKILLS_DIR) / skill_name
    if not skill_path.exists():
        return {'skill': skill_name, 'status': 'NOT_FOUND'}
    
    try:
        result = subprocess.run(
            ['python3', 'blue_army_sop.py', '--audit', str(skill_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=f"{SKILLS_DIR}/blue-auditor"
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {'skill': skill_name, 'status': 'ERROR', 'error': str(e)}

def main():
    """主执行循环"""
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    
    log("=" * 60)
    log("全量工程静默执行开始")
    log("=" * 60)
    
    results = []
    
    for task in EXECUTION_QUEUE:
        skill_name = task['skill']
        action = task['action']
        
        log(f"\n处理: {skill_name} ({action})")
        
        # 执行审计
        result = audit_skill(skill_name)
        results.append(result)
        
        status = result.get('overall_status', 'UNKNOWN')
        p0_failures = len(result.get('p0_failures', []))
        
        log(f"  状态: {status}, P0失败: {p0_failures}项")
        
        # 如果失败且需要修复，这里可以添加自动修复逻辑
        # 当前版本仅记录，手动修复
    
    # 保存报告
    report = {
        'execution_time': datetime.now().isoformat(),
        'total_tasks': len(EXECUTION_QUEUE),
        'completed': len(results),
        'summary': {
            'pass': sum(1 for r in results if r.get('overall_status') == 'PASS'),
            'conditional': sum(1 for r in results if r.get('overall_status') == 'CONDITIONAL'),
            'fail': sum(1 for r in results if r.get('overall_status') == 'FAIL'),
        },
        'results': results
    }
    
    with open(REPORT_FILE, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    log("\n" + "=" * 60)
    log("执行完成，报告已保存")
    log(f"  通过: {report['summary']['pass']}")
    log(f"  条件通过: {report['summary']['conditional']}")
    log(f"  失败: {report['summary']['fail']}")
    log(f"  报告: {REPORT_FILE}")
    log("=" * 60)

if __name__ == '__main__':
    main()
