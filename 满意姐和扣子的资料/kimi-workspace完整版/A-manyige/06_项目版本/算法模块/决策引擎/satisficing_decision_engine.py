#!/usr/bin/env python3
"""
satisficing_decision_engine.py
满意解决策引擎 V1.0
基于《43满意解决策引擎的数学形式化与算法架构设计》

功能:
- 三引擎架构：贝叶斯网络（BN）+ 模糊逻辑（Fuzzy）+ 多属性效用理论（MAUT）
- 按需调度：根据场景特征动态选择推理引擎或组合使用
- 合伙人评估场景：价值观冲突风险、技术能力、沟通适配性
- 输出置信度、评级（绿灯/黄灯/红灯）及决策建议
- Markdown 决策评估报告生成
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class BayesianEngine:
    """简化的贝叶斯网络引擎 — 不确定性下的概率推理"""

    def __init__(self):
        self.priors = {
            "价值观冲突风险": 0.3,
            "技术能力不足": 0.2,
            "沟通适配性差": 0.25,
        }
        self.likelihoods = {
            "股权讨论寸步不让": {"价值观冲突风险": 0.8},
            "前合伙人诉讼记录": {"价值观冲突风险": 0.9},
            "缺乏相关技术背景": {"技术能力不足": 0.75},
            "访谈中表达含糊": {"沟通适配性差": 0.7},
        }

    def infer(self, evidence: List[str]) -> Dict[str, float]:
        posteriors = {}
        for hypothesis, prior in self.priors.items():
            likelihood = 1.0
            for e in evidence:
                if e in self.likelihoods and hypothesis in self.likelihoods[e]:
                    likelihood *= self.likelihoods[e][hypothesis]
                else:
                    likelihood *= 0.3  # 默认弱相关
            # 简化后验（未归一化，用于相对排序）
            posteriors[hypothesis] = min(0.95, prior * likelihood / (prior * likelihood + (1 - prior) * 0.1))
        return posteriors


class FuzzyEngine:
    """简化的模糊逻辑引擎 — 语言变量到隶属度的映射"""

    def __init__(self):
        self.terms = {
            "技术能力": {"低": (0, 30), "中": (20, 70), "高": (60, 100)},
            "沟通意愿": {"弱": (0, 40), "一般": (30, 70), "强": (60, 100)},
            "价值观一致": {"差": (0, 30), "尚可": (20, 70), "好": (60, 100)},
        }

    def _membership(self, x: float, low: float, high: float) -> float:
        if x <= low:
            return 0.0
        if x >= high:
            return 1.0
        return (x - low) / (high - low)

    def evaluate(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        result = {}
        for dimension, value in inputs.items():
            if dimension not in self.terms:
                continue
            memberships = {}
            for label, (low, high) in self.terms[dimension].items():
                memberships[label] = round(self._membership(value, low, high), 3)
            result[dimension] = memberships
        return result


class MAUTEngine:
    """简化的 MAUT 引擎 — 多属性效用聚合"""

    def __init__(self):
        self.attributes = {
            "技术能力": {"weight": 0.25, "direction": "max"},
            "行业经验": {"weight": 0.20, "direction": "max"},
            "价值观一致": {"weight": 0.25, "direction": "max"},
            "沟通适配": {"weight": 0.15, "direction": "max"},
            "抗压韧性": {"weight": 0.15, "direction": "max"},
        }

    def aggregate(self, scores: Dict[str, float]) -> Dict[str, Any]:
        utility = 0.0
        details = {}
        for attr, cfg in self.attributes.items():
            score = scores.get(attr, 50.0) / 100.0
            w_score = score * cfg["weight"]
            utility += w_score
            details[attr] = {"原始评分": scores.get(attr, 50.0), "权重": cfg["weight"], "加权贡献": round(w_score, 4)}
        return {
            "总效用值": round(utility, 4),
            "属性分解": details,
            "interpretation": "效用值>0.75为绿灯，0.5-0.75为黄灯，<0.5为红灯",
        }


class SatisficingDecisionEngine(BaseComponent):
    """满意解决策引擎 — 三引擎按需调度"""

    def __init__(self, candidate_name: str = ""):
        super().__init__("satisficing_decision_engine")
        self.candidate_name = candidate_name
        self.bn = BayesianEngine()
        self.fuzzy = FuzzyEngine()
        self.maut = MAUTEngine()

    def evaluate(self, evidence: List[str], fuzzy_inputs: Dict[str, float], maut_scores: Dict[str, float]) -> Dict[str, Any]:
        # 按需调度
        bn_result = self.bn.infer(evidence) if evidence else {}
        fuzzy_result = self.fuzzy.evaluate(fuzzy_inputs) if fuzzy_inputs else {}
        maut_result = self.maut.aggregate(maut_scores) if maut_scores else {}

        # 三引擎融合：取最保守（风险最高）的结果作为主导
        overall_risk = 0.0
        risk_sources = []
        if bn_result:
            max_bn_risk = max(bn_result.values())
            overall_risk = max(overall_risk, max_bn_risk)
            risk_sources.append(f"BN风险:{max_bn_risk:.2f}")
        if fuzzy_result:
            fuzzy_dangers = [1 - m.get("高", 0) for m in fuzzy_result.values() if "高" in m]
            if fuzzy_dangers:
                avg_fuzzy_risk = sum(fuzzy_dangers) / len(fuzzy_dangers)
                overall_risk = max(overall_risk, avg_fuzzy_risk)
                risk_sources.append(f"Fuzzy风险:{avg_fuzzy_risk:.2f}")
        if maut_result:
            utility = maut_result.get("总效用值", 0.5)
            maut_risk = 1 - utility
            overall_risk = max(overall_risk, maut_risk)
            risk_sources.append(f"MAUT风险:{maut_risk:.2f}")

        if overall_risk < 0.3:
            signal = "绿灯"
            confidence = 0.75 + (0.3 - overall_risk)
        elif overall_risk < 0.6:
            signal = "黄灯"
            confidence = 0.55 + (0.6 - overall_risk) * 0.5
        else:
            signal = "红灯"
            confidence = 0.4 + (1.0 - overall_risk) * 0.3

        confidence = round(min(0.95, max(0.4, confidence)), 2)

        return {
            "候选人": self.candidate_name or "未命名",
            "评估时间": datetime.now().isoformat(),
            "信号": signal,
            "置信度": confidence,
            "总体风险": round(overall_risk, 2),
            "风险来源": risk_sources,
            "BN推理": bn_result,
            "模糊评估": fuzzy_result,
            "MAUT效用": maut_result,
            "建议": self._recommend(signal),
        }

    def _recommend(self, signal: str) -> str:
        return {
            "绿灯": "建议进入下一轮深度访谈，重点关注长期承诺度验证。",
            "黄灯": "存在中等风险信号，建议补充背景调查并启动二次评估。",
            "红灯": "风险信号显著，建议暂停推进或启动退出沟通机制。",
        }.get(signal, "")

    def generate_report(self, evidence: List[str], fuzzy_inputs: Dict[str, float], maut_scores: Dict[str, float]) -> str:
        result = self.evaluate(evidence, fuzzy_inputs, maut_scores)
        lines = [
            f"# 满意解决策引擎评估报告 — {self.candidate_name or '未命名候选人'}",
            f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**信号**: {result['信号']} | **置信度**: {result['置信度']}",
            "",
            "## 三引擎融合结果",
            "```json",
            json.dumps({k: v for k, v in result.items() if k not in ["BN推理", "模糊评估", "MAUT效用"]}, ensure_ascii=False, indent=2),
            "```",
            "",
            "## BN 概率推理",
            "```json",
            json.dumps(result["BN推理"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## 模糊逻辑评估",
            "```json",
            json.dumps(result["模糊评估"], ensure_ascii=False, indent=2),
            "```",
            "",
            "## MAUT 效用分析",
            "```json",
            json.dumps(result["MAUT效用"], ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"satisficing-decision-report-{self.candidate_name or 'draft'}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="满意解决策引擎（Satisficing Decision Engine）")
    parser.add_argument("--candidate", default="", help="候选人姓名")
    parser.add_argument("--report", action="store_true", help="生成决策评估报告")
    args = parser.parse_args()

    engine = SatisficingDecisionEngine(candidate_name=args.candidate)
    path = engine.generate_report(
        evidence=["股权讨论寸步不让", "访谈中表达含糊"],
        fuzzy_inputs={"技术能力": 75.0, "沟通意愿": 45.0, "价值观一致": 60.0},
        maut_scores={"技术能力": 75.0, "行业经验": 60.0, "价值观一致": 55.0, "沟通适配": 40.0, "抗压韧性": 70.0},
    )
    print(f"决策评估报告已生成: {path}")


if __name__ == "__main__":
    main()
