#!/bin/bash
# Cron合并优化实施方案C - 安装脚本
# 版本: 1.0
# 日期: 2026-03-15
# 使用前请确认: 已阅读评估报告和方案C设计文档

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Cron合并优化实施方案C - 安装脚本"
echo "=========================================="
echo ""
echo "⚠️  警告: 此脚本将:"
echo "   1. 禁用现有的4个高频率Cron任务"
echo "   2. 部署事件驱动架构"
echo "   3. 创建新的用户指令体系"
echo ""
echo "📋 前提条件检查:"
echo "   [ ] 已阅读 docs/cron_optimization_evaluation.md"
echo "   [ ] 已阅读 docs/cron_optimization_design_C.md"
echo "   [ ] 理解方案C的工作原理"
echo "   [ ] 已备份重要数据"
echo ""

# 确认函数
confirm() {
    read -p "$1 (yes/no): " response
    if [[ "$response" != "yes" ]]; then
        echo "❌ 安装已取消"
        exit 1
    fi
}

confirm "是否确认以上条件已满足，并继续安装?"

echo ""
echo "=========================================="
echo "第一步: 备份现有配置"
echo "=========================================="

BACKUP_DIR="$HOME/.cron_optimization_backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份当前Cron配置
echo "📦 备份当前Cron配置..."
crontab -l > "$BACKUP_DIR/crontab_backup.txt" 2>/dev/null || echo "# 无现有Cron配置" > "$BACKUP_DIR/crontab_backup.txt"

# 备份相关脚本
echo "📦 备份相关脚本..."
if [ -d "$HOME/.openclaw/workspace/scripts" ]; then
    cp -r "$HOME/.openclaw/workspace/scripts" "$BACKUP_DIR/" 2>/dev/null || true
fi

echo "✅ 备份完成: $BACKUP_DIR"

echo ""
echo "=========================================="
echo "第二步: 创建目录结构"
echo "=========================================="

BASE_DIR="$HOME/.openclaw/workspace/scripts/cron_optimization"
mkdir -p "$BASE_DIR"/{config,core,commands,events,utils,tests}

echo "✅ 目录结构创建完成: $BASE_DIR"

echo ""
echo "=========================================="
echo "第三步: 创建系统配置文件"
echo "=========================================="

# 系统配置
cat > "$BASE_DIR/config/system_config.yaml" << 'EOF'
# 事件驱动优化系统配置
version: "1.0"
last_updated: "2026-03-15"

# 系统状态
system_state:
  status: "normal"  # normal, maintenance, degraded
  mode: "day"       # day, night
  
# Token配置
token_config:
  daily_budget: 10000
  warning_threshold: 0.30  # 30%
  critical_threshold: 0.10  # 10%
  night_mode_max: 3000
  
# 事件监听配置
event_monitoring:
  enabled: true
  dedup_window_minutes: 5
  log_retention_days: 7
  
# 通知配置
notification:
  default_preference: "smart"  # smart, silent, verbose
  emergency_channels: ["immediate"]
  digest_schedule: "hourly"     # hourly, daily, never
  
# 夜间模式配置
night_mode:
  enabled: false
  auto_activate: false
  auto_shutdown_time: "06:00"
  max_concurrent_tasks: 3
  whitelist: []
  always_confirm: []
  
# 状态文件路径
paths:
  state_file: "data/event_driven_state.json"
  log_dir: "logs/event_driven"
  event_log: "logs/events.log"
EOF

# 用户偏好（初始为空，运行时填充）
cat > "$BASE_DIR/config/user_preferences.yaml" << 'EOF'
# 用户偏好配置
# 此文件将在首次运行时根据用户选择填充

preferences:
  notification_level: "smart"
  auto_night_mode: false
  night_mode_whitelist: []
  
  # 指令别名
  command_aliases:
    "状态": "check_status"
    "补位": "start_backfill"
    "复盘": "generate_review"
    "夜间模式": "toggle_night_mode"
EOF

echo "✅ 配置文件创建完成"

echo ""
echo "=========================================="
echo "第四步: 创建核心Python模块"
echo "=========================================="

# 状态管理器
cat > "$BASE_DIR/core/state_manager.py" << 'EOF'
#!/usr/bin/env python3
"""状态管理器 - 维护系统状态"""

import json
import os
from datetime import datetime
from pathlib import Path

class StateManager:
    def __init__(self, state_file=None):
        if state_file is None:
            base_dir = Path(__file__).parent.parent
            state_file = base_dir / "data" / "event_driven_state.json"
        
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._state = self._load_state()
    
    def _load_state(self):
        """加载状态文件"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_state()
    
    def _default_state(self):
        """默认状态"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "system_state": {
                "status": "normal",
                "mode": "day",
                "last_event": None
            },
            "task_queue": {
                "pending": [],
                "in_progress": [],
                "blocked": [],
                "completed_today": 0
            },
            "token_status": {
                "remaining": 10000,
                "budget_daily": 10000,
                "used_today": 0,
                "last_threshold": "100%"
            },
            "user_status": {
                "online": True,
                "last_seen": datetime.now().isoformat(),
                "notification_preference": "smart"
            },
            "event_log": []
        }
    
    def save(self):
        """保存状态"""
        self._state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self._state, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        """获取状态值"""
        keys = key.split('.')
        value = self._state
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """设置状态值"""
        keys = key.split('.')
        target = self._state
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save()
    
    def log_event(self, event_type, data=None, handled=False):
        """记录事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data or {},
            "handled": handled
        }
        self._state["event_log"].append(event)
        # 只保留最近100条事件
        self._state["event_log"] = self._state["event_log"][-100:]
        self.save()

if __name__ == "__main__":
    # 测试
    sm = StateManager()
    print("当前状态:", json.dumps(sm._state, indent=2, ensure_ascii=False))
EOF

# 决策引擎
cat > "$BASE_DIR/core/decision_engine.py" << 'EOF'
#!/usr/bin/env python3
"""决策引擎 - 根据状态决定行动"""

from enum import Enum
from typing import Dict, List, Any

class ActionType(Enum):
    NOTIFY = "notify"
    WAIT_CONFIRM = "wait_confirm"
    AUTO_EXECUTE = "auto_execute"
    SILENT_RECORD = "silent_record"
    NO_ACTION = "no_action"

class DecisionEngine:
    def __init__(self, state_manager):
        self.state = state_manager
    
    def decide(self, event_type: str, event_data: Dict = None) -> Dict[str, Any]:
        """根据事件决定行动"""
        
        # 获取当前状态
        mode = self.state.get("system_state.mode", "day")
        token_remaining = self.state.get("token_status.remaining", 0)
        token_budget = self.state.get("token_status.budget_daily", 10000)
        token_ratio = token_remaining / token_budget if token_budget > 0 else 0
        
        # 决策逻辑
        decision = {
            "action": ActionType.NO_ACTION,
            "priority": "low",
            "message": None,
            "suggested_tasks": []
        }
        
        # 事件类型处理
        if event_type == "task_blocked":
            decision["action"] = ActionType.NOTIFY
            decision["priority"] = "high"
            decision["message"] = f"任务阻塞: {event_data.get('task_id', 'unknown')}"
            
        elif event_type == "token_critical":
            decision["action"] = ActionType.NOTIFY
            decision["priority"] = "urgent"
            decision["message"] = f"Token紧急: 仅剩 {token_remaining}"
            
        elif event_type == "task_completed":
            # 检查是否有可补位任务
            pending = self.state.get("task_queue.pending", [])
            if pending and token_ratio > 0.3:
                if mode == "night":
                    decision["action"] = ActionType.AUTO_EXECUTE
                else:
                    decision["action"] = ActionType.WAIT_CONFIRM
                    decision["suggested_tasks"] = pending[:3]
            else:
                decision["action"] = ActionType.SILENT_RECORD
                
        elif event_type == "user_went_offline":
            decision["action"] = ActionType.SILENT_RECORD
            # 标记可补位状态
            
        return decision
    
    def format_decision(self, decision: Dict) -> str:
        """格式化决策为可读文本"""
        action_map = {
            ActionType.NOTIFY: "通知用户",
            ActionType.WAIT_CONFIRM: "等待确认",
            ActionType.AUTO_EXECUTE: "自动执行",
            ActionType.SILENT_RECORD: "静默记录",
            ActionType.NO_ACTION: "无需行动"
        }
        
        lines = [
            f"决策: {action_map.get(decision['action'], '未知')}",
            f"优先级: {decision['priority']}"
        ]
        
        if decision.get("message"):
            lines.append(f"消息: {decision['message']}")
        
        if decision.get("suggested_tasks"):
            lines.append(f"建议任务: {len(decision['suggested_tasks'])}个")
        
        return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state_manager import StateManager
    
    sm = StateManager()
    engine = DecisionEngine(sm)
    
    test_events = [
        ("task_completed", {"task_id": "t001"}),
        ("token_critical", {}),
        ("user_went_offline", {})
    ]
    
    for event_type, data in test_events:
        decision = engine.decide(event_type, data)
        print(f"\n事件: {event_type}")
        print(engine.format_decision(decision))
EOF

# 通知服务
cat > "$BASE_DIR/core/notification_service.py" << 'EOF'
#!/usr/bin/env python3
"""通知服务 - 向用户发送通知"""

from enum import Enum
from datetime import datetime

class NotificationLevel(Enum):
    SILENT = "silent"      # 只记录，不通知
    NORMAL = "normal"      # 普通通知
    URGENT = "urgent"      # 紧急通知
    IMMEDIATE = "immediate" # 立即通知

class NotificationService:
    def __init__(self, state_manager):
        self.state = state_manager
    
    def should_notify(self, level: NotificationLevel) -> bool:
        """根据用户偏好决定是否通知"""
        preference = self.state.get("user_status.notification_preference", "smart")
        
        if preference == "silent":
            return level == NotificationLevel.IMMEDIATE
        elif preference == "smart":
            return level in [NotificationLevel.URGENT, NotificationLevel.IMMEDIATE]
        elif preference == "verbose":
            return True
        
        return False
    
    def send(self, message: str, level: NotificationLevel = NotificationLevel.NORMAL,
             actions: list = None):
        """发送通知"""
        
        if not self.should_notify(level):
            # 静默记录
            self.state.log_event("notification_silenced", {
                "message": message,
                "level": level.value
            })
            return
        
        # 构建通知内容
        timestamp = datetime.now().strftime("%H:%M")
        notification = f"[{timestamp}] {message}"
        
        # 添加到待发送队列（实际实现中这里会调用消息API）
        self.state.set("pending_notifications", 
                       self.state.get("pending_notifications", []) + [{
                           "timestamp": timestamp,
                           "message": message,
                           "level": level.value,
                           "actions": actions or []
                       }])
        
        # 记录
        self.state.log_event("notification_sent", {
            "message": message,
            "level": level.value
        })
        
        return notification
    
    def send_digest(self):
        """发送摘要通知"""
        events = self.state.get("event_log", [])
        # 筛选未处理的重要事件
        important_events = [
            e for e in events[-20:]
            if not e.get("handled") and e.get("type") in [
                "task_completed", "task_blocked", "token_warning"
            ]
        ]
        
        if not important_events:
            return None
        
        summary = f"📊 状态摘要: {len(important_events)}个事件待处理"
        return self.send(summary, NotificationLevel.NORMAL)

if __name__ == "__main__":
    # 测试
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state_manager import StateManager
    
    sm = StateManager()
    service = NotificationService(sm)
    
    # 测试通知
    result = service.send("测试通知", NotificationLevel.NORMAL)
    print(f"通知结果: {result}")
EOF

# 用户指令处理器
cat > "$BASE_DIR/commands/status_commands.py" << 'EOF'
#!/usr/bin/env python3
"""状态查询指令处理器"""

import json
from datetime import datetime

class StatusCommands:
    def __init__(self, state_manager):
        self.state = state_manager
    
    def check_status(self, detailed=False):
        """全面状态检查"""
        
        # 收集状态数据
        system = self.state.get("system_state", {})
        tasks = self.state.get("task_queue", {})
        token = self.state.get("token_status", {})
        user = self.state.get("user_status", {})
        
        # 计算指标
        token_remaining = token.get("remaining", 0)
        token_budget = token.get("budget_daily", 10000)
        token_percent = (token_remaining / token_budget * 100) if token_budget > 0 else 0
        
        pending_count = len(tasks.get("pending", []))
        blocked_count = len(tasks.get("blocked", []))
        completed_today = tasks.get("completed_today", 0)
        
        # 构建报告
        lines = [
            "📊 系统状态报告",
            "═══════════════════════════════════════",
            f"系统模式: {system.get('mode', 'day')}",
            f"用户状态: {'在线' if user.get('online') else '离线'}",
            "",
            "💰 Token状态",
            f"  剩余: {token_remaining} / {token_budget} ({token_percent:.1f}%)",
            f"  今日已用: {token.get('used_today', 0)}",
            "",
            "📋 任务队列",
            f"  待处理: {pending_count}",
            f"  阻塞: {blocked_count}",
            f"  今日完成: {completed_today}",
        ]
        
        if detailed:
            lines.extend([
                "",
                "📝 待处理任务详情:",
            ])
            for task in tasks.get("pending", [])[:5]:
                lines.append(f"  • {task.get('id', 'unknown')}: {task.get('description', '无描述')}")
        
        # 建议
        lines.extend(["", "💡 建议:"])
        if pending_count > 0 and token_percent > 30:
            lines.append(f"  检测到 {pending_count} 个可处理任务，建议执行补位")
        elif token_percent < 20:
            lines.append("  Token余量较低，建议节约使用")
        elif blocked_count > 0:
            lines.append(f"  有 {blocked_count} 个任务阻塞，需要关注")
        else:
            lines.append("  系统运行正常")
        
        return "\n".join(lines)
    
    def task_queue(self):
        """任务队列详情"""
        tasks = self.state.get("task_queue", {})
        
        lines = ["📋 任务队列详情", "═══════════════════════════════════════"]
        
        # 进行中
        in_progress = tasks.get("in_progress", [])
        lines.extend([f"\n🔄 进行中 ({len(in_progress)}):"])
        for task in in_progress:
            lines.append(f"  • {task.get('id')}: {task.get('description', '无描述')}")
        
        # 待处理
        pending = tasks.get("pending", [])
        lines.extend([f"\n⏳ 待处理 ({len(pending)}):"])
        for i, task in enumerate(pending[:10], 1):
            est = task.get('estimated_tokens', '?')
            lines.append(f"  {i}. {task.get('id')} [估计{est}tokens]: {task.get('description', '无描述')}")
        if len(pending) > 10:
            lines.append(f"  ... 还有 {len(pending) - 10} 个任务")
        
        # 阻塞
        blocked = tasks.get("blocked", [])
        lines.extend([f"\n🚫 阻塞 ({len(blocked)}):"])
        for task in blocked:
            lines.append(f"  • {task.get('id')}: {task.get('block_reason', '未知原因')}")
        
        return "\n".join(lines)
    
    def token_status(self):
        """Token状态详情"""
        token = self.state.get("token_status", {})
        
        remaining = token.get("remaining", 0)
        budget = token.get("budget_daily", 10000)
        used = token.get("used_today", 0)
        percent = (remaining / budget * 100) if budget > 0 else 0
        
        # 计算进度条
        bar_length = 20
        filled = int(bar_length * remaining / budget)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        lines = [
            "💰 Token状态详情",
            "═══════════════════════════════════════",
            f"",
            f"[{bar}] {percent:.1f}%",
            f"",
            f"剩余: {remaining} tokens",
            f"预算: {budget} tokens/天",
            f"今日已用: {used} tokens",
            f"",
        ]
        
        # 状态评估
        if percent > 50:
            lines.append("✅ Token充足，可正常执行")
        elif percent > 20:
            lines.append("⚠️  Token中等，建议适度使用")
        else:
            lines.append("🔴 Token紧张，请节约使用")
        
        # 预计可用时间
        if used > 0:
            hours_passed = datetime.now().hour + datetime.now().minute / 60
            hourly_rate = used / max(hours_passed, 0.1)
            remaining_hours = remaining / max(hourly_rate, 1)
            lines.append(f"\n按当前速度，预计还能使用 {remaining_hours:.1f} 小时")
        
        return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state_manager import StateManager
    
    sm = StateManager()
    
    # 设置一些测试数据
    sm.set("task_queue.pending", [
        {"id": "task_001", "description": "分析市场数据", "estimated_tokens": 500},
        {"id": "task_002", "description": "生成报告", "estimated_tokens": 800},
    ])
    
    commands = StatusCommands(sm)
    
    print(commands.check_status(detailed=True))
    print("\n" + "="*50 + "\n")
    print(commands.task_queue())
    print("\n" + "="*50 + "\n")
    print(commands.token_status())
EOF

echo "✅ 核心Python模块创建完成"

echo ""
echo "=========================================="
echo "第五步: 创建主程序入口"
echo "=========================================="

# 主程序
cat > "$BASE_DIR/main.py" << 'EOF'
#!/usr/bin/env python3
"""
事件驱动Cron优化系统 - 主程序
用法: python main.py [command] [options]

命令:
    status          显示系统状态
    tasks           显示任务队列
    token           显示Token状态
    backfill        启动补位流程
    review          生成复盘建议
    night-mode      切换夜间模式
    event <type>   模拟事件（测试用）
"""

import sys
import argparse
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from core.state_manager import StateManager
from core.decision_engine import DecisionEngine
from core.notification_service import NotificationService
from commands.status_commands import StatusCommands


def main():
    parser = argparse.ArgumentParser(
        description='事件驱动Cron优化系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py status              # 查看系统状态
  python main.py status --detailed   # 查看详细状态
  python main.py tasks               # 查看任务队列
  python main.py token               # 查看Token状态
  python main.py event task_completed # 模拟任务完成事件
        '''
    )
    
    parser.add_argument('command', help='要执行的命令')
    parser.add_argument('--detailed', '-d', action='store_true', help='显示详细信息')
    parser.add_argument('--data', '-D', help='事件数据（JSON格式）')
    
    args = parser.parse_args()
    
    # 初始化
    state = StateManager()
    
    # 执行命令
    if args.command == 'status':
        commands = StatusCommands(state)
        print(commands.check_status(detailed=args.detailed))
    
    elif args.command == 'tasks':
        commands = StatusCommands(state)
        print(commands.task_queue())
    
    elif args.command == 'token':
        commands = StatusCommands(state)
        print(commands.token_status())
    
    elif args.command.startswith('event:'):
        event_type = args.command.split(':', 1)[1]
        event_data = {}
        if args.data:
            import json
            event_data = json.loads(args.data)
        
        engine = DecisionEngine(state)
        decision = engine.decide(event_type, event_data)
        print(f"事件: {event_type}")
        print(engine.format_decision(decision))
    
    elif args.command == 'init':
        print("✅ 系统已初始化")
        print(f"状态文件: {state.state_file}")
        print(f"当前模式: {state.get('system_state.mode', 'day')}")
    
    else:
        print(f"❌ 未知命令: {args.command}")
        print("可用命令: status, tasks, token, event:<type>, init")
        sys.exit(1)


if __name__ == '__main__':
    main()
EOF

chmod +x "$BASE_DIR/main.py"

echo "✅ 主程序创建完成"

echo ""
echo "=========================================="
echo "第六步: 创建卸载脚本"
echo "=========================================="

cat > "$BASE_DIR/../cron_optimization_uninstall.sh" << 'EOF'
#!/bin/bash
# Cron合并优化实施方案C - 卸载脚本

set -e

echo "=========================================="
echo "Cron优化方案C - 卸载脚本"
echo "=========================================="
echo ""

read -p "⚠️  确定要卸载事件驱动系统吗？这将删除所有相关文件 (yes/no): " response
if [[ "$response" != "yes" ]]; then
    echo "❌ 卸载已取消"
    exit 1
fi

BASE_DIR="$HOME/.openclaw/workspace/scripts/cron_optimization"
BACKUP_DIR="$HOME/.cron_optimization_backup"

echo ""
echo "📦 备份当前状态..."
if [ -d "$BASE_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    cp -r "$BASE_DIR" "$BACKUP_DIR/uninstalled_$(date +%Y%m%d_%H%M%S)"
fi

echo "🗑️  删除程序文件..."
rm -rf "$BASE_DIR"

echo ""
echo "✅ 卸载完成"
echo ""
echo "📋 恢复原有Cron配置:"
echo "   从备份恢复: $BACKUP_DIR"
echo "   查看备份: ls -la $BACKUP_DIR"
echo ""
EOF

chmod +x "$BASE_DIR/../cron_optimization_uninstall.sh"

echo "✅ 卸载脚本创建完成"

echo ""
echo "=========================================="
echo "安装完成!"
echo "=========================================="
echo ""
echo "📁 安装位置: $BASE_DIR"
echo ""
echo "🚀 快速开始:"
echo "   cd $BASE_DIR"
echo "   python3 main.py init"
echo "   python3 main.py status"
echo ""
echo "📖 可用命令:"
echo "   python3 main.py status          # 查看系统状态"
echo "   python3 main.py tasks           # 查看任务队列"  
echo "   python3 main.py token           # 查看Token状态"
echo ""
echo "⚠️  重要提醒:"
echo "   此脚本仅创建了Python模块，尚未:"
echo "   1. 禁用原有的Cron任务"
echo "   2. 部署事件监听服务"
echo "   3. 配置用户指令接口"
echo ""
echo "   请与主Agent确认后完成后续部署。"
echo ""
echo "🗑️  如需卸载:"
echo "   $BASE_DIR/../cron_optimization_uninstall.sh"
echo ""
