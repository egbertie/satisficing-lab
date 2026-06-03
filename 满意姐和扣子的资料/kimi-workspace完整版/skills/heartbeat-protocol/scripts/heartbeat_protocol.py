#!/usr/bin/env python3
"""
Heartbeat Protocol V3.0 - 主控脚本
实现L1-L5五级Token档位管理系统

核心功能:
- Token档位自动计算与管理
- 动态通知频率调整
- 档位切换自检
- 对抗测试
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# 配置路径
SKILL_DIR = Path("/root/.openclaw/workspace/skills/heartbeat-protocol")
LOG_DIR = SKILL_DIR / "logs"
REPORT_DIR = SKILL_DIR / "reports"
CONFIG_DIR = SKILL_DIR / "config"

# 确保目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


class GearLevel(Enum):
    """档位枚举"""
    L1 = "L1"  # <15%: 休眠模式
    L2 = "L2"  # 15-30%: 重度节流
    L3 = "L3"  # 30-50%: 中度节流
    L4 = "L4"  # 50-70%: 轻度节流
    L5 = "L5"  # 70-100%: 正常运营


@dataclass
class GearConfig:
    """档位配置"""
    min_pct: float
    max_pct: float
    notification_frequency: float  # 百分比
    heartbeat_interval_min: int
    max_parallel_tasks: int
    log_level: str


@dataclass
class TokenStatus:
    """Token状态"""
    percentage: float
    consumed: int
    remaining: int
    trend: str  # increasing/decreasing/stable
    trend_rate: float  # %/hour


@dataclass
class GearState:
    """档位状态"""
    current: GearLevel
    previous: Optional[GearLevel]
    changed: bool
    changed_at: Optional[str]


class GearCalculator:
    """档位计算器"""
    
    # 档位边界定义
    BOUNDARIES = {
        GearLevel.L5: (70.0, 100.0),
        GearLevel.L4: (50.0, 70.0),
        GearLevel.L3: (30.0, 50.0),
        GearLevel.L2: (15.0, 30.0),
        GearLevel.L1: (0.0, 15.0),
    }
    
    # 档位配置
    GEAR_CONFIG = {
        GearLevel.L5: GearConfig(
            min_pct=70.0, max_pct=100.0,
            notification_frequency=1.0,
            heartbeat_interval_min=30,
            max_parallel_tasks=5,
            log_level="INFO"
        ),
        GearLevel.L4: GearConfig(
            min_pct=50.0, max_pct=70.0,
            notification_frequency=0.8,
            heartbeat_interval_min=45,
            max_parallel_tasks=4,
            log_level="INFO"
        ),
        GearLevel.L3: GearConfig(
            min_pct=30.0, max_pct=50.0,
            notification_frequency=0.5,
            heartbeat_interval_min=60,
            max_parallel_tasks=3,
            log_level="WARN"
        ),
        GearLevel.L2: GearConfig(
            min_pct=15.0, max_pct=30.0,
            notification_frequency=0.2,
            heartbeat_interval_min=120,
            max_parallel_tasks=2,
            log_level="WARN"
        ),
        GearLevel.L1: GearConfig(
            min_pct=0.0, max_pct=15.0,
            notification_frequency=0.0,
            heartbeat_interval_min=0,
            max_parallel_tasks=1,
            log_level="ERROR"
        ),
    }
    
    def __init__(self, hysteresis: float = 5.0):
        self.hysteresis = hysteresis
        self.last_gear: Optional[GearLevel] = None
        
    def calculate_gear(self, token_pct: float) -> GearLevel:
        """
        计算当前档位（含滞后处理）
        
        Args:
            token_pct: 当前Token百分比
            
        Returns:
            GearLevel: 计算后的档位
        """
        # 边界保护
        token_pct = max(0.0, min(100.0, token_pct))
        
        # 确定新档位
        new_gear = None
        for gear, (low, high) in self.BOUNDARIES.items():
            if low <= token_pct <= high:
                new_gear = gear
                break
        
        if new_gear is None:
            new_gear = GearLevel.L1 if token_pct < 15 else GearLevel.L5
        
        # 滞后处理：避免边界抖动
        if self.last_gear and new_gear != self.last_gear:
            last_low, last_high = self.BOUNDARIES[self.last_gear]
            
            # 检查是否在滞后区间内
            near_lower = abs(token_pct - last_low) < self.hysteresis
            near_upper = abs(token_pct - last_high) < self.hysteresis
            
            if near_lower or near_upper:
                return self.last_gear
        
        self.last_gear = new_gear
        return new_gear
    
    def get_config(self, gear: GearLevel) -> GearConfig:
        """获取档位配置"""
        return self.GEAR_CONFIG[gear]
    
    def get_gear_range(self, gear: GearLevel) -> Tuple[float, float]:
        """获取档位范围"""
        return self.BOUNDARIES[gear]


class NotificationManager:
    """通知管理器"""
    
    NOTIFICATION_HISTORY_FILE = LOG_DIR / "notification_history.json"
    
    def __init__(self):
        self.history: List[Dict] = []
        self._load_history()
    
    def _load_history(self):
        """加载通知历史"""
        if self.NOTIFICATION_HISTORY_FILE.exists():
            with open(self.NOTIFICATION_HISTORY_FILE, 'r') as f:
                self.history = json.load(f)
    
    def _save_history(self):
        """保存通知历史"""
        # 只保留最近100条
        self.history = self.history[-100:]
        with open(self.NOTIFICATION_HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def record_notification(self, notification_type: str, gear_from: str, 
                           gear_to: str, message: str, channel: str = "system"):
        """记录通知"""
        notification = {
            "timestamp": datetime.now().isoformat(),
            "type": notification_type,
            "gear_from": gear_from,
            "gear_to": gear_to,
            "message": message,
            "channel": channel,
            "read": False
        }
        self.history.append(notification)
        self._save_history()
    
    def get_recent_notifications(self, limit: int = 10) -> List[Dict]:
        """获取最近通知"""
        return self.history[-limit:]
    
    def should_notify(self, gear: GearLevel, notification_type: str) -> bool:
        """判断是否应该发送通知"""
        calculator = GearCalculator()
        config = calculator.get_config(gear)
        
        # L1档位：完全静默
        if gear == GearLevel.L1:
            return notification_type == "critical"
        
        # 根据频率概率决定是否通知
        import random
        return random.random() < config.notification_frequency


class SelfValidator:
    """自检验证器"""
    
    def __init__(self, calculator: GearCalculator):
        self.calculator = calculator
        self.validation_results: List[Dict] = []
    
    def validate_gear_change(self, old_gear: GearLevel, new_gear: GearLevel, 
                            token_pct: float) -> Dict:
        """
        档位切换前自检
        
        Returns:
            验证结果字典
        """
        checks = {
            'token_calculation': self._verify_token_calculation(token_pct),
            'boundary_correctness': self._check_boundary_correctness(new_gear, token_pct),
            'anti_jitter': self._check_recent_changes(),
            'time_appropriateness': self._check_time_context(),
            'resource_availability': self._check_resources()
        }
        
        all_passed = all(checks.values())
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "old_gear": old_gear.value,
            "new_gear": new_gear.value,
            "token_pct": token_pct,
            "checks": checks,
            "all_passed": all_passed
        }
        
        self.validation_results.append(result)
        return result
    
    def _verify_token_calculation(self, token_pct: float) -> bool:
        """验证Token计算"""
        return 0.0 <= token_pct <= 100.0
    
    def _check_boundary_correctness(self, gear: GearLevel, token_pct: float) -> bool:
        """检查档位边界正确性"""
        low, high = self.calculator.get_gear_range(gear)
        return low <= token_pct <= high
    
    def _check_recent_changes(self) -> bool:
        """检查近期切换频率（防抖动）"""
        # 检查24小时内切换次数
        recent_changes = [
            r for r in self.validation_results
            if datetime.fromisoformat(r["timestamp"]) > datetime.now() - timedelta(hours=24)
        ]
        return len(recent_changes) < 3  # 24小时内少于3次
    
    def _check_time_context(self) -> bool:
        """检查时间上下文"""
        hour = datetime.now().hour
        # 深夜时段(23-8)限制档位切换
        if 23 <= hour or hour < 8:
            return False  # 深夜时段需要额外确认
        return True
    
    def _check_resources(self) -> bool:
        """检查资源可用性"""
        # 检查磁盘空间
        try:
            stat = os.statvfs('/')
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            return free_gb > 1.0  # 至少1GB可用空间
        except:
            return True  # 无法检查时默认通过
    
    def generate_validation_report(self) -> str:
        """生成验证报告"""
        if not self.validation_results:
            return "暂无验证记录"
        
        latest = self.validation_results[-1]
        
        report_lines = [
            "🔍 档位切换自检报告",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"切换时间: {latest['timestamp']}",
            f"档位变化: {latest['old_gear']} → {latest['new_gear']}",
            f"Token百分比: {latest['token_pct']:.1f}%",
            "",
            "验证项:"
        ]
        
        for check_name, passed in latest['checks'].items():
            status = "✅" if passed else "❌"
            report_lines.append(f"  {status} {check_name}")
        
        report_lines.extend([
            "",
            f"自检结果: {'全部通过 ✅' if latest['all_passed'] else '存在失败项 ❌'}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ])
        
        return "\n".join(report_lines)


class AdversarialTester:
    """对抗测试器"""
    
    TEST_SCENARIOS = [
        {'id': 'T01', 'name': '正常消耗', 'start': 100, 'rate': -10, 'hours': 12},
        {'id': 'T02', 'name': '快速消耗', 'start': 100, 'rate': -30, 'hours': 4},
        {'id': 'T03', 'name': '极速消耗', 'start': 80, 'rate': -50, 'hours': 2},
        {'id': 'T04', 'name': '边界抖动', 'start': 70, 'rate': -2, 'hours': 10, 'fluctuation': True},
        {'id': 'T05', 'name': '耗尽恢复', 'start': 5, 'rate': 20, 'hours': 6},
        {'id': 'T06', 'name': '完全耗尽', 'start': 20, 'rate': -25, 'hours': 2},
        {'id': 'T07', 'name': '异常负值', 'start': -5, 'rate': 0, 'hours': 1},
        {'id': 'T08', 'name': '超出100%', 'start': 105, 'rate': 0, 'hours': 1},
    ]
    
    def __init__(self, calculator: GearCalculator):
        self.calculator = calculator
        self.test_results: List[Dict] = []
    
    def run_all_tests(self) -> List[Dict]:
        """运行所有对抗测试"""
        self.test_results = []
        
        for scenario in self.TEST_SCENARIOS:
            result = self._run_scenario(scenario)
            self.test_results.append(result)
        
        return self.test_results
    
    def _run_scenario(self, scenario: Dict) -> Dict:
        """运行单个测试场景"""
        calculator = GearCalculator()
        transitions = []
        current_gear = None
        token = scenario['start']
        
        for hour in range(scenario['hours']):
            # 如果有波动，添加随机抖动
            if scenario.get('fluctuation'):
                import random
                token += scenario['rate'] + random.uniform(-3, 3)
            else:
                token += scenario['rate']
            
            # 边界保护
            token = max(0.0, min(100.0, token))
            
            new_gear = calculator.calculate_gear(token)
            
            if new_gear != current_gear:
                transitions.append({
                    'hour': hour,
                    'from': current_gear.value if current_gear else None,
                    'to': new_gear.value,
                    'token': round(token, 1)
                })
                current_gear = new_gear
            
            if token <= 0 and scenario['rate'] < 0:
                break
        
        # 验证结果
        passed = self._verify_scenario(scenario, transitions, current_gear, token)
        
        return {
            'id': scenario['id'],
            'name': scenario['name'],
            'scenario': scenario,
            'transitions': transitions,
            'final_gear': current_gear.value if current_gear else None,
            'final_token': round(token, 1),
            'passed': passed
        }
    
    def _verify_scenario(self, scenario: Dict, transitions: List[Dict], 
                        final_gear, final_token: float) -> bool:
        """验证场景结果"""
        scenario_id = scenario['id']
        
        # 将枚举转换为字符串值进行比较
        gear_value = final_gear.value if final_gear else None
        
        if scenario_id == 'T01':
            # 正常消耗: 应该逐级降级 (100->90->80->70->60->50->40->30->20->10->0)
            # 预期经过L5,L4,L3,L2,L1，至少3次切换
            return len(transitions) >= 3 and gear_value == 'L1'
        elif scenario_id == 'T02':
            # 快速消耗: 可能跳级 (100->70->40->10)
            # 预期至少2次切换，最终到L1
            return len(transitions) >= 2 and gear_value == 'L1'
        elif scenario_id == 'T03':
            # 极速消耗: 80%开始，-50%/h，2小时后到0%
            # 80->30->0，应该经过L2到L1
            return gear_value == 'L1'
        elif scenario_id == 'T04':
            # 边界抖动: 应该保持稳定（滞后机制生效）
            # 在70%附近波动，由于滞后机制，应该保持在一个档位
            return len(transitions) <= 3
        elif scenario_id == 'T05':
            # 耗尽恢复: 5%开始，+20%/h，6小时后到105%(限制100%)
            # 5->25->45->65->85->100，应该逐级恢复
            # 最终应该在L5或L4
            return gear_value in ['L4', 'L5']
        elif scenario_id == 'T06':
            # 完全耗尽: 20%开始，-25%/h，2小时后到0%
            # 20->0，应该到L1或低于0被限制到L1
            return gear_value == 'L1' or final_token <= 0
        elif scenario_id == 'T07':
            # 异常负值: -5%应该被边界保护处理为0%，档位L1
            return gear_value == 'L1' and final_token == 0.0
        elif scenario_id == 'T08':
            # 超出100%: 105%应该被边界保护处理为100%，档位L5
            return gear_value == 'L5' and final_token == 100.0
        
        return True
    
    def generate_test_report(self) -> str:
        """生成测试报告"""
        if not self.test_results:
            return "请先运行测试"
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        report_lines = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "🛡️ Token耗尽对抗测试报告",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"测试时间: {datetime.now().isoformat()}",
            f"测试场景: {total}个",
            f"通过: {passed}/{total}",
            f"失败: {total - passed}/{total}",
            "",
            "详细结果:"
        ]
        
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            report_lines.append(
                f"{status} {result['id']} {result['name']} - "
                f"切换{len(result['transitions'])}次 → {result['final_gear']}"
            )
        
        report_lines.extend([
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"结论: {'所有测试通过 ✅' if passed == total else '部分测试失败 ❌'}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ])
        
        return "\n".join(report_lines)


class HeartbeatProtocol:
    """Heartbeat Protocol主控类"""
    
    STATE_FILE = LOG_DIR / "gear_state.json"
    TRANSITION_LOG = LOG_DIR / "gear_transitions.log"
    
    def __init__(self):
        self.calculator = GearCalculator()
        self.notification_manager = NotificationManager()
        self.validator = SelfValidator(self.calculator)
        self.adversarial_tester = AdversarialTester(self.calculator)
        self.logger = self._setup_logging()
        
        self.current_state: Optional[GearState] = None
        self.token_status: Optional[TokenStatus] = None
        
        self._load_state()
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("heartbeat_protocol")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(LOG_DIR / "heartbeat_protocol.log")
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(handler)
        
        return logger
    
    def _load_state(self):
        """加载状态"""
        if self.STATE_FILE.exists():
            with open(self.STATE_FILE, 'r') as f:
                data = json.load(f)
                self.current_state = GearState(
                    current=GearLevel(data['current']),
                    previous=GearLevel(data['previous']) if data.get('previous') else None,
                    changed=data.get('changed', False),
                    changed_at=data.get('changed_at')
                )
    
    def _save_state(self):
        """保存状态"""
        if self.current_state:
            data = {
                'current': self.current_state.current.value,
                'previous': self.current_state.previous.value if self.current_state.previous else None,
                'changed': self.current_state.changed,
                'changed_at': self.current_state.changed_at
            }
            with open(self.STATE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
    
    def _log_transition(self, old_gear: GearLevel, new_gear: GearLevel, token_pct: float):
        """记录档位切换"""
        with open(self.TRANSITION_LOG, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | {old_gear.value} → {new_gear.value} | Token: {token_pct:.1f}%\n")
    
    def check_gear(self, token_pct: float, consumed: int = 0, remaining: int = 10000) -> Dict:
        """
        检查并调整档位
        
        Args:
            token_pct: 当前Token百分比
            consumed: 已消耗Token数
            remaining: 剩余Token数
            
        Returns:
            档位状态报告
        """
        # 计算新档位
        new_gear = self.calculator.calculate_gear(token_pct)
        
        # 初始化或获取当前档位
        if self.current_state is None:
            self.current_state = GearState(
                current=new_gear,
                previous=None,
                changed=False,
                changed_at=None
            )
            old_gear = new_gear
        else:
            old_gear = self.current_state.current
        
        # 检测档位变化
        gear_changed = new_gear != old_gear
        
        if gear_changed:
            self.logger.info(f"档位变化检测: {old_gear.value} → {new_gear.value}")
            
            # 执行自检
            validation = self.validator.validate_gear_change(old_gear, new_gear, token_pct)
            
            if validation['all_passed']:
                # 更新状态
                self.current_state = GearState(
                    current=new_gear,
                    previous=old_gear,
                    changed=True,
                    changed_at=datetime.now().isoformat()
                )
                
                # 记录切换
                self._log_transition(old_gear, new_gear, token_pct)
                
                # 发送通知
                self.notification_manager.record_notification(
                    notification_type="gear_change",
                    gear_from=old_gear.value,
                    gear_to=new_gear.value,
                    message=f"Token降至{token_pct:.1f}%，进入{new_gear.value}模式",
                    channel="system"
                )
                
                self.logger.info(f"档位切换完成: {new_gear.value}")
            else:
                self.logger.warning(f"自检未通过，维持原档位: {old_gear.value}")
                gear_changed = False
        
        # 保存状态
        self._save_state()
        
        # 构建状态报告
        config = self.calculator.get_config(new_gear)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "gear": {
                "current": new_gear.value,
                "previous": old_gear.value if old_gear != new_gear else None,
                "changed": gear_changed,
                "changed_at": self.current_state.changed_at if gear_changed else None
            },
            "token": {
                "percentage": round(token_pct, 1),
                "consumed": consumed,
                "remaining": remaining,
                "trend": "decreasing" if gear_changed and new_gear.value < old_gear.value else "stable"
            },
            "notification": {
                "frequency_pct": int(config.notification_frequency * 100),
                "heartbeat_interval_min": config.heartbeat_interval_min,
                "max_parallel_tasks": config.max_parallel_tasks,
                "log_level": config.log_level
            },
            "validation": self.validator.validation_results[-1] if self.validator.validation_results else None
        }
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        if not self.current_state:
            return {"status": "未初始化"}
        
        config = self.calculator.get_config(self.current_state.current)
        notifications = self.notification_manager.get_recent_notifications(5)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "gear": {
                "current": self.current_state.current.value,
                "previous": self.current_state.previous.value if self.current_state.previous else None,
                "changed_at": self.current_state.changed_at
            },
            "config": {
                "notification_frequency": config.notification_frequency,
                "heartbeat_interval": config.heartbeat_interval_min,
                "max_parallel_tasks": config.max_parallel_tasks
            },
            "recent_notifications": notifications
        }
    
    def get_history(self) -> List[str]:
        """获取档位历史"""
        if not self.TRANSITION_LOG.exists():
            return []
        
        with open(self.TRANSITION_LOG, 'r') as f:
            return f.readlines()[-20:]  # 最近20条
    
    def run_adversarial_tests(self) -> str:
        """运行对抗测试"""
        self.adversarial_tester.run_all_tests()
        return self.adversarial_tester.generate_test_report()


def main():
    parser = argparse.ArgumentParser(description="Heartbeat Protocol V3.0")
    parser.add_argument("command", nargs="?", default="status",
                       choices=["status", "check", "history", "test", "report"])
    parser.add_argument("--token-pct", type=float, help="当前Token百分比")
    parser.add_argument("--consumed", type=int, default=0, help="已消耗Token")
    parser.add_argument("--remaining", type=int, default=10000, help="剩余Token")
    
    args = parser.parse_args()
    
    hp = HeartbeatProtocol()
    
    if args.command == "status":
        status = hp.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.command == "check":
        if args.token_pct is None:
            print("❌ 请提供 --token-pct 参数")
            sys.exit(1)
        
        result = hp.check_gear(args.token_pct, args.consumed, args.remaining)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result['gear']['changed']:
            print(f"\n⚙️ 档位已切换: {result['gear']['previous']} → {result['gear']['current']}")
    
    elif args.command == "history":
        history = hp.get_history()
        if history:
            print("📜 档位切换历史:")
            for line in history:
                print(line.strip())
        else:
            print("暂无档位切换记录")
    
    elif args.command == "test":
        print("🧪 运行对抗测试...")
        report = hp.run_adversarial_tests()
        print(report)
    
    elif args.command == "report":
        # 生成完整报告
        print("📊 Heartbeat Protocol 状态报告")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        status = hp.get_status()
        
        if 'gear' in status and status['gear']:
            print(f"当前档位: {status['gear'].get('current', '未初始化')}")
        else:
            print("当前档位: 未初始化")
            
        if 'config' in status:
            print(f"通知频率: {status['config'].get('notification_frequency', 0)*100:.0f}%")
            print(f"心跳间隔: {status['config'].get('heartbeat_interval', 0)}分钟")
            print(f"并行任务: {status['config'].get('max_parallel_tasks', 0)}个")
        
        if hp.validator.validation_results:
            print("\n" + hp.validator.generate_validation_report())
        else:
            print("\n暂无验证记录")


if __name__ == "__main__":
    main()
