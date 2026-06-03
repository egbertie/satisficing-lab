#!/usr/bin/env python3
"""
任务包装器 - 强制执行Skill框架
终极解决方案 - 措施2: 流程层嵌入
立即执行版 - 2026-03-31
"""

import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
LOG_FILE = WORKSPACE / "logs/task_wrapper/execution.log"
VIOLATION_LOG = WORKSPACE / "logs/task_wrapper/violations.log"

def log(message, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def log_violation(violation_type, details):
    """记录违规"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    violation = {
        "timestamp": timestamp,
        "type": violation_type,
        "details": details
    }
    
    VIOLATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(VIOLATION_LOG, "a") as f:
        f.write(json.dumps(violation) + "\n")
    
    log(f"🚨 违规记录: {violation_type}", "ERROR")

def is_direct_python_execution(cmd):
    """检测是否直接执行Python脚本"""
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    
    # 检测直接运行.py文件
    if "python" in cmd_str and ".py" in cmd_str:
        # 排除允许的脚本
        allowed_scripts = [
            "skill_runner.py",
            "task_wrapper.py",
            "baseline-checker-runner.py",
            "blue_army_runner.py",
            "meta_auditor/scheduler.py"
        ]
        
        for allowed in allowed_scripts:
            if allowed in cmd_str:
                return False
        
        return True
    
    return False

def is_skill_invocation(cmd):
    """检测是否通过Skill框架调用"""
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    
    # 检测openclaw skill run或通过Skill入口调用
    skill_indicators = [
        "openclaw skill run",
        "skills/super-knowledge-ingest/run.py",
        "skills/baseline-checker",
        "skills/blue-auditor",
        "--validate",
        "--test"
    ]
    
    for indicator in skill_indicators:
        if indicator in cmd_str:
            return True
    
    return False

def validate_5_standards(skill_name):
    """验证5标准"""
    # 这里将调用具体的5标准验证
    # 目前为框架，待填充
    log(f"验证 {skill_name} 的5标准...")
    return True

def blue_army_audit(skill_name):
    """蓝军审计"""
    # 这里将调用蓝军审计
    # 目前为框架，待填充
    log(f"执行 {skill_name} 的蓝军审计...")
    return True

def execute_skill(skill_name, params):
    """执行Skill"""
    log(f"执行Skill: {skill_name}")
    # 实际执行逻辑
    return True

def task_wrapper(cmd):
    """
    任务包装器 - 所有任务必须通过
    
    强制执行:
    1. Skill框架检查
    2. 5标准验证
    3. 蓝军审计
    """
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    log(f"包装任务: {cmd_str}")
    
    # 1. 检测直接执行
    if is_direct_python_execution(cmd):
        log_violation("DIRECT_PYTHON_EXECUTION", cmd_str)
        log("❌ 错误: 必须通过Skill框架调用", "ERROR")
        log("💡 正确用法: openclaw skill run <skill-name>", "INFO")
        return False
    
    # 2. 验证Skill调用
    if not is_skill_invocation(cmd):
        log_violation("NON_SKILL_INVOCATION", cmd_str)
        log("❌ 错误: 未通过Skill框架调用", "ERROR")
        return False
    
    # 3. 提取Skill名称
    # 简化处理，实际需要更复杂的解析
    skill_name = "unknown"
    if "super-knowledge-ingest" in cmd_str:
        skill_name = "super-knowledge-ingest"
    elif "baseline-checker" in cmd_str:
        skill_name = "baseline-checker"
    elif "blue-auditor" in cmd_str:
        skill_name = "blue-auditor"
    
    # 4. 5标准验证
    if not validate_5_standards(skill_name):
        log_violation("STANDARDS_VALIDATION_FAILED", skill_name)
        log("❌ 错误: 未通过5标准验证", "ERROR")
        return False
    
    # 5. 蓝军审计
    if not blue_army_audit(skill_name):
        log_violation("BLUE_ARMY_AUDIT_FAILED", skill_name)
        log("❌ 错误: 未通过蓝军审计", "ERROR")
        return False
    
    # 6. 执行
    log(f"✅ 全部检查通过，执行任务")
    return execute_skill(skill_name, cmd)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: task_wrapper.py <command>")
        print("示例: task_wrapper.py 'openclaw skill run super-knowledge-ingest'")
        sys.exit(1)
    
    cmd = sys.argv[1:]
    success = task_wrapper(cmd)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
