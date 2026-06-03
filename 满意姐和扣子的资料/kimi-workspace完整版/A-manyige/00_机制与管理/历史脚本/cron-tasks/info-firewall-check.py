#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息防火墙检查脚本 (Information Firewall Check)
执行时间: 每日 12:00 和 18:00
功能:
1. 检查敏感信息泄露风险
2. 验证MEMORY.md中无绝对机密
3. 检查临时文件是否清理
4. 生成安全检查报告
"""

import os
import sys
import re
import logging
from datetime import datetime
from pathlib import Path

# ============ 配置区域 ============
WORKSPACE = Path("/root/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs" / "cron-tasks"
MEMORY_DIR = WORKSPACE / "memory"
TMP_DIR = Path("/tmp")

# 敏感信息模式（正则表达式）
SENSITIVE_PATTERNS = {
    "api_key": r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}',
    "password": r'(password|passwd|pwd)["\']?\s*[:=]\s*["\'][^"\']{4,}',
    "token": r'(token|secret)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}',
    "private_key": r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    "phone": r'1[3-9]\d{9}',  # 中国手机号
}

# 检查的文件扩展名
CHECK_EXTENSIONS = {'.md', '.txt', '.json', '.yaml', '.yml', '.py', '.sh'}
# ===================================

# 设置日志
os.makedirs(LOG_DIR, exist_ok=True)
log_file = LOG_DIR / f"info-firewall-check-{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('info-firewall')

# 超时保护
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Script execution timeout")

def set_timeout(seconds=180):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

def clear_timeout():
    signal.alarm(0)

def scan_file_for_sensitive_info(filepath):
    """扫描单个文件中的敏感信息"""
    findings = []
    
    try:
        # 跳过二进制文件和大文件
        if filepath.stat().st_size > 1024 * 1024:  # 1MB
            return findings
        
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in SENSITIVE_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    # 找到敏感信息，记录但隐藏具体内容
                    masked_line = re.sub(r'[a-zA-Z0-9_-]{10,}', '***', line.strip())
                    findings.append({
                        "file": str(filepath),
                        "line": line_num,
                        "type": pattern_name,
                        "preview": masked_line[:100]
                    })
        
        return findings
        
    except Exception as e:
        logger.warning(f"扫描文件失败 {filepath}: {e}")
        return []

def scan_directory(directory, extensions):
    """扫描目录中的所有文件"""
    all_findings = []
    scanned_count = 0
    
    try:
        for ext in extensions:
            for filepath in directory.rglob(f"*{ext}"):
                # 跳过日志目录
                if "logs" in str(filepath) or "archive" in str(filepath):
                    continue
                
                findings = scan_file_for_sensitive_info(filepath)
                if findings:
                    all_findings.extend(findings)
                scanned_count += 1
                
                # 每扫描100个文件输出一次进度
                if scanned_count % 100 == 0:
                    logger.info(f"  已扫描 {scanned_count} 个文件...")
        
        return all_findings, scanned_count
        
    except Exception as e:
        logger.error(f"扫描目录失败 {directory}: {e}")
        return all_findings, scanned_count

def check_temporary_files():
    """检查临时文件是否有过期文件"""
    temp_findings = []
    
    try:
        # 检查workspace下的临时文件
        for tmp_file in WORKSPACE.rglob("*.tmp"):
            temp_findings.append(str(tmp_file))
        
        # 检查~/.openclaw/tmp下的文件
        openclaw_tmp = Path.home() / ".openclaw" / "tmp"
        if openclaw_tmp.exists():
            for tmp_file in openclaw_tmp.iterdir():
                if tmp_file.is_file():
                    # 检查文件年龄
                    age_days = (datetime.now().timestamp() - tmp_file.stat().st_mtime) / 86400
                    if age_days > 7:  # 超过7天的临时文件
                        temp_findings.append(f"{tmp_file} (age: {age_days:.1f} days)")
        
        return temp_findings
        
    except Exception as e:
        logger.error(f"检查临时文件失败: {e}")
        return []

def verify_memory_safety():
    """验证MEMORY.md系列文件的安全性"""
    safety_status = {
        "memory_files_checked": 0,
        "issues_found": 0,
        "high_risk_files": []
    }
    
    try:
        # 检查主MEMORY.md
        memory_main = WORKSPACE / "MEMORY.md"
        if memory_main.exists():
            findings = scan_file_for_sensitive_info(memory_main)
            if findings:
                safety_status["issues_found"] += len(findings)
                safety_status["high_risk_files"].append(str(memory_main))
            safety_status["memory_files_checked"] += 1
        
        # 检查每日memory文件
        if MEMORY_DIR.exists():
            for mem_file in MEMORY_DIR.glob("*.md"):
                findings = scan_file_for_sensitive_info(mem_file)
                if findings:
                    safety_status["issues_found"] += len(findings)
                    safety_status["high_risk_files"].append(str(mem_file))
                safety_status["memory_files_checked"] += 1
        
        return safety_status
        
    except Exception as e:
        logger.error(f"验证memory安全失败: {e}")
        return safety_status

def perform_firewall_check():
    """执行信息防火墙检查"""
    logger.info("=" * 60)
    logger.info("🔒 信息防火墙检查开始")
    logger.info("=" * 60)
    
    # 1. 扫描工作空间
    logger.info("\n【步骤1】扫描工作空间敏感信息...")
    workspace_findings, scanned = scan_directory(WORKSPACE, CHECK_EXTENSIONS)
    logger.info(f"✓ 扫描完成: {scanned} 个文件")
    if workspace_findings:
        logger.warning(f"⚠ 发现 {len(workspace_findings)} 处敏感信息模式")
        for finding in workspace_findings[:5]:  # 只显示前5个
            logger.warning(f"  - {finding['file']}:{finding['line']} [{finding['type']}]")
    else:
        logger.info("✓ 未发现敏感信息泄露风险")
    
    # 2. 验证MEMORY.md安全
    logger.info("\n【步骤2】验证MEMORY.md安全性...")
    memory_safety = verify_memory_safety()
    logger.info(f"✓ 检查 {memory_safety['memory_files_checked']} 个memory文件")
    if memory_safety["issues_found"]:
        logger.warning(f"⚠ 发现 {memory_safety['issues_found']} 处潜在问题")
    else:
        logger.info("✓ MEMORY.md系列文件安全")
    
    # 3. 检查临时文件
    logger.info("\n【步骤3】检查临时文件...")
    temp_files = check_temporary_files()
    if temp_files:
        logger.warning(f"⚠ 发现 {len(temp_files)} 个临时文件/过期文件")
        for tf in temp_files[:3]:
            logger.warning(f"  - {tf}")
    else:
        logger.info("✓ 临时文件状态正常")
    
    # 4. 生成检查报告
    logger.info("\n" + "=" * 60)
    logger.info("🔒 信息防火墙检查完成")
    logger.info("=" * 60)
    
    total_issues = len(workspace_findings) + memory_safety["issues_found"]
    
    if total_issues == 0:
        logger.info("✅ 检查结果: 安全 (未发现敏感信息泄露风险)")
    elif total_issues < 5:
        logger.warning("⚠️ 检查结果: 低风险 (发现少量敏感模式，建议复查)")
    else:
        logger.error("🚨 检查结果: 高风险 (发现多处敏感信息，需要立即处理)")
    
    logger.info(f"  - 扫描文件: {scanned} 个")
    logger.info(f"  - 敏感模式: {len(workspace_findings)} 处")
    logger.info(f"  - Memory问题: {memory_safety['issues_found']} 处")
    logger.info(f"  - 临时文件: {len(temp_files)} 个")
    logger.info("=" * 60)
    
    return {
        "workspace_findings": workspace_findings,
        "memory_safety": memory_safety,
        "temp_files": temp_files,
        "total_issues": total_issues
    }

def main():
    """主函数"""
    try:
        set_timeout(180)  # 3分钟超时
        result = perform_firewall_check()
        clear_timeout()
        
        # 根据问题数量返回状态码
        if result["total_issues"] == 0:
            sys.exit(0)
        elif result["total_issues"] < 5:
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
