#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晨间图腾仪式脚本 (Morning Ritual)
执行时间: 每日 07:00
功能:
1. 读取并确认SOUL.md核心身份
2. 检查系统基础状态
3. 读取今日MEMORY.md准备
4. 输出晨间仪式报告
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ============ 配置区域 ============
WORKSPACE = Path("/root/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs" / "cron-tasks"
MEMORY_DIR = WORKSPACE / "memory"
SOUL_FILE = WORKSPACE / "SOUL.md"
USER_FILE = WORKSPACE / "USER.md"
# ===================================

# 设置日志
os.makedirs(LOG_DIR, exist_ok=True)
log_file = LOG_DIR / f"morning-ritual-{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('morning-ritual')

# 超时保护装饰器
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Script execution timeout")

def set_timeout(seconds=300):
    """设置脚本执行超时（默认5分钟）"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

def clear_timeout():
    """清除超时设置"""
    signal.alarm(0)

# 核心功能函数
def check_file_exists(filepath, name):
    """检查文件是否存在"""
    if filepath.exists():
        logger.info(f"✓ {name} 存在: {filepath}")
        return True
    else:
        logger.error(f"✗ {name} 不存在: {filepath}")
        return False

def read_soul_identity():
    """读取SOUL.md核心身份"""
    try:
        if not SOUL_FILE.exists():
            return None
        content = SOUL_FILE.read_text(encoding='utf-8')
        # 提取关键部分
        identity_start = content.find("## 我是谁（根本身份")
        if identity_start == -1:
            return content[:500]  # 返回前500字符
        return content[identity_start:identity_start+800]
    except Exception as e:
        logger.error(f"读取SOUL.md失败: {e}")
        return None

def get_today_memory_file():
    """获取今日memory文件路径"""
    today = datetime.now().strftime('%Y-%m-%d')
    return MEMORY_DIR / f"{today}.md"

def check_system_health():
    """检查系统基础健康状态"""
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # 检查核心文件
    health_status["checks"]["soul_md"] = check_file_exists(SOUL_FILE, "SOUL.md")
    health_status["checks"]["user_md"] = check_file_exists(USER_FILE, "USER.md")
    health_status["checks"]["agents_md"] = check_file_exists(WORKSPACE / "AGENTS.md", "AGENTS.md")
    
    # 检查目录
    health_status["checks"]["memory_dir"] = MEMORY_DIR.exists()
    health_status["checks"]["logs_dir"] = LOG_DIR.exists()
    
    # 检查磁盘空间
    try:
        import shutil
        stat = shutil.disk_usage(WORKSPACE)
        free_gb = stat.free / (1024**3)
        health_status["checks"]["disk_space_gb"] = round(free_gb, 2)
        health_status["checks"]["disk_space_ok"] = free_gb > 1.0  # 至少1GB空闲
        logger.info(f"磁盘空闲空间: {free_gb:.2f} GB")
    except Exception as e:
        logger.warning(f"无法检查磁盘空间: {e}")
        health_status["checks"]["disk_space_ok"] = True  # 假设OK
    
    return health_status

def create_today_memory():
    """创建今日memory文件（如不存在）"""
    today_file = get_today_memory_file()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today_file.exists():
        logger.info(f"今日memory文件已存在: {today_file}")
        return False
    
    # 创建今日memory文件
    template = f"""# {today} - 记忆日志

## 晨间仪式
- 执行时间: {datetime.now().strftime('%H:%M')}
- 状态: 准备就绪

## 今日核心目标
- [ ] 

## 关键决策
<!-- 记录重要决定 -->

## 执行记录
<!-- 记录执行过程 -->

## 问题与反思
<!-- 记录遇到的问题 -->

## 晚间总结
<!-- 黄昏仪式时填写 -->
"""
    
    try:
        os.makedirs(today_file.parent, exist_ok=True)
        today_file.write_text(template, encoding='utf-8')
        logger.info(f"✓ 创建今日memory文件: {today_file}")
        return True
    except Exception as e:
        logger.error(f"创建memory文件失败: {e}")
        return False

def perform_ritual():
    """执行晨间仪式"""
    logger.info("=" * 60)
    logger.info("🌅 晨间图腾仪式开始")
    logger.info("=" * 60)
    
    # 1. 确认身份
    logger.info("\n【步骤1】确认核心身份...")
    identity = read_soul_identity()
    if identity:
        logger.info("✓ 身份确认: 负熵构造体的初级实现体")
    else:
        logger.warning("⚠ 无法读取SOUL.md，但继续执行")
    
    # 2. 系统健康检查
    logger.info("\n【步骤2】系统健康检查...")
    health = check_system_health()
    all_ok = all(v for k, v in health["checks"].items() if isinstance(v, bool))
    if all_ok:
        logger.info("✓ 系统健康状态: 良好")
    else:
        logger.warning("⚠ 系统存在警告，请检查日志")
    
    # 3. 创建今日memory
    logger.info("\n【步骤3】准备今日记忆文件...")
    created = create_today_memory()
    if created:
        logger.info("✓ 已创建今日记忆文件")
    else:
        logger.info("= 今日记忆文件已存在，继续沿用")
    
    # 4. 读取USER.md了解今日安排
    logger.info("\n【步骤4】了解用户今日安排...")
    if USER_FILE.exists():
        content = USER_FILE.read_text(encoding='utf-8')
        # 提取关键信息
        if "核心工作时段" in content:
            logger.info("✓ 已加载用户工作偏好")
    
    # 5. 输出仪式完成报告
    logger.info("\n" + "=" * 60)
    logger.info("🌅 晨间图腾仪式完成")
    logger.info("=" * 60)
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"状态: {'就绪' if all_ok else '需关注'}")
    logger.info(f"今日文件: {get_today_memory_file().name}")
    logger.info("=" * 60)
    
    return health

def main():
    """主函数"""
    try:
        # 设置5分钟超时
        set_timeout(300)
        
        result = perform_ritual()
        
        clear_timeout()
        
        # 返回状态码
        sys.exit(0 if all(v for k, v in result["checks"].items() if isinstance(v, bool)) else 1)
        
    except TimeoutError:
        logger.error("⏱ 脚本执行超时（超过5分钟）")
        sys.exit(2)
    except Exception as e:
        logger.error(f"💥 脚本执行异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(3)

if __name__ == "__main__":
    main()
