#!/usr/bin/env python3
"""
perceptual_tracker_proxy.py - 感知追踪代理（硬件降级版）
来源: 系统深度优化方案.docx - 第十三轮
功能: 当无可穿戴设备时，提供手动记录接口和数据分析规则
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import sys


class PerceptualTrackerProxy:
    """
    感知追踪代理（P2降级版）
    无硬件传感器时的手动记录与规则分析接口
    """

    def __init__(self, data_dir: str = "memory/perceptual_logs"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "manual_perceptual_log.jsonl"

    def record_session(self, session_id: str, metrics: Dict[str, float],
                       context: Dict[str, str]) -> bool:
        """手动记录一次感知数据会话"""
        entry = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "context": context
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True

    def analyze_trend(self, sessions: List[Dict]) -> Dict:
        """分析近期感知数据趋势"""
        if not sessions:
            return {"status": "NO_DATA", "insight": "请先记录感知数据"}
        hr_values = [s["metrics"].get("resting_hr", 0) for s in sessions if "resting_hr" in s["metrics"]]
        hrv_values = [s["metrics"].get("hrv_rmssd", 0) for s in sessions if "hrv_rmssd" in s["metrics"]]
        sleep_scores = [s["metrics"].get("sleep_score", 0) for s in sessions if "sleep_score" in s["metrics"]]
        insights = []
        if hr_values and hr_values[-1] > sum(hr_values[:-1]) / max(len(hr_values)-1, 1) * 1.1:
            insights.append("静息心率较近期均值上升>10%，提示压力累积")
        if hrv_values and hrv_values[-1] < sum(hrv_values[:-1]) / max(len(hrv_values)-1, 1) * 0.9:
            insights.append("HRV较近期均值下降>10%，自主神经调节能力可能下降")
        if sleep_scores and sleep_scores[-1] < 70:
            insights.append("睡眠质量评分<70，建议优先恢复睡眠")
        return {
            "status": "ANALYZED",
            "sessions_count": len(sessions),
            "latest_metrics": {
                "resting_hr": hr_values[-1] if hr_values else None,
                "hrv_rmssd": hrv_values[-1] if hrv_values else None,
                "sleep_score": sleep_scores[-1] if sleep_scores else None,
            },
            "insights": insights,
            "recommendation": "数据足够时建议咨询专家" if len(sessions) >= 7 else "继续记录至少7天数据以获得可靠趋势"
        }

    def load_sessions(self, limit: int = 30) -> List[Dict]:
        sessions = []
        if not self.log_file.exists():
            return sessions
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    sessions.append(json.loads(line))
        return sessions[-limit:]


if __name__ == "__main__":
    ptp = PerceptualTrackerProxy()
    ptp.record_session("S001", {"resting_hr": 65, "hrv_rmssd": 45, "sleep_score": 75},
                       {"activity": "决策会议", "duration_min": 60})
    ptp.record_session("S002", {"resting_hr": 72, "hrv_rmssd": 38, "sleep_score": 68},
                       {"activity": "高压谈判", "duration_min": 90})
    sessions = ptp.load_sessions()
    result = ptp.analyze_trend(sessions)
    print(f"✓ 感知追踪代理: {result['status']}, {result['sessions_count']}条记录")
    for ins in result["insights"]:
        print(f"  - {ins}")
    assert result["status"] == "ANALYZED"
    assert len(result["insights"]) > 0, "应检测到异常趋势"
    print("\n✓ 感知追踪代理验证通过")
    sys.exit(0)
