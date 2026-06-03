#!/usr/bin/env python3
"""
上下文大小监控脚本

功能：
- 监控当前对话上下文大小
- 超过阈值自动提醒
- 建议压缩时机

阈值规则：
- 黄色预警（30KB）：建议压缩
- 红色预警（50KB）：强制压缩
- 对话轮数 >100：建议新开会话
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# ============ 配置 ============

# 阈值配置（字节）
YELLOW_THRESHOLD = int(os.getenv("CONTEXT_YELLOW_THRESHOLD", 30720))  # 30KB
RED_THRESHOLD = int(os.getenv("CONTEXT_RED_THRESHOLD", 51200))        # 50KB
MAX_THRESHOLD = int(os.getenv("CONTEXT_MAX_THRESHOLD", 65536))        # 64KB

# 对话轮数限制
CONVERSATION_SOFT_LIMIT = int(os.getenv("CONVERSATION_SOFT_LIMIT", 50))
CONVERSATION_HARD_LIMIT = int(os.getenv("CONVERSATION_HARD_LIMIT", 100))

# 工具调用限制
TOOL_CALL_LIMIT_PER_TURN = int(os.getenv("TOOL_CALL_LIMIT_PER_TURN", 5))

# 状态文件路径
STATUS_FILE = Path("/tmp/context_monitor_status.json")
LOG_FILE = Path("/tmp/context_monitor.log")

# ============ 颜色输出 ============

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def color_text(text: str, color: str) -> str:
    """为文本添加颜色"""
    color_code = getattr(Colors, color.upper(), Colors.RESET)
    return f"{color_code}{text}{Colors.RESET}"

# ============ 核心功能 ============

def estimate_context_size() -> dict:
    """
    估算当前对话上下文大小
    
    通过检查环境变量和系统状态来估算
    """
    context_info = {
        "timestamp": datetime.now().isoformat(),
        "estimated_size_bytes": 0,
        "estimated_size_kb": 0,
        "turn_count": 0,
        "tool_calls_this_turn": 0,
        "status": "unknown",
        "recommendation": ""
    }
    
    # 尝试从环境变量获取信息
    if "OPENCLAW_CONTEXT_SIZE" in os.environ:
        try:
            context_info["estimated_size_bytes"] = int(os.environ["OPENCLAW_CONTEXT_SIZE"])
        except ValueError:
            pass
    
    # 检查对话轮数
    if "OPENCLAW_TURN_COUNT" in os.environ:
        try:
            context_info["turn_count"] = int(os.environ["OPENCLAW_TURN_COUNT"])
        except ValueError:
            pass
    
    # 检查当前轮工具调用数
    if "OPENCLAW_TOOL_CALLS_THIS_TURN" in os.environ:
        try:
            context_info["tool_calls_this_turn"] = int(os.environ["OPENCLAW_TOOL_CALLS_THIS_TURN"])
        except ValueError:
            pass
    
    # 如果没有环境变量，使用启发式估算
    if context_info["estimated_size_bytes"] == 0:
        # 基于历史日志估算（如果有）
        context_info["estimated_size_bytes"] = heuristic_estimate()
    
    context_info["estimated_size_kb"] = round(context_info["estimated_size_bytes"] / 1024, 2)
    
    # 确定状态和推荐操作
    context_info["status"], context_info["recommendation"] = determine_status(context_info)
    
    return context_info

def heuristic_estimate() -> int:
    """
    启发式估算上下文大小
    
    基于常见的对话模式进行估算
    """
    base_size = 5120  # 基础系统提示词 ~5KB
    
    # 检查是否有内存文件记录
    memory_dir = Path("/root/.openclaw/workspace/memory")
    if memory_dir.exists():
        # 估算最近的记忆文件大小
        recent_files = sorted(memory_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        if recent_files:
            # 每个记忆文件约贡献上下文
            for f in recent_files[:5]:  # 最近5个文件
                size = f.stat().st_size
                base_size += min(size, 2048)  # 每个文件最多算2KB
    
    # 检查 AGENTS.md 等上下文文件
    context_files = [
        "/root/.openclaw/workspace/AGENTS.md",
        "/root/.openclaw/workspace/SOUL.md",
        "/root/.openclaw/workspace/USER.md",
        "/root/.openclaw/workspace/MEMORY.md"
    ]
    for file_path in context_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            base_size += min(size, 5120)  # 每个上下文文件最多算5KB
    
    return base_size

def determine_status(context_info: dict) -> tuple:
    """
    根据上下文信息确定状态和推荐操作
    
    Returns:
        tuple: (status, recommendation)
    """
    size = context_info["estimated_size_bytes"]
    turns = context_info["turn_count"]
    tool_calls = context_info["tool_calls_this_turn"]
    
    warnings = []
    
    # 检查上下文大小
    if size >= RED_THRESHOLD:
        warnings.append(f"🔴 红色预警：上下文 {size/1024:.1f}KB 超过 {RED_THRESHOLD/1024:.0f}KB")
    elif size >= YELLOW_THRESHOLD:
        warnings.append(f"🟡 黄色预警：上下文 {size/1024:.1f}KB 超过 {YELLOW_THRESHOLD/1024:.0f}KB")
    
    # 检查对话轮数
    if turns >= CONVERSATION_HARD_LIMIT:
        warnings.append(f"🔴 对话轮数 {turns} 超过 {CONVERSATION_HARD_LIMIT}，建议新开会话")
    elif turns >= CONVERSATION_SOFT_LIMIT:
        warnings.append(f"🟡 对话轮数 {turns}，关注上下文增长")
    
    # 检查工具调用
    if tool_calls > TOOL_CALL_LIMIT_PER_TURN:
        warnings.append(f"🔴 单轮工具调用 {tool_calls} 超过限制 {TOOL_CALL_LIMIT_PER_TURN}")
    elif tool_calls >= TOOL_CALL_LIMIT_PER_TURN - 1:
        warnings.append(f"🟡 单轮工具调用较多 ({tool_calls})，建议优化")
    
    # 确定状态
    if any("🔴" in w for w in warnings):
        status = "danger"
    elif any("🟡" in w for w in warnings):
        status = "warning"
    else:
        status = "ok"
    
    # 生成推荐操作
    if status == "danger":
        recommendation = "\n".join([
            "⚠️  立即执行以下操作：",
            "1. 暂停非必要操作",
            "2. 执行上下文压缩：/compress 或总结关键信息",
            "3. 考虑重置会话：/reset",
            "4. 如需继续，请分批次处理任务"
        ])
    elif status == "warning":
        recommendation = "\n".join([
            "💡 建议操作：",
            "1. 关注上下文增长趋势",
            "2. 适时总结已完成的工作",
            "3. 单轮工具调用控制在 3-4 个以内",
            "4. 考虑在合适时机新开会话"
        ])
    else:
        recommendation = "✅ 当前状态正常，继续保持"
    
    return status, "\n".join(warnings) + "\n\n" + recommendation if warnings else recommendation

def save_status(context_info: dict):
    """保存状态到文件"""
    try:
        # 读取历史状态
        history = []
        if STATUS_FILE.exists():
            with open(STATUS_FILE, 'r') as f:
                data = json.load(f)
                history = data.get("history", [])
        
        # 添加当前状态
        history.append({
            "timestamp": context_info["timestamp"],
            "size_kb": context_info["estimated_size_kb"],
            "status": context_info["status"]
        })
        
        # 只保留最近 100 条记录
        history = history[-100:]
        
        # 保存
        with open(STATUS_FILE, 'w') as f:
            json.dump({
                "current": context_info,
                "history": history
            }, f, indent=2)
    except Exception as e:
        print(f"警告：无法保存状态文件: {e}", file=sys.stderr)

def log_event(message: str):
    """记录日志"""
    try:
        with open(LOG_FILE, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

def print_report(context_info: dict):
    """打印监控报告"""
    size_kb = context_info["estimated_size_kb"]
    status = context_info["status"]
    
    # 选择颜色
    if status == "ok":
        size_color = "green"
        status_text = color_text("✅ 正常", "green")
    elif status == "warning":
        size_color = "yellow"
        status_text = color_text("⚠️  警告", "yellow")
    else:
        size_color = "red"
        status_text = color_text("🚨 危险", "red")
    
    # 打印报告
    print()
    print(color_text("=" * 60, "cyan"))
    print(color_text("          上下文大小监控报告", "bold"))
    print(color_text("=" * 60, "cyan"))
    print()
    
    print(f"📊 当前状态: {status_text}")
    print()
    
    print(f"📏 上下文大小: {color_text(f'{size_kb:.2f} KB', size_color)}")
    print(f"   - 黄色阈值: {YELLOW_THRESHOLD/1024:.0f} KB")
    print(f"   - 红色阈值: {RED_THRESHOLD/1024:.0f} KB")
    print()
    
    if context_info["turn_count"] > 0:
        turn_color = "red" if context_info["turn_count"] >= CONVERSATION_HARD_LIMIT else \
                     "yellow" if context_info["turn_count"] >= CONVERSATION_SOFT_LIMIT else "green"
        print(f"💬 对话轮数: {color_text(str(context_info['turn_count']), turn_color)}")
        print(f"   - 软限制: {CONVERSATION_SOFT_LIMIT}")
        print(f"   - 硬限制: {CONVERSATION_HARD_LIMIT}")
        print()
    
    if context_info["tool_calls_this_turn"] > 0:
        tool_color = "red" if context_info["tool_calls_this_turn"] > TOOL_CALL_LIMIT_PER_TURN else \
                     "yellow" if context_info["tool_calls_this_turn"] >= TOOL_CALL_LIMIT_PER_TURN - 1 else "green"
        print(f"🔧 本轮工具调用: {color_text(str(context_info['tool_calls_this_turn']), tool_color)}")
        print(f"   - 限制: {TOOL_CALL_LIMIT_PER_TURN}")
        print()
    
    print(color_text("-" * 60, "cyan"))
    print(color_text("📋 建议操作:", "bold"))
    print()
    print(context_info["recommendation"])
    print()
    
    print(color_text("-" * 60, "cyan"))
    print(f"🕐 检查时间: {context_info['timestamp']}")
    print(color_text("=" * 60, "cyan"))
    print()

def check_context_threshold() -> dict:
    """
    主检查函数
    
    Returns:
        dict: 包含状态信息的字典
    """
    context_info = estimate_context_size()
    save_status(context_info)
    
    if context_info["status"] != "ok":
        log_event(f"Status: {context_info['status']}, Size: {context_info['estimated_size_kb']:.2f}KB")
    
    return context_info

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OpenClaw 上下文大小监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 运行监控检查
  %(prog)s --quiet            # 静默模式，只返回状态码
  %(prog)s --json             # 输出 JSON 格式
  %(prog)s --threshold 40     # 自定义阈值（KB）
        """
    )
    
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    parser.add_argument("--json", "-j", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--threshold", "-t", type=int, help="自定义黄色阈值（KB）")
    
    args = parser.parse_args()
    
    # 应用自定义阈值
    global YELLOW_THRESHOLD, RED_THRESHOLD
    if args.threshold:
        YELLOW_THRESHOLD = args.threshold * 1024
        RED_THRESHOLD = YELLOW_THRESHOLD * 1.67  # 红色阈值约为黄色的 1.67 倍
    
    # 执行检查
    context_info = check_context_threshold()
    
    # 输出结果
    if args.json:
        print(json.dumps(context_info, indent=2, ensure_ascii=False))
    elif not args.quiet:
        print_report(context_info)
    
    # 返回状态码
    if context_info["status"] == "danger":
        sys.exit(2)
    elif context_info["status"] == "warning":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
