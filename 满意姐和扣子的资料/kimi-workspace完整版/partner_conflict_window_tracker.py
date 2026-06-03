#!/usr/bin/env python3
"""
partner_conflict_window_tracker.py
合伙人冲突窗口期追踪器 V1.0
基于《34硬科合伙冲突窗口2.0》和《32硬科技创业合伙人冲突的关键窗口期与干预机制研究》

功能:
- 识别硬科技创业合伙人冲突的"三阶段两节点"进程
- 记录冲突预警信号（沟通频率下降、决策僵局、情绪爆发、信任侵蚀）
- 评估冲突所处窗口期（早期可逆期 / 中期胶着期 / 晚期解体期）
- 推荐对应干预机制（预防性对话、第三方调解、结构性重构、退出谈判）
- 生成冲突窗口追踪报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class PartnerConflictWindowTracker(BaseComponent):
    """合伙人冲突窗口期追踪器"""

    WARNING_SIGNALS = {
        "沟通频率显著下降": 2,
        "决策反复陷入僵局": 3,
        "公开场合情绪爆发": 4,
        "相互信任明显侵蚀": 3,
        "股权/控制权争议升温": 4,
        "技术路线不可调和": 5,
        "一方长期回避关键议题": 3,
    }

    INTERVENTIONS = {
        "早期可逆期": "预防性对话 + 角色边界重定义",
        "中期胶着期": "第三方调解 + 结构性重构（股权/决策权调整）",
        "晚期解体期": "退出谈判 + 知识/资产分割协议",
    }

    def __init__(self, startup_name: str = ""):
        super().__init__("partner_conflict_window_tracker")
        self.startup_name = startup_name
        self.signals = []

    def add_signal(self, signal_type: str, timestamp: str = None, severity: int = None) -> None:
        weight = self.WARNING_SIGNALS.get(signal_type, 2)
        self.signals.append({
            "信号": signal_type,
            "时间": timestamp or datetime.now().isoformat(),
            "严重程度": severity or weight,
        })

    def assess_window(self) -> Dict[str, Any]:
        if not self.signals:
            return {"窗口期": "无冲突信号", "风险评分": 0, "干预建议": "保持常规沟通机制"}

        total_score = sum(s["严重程度"] for s in self.signals)
        unique_signals = len(set(s["信号"] for s in self.signals))

        if total_score <= 5 and unique_signals <= 2:
            window = "早期可逆期"
        elif total_score <= 12 and unique_signals <= 5:
            window = "中期胶着期"
        else:
            window = "晚期解体期"

        return {
            "企业名称": self.startup_name or "未命名",
            "窗口期": window,
            "风险评分": total_score,
            "不重复信号数": unique_signals,
            "已记录信号": self.signals,
            "干预建议": self.INTERVENTIONS.get(window, ""),
        }

    def generate_report(self) -> str:
        result = self.assess_window()
        lines = [
            f"# 合伙人冲突窗口期追踪报告 — {self.startup_name or '未命名企业'}",
            f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**冲突窗口期**: {result['窗口期']}",
            f"**风险评分**: {result['风险评分']}",
            "",
            "## 已记录预警信号",
            "```json",
            json.dumps(result['已记录信号'], ensure_ascii=False, indent=2),
            "```",
            "",
            f"## 干预建议\n\n{result['干预建议']}",
        ]
        report_path = Path(self.workspace) / "memory" / f"conflict-window-report-{self.startup_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="合伙人冲突窗口期追踪器")
    parser.add_argument("--startup", default="", help="企业名称")
    parser.add_argument("--report", action="store_true", help="生成追踪报告")
    args = parser.parse_args()

    tracker = PartnerConflictWindowTracker(startup_name=args.startup)
    tracker.add_signal("决策反复陷入僵局", severity=3)
    tracker.add_signal("相互信任明显侵蚀", severity=3)
    tracker.add_signal("股权/控制权争议升温", severity=4)

    path = tracker.generate_report()
    print(f"冲突窗口追踪报告已生成: {path}")


if __name__ == "__main__":
    main()
