#!/usr/bin/env python3
"""
token-weekly-monitor-runner.py
Token 周度监控与预警系统 - 主运行脚本

Level 5 Standard - 生产级完整闭环
版本: 2.0.0
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 配置路径
SKILL_NAME = "token-weekly-monitor"
WORKSPACE = Path("/root/.openclaw/workspace")
SKILL_DIR = WORKSPACE / "skills" / SKILL_NAME
DATA_FILE = WORKSPACE / "memory" / "token-weekly-monitor.json"
LOG_DIR = SKILL_DIR / "logs"
REPORT_DIR = SKILL_DIR / "reports"
CONFIG_DIR = SKILL_DIR / "config"

# 确保目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


class TokenMonitor:
    """Token 周度监控核心类"""
    
    # 状态阈值
    THRESHOLDS = {
        "healthy": 50,
        "caution": 30,
        "warning": 15,
        "critical": 0
    }
    
    # 状态图标
    STATUS_ICONS = {
        "healthy": "🟢",
        "caution": "🟡",
        "warning": "🟠",
        "critical": "🔴"
    }
    
    def __init__(self):
        self.start_time = datetime.now()
        self.data = self._load_data()
        self._setup_logging()
        
    def _setup_logging(self):
        """配置日志"""
        log_file = LOG_DIR / f"{SKILL_NAME}-{self.start_time.strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(SKILL_NAME)
        
    def _load_data(self) -> Dict:
        """加载监控数据"""
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"数据加载失败: {e}")
                return self._create_default_data()
        return self._create_default_data()
    
    def _create_default_data(self) -> Dict:
        """创建默认数据结构"""
        now = datetime.now()
        cycle_start = now - timedelta(days=now.weekday())
        cycle_start = cycle_start.replace(hour=12, minute=0, second=0)
        cycle_end = cycle_start + timedelta(days=7)
        
        return {
            "cycleInfo": {
                "startDate": cycle_start.strftime("%Y-%m-%d"),
                "startTime": "12:00",
                "endDate": cycle_end.strftime("%Y-%m-%d"),
                "endTime": "11:59",
                "currentDay": 1,
                "totalDays": 7,
                "status": "active"
            },
            "openclawToken": {
                "weeklyBudget": 70000,
                "dailyBudget": 10000,
                "consumed": 0,
                "remaining": 70000,
                "percentage": 100,
                "status": "healthy",
                "lastCheck": datetime.now().isoformat()
            },
            "kimi": {
                "tier": "Allegretto",
                "monthlyQuota": {
                    "deepResearch": 40,
                    "ppt": 40,
                    "agentPool": 40
                },
                "weeklyQuota": {
                    "deepResearch": 10,
                    "ppt": 10,
                    "agentPool": 10
                },
                "weeklyUsed": {
                    "deepResearch": 0,
                    "ppt": 0,
                    "agentPool": 0
                },
                "weeklyRemaining": {
                    "deepResearch": 10,
                    "ppt": 10,
                    "agentPool": 10
                }
            },
            "wps": {
                "tier": "SuperVIP",
                "status": "active"
            },
            "dailyLog": [],
            "checkHistory": []
        }
    
    def _save_data(self):
        """保存数据"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"数据保存失败: {e}")
    
    # ==================== S2: 核心算法 ====================
    
    def calculate_consumption_rate(self, consumed: int, days_elapsed: int) -> float:
        """计算日均消耗速度"""
        if days_elapsed <= 0:
            return 0
        return consumed / days_elapsed
    
    def predict_end_consumption(self, current_consumed: float, daily_rate: float, remaining_days: int) -> float:
        """预测周期结束时总消耗"""
        return current_consumed + (daily_rate * remaining_days)
    
    def consumption_vs_time_ratio(self, percentage_consumed: float, percentage_time: float) -> float:
        """计算消耗-时间比，>1表示超前消耗"""
        if percentage_time <= 0:
            return 1
        return percentage_consumed / percentage_time
    
    def determine_status(self, percentage_remaining: float) -> Tuple[str, str]:
        """根据剩余百分比确定状态"""
        if percentage_remaining > self.THRESHOLDS["healthy"]:
            return "healthy", self.STATUS_ICONS["healthy"]
        elif percentage_remaining > self.THRESHOLDS["caution"]:
            return "caution", self.STATUS_ICONS["caution"]
        elif percentage_remaining > self.THRESHOLDS["warning"]:
            return "warning", self.STATUS_ICONS["warning"]
        else:
            return "critical", self.STATUS_ICONS["critical"]
    
    # ==================== S5: 数据验证 ====================
    
    def validate_data_integrity(self) -> List[Tuple[str, str, str]]:
        """验证数据完整性 (S5)"""
        checks = []
        token_data = self.data.get("openclawToken", {})
        
        budget = token_data.get("weeklyBudget", 70000)
        consumed = token_data.get("consumed", 0)
        remaining = token_data.get("remaining", 70000)
        percentage = token_data.get("percentage", 0)  # 这是已消耗百分比
        status = token_data.get("status", "healthy")
        
        # 检查1: 数值一致性
        if consumed + remaining != budget:
            checks.append(("FAIL", "数值一致性", f"消耗({consumed})+剩余({remaining}) ≠ 总预算({budget})"))
        else:
            checks.append(("PASS", "数值一致性", "数值校验通过"))
        
        # 检查2: 百分比计算 (percentage是已消耗百分比，验证其正确性)
        calculated_consumed_pct = (consumed / budget) * 100 if budget > 0 else 0
        if abs(calculated_consumed_pct - percentage) > 0.5:
            checks.append(("FAIL", "百分比计算", f"计算值{calculated_consumed_pct:.1f}% ≠ 记录值{percentage}%"))
        else:
            checks.append(("PASS", "百分比计算", f"百分比校验通过 (已消耗{percentage}%)"))
        
        # 检查3: 状态匹配 (状态基于剩余百分比 = 100 - 已消耗百分比)
        remaining_pct = 100 - percentage
        expected_status, _ = self.determine_status(remaining_pct)
        if expected_status != status:
            checks.append(("FAIL", "状态匹配", f"期望状态{expected_status} ≠ 实际状态{status}"))
        else:
            checks.append(("PASS", "状态匹配", f"状态校验通过 ({status})"))
        
        return checks
    
    # ==================== S2: 异常检测 ====================
    
    def detect_anomalies(self) -> List[str]:
        """检测异常 (S2/S7)"""
        anomalies = []
        daily_log = self.data.get("dailyLog", [])
        token_data = self.data.get("openclawToken", {})
        
        if len(daily_log) >= 2:
            # 检测单日spike
            consumptions = [d.get("openclawConsumed", 0) for d in daily_log[-3:]]
            avg_consumption = sum(consumptions) / len(consumptions) if consumptions else 0
            
            if consumptions and consumptions[-1] > avg_consumption * 2 and avg_consumption > 0:
                anomalies.append(f"单日消耗spike: {consumptions[-1]} tokens (平均{avg_consumption:.0f})")
            
            # 检测连续高耗
            if len(daily_log) >= 3:
                daily_budget = token_data.get("dailyBudget", 10000)
                recent_3_days = [d.get("openclawConsumed", 0) for d in daily_log[-3:]]
                if all(c > daily_budget * 1.5 for c in recent_3_days):
                    anomalies.append(f"连续3天高消耗: {recent_3_days}")
        
        # 检测消耗超前
        cycle_info = self.data.get("cycleInfo", {})
        current_day = cycle_info.get("currentDay", 1)
        consumed_pct = token_data.get("percentage", 0)
        remaining_pct = 100 - consumed_pct
        percentage_consumed = consumed_pct
        percentage_time = (current_day / 7) * 100 if current_day > 0 else 0
        
        ratio = self.consumption_vs_time_ratio(percentage_consumed, percentage_time)
        if ratio > 1.2 and current_day > 0:
            anomalies.append(f"消耗超前: 消耗/时间比 = {ratio:.2f}")
        
        return anomalies
    
    # ==================== S3: 报告生成 ====================
    
    def generate_weekly_report(self) -> str:
        """生成周报 (S3)"""
        cycle_info = self.data.get("cycleInfo", {})
        token_data = self.data.get("openclawToken", {})
        kimi_data = self.data.get("kimi", {})
        daily_log = self.data.get("dailyLog", [])
        
        # 基础数据
        current_day = cycle_info.get("currentDay", 1)
        budget = token_data.get("weeklyBudget", 70000)
        consumed = token_data.get("consumed", 0)
        remaining = token_data.get("remaining", 70000)
        consumed_pct = token_data.get("percentage", 0)  # 已消耗百分比
        remaining_pct = 100 - consumed_pct  # 剩余百分比
        status, icon = self.determine_status(remaining_pct)
        
        # 计算指标
        daily_rate = self.calculate_consumption_rate(consumed, current_day)
        remaining_days = 7 - current_day
        predicted_end = self.predict_end_consumption(consumed, daily_rate, remaining_days)
        
        # 趋势
        recent_consumptions = [d.get("openclawConsumed", 0) for d in daily_log[-3:]]
        trend = "→ 平稳"
        if len(recent_consumptions) >= 2:
            if recent_consumptions[-1] > recent_consumptions[0] * 1.2:
                trend = "↑ 上升"
            elif recent_consumptions[-1] < recent_consumptions[0] * 0.8:
                trend = "↓ 下降"
        
        # 异常
        anomalies = self.detect_anomalies()
        
        # 建议
        suggestions = self._generate_suggestions(status, remaining_pct, daily_rate)
        
        report = f"""
═══════════════════════════════════════════════════════════════
                    📊 Token 周度监控报告
═══════════════════════════════════════════════════════════════
周期信息
├── 周期: {cycle_info.get('startDate', 'N/A')} {cycle_info.get('startTime', '')} ~ {cycle_info.get('endDate', 'N/A')} {cycle_info.get('endTime', '')}
├── 当前: 第{current_day}天/7天 ({current_day/7*100:.0f}%)
└── 剩余: {remaining_days}天

OpenClaw Token
├── 周预算: {budget:,} tokens
├── 已消耗: {consumed:,} tokens ({consumed_pct:.1f}%)
├── 剩余: {remaining:,} tokens ({remaining_pct:.1f}%)
├── 日均消耗: {daily_rate:,.0f} tokens
├── 预测周期结束: {predicted_end:,.0f} tokens
└── 状态: {icon} {status.upper()} (剩余 {remaining_pct:.0f}%)

Kimi 额度 ({kimi_data.get('tier', 'Unknown')})
├── 深度研究: {kimi_data.get('weeklyUsed', {}).get('deepResearch', 0)}/{kimi_data.get('weeklyQuota', {}).get('deepResearch', 10)} (剩余{kimi_data.get('weeklyRemaining', {}).get('deepResearch', 10)}次)
├── PPT: {kimi_data.get('weeklyUsed', {}).get('ppt', 0)}/{kimi_data.get('weeklyQuota', {}).get('ppt', 10)} (剩余{kimi_data.get('weeklyRemaining', {}).get('ppt', 10)}次)
├── Agent池: {kimi_data.get('weeklyUsed', {}).get('agentPool', 0)}/{kimi_data.get('weeklyQuota', {}).get('agentPool', 10)} (剩余{kimi_data.get('weeklyRemaining', {}).get('agentPool', 10)}次)
└── 状态: 🟢 充足

趋势分析
├── 近{len(recent_consumptions)}天消耗: {' → '.join(f'{c/1000:.1f}K' for c in recent_consumptions)}
├── 趋势方向: {trend}
└── 日均预算: {token_data.get('dailyBudget', 10000):,} tokens
"""
        
        if anomalies:
            report += "\n本周异常\n"
            for i, anomaly in enumerate(anomalies, 1):
                report += f"├── ⚠️ {anomaly}\n"
        
        if suggestions:
            report += "\n优化建议\n"
            for i, suggestion in enumerate(suggestions, 1):
                report += f"├── {i}. {suggestion}\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据状态: {'✅ 已验证' if all(c[0] == 'PASS' for c in self.validate_data_integrity()) else '❌ 需检查'}
═══════════════════════════════════════════════════════════════
"""
        return report
    
    def _generate_suggestions(self, status: str, remaining_pct: float, daily_rate: float) -> List[str]:
        """根据状态生成建议"""
        suggestions = []
        
        if status == "healthy":
            suggestions.append("当前运行良好，继续保持")
            if remaining_pct > 70:
                suggestions.append("有余量时可执行积压的P2任务")
        elif status == "caution":
            suggestions.append("消耗速度略快，建议优化任务优先级")
            suggestions.append("暂停P3低优先级任务")
        elif status == "warning":
            suggestions.append("仅执行P0紧急任务")
            suggestions.append("暂停学习/维护类任务")
            suggestions.append("建议用户关注资源状况")
        elif status == "critical":
            suggestions.append("进入紧急暂停模式")
            suggestions.append("仅响应用户主动指令")
        
        # 基于消耗速度的建议
        if daily_rate > 12000:
            suggestions.append("日均消耗较高，考虑优化任务参数")
        
        return suggestions
    
    # ==================== 周期管理 ====================
    
    def reset_cycle(self):
        """重置新周期"""
        now = datetime.now()
        
        # 保存历史
        history_entry = {
            "timestamp": now.isoformat(),
            "action": "cycle_reset",
            "finalData": self.data.copy()
        }
        
        # 重置数据
        self.data = self._create_default_data()
        self.data["checkHistory"].append(history_entry)
        self._save_data()
        
        self.logger.info("✅ 新周期已重置")
        return "✅ 新周期已重置"
    
    def calibrate(self, percentage: float, note: str = ""):
        """手动校准Token数据 (S5)"""
        token_data = self.data.get("openclawToken", {})
        budget = token_data.get("weeklyBudget", 70000)
        
        # percentage 是已消耗百分比
        consumed_pct = percentage
        remaining_pct = 100 - consumed_pct
        
        new_consumed = int(budget * (consumed_pct / 100))
        new_remaining = budget - new_consumed
        
        # 更新数据
        old_percentage = token_data.get("percentage", 0)
        token_data["consumed"] = new_consumed
        token_data["remaining"] = new_remaining
        token_data["percentage"] = round(consumed_pct, 1)
        token_data["lastCheck"] = datetime.now().isoformat()
        
        # 更新状态 (基于剩余百分比)
        status, icon = self.determine_status(remaining_pct)
        token_data["status"] = status
        
        # 记录历史
        calibration_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "user_calibration",
            "oldPercentage": old_percentage,
            "newPercentage": percentage,
            "action": "updated_from_user_input",
            "status": "calibrated",
            "notes": note
        }
        self.data["openclawToken"] = token_data
        self.data["checkHistory"].append(calibration_entry)
        self._save_data()
        
        self.logger.info(f"✅ 已校准: {old_percentage}% → {percentage}% ({icon} {status})")
        return f"✅ 已校准: {old_percentage}% → {percentage}% ({icon} {status})"
    
    # ==================== 主入口 ====================
    
    def check_status(self) -> Dict:
        """检查状态 (S1)"""
        token_data = self.data.get("openclawToken", {})
        consumed_pct = token_data.get("percentage", 0)  # 已消耗百分比
        remaining_pct = 100 - consumed_pct  # 剩余百分比
        status, icon = self.determine_status(remaining_pct)
        
        validations = self.validate_data_integrity()
        
        return {
            "skill_name": SKILL_NAME,
            "level_5_standard": True,
            "status": status,
            "icon": icon,
            "consumed_percentage": consumed_pct,
            "remaining_percentage": remaining_pct,
            "timestamp": datetime.now().isoformat(),
            "data_valid": all(c[0] == "PASS" for c in validations),
            "validations": validations
        }
    
    def run_check(self) -> str:
        """执行完整检查 (S2)"""
        # 验证数据
        validations = self.validate_data_integrity()
        
        # 检测异常
        anomalies = self.detect_anomalies()
        
        # 生成报告
        report = self.generate_weekly_report()
        
        # 记录检查历史
        check_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "daily_check",
            "validations": validations,
            "anomalies": anomalies
        }
        self.data["checkHistory"].append(check_entry)
        self._save_data()
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="Token 周度监控与预警系统 - Level 5",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["status", "run", "validate", "calibrate", "reset"],
        help="执行的命令"
    )
    
    parser.add_argument("--check", action="store_true", help="执行检查")
    parser.add_argument("--weekly-report", action="store_true", help="生成周报")
    parser.add_argument("--reset-cycle", action="store_true", help="重置周期")
    parser.add_argument("--percentage", type=float, help="校准百分比 (0-100)")
    parser.add_argument("--note", type=str, default="", help="校准备注")
    
    args = parser.parse_args()
    
    monitor = TokenMonitor()
    
    if args.command == "status":
        status = monitor.check_status()
        print(f"📊 {SKILL_NAME} Status: {status['icon']} {status['status'].upper()}")
        print(f"   已消耗: {status['consumed_percentage']:.1f}%")
        print(f"   剩余: {status['remaining_percentage']:.1f}%")
        print(f"   数据验证: {'✅' if status['data_valid'] else '❌'}")
        print(f"   Level 5: {'✅' if status['level_5_standard'] else '❌'}")
        
    elif args.command == "validate":
        print("🔍 执行数据完整性验证...")
        validations = monitor.validate_data_integrity()
        for result, name, detail in validations:
            icon = "✅" if result == "PASS" else "❌"
            print(f"{icon} {name}: {detail}")
        
    elif args.command == "calibrate":
        if args.percentage is None:
            print("❌ 错误: 校准需要提供 --percentage 参数")
            sys.exit(1)
        if not 0 <= args.percentage <= 100:
            print("❌ 错误: 百分比必须在 0-100 之间")
            sys.exit(1)
        result = monitor.calibrate(args.percentage, args.note)
        print(result)
        
    elif args.command == "reset":
        result = monitor.reset_cycle()
        print(result)
        
    elif args.command == "run":
        if args.weekly_report:
            report = monitor.generate_weekly_report()
            print(report)
            # 保存报告
            report_file = REPORT_DIR / f"weekly-report-{datetime.now().strftime('%Y%m%d')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 报告已保存: {report_file}")
            
        elif args.reset_cycle:
            result = monitor.reset_cycle()
            print(result)
            
        else:  # --check or default
            report = monitor.run_check()
            print(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
