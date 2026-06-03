#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄昏图腾归位脚本 (Evening Ritual)
执行时间: 每日 22:00
功能:
1. 汇总今日执行记录
2. 归档过期日志（保留30天）
3. 检查今日任务完成情况
4. 生成黄昏总结报告
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
ARCHIVE_DIR = WORKSPACE / "logs" / "archive"
SOUL_FILE = WORKSPACE / "SOUL.md"
USER_FILE = WORKSPACE / "USER.md"
KEEP_LOG_DAYS = 30  # 日志保留天数
# ===================================

# 设置日志
os.makedirs(LOG_DIR, exist_ok=True)
log_file = LOG_DIR / f"evening-ritual-{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('evening-ritual')

# 超时保护
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Script execution timeout")

def set_timeout(seconds=300):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

def clear_timeout():
    signal.alarm(0)

def get_today_memory_file():
    """获取今日memory文件路径"""
    today = datetime.now().strftime('%Y-%m-%d')
    return MEMORY_DIR / f"{today}.md"

def archive_old_logs():
    """归档超过保留期的日志文件"""
    archived_count = 0
    cutoff_date = datetime.now() - timedelta(days=KEEP_LOG_DAYS)
    
    try:
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
        # 查找所有旧日志文件
        for log_file in LOG_DIR.glob("*.log"):
            try:
                # 从文件名提取日期
                file_stat = log_file.stat()
                file_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                if file_time < cutoff_date:
                    # 移动到归档目录
                    archive_path = ARCHIVE_DIR / log_file.name
                    shutil.move(str(log_file), str(archive_path))
                    archived_count += 1
                    logger.info(f"已归档: {log_file.name}")
            except Exception as e:
                logger.warning(f"归档文件失败 {log_file.name}: {e}")
        
        logger.info(f"✓ 归档完成: {archived_count} 个文件")
        return archived_count
        
    except Exception as e:
        logger.error(f"归档过程出错: {e}")
        return 0

def update_today_memory_summary():
    """更新今日memory的晚间总结部分"""
    today_file = get_today_memory_file()
    
    if not today_file.exists():
        logger.warning("今日memory文件不存在")
        return False
    
    try:
        content = today_file.read_text(encoding='utf-8')
        
        # 检查是否已有晚间总结
        if "晚间总结完成" in content:
            logger.info("今日memory已包含晚间总结")
            return True
        
        # 添加晚间总结标记
        summary = f"""

### 晚间总结完成
- 归档时间: {datetime.now().strftime('%H:%M')}
- 日志归档: 已完成
- 状态: 今日归档

"""
        
        # 在文件末尾添加
        updated_content = content + summary
        today_file.write_text(updated_content, encoding='utf-8')
        
        logger.info("✓ 已更新今日memory晚间总结")
        return True
        
    except Exception as e:
        logger.error(f"更新memory文件失败: {e}")
        return False

def summarize_today_logs():
    """汇总今日所有日志"""
    today_str = datetime.now().strftime('%Y%m%d')
    log_summary = []
    
    try:
        for log_file in LOG_DIR.glob(f"*-{today_str}.log"):
            try:
                content = log_file.read_text(encoding='utf-8')
                lines = content.strip().split('\n')
                error_count = sum(1 for line in lines if '[ERROR]' in line)
                warning_count = sum(1 for line in lines if '[WARNING]' in line)
                
                log_summary.append({
                    "file": log_file.name,
                    "lines": len(lines),
                    "errors": error_count,
                    "warnings": warning_count
                })
            except Exception as e:
                logger.warning(f"读取日志失败 {log_file.name}: {e}")
        
        return log_summary
        
    except Exception as e:
        logger.error(f"汇总日志失败: {e}")
        return []

def check_today_completions():
    """检查今日任务完成情况"""
    today_file = get_today_memory_file()
    completions = {
        "memory_exists": today_file.exists(),
        "has_core_goals": False,
        "completed_items": 0,
        "total_items": 0
    }
    
    if today_file.exists():
        try:
            content = today_file.read_text(encoding='utf-8')
            # 统计完成的checkbox
            completions["completed_items"] = content.count("- [x]")
            completions["total_items"] = content.count("- [x]") + content.count("- [ ]")
            completions["has_core_goals"] = "## 今日核心目标" in content
        except Exception as e:
            logger.warning(f"读取memory统计失败: {e}")
    
    return completions

def perform_evening_ritual():
    """执行黄昏归位仪式"""
    logger.info("=" * 60)
    logger.info("🌆 黄昏图腾归位仪式开始")
    logger.info("=" * 60)
    
    # 1. 归档旧日志
    logger.info("\n【步骤1】归档旧日志...")
    archived = archive_old_logs()
    
    # 2. 汇总今日日志
    logger.info("\n【步骤2】汇总今日执行记录...")
    log_summary = summarize_today_logs()
    if log_summary:
        total_errors = sum(l["errors"] for l in log_summary)
        total_warnings = sum(l["warnings"] for l in log_summary)
        logger.info(f"✓ 今日日志: {len(log_summary)} 个文件")
        logger.info(f"  - 错误: {total_errors} 条")
        logger.info(f"  - 警告: {total_warnings} 条")
    else:
        logger.info("= 今日暂无其他日志")
    
    # 3. 检查任务完成
    logger.info("\n【步骤3】检查今日任务完成度...")
    completions = check_today_completions()
    if completions["memory_exists"]:
        logger.info(f"✓ 今日memory存在")
        if completions["total_items"] > 0:
            rate = completions["completed_items"] / completions["total_items"] * 100
            logger.info(f"  - 任务完成: {completions['completed_items']}/{completions['total_items']} ({rate:.0f}%)")
        else:
            logger.info("  - 今日未设置任务清单")
    else:
        logger.warning("⚠ 今日memory文件不存在")
    
    # 4. 更新memory晚间总结
    logger.info("\n【步骤4】更新晚间总结...")
    updated = update_today_memory_summary()
    if updated:
        logger.info("✓ 已更新晚间总结")
    
    # 5. 输出仪式完成报告
    logger.info("\n" + "=" * 60)
    logger.info("🌆 黄昏图腾归位仪式完成")
    logger.info("=" * 60)
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"归档文件: {archived} 个")
    logger.info(f"日志汇总: {len(log_summary)} 个文件")
    logger.info(f"今日任务: {completions.get('completed_items', 0)}/{completions.get('total_items', 0)} 完成")
    logger.info("=" * 60)
    
    return {
        "archived": archived,
        "log_summary": log_summary,
        "completions": completions
    }

def main():
    """主函数"""
    try:
        set_timeout(300)  # 5分钟超时
        result = perform_evening_ritual()
        clear_timeout()
        sys.exit(0)
    except TimeoutError:
        logger.error("⏱ 脚本执行超时")
        sys.exit(2)
    except Exception as e:
        logger.error(f"💥 脚本执行异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(3)

if __name__ == "__main__":
    main()
