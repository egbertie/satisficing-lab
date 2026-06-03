#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查点健康验证脚本 (Checkpoint Health Check)
执行时间: 每日 16:00
功能:
1. 验证checkpoint文件存在性和完整性
2. 检查磁盘空间
3. 验证关键文件可访问
4. 生成健康报告
"""

import os
import sys
import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# ============ 配置区域 ============
WORKSPACE = Path("/root/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs" / "cron-tasks"
MEMORY_DIR = WORKSPACE / "memory"
CHECKPOINT_FILE = MEMORY_DIR / "system_state_checkpoint.json"
RECOVERY_SCRIPT = WORKSPACE / "scripts" / "system_restart_recovery.py"

# 磁盘空间阈值（GB）
DISK_WARNING_GB = 2.0
DISK_CRITICAL_GB = 0.5
# ===================================

# 设置日志
os.makedirs(LOG_DIR, exist_ok=True)
log_file = LOG_DIR / f"checkpoint-health-check-{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('checkpoint-health')

# 超时保护
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Script execution timeout")

def set_timeout(seconds=120):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

def clear_timeout():
    signal.alarm(0)

def check_checkpoint_file():
    """检查checkpoint文件状态"""
    status = {
        "exists": False,
        "readable": False,
        "valid_json": False,
        "age_hours": None,
        "size_kb": 0
    }
    
    try:
        if CHECKPOINT_FILE.exists():
            status["exists"] = True
            stat = CHECKPOINT_FILE.stat()
            status["size_kb"] = round(stat.st_size / 1024, 2)
            
            # 检查文件年龄
            age_seconds = datetime.now().timestamp() - stat.st_mtime
            status["age_hours"] = round(age_seconds / 3600, 1)
            
            # 尝试读取
            try:
                content = CHECKPOINT_FILE.read_text(encoding='utf-8')
                status["readable"] = True
                
                # 验证JSON
                data = json.loads(content)
                status["valid_json"] = True
                
                # 检查关键字段
                required_fields = ["timestamp", "last_update", "session_count"]
                status["has_required_fields"] = all(f in data for f in required_fields)
                
            except json.JSONDecodeError:
                logger.error("Checkpoint文件JSON格式无效")
            except Exception as e:
                logger.error(f"读取checkpoint失败: {e}")
        
        return status
        
    except Exception as e:
        logger.error(f"检查checkpoint文件失败: {e}")
        return status

def check_recovery_script():
    """检查恢复脚本状态"""
    status = {
        "exists": False,
        "executable": False,
        "syntax_valid": False
    }
    
    try:
        if RECOVERY_SCRIPT.exists():
            status["exists"] = True
            
            # 检查是否可执行
            status["executable"] = os.access(RECOVERY_SCRIPT, os.X_OK) or RECOVERY_SCRIPT.suffix == '.py'
            
            # 验证Python语法
            if RECOVERY_SCRIPT.suffix == '.py':
                try:
                    import py_compile
                    py_compile.compile(str(RECOVERY_SCRIPT), doraise=True)
                    status["syntax_valid"] = True
                except Exception as e:
                    logger.warning(f"恢复脚本语法检查失败: {e}")
        
        return status
        
    except Exception as e:
        logger.error(f"检查恢复脚本失败: {e}")
        return status

def check_disk_space():
    """检查磁盘空间"""
    status = {
        "total_gb": 0,
        "used_gb": 0,
        "free_gb": 0,
        "percent_used": 0,
        "status": "unknown"
    }
    
    try:
        disk_usage = shutil.disk_usage(WORKSPACE)
        
        status["total_gb"] = round(disk_usage.total / (1024**3), 2)
        status["used_gb"] = round(disk_usage.used / (1024**3), 2)
        status["free_gb"] = round(disk_usage.free / (1024**3), 2)
        status["percent_used"] = round(disk_usage.used / disk_usage.total * 100, 1)
        
        if status["free_gb"] < DISK_CRITICAL_GB:
            status["status"] = "critical"
        elif status["free_gb"] < DISK_WARNING_GB:
            status["status"] = "warning"
        else:
            status["status"] = "ok"
        
        return status
        
    except Exception as e:
        logger.error(f"检查磁盘空间失败: {e}")
        return status

def check_critical_files():
    """检查关键文件可访问性"""
    critical_files = {
        "SOUL.md": WORKSPACE / "SOUL.md",
        "AGENTS.md": WORKSPACE / "AGENTS.md",
        "USER.md": WORKSPACE / "USER.md",
        "MEMORY.md": WORKSPACE / "MEMORY.md"
    }
    
    results = {}
    for name, filepath in critical_files.items():
        try:
            results[name] = {
                "exists": filepath.exists(),
                "readable": os.access(filepath, os.R_OK) if filepath.exists() else False,
                "writable": os.access(filepath, os.W_OK) if filepath.exists() else False
            }
        except Exception as e:
            logger.warning(f"检查文件 {name} 失败: {e}")
            results[name] = {"exists": False, "readable": False, "writable": False}
    
    return results

def perform_health_check():
    """执行健康检查"""
    logger.info("=" * 60)
    logger.info("🏥 检查点健康验证开始")
    logger.info("=" * 60)
    
    # 1. 检查checkpoint文件
    logger.info("\n【步骤1】验证checkpoint文件...")
    checkpoint = check_checkpoint_file()
    if checkpoint["exists"]:
        logger.info(f"✓ Checkpoint文件存在 ({checkpoint['size_kb']} KB)")
        logger.info(f"  年龄: {checkpoint['age_hours']} 小时")
        if checkpoint["valid_json"]:
            logger.info("✓ JSON格式有效")
        else:
            logger.error("✗ JSON格式无效")
    else:
        logger.warning("⚠ Checkpoint文件不存在")
    
    # 2. 检查恢复脚本
    logger.info("\n【步骤2】验证恢复脚本...")
    recovery = check_recovery_script()
    if recovery["exists"]:
        logger.info(f"✓ 恢复脚本存在")
        if recovery["syntax_valid"]:
            logger.info("✓ Python语法有效")
    else:
        logger.warning("⚠ 恢复脚本不存在")
    
    # 3. 检查磁盘空间
    logger.info("\n【步骤3】检查磁盘空间...")
    disk = check_disk_space()
    logger.info(f"  总计: {disk['total_gb']} GB")
    logger.info(f"  已用: {disk['used_gb']} GB ({disk['percent_used']}%)")
    logger.info(f"  空闲: {disk['free_gb']} GB")
    
    if disk["status"] == "ok":
        logger.info("✓ 磁盘空间充足")
    elif disk["status"] == "warning":
        logger.warning(f"⚠ 磁盘空间偏低 (< {DISK_WARNING_GB} GB)")
    else:
        logger.error(f"🚨 磁盘空间严重不足 (< {DISK_CRITICAL_GB} GB)")
    
    # 4. 检查关键文件
    logger.info("\n【步骤4】检查关键文件...")
    files = check_critical_files()
    all_accessible = True
    for name, status in files.items():
        if status["exists"] and status["readable"] and status["writable"]:
            logger.info(f"✓ {name}")
        else:
            logger.warning(f"⚠ {name} (存在:{status['exists']} 可读:{status['readable']} 可写:{status['writable']})")
            all_accessible = False
    
    # 5. 生成健康报告
    logger.info("\n" + "=" * 60)
    logger.info("🏥 检查点健康验证完成")
    logger.info("=" * 60)
    
    # 综合健康状态
    issues = []
    if not checkpoint["exists"]:
        issues.append("checkpoint文件缺失")
    if not checkpoint["valid_json"]:
        issues.append("checkpoint格式无效")
    if disk["status"] == "critical":
        issues.append("磁盘空间严重不足")
    elif disk["status"] == "warning":
        issues.append("磁盘空间偏低")
    if not all_accessible:
        issues.append("部分关键文件不可访问")
    
    if not issues:
        logger.info("✅ 健康状态: 良好 (无严重问题)")
    else:
        logger.warning(f"⚠️ 健康状态: 需要关注 ({len(issues)} 个问题)")
        for issue in issues:
            logger.warning(f"  - {issue}")
    
    logger.info("\n详细报告:")
    logger.info(f"  Checkpoint: {'✓' if checkpoint['valid_json'] else '✗'}")
    logger.info(f"  恢复脚本: {'✓' if recovery['exists'] else '✗'}")
    logger.info(f"  磁盘状态: {disk['status'].upper()}")
    logger.info(f"  关键文件: {'✓' if all_accessible else '⚠'}")
    logger.info("=" * 60)
    
    return {
        "checkpoint": checkpoint,
        "recovery": recovery,
        "disk": disk,
        "files": files,
        "issues": issues
    }

def main():
    """主函数"""
    try:
        set_timeout(120)  # 2分钟超时
        result = perform_health_check()
        clear_timeout()
        
        # 根据问题返回状态码
        if len(result["issues"]) == 0:
            sys.exit(0)
        elif len(result["issues"]) < 3:
            sys.exit(1)  # 警告
        else:
            sys.exit(2)  # 严重
            
    except TimeoutError:
        logger.error("⏱ 脚本执行超时")
        sys.exit(3)
    except Exception as e:
        logger.error(f"💥 脚本执行异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(4)

if __name__ == "__main__":
    main()
