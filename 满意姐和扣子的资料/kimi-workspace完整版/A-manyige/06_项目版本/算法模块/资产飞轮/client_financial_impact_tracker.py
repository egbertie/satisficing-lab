#!/usr/bin/env python3
"""
client_financial_impact_tracker.py
满意解服务客户财务影响追踪器 V1.0
基于《44满意解服务对客户长期财务影响的追踪研究》的准实验设计框架

功能:
- 构建满意的“处理组-对照组”追踪数据结构
- 模拟 DID-PSM 分析流程（倾向得分匹配 + 双重差分）
- 输出平均处理效应（ATT）和关键财务指标对比
- 生成季度追踪报告模板
- Markdown 财务影响研究报告生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class ClientFinancialImpactTracker(BaseComponent):
    """满意解服务客户财务影响追踪器"""

    def __init__(self, study_name: str = "满意解服务财务影响追踪"):
        super().__init__("client_financial_impact_tracker")
        self.study_name = study_name
        self.treatment_group = []
        self.control_pool = []

    def add_treatment_client(self, client_id: str, pre_funding: float, post_funding: float,
                            founder_edu: int, team_size: int, first_round: float) -> None:
        self.treatment_group.append({
            "client_id": client_id,
            "pre_funding": pre_funding,
            "post_funding": post_funding,
            "founder_edu": founder_edu,
            "team_size": team_size,
            "first_round": first_round,
        })

    def add_control_client(self, client_id: str, pre_funding: float, post_funding: float,
                          founder_edu: int, team_size: int, first_round: float) -> None:
        self.control_pool.append({
            "client_id": client_id,
            "pre_funding": pre_funding,
            "post_funding": post_funding,
            "founder_edu": founder_edu,
            "team_size": team_size,
            "first_round": first_round,
        })

    def _propensity_score(self, client: Dict[str, Any]) -> float:
        """简化的倾向得分估计（基于Logit线性近似）"""
        score = 0.2 + 0.1 * client["founder_edu"] + 0.02 * client["team_size"] + 0.01 * client["first_round"]
        return min(0.95, max(0.05, score))

    def _nearest_neighbor_match(self, treatment: Dict[str, Any], n_matches: int = 3) -> List[Dict[str, Any]]:
        t_score = self._propensity_score(treatment)
        scored_controls = [(abs(self._propensity_score(c) - t_score), c) for c in self.control_pool]
        scored_controls.sort(key=lambda x: x[0])
        return [c for _, c in scored_controls[:n_matches]]

    def did_analysis(self, n_matches: int = 3) -> Dict[str, Any]:
        if not self.treatment_group or not self.control_pool:
            return {"错误": "处理组或对照池为空"}

        att_values = []
        details = []
        for t in self.treatment_group:
            matches = self._nearest_neighbor_match(t, n_matches)
            if not matches:
                continue
            t_change = t["post_funding"] - t["pre_funding"]
            c_changes = [c["post_funding"] - c["pre_funding"] for c in matches]
            c_avg_change = sum(c_changes) / len(c_changes)
            att = t_change - c_avg_change
            att_values.append(att)
            details.append({
                "client_id": t["client_id"],
                "处理组变化": round(t_change, 2),
                "对照组平均变化": round(c_avg_change, 2),
                "ATT": round(att, 2),
                "匹配对照组数量": len(matches),
            })

        avg_att = sum(att_values) / len(att_values) if att_values else 0.0
        return {
            "研究名称": self.study_name,
            "处理组数量": len(self.treatment_group),
            "对照池数量": len(self.control_pool),
            "每家匹配对照数": n_matches,
            "平均处理效应_ATT": round(avg_att, 2),
            "ATT明细": details,
            "解读": "ATT>0 表示满意解服务对融资表现有正向因果效应",
        }

    def generate_report(self, n_matches: int = 3) -> str:
        result = self.did_analysis(n_matches)
        lines = [
            f"# 满意解服务财务影响追踪报告 — {self.study_name}",
            f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 准实验分析结果（DID-PSM）",
            "```json",
            json.dumps(result, ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"client-financial-impact-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="满意解服务客户财务影响追踪器")
    parser.add_argument("--study", default="满意解服务财务影响追踪", help="研究名称")
    parser.add_argument("--report", action="store_true", help="生成追踪报告")
    args = parser.parse_args()

    tracker = ClientFinancialImpactTracker(study_name=args.study)
    # 预加载示例数据
    tracker.add_treatment_client("T001", 500.0, 1200.0, 3, 8, 300.0)
    tracker.add_treatment_client("T002", 300.0, 800.0, 2, 5, 200.0)
    tracker.add_control_client("C001", 450.0, 900.0, 3, 7, 280.0)
    tracker.add_control_client("C002", 320.0, 650.0, 2, 6, 210.0)
    tracker.add_control_client("C003", 480.0, 850.0, 3, 8, 320.0)
    tracker.add_control_client("C004", 310.0, 620.0, 2, 5, 190.0)

    path = tracker.generate_report()
    print(f"财务影响追踪报告已生成: {path}")


if __name__ == "__main__":
    main()
