#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自我评估校准脚本 (Self-Assessment Calibrator)
执行时间: 每日 14:00 和 20:00
功能:
1. 检查SOUL.md是否被修改
2. 验证核心工作准则是否执行
3. 统计今日诚实度指标
4. 生成校准报告
"""

import os
import sys
import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ============ 配置区域 ============
WORKSPACE = Path("/root/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs" / "cron-tasks"
MEMORY_DIR = WORKSPACE / "memory"
STATE_FILE = LOG_DIR / ".calibrator_state.json"
SOUL_FILE = WORKSPACE / "SOUL.md"
AGENTS_FILE = WORKSPACE / "AGENTS.md"
USER_FILE = WORKSPACE / "USER.md"
# ===================================

# 设置日志
os.makedirs(LOG_DIR, exist_ok=True)
log_file = LOG_DIR / f"self-assessment-calibrator-{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('self-assessment')

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

def get_file_hash(filepath):
    """计算文件MD5哈希"""
    try:
        if not filepath.exists():
            return None
        content = filepath.read_bytes()
        return hashlib.md5(content).hexdigest()
    except Exception as e:
        logger.warning(f"计算文件哈希失败 {filepath}: {e}")
        return None

def load_state():
    """加载上次校准状态"""
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        logger.warning(f"加载状态失败: {e}")
    return {}

def save_state(state):
    """保存校准状态"""
    try:
        os.makedirs(STATE_FILE.parent, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')
    except Exception as e:
        logger.error(f"保存状态失败: {e}")

def check_core_files_integrity():
    """检查核心文件完整性"""
    state = load_state()
    current_hashes = {}
    changes = []
    
    core_files = {
        "soul": SOUL_FILE,
        "agents": AGENTS_FILE,
        "user": USER_FILE
    }
    
    for name, filepath in core_files.items():
        current_hash = get_file_hash(filepath)
        current_hashes[name] = current_hash
        
        if name in state.get("file_hashes", {}):
            if state["file_hashes"][name] != current_hash:
                changes.append(name)
                logger.info(f"✓ {name} 文件自上次校准后有更新")
        else:
            logger.info(f"✓ {name} 文件首次记录")
    
    # 保存新状态
    state["file_hashes"] = current_hashes
    state["last_check"] = datetime.now().isoformat()
    save_state(state)
    
    return {
        "current_hashes": current_hashes,
        "changes": changes,
        "all_exist": all(h is not None for h in current_hashes.values())
    }

def verify_core_principles():
    """验证核心工作准则"""
    principles_status = {
        "诚实准则": False,
        "Token感知": False,
        "立即执行": False,
        "五层深挖": False,
        "蓝军审计": False
    }
    
    try:
        if SOUL_FILE.exists():
            content = SOUL_FILE.read_text(encoding='utf-8')
            
            # 检查各准则是否存在
            principles_status["诚实准则"] = "诚实" in content and "实事求是" in content
            principles_status["Token感知"] = "Token感知基因" in content
            principles_status["立即执行"] = "立即执行文化" in content
            principles_status["五层深挖"] = "五层深挖" in content
            principles_status["蓝军审计"] = "蓝军审计" in content
        
        return principles_status
        
    except Exception as e:
        logger.error(f"验证核心准则失败: {e}")
        return principles_status

def analyze_today_honesty():
    """分析今日诚实度指标"""
    today_file = MEMORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    honesty_metrics = {
        "memory_exists": today_file.exists(),
        "has_reflection": False,
        "has_error_record": False,
        "has_lesson_learned": False
    }
    
    if today_file.exists():
        try:
            content = today_file.read_text(encoding='utf-8')
            
            # 检查反思
            honesty_metrics["has_reflection"] = any(kw in content for kw in 
                ["反思", "问题与反思", "为什么", "根因"])
            
            # 检查错误记录
            honesty_metrics["has_error_record"] = any(kw in content for kw in 
                ["错误", "ERR-", "mistake", "failed", "失败"])
            
            # 检查经验教训
            honesty_metrics["has_lesson_learned"] = any(kw in content for kw in 
                ["教训", "lesson", "learned", "改进", "优化"])
            
        except Exception as e:
            logger.warning(f"分析今日memory失败: {e}")
    
    return honesty_metrics

def calculate_calibration_score(integrity, principles, honesty):
    """计算校准得分"""
    score = 0
    max_score = 100
    
    # 文件完整性 (30分)
    if integrity["all_exist"]:
        score += 30
    
    # 核心准则 (40分)
    principle_score = sum(principles.values()) / len(principles) * 40
    score += principle_score
    
    # 诚实指标 (30分)
    if honesty["memory_exists"]:
        score += 10
    if honesty["has_reflection"]:
        score += 10
    if honesty["has_error_record"] or honesty["has_lesson_learned"]:
        score += 10
    
    return round(score, 1)

def perform_self_calibration():
    """执行自我校准"""
    logger.info("=" * 60)
    logger.info("⚖️ 自我评估校准开始")
    logger.info("=" * 60)
    
    # 1. 检查核心文件完整性
    logger.info("\n【步骤1】检查核心文件完整性...")
    integrity = check_core_files_integrity()
    if integrity["all_exist"]:
        logger.info("✓ 所有核心文件存在")
    else:
        logger.error("✗ 部分核心文件缺失")
    if integrity["changes"]:
        logger.info(f"✓ 自上次校准后 {len(integrity['changes'])} 个文件有更新")
    
    # 2. 验证核心工作准则
    logger.info("\n【步骤2】验证核心工作准则...")
    principles = verify_core_principles()
    for name, status in principles.items():
        if status:
            logger.info(f"✓ {name}: 已固化")
        else:
            logger.warning(f"⚠ {name}: 未检测到或未固化")
    
    # 3. 分析今日诚实度
    logger.info("\n【步骤3】分析今日诚实度指标...")
    honesty = analyze_today_honesty()
    logger.info(f"  - memory文件: {'✓ 存在' if honesty['memory_exists'] else '✗ 不存在'}")
    logger.info(f"  - 反思记录: {'✓ 有' if honesty['has_reflection'] else '⚠ 无'}")
    logger.info(f"  - 错误记录: {'✓ 有' if honesty['has_error_record'] else '⚠ 无'}")
    logger.info(f"  - 经验教训: {'✓ 有' if honesty['has_lesson_learned'] else '⚠ 无'}")
    
    # 4. 计算校准得分
    logger.info("\n【步骤4】计算校准得分...")
    score = calculate_calibration_score(integrity, principles, honesty)
    
    # 5. 输出校准报告
    logger.info("\n" + "=" * 60)
    logger.info("⚖️ 自我评估校准完成")
    logger.info("=" * 60)
    
    if score >= 90:
        logger.info(f"✅ 校准得分: {score}/100 (优秀)")
    elif score >= 70:
        logger.info(f"⚠️ 校准得分: {score}/100 (良好)")
    else:
        logger.warning(f"🚨 校准得分: {score}/100 (需要改进)")
    
    logger.info("\n详细指标:")
    logger.info(f"  文件完整性: {'✓' if integrity['all_exist'] else '✗'}")
    logger.info(f"  准则固化度: {sum(principles.values())}/{len(principles)}")
    logger.info(f"  诚实记录度: {sum([honesty['has_reflection'], honesty['has_error_record'], honesty['has_lesson_learned']])}/3")
    logger.info("=" * 60)
    
    return {
        "score": score,
        "integrity": integrity,
        "principles": principles,
        "honesty": honesty
    }

def main():
    """主函数"""
    try:
        set_timeout(120)  # 2分钟超时
        result = perform_self_calibration()
        clear_timeout()
        
        # 根据得分返回状态码
        if result["score"] >= 90:
            sys.exit(0)
        elif result["score"] >= 70:
            sys.exit(1)  # 警告
        else:
            sys.exit(2)  # 需要改进
            
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
