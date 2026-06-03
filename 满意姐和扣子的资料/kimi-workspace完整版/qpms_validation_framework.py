#!/usr/bin/env python3
"""
qpms_validation_framework.py
QPMS 量子感知引擎算法效度验证框架 V1.0
基于《39QPMS量子感知引擎算法效度验证研究》的简化可运行实现

功能:
- ECBM 躯体信号模块效度验证（相关性分析）
- REPA 伦理对齐模块效度验证（二分类 AUC-ROC、校准误差）
- ETDS 涌现匹配模块效度验证（对比实验统计量）
- 综合验证报告生成（Markdown 格式）
- 偏误控制机制检查清单
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

from defense_base_components import BaseComponent


class QPMSValidationFramework(BaseComponent):
    """QPMS 量子感知引擎算法效度验证框架"""

    def __init__(self):
        super().__init__("qpms_validation_framework")
        self.results = {}

    # ------------------------------------------------------------------
    # 统计工具函数（轻量实现，无外部 heavy-dependency）
    # ------------------------------------------------------------------
    @staticmethod
    def mean(vals: List[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    @staticmethod
    def pearson_r(x: List[float], y: List[float]) -> float:
        n = len(x)
        if n != len(y) or n == 0:
            return 0.0
        mx, my = sum(x) / n, sum(y) / n
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        den = math.sqrt(sum((xi - mx) ** 2 for xi in x)) * math.sqrt(sum((yi - my) ** 2 for yi in y))
        return num / den if den else 0.0

    @staticmethod
    def spearman_rho(x: List[float], y: List[float]) -> float:
        def rank(v):
            sorted_v = sorted(set(v))
            return [sorted_v.index(i) + 1 for i in v]
        return QPMSValidationFramework.pearson_r(rank(x), rank(y))

    @staticmethod
    def auc_roc(y_true: List[int], y_score: List[float]) -> float:
        """Mann-Whitney U 估计 AUC（简化版）"""
        pos = [s for t, s in zip(y_true, y_score) if t == 1]
        neg = [s for t, s in zip(y_true, y_score) if t == 0]
        if not pos or not neg:
            return 0.0
        # 使用梯形法则做粗略估计（要求 y_score 已排序时更准）
        pairs = [(t, s) for t, s in zip(y_true, y_score)]
        pairs.sort(key=lambda p: p[1])
        n_pos = sum(1 for t, _ in pairs if t == 1)
        n_neg = len(pairs) - n_pos
        if n_pos == 0 or n_neg == 0:
            return 0.5
        # 简单排序后计算 Concordant 比例
        concordant = 0
        for i, (t1, s1) in enumerate(pairs):
            if t1 == 1:
                concordant += sum(1 for j in range(i + 1, len(pairs)) if pairs[j][0] == 0)
        return 1.0 - (concordant / (n_pos * n_neg))

    @staticmethod
    def ece(y_true: List[int], y_prob: List[float], n_bins: int = 10) -> float:
        """期望校准误差（简化等宽分箱）"""
        bins = {i: [] for i in range(n_bins)}
        for t, p in zip(y_true, y_prob):
            bin_idx = min(int(p * n_bins), n_bins - 1)
            bins[bin_idx].append(t)
        total = len(y_true)
        ece_val = 0.0
        for i in range(n_bins):
            if not bins[i]:
                continue
            avg_conf = (i + 0.5) / n_bins
            acc = sum(bins[i]) / len(bins[i])
            ece_val += (len(bins[i]) / total) * abs(acc - avg_conf)
        return ece_val

    @staticmethod
    def brier_score(y_true: List[int], y_prob: List[float]) -> float:
        return sum((p - t) ** 2 for t, p in zip(y_true, y_prob)) / len(y_true)

    @staticmethod
    def cohens_d(group1: List[float], group2: List[float]) -> float:
        m1, m2 = sum(group1) / len(group1), sum(group2) / len(group2)
        pooled_std = math.sqrt(
            (sum((x - m1) ** 2 for x in group1) + sum((x - m2) ** 2 for x in group2))
            / (len(group1) + len(group2) - 2)
        )
        return (m1 - m2) / pooled_std if pooled_std else 0.0

    # ------------------------------------------------------------------
    # ECBM 模块验证
    # ------------------------------------------------------------------
    def validate_ecbm(self, data: List[Dict[str, float]] = None) -> Dict[str, Any]:
        """ECBM: 躯体信号与团队稳定性关联验证"""
        if data is None:
            # 合成示例数据（n=50）
            import random
            random.seed(42)
            data = []
            for _ in range(50):
                anxiety = random.uniform(1.0, 5.0)
                defense = random.uniform(1.0, 5.0)
                openness = random.uniform(1.0, 5.0)
                # 稳定性与焦虑/防御负相关，与开放正相关（带噪声）
                stability = (
                    5.0 - 0.4 * anxiety - 0.3 * defense + 0.35 * openness + random.gauss(0, 0.8)
                )
                stability = max(1.0, min(5.0, stability))
                data.append({
                    "anxiety": anxiety,
                    "defense": defense,
                    "openness": openness,
                    "stability": stability,
                })

        anxiety = [d["anxiety"] for d in data]
        defense = [d["defense"] for d in data]
        openness = [d["openness"] for d in data]
        stability = [d["stability"] for d in data]

        return {
            "sample_size": len(data),
            "anxiety_stability_r": round(self.pearson_r(anxiety, stability), 3),
            "defense_stability_r": round(self.pearson_r(defense, stability), 3),
            "openness_stability_r": round(self.pearson_r(openness, stability), 3),
            "interpretation": {
                "anxiety": "负相关（焦虑信号越高，团队稳定性越低）",
                "defense": "负相关（防御信号越高，团队稳定性越低）",
                "openness": "正相关（开放信号越高，团队稳定性越高）",
            },
            "note": "预期中等效应量 r=0.30-0.40；本框架使用合成数据演示计算流程，真实研究需替换为实际采集数据。",
        }

    # ------------------------------------------------------------------
    # REPA 模块验证
    # ------------------------------------------------------------------
    def validate_repa(self, data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """REPA: 伦理对齐度预测效度验证"""
        if data is None:
            import random
            random.seed(42)
            data = []
            for _ in range(100):
                ethical_score = random.uniform(1.0, 5.0)
                # 伦理分数越高，负面事件概率越低
                prob_negative = 1.0 / (1.0 + math.exp(ethical_score - 3.0))
                is_negative = 1 if random.random() < prob_negative else 0
                data.append({
                    "ethical_score": ethical_score,
                    "is_negative": is_negative,
                    "predicted_prob": prob_negative,
                })

        ethical_scores = [d["ethical_score"] for d in data]
        y_true = [d["is_negative"] for d in data]
        y_prob = [d["predicted_prob"] for d in data]

        # 划分为高伦理组 vs 低伦理组（中位数分割）
        median = sorted(ethical_scores)[len(ethical_scores) // 2]
        high_group = [s for s, d in zip(ethical_scores, data) if d["ethical_score"] >= median]
        low_group = [s for s, d in zip(ethical_scores, data) if d["ethical_score"] < median]

        return {
            "sample_size": len(data),
            "cohens_d": round(self.cohens_d(high_group, low_group), 3),
            "spearman_rho": round(self.spearman_rho(ethical_scores, y_true), 3),
            "auc_roc": round(self.auc_roc(y_true, y_prob), 3),
            "ece": round(self.ece(y_true, y_prob), 3),
            "brier_score": round(self.brier_score(y_true, y_prob), 3),
            "threshold_check": {
                "cohens_d_target": ">0.5",
                "spearman_rho_target": ">0.4",
                "auc_roc_target": ">0.75",
                "ece_target": "<0.1",
            },
            "note": "预期：区分效度 d>0.5，排序效度 ρ>0.4，预测效度 AUC>0.75，校准误差 ECE<0.1。",
        }

    # ------------------------------------------------------------------
    # ETDS 模块验证
    # ------------------------------------------------------------------
    def validate_etds(self, data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """ETDS: 涌现匹配 vs 能力互补 对比验证"""
        if data is None:
            import random
            random.seed(42)
            data = []
            for _ in range(80):
                etds_score = random.uniform(40.0, 95.0)
                ability_comp_score = random.uniform(40.0, 90.0)
                # ETDS 在价值观冲突情境下更有优势
                outcome = 1.0 / (1.0 + math.exp(-0.1 * (etds_score - 65))) + random.gauss(0, 0.1)
                data.append({
                    "etds_score": etds_score,
                    "ability_comp_score": ability_comp_score,
                    "outcome": outcome,
                })

        etds = [d["etds_score"] for d in data]
        ability = [d["ability_comp_score"] for d in data]
        outcome = [d["outcome"] for d in data]

        return {
            "sample_size": len(data),
            "etds_outcome_r": round(self.pearson_r(etds, outcome), 3),
            "ability_outcome_r": round(self.pearson_r(ability, outcome), 3),
            "advantage_scenarios": [
                "价值观冲突情境：ETDS 相对优势显著（捕捉隐性张力）",
                "能力不匹配情境：传统规则已覆盖，ETDS 优势有限",
                "外部冲击情境：两者均可预测",
            ],
            "note": "真实研究需通过分样本（价值观冲突子样本 vs 能力不匹配子样本）进行调节效应检验。",
        }

    # ------------------------------------------------------------------
    # 偏误控制清单
    # ------------------------------------------------------------------
    def bias_control_checklist(self) -> Dict[str, Any]:
        return {
            "事后偏差防御": {
                "盲法评估设计": "结局标注与躯体信号编码由不知晓对方信息的研究员独立完成",
                "时间切片验证": "按时间排序案例，用前N个训练、预测第N+1个",
                "元认知监控": "记录分析前预测与推理，纳入敏感性分析",
            },
            "过拟合防御": {
                "检测": "样本外验证、交叉验证（k-fold/LOOCV）、置换检验",
                "预防": "正则化（L1/L2）、早停（early stopping）、特征选择",
                "简约性原则": "模型复杂度与样本量匹配",
            },
        }

    # ------------------------------------------------------------------
    # 报告生成
    # ------------------------------------------------------------------
    def run_full_validation(self, ecbm_data=None, repa_data=None, etds_data=None) -> str:
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "ecbm": self.validate_ecbm(ecbm_data),
            "repa": self.validate_repa(repa_data),
            "etds": self.validate_etds(etds_data),
            "bias_control": self.bias_control_checklist(),
        }
        return self.generate_report()

    def generate_report(self) -> str:
        lines = [
            "# QPMS 量子感知引擎算法效度验证报告",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 一、ECBM 躯体信号模块验证",
            "```json",
            json.dumps(self.results.get("ecbm", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 二、REPA 伦理对齐模块验证",
            "```json",
            json.dumps(self.results.get("repa", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 三、ETDS 涌现匹配模块验证",
            "```json",
            json.dumps(self.results.get("etds", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## 四、偏误控制机制检查清单",
            "```json",
            json.dumps(self.results.get("bias_control", {}), ensure_ascii=False, indent=2),
            "```",
        ]
        report_path = Path(self.workspace) / "memory" / f"qpms-validation-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="QPMS 量子感知引擎算法效度验证框架")
    parser.add_argument("--report", action="store_true", help="运行全套验证并生成报告")
    args = parser.parse_args()

    framework = QPMSValidationFramework()
    if args.report:
        path = framework.run_full_validation()
        print(f"验证报告已生成: {path}")
    else:
        path = framework.run_full_validation()
        print(f"验证报告已生成: {path}")


if __name__ == "__main__":
    main()
