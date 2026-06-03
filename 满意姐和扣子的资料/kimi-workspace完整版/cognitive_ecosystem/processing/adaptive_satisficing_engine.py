"""
Adaptive Satisficing Engine - 满意解停止规则精确化
秘书问题变体 + 前景理论调整
"""

import math
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class SatisficingResult:
    should_stop: bool
    current_best_index: int
    current_best_score: float
    stopping_rationale: str
    expected_regret: float


class AdaptiveSatisficingEngine:
    """
    自适应满意解引擎
    """

    def __init__(self, loss_aversion_lambda: float = 2.25):
        self.loss_aversion = loss_aversion_lambda

    def evaluate_sequence(self, scores: List[float], aspiration_level: float,
                          search_cost_per_step: float = 0.02) -> SatisficingResult:
        """
        基于秘书问题变体和前景理论的停止决策。
        scores: 已观察候选人的评分列表（按顺序）
        aspiration_level: 满意阈值（0-1）
        search_cost_per_step: 每多搜索一步的代价
        """
        n = len(scores)
        if n == 0:
            return SatisficingResult(False, -1, 0.0, "无样本，继续搜索", 1.0)

        current_best = max(scores)
        current_best_idx = scores.index(current_best)

        # 秘书问题最优停止边界：当 n 较大时，前 ~n/e 个作为观察期
        observation_threshold = max(1, int(n / math.e))

        # 前景理论调整：如果当前最佳已超过满意阈值，考虑停止
        above_aspiration = current_best >= aspiration_level

        # 边际收益递减：后续找到一个明显更好的候选人的概率
        remaining = len(scores)  # 假设无限总体时，用当前样本估计
        if remaining > 0:
            prob_better = sum(1 for s in scores if s > current_best) / remaining
            marginal_benefit = prob_better * (1.0 - current_best)
        else:
            marginal_benefit = 0.0

        # 损失厌恶：如果已有控制权/高评分，更倾向于停止（害怕失去当前最佳）
        if current_best >= 0.8:
            loss_premium = self.loss_aversion * 0.05
        else:
            loss_premium = 0.0

        should_stop = False
        rationale = ""

        if above_aspiration and n >= observation_threshold:
            effective_cost = search_cost_per_step + loss_premium
            if marginal_benefit <= effective_cost:
                should_stop = True
                rationale = (
                    f"当前最佳 {current_best:.2f} 已达到满意阈值 {aspiration_level:.2f}，"
                    f"且边际收益 {marginal_benefit:.3f} <= 有效搜索成本 {effective_cost:.3f}，"
                    f"应停止搜索。"
                )
            else:
                rationale = f"虽达阈值，但边际收益 {marginal_benefit:.3f} 仍高于成本，可继续。"
        else:
            rationale = f"观察样本数 {n} 不足阈值 {observation_threshold} 或当前最佳 {current_best:.2f} 未达阈值 {aspiration_level:.2f}。"

        # 预期后悔值（如果现在就停止，后续可能失去多大收益）
        expected_regret = marginal_benefit * (1 - prob_better) if remaining > 0 else 0.0

        return SatisficingResult(
            should_stop=should_stop,
            current_best_index=current_best_idx,
            current_best_score=current_best,
            stopping_rationale=rationale,
            expected_regret=expected_regret
        )

    def satisficing_checklist(self, scores: List[float], context: Dict) -> Dict:
        """
        生成"满意解检查清单"
        """
        aspiration = context.get("aspiration_level", 0.75)
        result = self.evaluate_sequence(scores, aspiration)

        return {
            "已经达到满意解的5个信号": [
                "1. 当前最佳选项评分 ≥ 预设满意阈值",
                "2. 观察样本数已超过秘书问题的最优停止点（n/e）",
                "3. 继续搜索的边际收益 ≤ 边际成本",
                "4. 没有出现显著超预期的新信息（无黑天鹅信号）",
                "5. 时间/Token/注意力预算已使用超过70%",
            ],
            "仍在最优解陷阱中的5个危险信号": [
                "1. 持续因为'可能有更好的'而拒绝已达标的选项",
                "2. 搜索成本已经超过选项本身价值的一半",
                "3. 对未来选项的评估过度乐观（计划谬误）",
                "4. 同一批候选人反复比较超过3轮",
                "5. 决策者自述'再给我一点时间'超过2次",
            ],
            "信息已够用的3个操作性测试": [
                f"测试1：当前最高分 {result.current_best_score:.2f} ≥ 阈值 {aspiration:.2f}？{'是' if result.current_best_score >= aspiration else '否'}",
                f"测试2：若此时停止，预期后悔值 {result.expected_regret:.3f} < 0.1？{'是' if result.expected_regret < 0.1 else '否'}",
                f"测试3：{'系统建议停止' if result.should_stop else '系统建议继续搜索'}",
            ],
            "decision": result
        }
