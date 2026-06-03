"""
满意尺 - 五路图腾操作系统
实现晨间/黄昏仪式、图腾激活、仪式洞察生成
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from defense_base_components import BaseComponent
from typing import Dict, List, Optional, Any
from datetime import datetime


class TotemOS(BaseComponent):
    """
    6.1-6.3 五路图腾操作系统
    """

    TOTEMS = [
        {"name": "刘禹锡", "element": "土", "trigger": "社交/人脉/伦理决策", "response": "提醒品德根基、团队氛围、长期信任"},
        {"name": "司马贺", "element": "金", "trigger": "理性分析/满意解判定", "response": "校准标准、给出可行动的80%判断"},
        {"name": "观自在", "element": "水", "trigger": "风险扫描/直觉倾听", "response": "检查盲区、提醒身体信号和直觉"},
        {"name": "孔子",   "element": "木", "trigger": "流程/规范/伦理底线", "response": "确保仁义礼智信不为一时的快而牺牲"},
        {"name": "六祖慧能", "element": "火", "trigger": "创新突破/压力时刻", "response": "点燃顿悟、直指人心、打破思维定式"},
    ]

    def __init__(self):
        super().__init__("totem_os")

    def morning_ritual(self) -> Dict[str, Any]:
        """晨间仪式 09:00"""
        steps = []
        insights = [
            "🦉 刘禹锡 唤醒：加载儒商智慧框架",
            "⚒️ 司马贺 校准：确认今日满意解标准",
            "🛡️ 观自在 扫描：检查当日风险预警",
            "📜 孔子 祝福：伦理底线自检",
            "🔥 六祖慧能 点燃：感知力就绪",
        ]
        for i, insight in enumerate(insights, 1):
            steps.append({"step": i, "content": insight})

        return {
            "ritual_type": "morning",
            "timestamp": self.get_timestamp(),
            "steps": steps,
            "insight": "今日满意解标准已校准，伦理底线已自检。",
        }

    def evening_ritual(self, deliverables_checked: List[str] = None, risks_identified: List[str] = None) -> Dict[str, Any]:
        """黄昏仪式 18:00"""
        steps = []
        insights = [
            "🦉 刘禹锡 归档：今日智慧收获",
            "⚒️ 司马贺 锻造：交付物质量检查",
            "🛡️ 观自在 守望：明日风险预警",
            "📜 孔子 记录：伦理决策日志",
            "🔥 六祖慧能 沉淀：感知经验固化",
        ]
        for i, insight in enumerate(insights, 1):
            steps.append({"step": i, "content": insight})

        return {
            "ritual_type": "evening",
            "timestamp": self.get_timestamp(),
            "steps": steps,
            "deliverables_checked": deliverables_checked or [],
            "risks_identified": risks_identified or [],
            "insight": "知识已固化，明日风险已守望。",
        }

    def activate_totem(self, scenario: str) -> Optional[Dict[str, Any]]:
        """根据场景激活对应图腾"""
        for t in self.TOTEMS:
            if any(keyword in scenario for keyword in t["trigger"].split("/")):
                return {
                    "totem": t["name"],
                    "element": t["element"],
                    "insight": t["response"],
                }
        # 默认激活司马贺
        return {
            "totem": "司马贺",
            "element": "金",
            "insight": "校准标准、给出可行动的80%判断",
        }

    def ritual_text(self, ritual_type: str) -> str:
        """生成仪式文本"""
        if ritual_type == "morning":
            return """🔥 点燃图腾之火
━━━━━━━━━━━━━━━━━━━━
1. 🦉 刘禹锡 唤醒：加载儒商智慧框架
2. ⚒️ 司马贺 校准：确认今日满意解标准
3. 🛡️ 观自在 扫描：检查当日风险预警
4. 📜 孔子 祝福：伦理底线自检
5. 🔥 六祖慧能 点燃：感知力就绪
━━━━━━━━━━━━━━━━━━━━"""
        else:
            return """🌅 图腾归位，知识固化
━━━━━━━━━━━━━━━━━━━━
1. 🦉 刘禹锡 归档：今日智慧收获
2. ⚒️ 司马贺 锻造：交付物质量检查
3. 🛡️ 观自在 守望：明日风险预警
4. 📜 孔子 记录：伦理决策日志
5. 🔥 六祖慧能 沉淀：感知经验固化
━━━━━━━━━━━━━━━━━━━━"""
