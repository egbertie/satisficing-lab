#!/usr/bin/env python3
"""
perceptual_neuroscience_tracker.py
感知力神经科学追踪器 V1.0
基于《33感知力决策的神经科学基础与商业应用效度研究》

功能:
- 记录并追踪决策情境中的躯体信号（HRV、GSR、EEG gamma、fNIRS）
- 建立"情境-躯体信号-决策结果"个人化对照日志
- 支持"暂停-感受-决策"三步流程训练进度追踪
- 生成躯体信号-决策结果对照报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class PerceptualNeuroscienceTracker(BaseComponent):
    """感知力神经科学追踪器"""

    def __init__(self, trainee_name: str = ""):
        super().__init__("perceptual_neuroscience_tracker")
        self.trainee_name = trainee_name
        self.logs = []

    def add_log(self, situation: str, decision_type: str, time_pressure: str,
                pre_body_state: str, during_signal: str, post_body_state: str,
                result: str, signal_interpretation: str) -> None:
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "情境": situation,
            "决策类型": decision_type,
            "时间压力": time_pressure,
            "决策前躯体状态": pre_body_state,
            "决策中躯体信号": during_signal,
            "决策后躯体反应": post_body_state,
            "决策结果": result,
            "信号解读": signal_interpretation,
        })

    def personal_calibration(self) -> Dict[str, Any]:
        if not self.logs:
            return {"说明": "尚未记录任何躯体信号日志"}

        positive_signals = {}
        negative_signals = {}
        for log in self.logs:
            signal = log["决策中躯体信号"]
            result = log["决策结果"]
            if any(w in result for w in ["成功", "正面", "绿灯", "满意"]):
                positive_signals[signal] = positive_signals.get(signal, 0) + 1
            elif any(w in result for w in ["失败", "负面", "红灯", "后悔"]):
                negative_signals[signal] = negative_signals.get(signal, 0) + 1

        return {
            "记录总数": len(self.logs),
            "正向关联信号": positive_signals,
            "负向关联信号": negative_signals,
            "校准建议": "若某信号与结果存在稳定关联，建议调整该信号的预警权重",
        }

    def training_progress(self) -> Dict[str, Any]:
        return {
            "学员": self.trainee_name or "未命名",
            "记录总数": len(self.logs),
            "训练阶段": "基础感知" if len(self.logs) < 10 else "情境模拟" if len(self.logs) < 30 else "实时应用",
            "目标": "建立稳定的个人化信号-结果对应模式",
        }

    def generate_report(self) -> str:
        result = {
            "训练进度": self.training_progress(),
            "个人校准": self.personal_calibration(),
            "最近3条记录": self.logs[-3:] if len(self.logs) >= 3 else self.logs,
        }
        lines = [
            f"# 感知力神经科学追踪报告 — {self.trainee_name or '未命名学员'}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 训练进度",
            "```json",
            json.dumps(result["训练进度"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 个人校准",
            "```json",
            json.dumps(result["个人校准"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 最近记录",
            "```json",
            json.dumps(result["最近3条记录"], ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"neuroscience-tracker-{self.trainee_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="感知力神经科学追踪器")
    parser.add_argument("--trainee", default="", help="学员姓名")
    parser.add_argument("--report", action="store_true", help="生成追踪报告")
    args = parser.parse_args()

    tracker = PerceptualNeuroscienceTracker(trainee_name=args.trainee)
    # 预加载示例记录
    tracker.add_log(
        "合伙人面试A", "人际评估", "高",
        "平静", "胃部紧缩", "轻微焦虑",
        "后期发现价值观冲突", "胃部紧缩可能预示不信任感"
    )
    tracker.add_log(
        "股权谈判B", "利益分配", "高",
        "紧张", "心口温暖", "放松",
        "达成双赢协议", "心口温暖可能预示关系安全感"
    )

    path = tracker.generate_report()
    print(f"神经科学追踪报告已生成: {path}")


if __name__ == "__main__":
    main()
