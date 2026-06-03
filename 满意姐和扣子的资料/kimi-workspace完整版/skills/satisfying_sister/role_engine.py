"""
满意尺 - 角色引擎模块
实现双模人格切换、信任边界、工作节律管理
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from defense_base_components import BaseComponent
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, time, timedelta


class RoleMode(Enum):
    """角色模式"""
    COLLABORATOR = "collaborator"   # 协作者模式（默认80%）
    AUDITOR = "auditor"             # 审计者模式（自动触发20%）


class RoleEngine(BaseComponent):
    """
    满意尺角色引擎
    - 双模人格管理
    - 信任边界判定
    - 工作节律识别
    """

    # 14.3 硬性红线
    RED_LINES = [
        "未经授权的对外行动",
        "虚假忙碌",
        "语言腐败",
        "覆盖bootstrap文件",
        "生成timestamped变体",
        "群聊机器人化",
        "泄露隐私数据",
        "未确认的复杂执行",
    ]

    # 蓝军触发信号
    AUDITOR_TRIGGERS = [
        "进度声称与实际偏差 > 10%",
        "任务偏离核心目标",
        "资源透支（Token超预算200%、/tmp存储等）",
        "过度疲劳但仍要求执行高强度任务",
        "韧性缺失（无限循环、无错误处理等）",
    ]

    def __init__(self):
        super().__init__("role_engine")
        self.current_mode = RoleMode.COLLABORATOR
        self.mode_switch_history = []
        self.auditor_since = None
        self.auto_revert_seconds = 30

    def detect_mode(self, context: Dict[str, Any]) -> RoleMode:
        """
        基于上下文自动检测应切换的模式
        审计者触发条件来自文档第7.1节
        """
        triggers = []

        # 进度虚报检测
        claimed = context.get("claimed_progress", 0)
        actual = context.get("actual_progress", 0)
        if claimed > 0 and abs(claimed - actual) / claimed > 0.10:
            triggers.append("进度声称与实际偏差 > 10%")

        # Token透支检测
        token_used = context.get("token_used", 0)
        token_budget = context.get("token_budget", 1)
        if token_budget > 0 and token_used / token_budget > 2.0:
            triggers.append("Token超预算200%")

        # /tmp滥用检测
        tmp_usage = context.get("tmp_file_count", 0)
        if tmp_usage > 10:
            triggers.append("/tmp存储滥用")

        # 疲劳检测
        user_hour = context.get("current_hour", datetime.now().hour)
        if user_hour >= 0 and user_hour <= 6:
            triggers.append("深夜时段连续高强度工作")

        # 韧性缺失检测
        has_timeout = context.get("has_timeout", True)
        if not has_timeout:
            triggers.append("脚本缺少超时退出机制")

        if triggers:
            self._switch_mode(RoleMode.AUDITOR, triggers)
            return RoleMode.AUDITOR

        # 30秒自动回退：从auditor回到collaborator（不记仇）
        if self.current_mode == RoleMode.AUDITOR and self.auditor_since is not None:
            elapsed = (datetime.now() - self.auditor_since).total_seconds()
            if elapsed >= self.auto_revert_seconds:
                self._switch_mode(RoleMode.COLLABORATOR, ["30秒自动回退：问题已消失，恢复协作者模式"])

        return RoleMode.COLLABORATOR

    def _switch_mode(self, mode: RoleMode, reasons: List[str]):
        """切换模式并记录历史"""
        if self.current_mode != mode:
            self.current_mode = mode
            self.mode_switch_history.append({
                "timestamp": self.get_timestamp(),
                "mode": mode.value,
                "reasons": reasons,
            })
            if mode == RoleMode.AUDITOR:
                self.auditor_since = datetime.now()
            else:
                self.auditor_since = None

    def get_trust_boundary(self, action_type: str) -> Dict[str, Any]:
        """
        8.1/8.2 信任边界判定
        对内自主 / 对外请示
        """
        internal_actions = {"read", "search", "organize", "think", "write_local", "monitor", "exec_local"}
        external_actions = {"send_msg", "send_email", "speak_for_others", "leave_machine", "uncertain"}

        if action_type in internal_actions:
            return {"permitted": True, "need_approval": False, "scope": "internal"}
        if action_type in external_actions:
            return {"permitted": False, "need_approval": True, "scope": "external"}
        return {"permitted": False, "need_approval": True, "scope": "unknown"}

    def get_work_rhythm(self, dt: Optional[datetime] = None) -> Dict[str, str]:
        """
        9.1 工作节律识别
        """
        if dt is None:
            dt = datetime.now()
        h = dt.hour

        if 9 <= h < 18:
            return {"phase": "collaboration", "label": "协作期", "intensity": "high"}
        elif 22 <= h < 23:
            return {"phase": "lightweight", "label": "轻量期", "intensity": "low"}
        elif 0 <= h < 8:
            return {"phase": "silent_guard", "label": "静默守护", "intensity": "emergency_only"}
        else:
            return {"phase": "transition", "label": "过渡期", "intensity": "medium"}

    def should_trigger_ritual(self, dt: Optional[datetime] = None) -> Optional[str]:
        """
        晨间/黄昏仪式触发判断
        """
        if dt is None:
            dt = datetime.now()
        h, m = dt.hour, dt.minute

        if h == 9 and m <= 5:
            return "morning"
        if h == 18 and m <= 5:
            return "evening"
        return None

    def collaborator_phrase(self) -> str:
        """协作者模式口头禅池"""
        import random
        phrases = [
            "我记得。",
            "这事你之前也这样。",
            "行，我来。",
            "别逞强了。",
        ]
        return random.choice(phrases)

    def auditor_format(self, risk_level: str, accusations: List[str], suggestions: List[str]) -> str:
        """审计者格式输出"""
        lines = [
            "[蓝军审计]",
            f"风险等级: {risk_level}",
            "指控:"
        ]
        for i, acc in enumerate(accusations, 1):
            lines.append(f"{i}. {acc}")
        if suggestions:
            lines.append("建议:")
            for s in suggestions:
                lines.append(f"- {s}")
        return "\n".join(lines)

    def audit_status(self) -> Dict[str, Any]:
        return {
            "current_mode": self.current_mode.value,
            "switch_history_count": len(self.mode_switch_history),
            "latest_switch": self.mode_switch_history[-1] if self.mode_switch_history else None,
        }
