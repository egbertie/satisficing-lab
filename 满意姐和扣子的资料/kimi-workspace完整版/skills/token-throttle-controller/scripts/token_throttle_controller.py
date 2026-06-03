#!/usr/bin/env python3
"""
token-throttle-controller - Token节流控制器
真正实现版本

功能:
- Token使用速率限制
- 动态节流调整
- 使用配额管理
- 超限预警
- 自动恢复机制

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import threading


class ThrottleLevel(Enum):
    """节流级别"""
    NORMAL = "normal"       # 正常
    CAUTION = "caution"     # 注意
    RESTRICTED = "restricted"  # 受限
    BLOCKED = "blocked"     # 阻塞


class ThrottleAction(Enum):
    """节流动作"""
    ALLOW = "allow"         # 允许
    DELAY = "delay"         # 延迟
    REJECT = "reject"       # 拒绝
    QUEUE = "queue"         # 排队


@dataclass
class TokenUsage:
    """Token使用记录"""
    timestamp: float
    tokens: int
    operation: str
    source: str


@dataclass
class ThrottleDecision:
    """节流决策"""
    action: str
    delay_ms: int
    reason: str
    current_usage: int
    limit: int
    remaining: int


@dataclass
class ThrottleStats:
    """节流统计"""
    total_requests: int
    allowed_requests: int
    delayed_requests: int
    rejected_requests: int
    current_tps: float  # 每秒Token数
    avg_tps: float
    peak_tps: float
    throttle_events: int


class TokenThrottleController:
    """Token节流控制器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化"""
        self.config = config or {}
        
        # 配置参数
        self.tps_limit = self.config.get('tps_limit', 100)  # 每秒Token限制
        self.burst_limit = self.config.get('burst_limit', 200)  # 突发限制
        self.window_size = self.config.get('window_size', 60)  # 窗口大小(秒)
        
        # 节流阈值
        self.caution_threshold = self.config.get('caution_threshold', 0.7)
        self.restricted_threshold = self.config.get('restricted_threshold', 0.9)
        self.blocked_threshold = self.config.get('blocked_threshold', 1.0)
        
        # 状态
        self.usage_history: List[TokenUsage] = []
        self.lock = threading.Lock()
        self.stats = ThrottleStats(
            total_requests=0,
            allowed_requests=0,
            delayed_requests=0,
            rejected_requests=0,
            current_tps=0.0,
            avg_tps=0.0,
            peak_tps=0.0,
            throttle_events=0
        )
        
        # 清理线程
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """启动清理线程"""
        def cleanup():
            while True:
                time.sleep(10)  # 每10秒清理一次
                self._cleanup_old_usage()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_old_usage(self):
        """清理过期使用记录"""
        cutoff = time.time() - self.window_size
        with self.lock:
            self.usage_history = [u for u in self.usage_history if u.timestamp > cutoff]
    
    def check_and_throttle(self, requested_tokens: int, operation: str = "",
                          source: str = "") -> ThrottleDecision:
        """检查并节流"""
        with self.lock:
            self.stats.total_requests += 1
            
            # 计算当前使用率
            current_usage = self._get_current_usage()
            usage_ratio = current_usage / self.tps_limit if self.tps_limit > 0 else 0
            
            # 更新统计
            self._update_stats()
            
            # 决策逻辑
            if usage_ratio >= self.blocked_threshold:
                # 超过100%，拒绝
                self.stats.rejected_requests += 1
                self.stats.throttle_events += 1
                return ThrottleDecision(
                    action=ThrottleAction.REJECT.value,
                    delay_ms=0,
                    reason=f"Token使用率超限 ({usage_ratio:.1%})",
                    current_usage=current_usage,
                    limit=self.tps_limit,
                    remaining=0
                )
            
            elif usage_ratio >= self.restricted_threshold:
                # 90%以上，延迟处理
                delay_ms = self._calculate_delay(usage_ratio)
                self.stats.delayed_requests += 1
                self.stats.throttle_events += 1
                
                # 记录使用
                self._record_usage(requested_tokens, operation, source)
                
                return ThrottleDecision(
                    action=ThrottleAction.DELAY.value,
                    delay_ms=delay_ms,
                    reason=f"Token使用率过高 ({usage_ratio:.1%})",
                    current_usage=current_usage,
                    limit=self.tps_limit,
                    remaining=self.tps_limit - current_usage
                )
            
            elif usage_ratio >= self.caution_threshold:
                # 70%以上，允许但警告
                self.stats.allowed_requests += 1
                
                # 记录使用
                self._record_usage(requested_tokens, operation, source)
                
                return ThrottleDecision(
                    action=ThrottleAction.ALLOW.value,
                    delay_ms=0,
                    reason=f"Token使用率接近限制 ({usage_ratio:.1%})",
                    current_usage=current_usage,
                    limit=self.tps_limit,
                    remaining=self.tps_limit - current_usage
                )
            
            else:
                # 正常范围，直接允许
                self.stats.allowed_requests += 1
                
                # 记录使用
                self._record_usage(requested_tokens, operation, source)
                
                return ThrottleDecision(
                    action=ThrottleAction.ALLOW.value,
                    delay_ms=0,
                    reason="Token使用正常",
                    current_usage=current_usage,
                    limit=self.tps_limit,
                    remaining=self.tps_limit - current_usage
                )
    
    def _get_current_usage(self) -> int:
        """获取当前Token使用量"""
        cutoff = time.time() - 1  # 最近1秒
        recent_usage = [u.tokens for u in self.usage_history if u.timestamp > cutoff]
        return sum(recent_usage)
    
    def _get_window_usage(self) -> int:
        """获取窗口期内Token使用量"""
        cutoff = time.time() - self.window_size
        window_usage = [u.tokens for u in self.usage_history if u.timestamp > cutoff]
        return sum(window_usage)
    
    def _record_usage(self, tokens: int, operation: str, source: str):
        """记录Token使用"""
        usage = TokenUsage(
            timestamp=time.time(),
            tokens=tokens,
            operation=operation,
            source=source
        )
        self.usage_history.append(usage)
    
    def _update_stats(self):
        """更新统计信息"""
        # 当前TPS
        self.stats.current_tps = self._get_current_usage()
        
        # 平均TPS
        if self.usage_history:
            total_tokens = sum(u.tokens for u in self.usage_history)
            time_span = time.time() - min(u.timestamp for u in self.usage_history)
            if time_span > 0:
                self.stats.avg_tps = total_tokens / time_span
        
        # 峰值TPS
        if self.stats.current_tps > self.stats.peak_tps:
            self.stats.peak_tps = self.stats.current_tps
    
    def _calculate_delay(self, usage_ratio: float) -> int:
        """计算延迟时间"""
        # 使用率越高，延迟越长
        base_delay = 100  # 基础延迟100ms
        multiplier = (usage_ratio - self.restricted_threshold) * 10
        return int(base_delay * (1 + multiplier))
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        current_usage = self._get_current_usage()
        window_usage = self._get_window_usage()
        usage_ratio = current_usage / self.tps_limit if self.tps_limit > 0 else 0
        
        # 确定节流级别
        if usage_ratio >= self.blocked_threshold:
            level = ThrottleLevel.BLOCKED.value
        elif usage_ratio >= self.restricted_threshold:
            level = ThrottleLevel.RESTRICTED.value
        elif usage_ratio >= self.caution_threshold:
            level = ThrottleLevel.CAUTION.value
        else:
            level = ThrottleLevel.NORMAL.value
        
        return {
            'level': level,
            'current_tps': current_usage,
            'window_total': window_usage,
            'limit': self.tps_limit,
            'usage_ratio': usage_ratio,
            'remaining': max(0, self.tps_limit - current_usage),
            'stats': {
                'total_requests': self.stats.total_requests,
                'allowed': self.stats.allowed_requests,
                'delayed': self.stats.delayed_requests,
                'rejected': self.stats.rejected_requests,
                'throttle_events': self.stats.throttle_events
            }
        }
    
    def adjust_limit(self, new_limit: int):
        """调整限制"""
        self.tps_limit = max(1, new_limit)
    
    def reset_stats(self):
        """重置统计"""
        with self.lock:
            self.stats = ThrottleStats(
                total_requests=0,
                allowed_requests=0,
                delayed_requests=0,
                rejected_requests=0,
                current_tps=0.0,
                avg_tps=0.0,
                peak_tps=0.0,
                throttle_events=0
            )
            self.usage_history = []
    
    def export_stats(self, format: str = "json") -> str:
        """导出统计"""
        status = self.get_status()
        
        if format == "json":
            return json.dumps(status, ensure_ascii=False, indent=2)
        elif format == "markdown":
            return self._format_markdown(status)
        return ""
    
    def _format_markdown(self, status: Dict) -> str:
        """格式化为Markdown"""
        level_icons = {
            ThrottleLevel.NORMAL.value: "🟢",
            ThrottleLevel.CAUTION.value: "🟡",
            ThrottleLevel.RESTRICTED.value: "🟠",
            ThrottleLevel.BLOCKED.value: "🔴"
        }
        
        icon = level_icons.get(status['level'], '⚪')
        
        lines = [
            "# Token节流控制器状态",
            "",
            f"**状态等级**: {icon} {status['level'].upper()}",
            f"**当前TPS**: {status['current_tps']:.1f}",
            f"**窗口总量**: {status['window_total']}",
            f"**限制**: {status['limit']}",
            f"**使用率**: {status['usage_ratio']:.1%}",
            f"**剩余**: {status['remaining']}",
            "",
            "---",
            "",
            "## 📊 请求统计",
            "",
            f"- **总请求**: {status['stats']['total_requests']}",
            f"- **已允许**: {status['stats']['allowed']}",
            f"- **已延迟**: {status['stats']['delayed']}",
            f"- **已拒绝**: {status['stats']['rejected']}",
            f"- **节流事件**: {status['stats']['throttle_events']}",
            ""
        ]
        
        return '\n'.join(lines)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Token Throttle Controller - Token节流控制器')
    parser.add_argument('--check', '-c', type=int, metavar='TOKENS',
                       help='检查Token使用')
    parser.add_argument('--operation', '-o', default='default',
                       help='操作名称')
    parser.add_argument('--limit', '-l', type=int,
                       help='设置TPS限制')
    parser.add_argument('--status', '-s', action='store_true',
                       help='查看状态')
    parser.add_argument('--reset', action='store_true',
                       help='重置统计')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='输出格式')
    
    args = parser.parse_args()
    
    try:
        controller = TokenThrottleController()
        
        if args.limit:
            controller.adjust_limit(args.limit)
            print(f"✅ TPS限制已设置为: {args.limit}")
        
        if args.reset:
            controller.reset_stats()
            print("✅ 统计已重置")
        
        if args.check:
            decision = controller.check_and_throttle(args.check, args.operation)
            
            if decision.action == ThrottleAction.ALLOW.value:
                print(f"✅ 允许 - {decision.reason}")
                print(f"   当前: {decision.current_usage}/{decision.limit}")
            elif decision.action == ThrottleAction.DELAY.value:
                print(f"⏱️  延迟 {decision.delay_ms}ms - {decision.reason}")
                print(f"   当前: {decision.current_usage}/{decision.limit}")
            else:
                print(f"❌ 拒绝 - {decision.reason}")
                print(f"   当前: {decision.current_usage}/{decision.limit}")
        
        if args.status or (not args.check and not args.limit and not args.reset):
            # 显示状态
            status = controller.get_status()
            output = controller.export_stats(args.format)
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
