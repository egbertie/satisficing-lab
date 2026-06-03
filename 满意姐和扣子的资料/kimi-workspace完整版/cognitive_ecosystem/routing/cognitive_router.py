"""
认知路由层：五路图腾作为动态路由器
"""

import os
from typing import Dict, List, Optional
from enum import Enum
import numpy as np
import openai

from memory.temporal_store import TemporalCrystalStore


class CognitiveState(Enum):
    EXPLORATION = "exploration"
    CRISIS = "crisis"
    ETHICAL_DILEMMA = "ethical"
    RESOURCE_CONSTRAINT = "resource"
    SOCIAL_BINDING = "social"
    ROUTINE = "routine"


class CognitiveRouter:
    """
    认知路由器：基于输入语义和系统状态，动态路由到处理管道
    """

    def __init__(self, temporal_store: Optional[TemporalCrystalStore] = None):
        self.temporal_store = temporal_store
        self.client = openai.OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=os.getenv("GITHUB_TOKEN")
        )

    def route(self, user_input: str, current_context: Dict = None) -> Dict:
        """主路由函数"""
        current_context = current_context or {}
        current_state = self._detect_cognitive_state(user_input, current_context)
        totem_weights = self._calculate_totem_weights(current_state)
        pipeline = self._select_pipeline(totem_weights, current_state)
        return {
            "pipeline": pipeline,
            "totem_weights": totem_weights,
            "cognitive_state": current_state.value,
            "routing_reason": self._generate_rationale(totem_weights, current_state)
        }

    def _detect_cognitive_state(self, text: str, context: Dict) -> CognitiveState:
        """基于规则+可选LLM的零成本状态检测"""
        text_lower = text.lower()
        crisis_signals = ["删除", "清空", "风险", "危机", "错误", "失败", "污染", "崩溃"]
        ethical_signals = ["伦理", "道德", "隐私", "价值观", "诚信", "对错"]
        resource_signals = ["优化", "成本", "预算", "效率", "配额", "节省", "简化"]
        social_signals = ["关系", "合作", "伙伴", "团队", "人际", "连接"]
        explore_signals = ["创新", "突破", "新方案", "重构", "跃迁", "范式"]

        scores = {
            CognitiveState.CRISIS: sum(1 for s in crisis_signals if s in text_lower),
            CognitiveState.ETHICAL_DILEMMA: sum(1 for s in ethical_signals if s in text_lower),
            CognitiveState.RESOURCE_CONSTRAINT: sum(1 for s in resource_signals if s in text_lower),
            CognitiveState.SOCIAL_BINDING: sum(1 for s in social_signals if s in text_lower),
            CognitiveState.EXPLORATION: sum(1 for s in explore_signals if s in text_lower),
        }

        # 上下文加成
        if context.get("risk_level") == "high" or context.get("previous_errors", 0) > 2:
            scores[CognitiveState.CRISIS] += 2
        if context.get("stuck_iterations", 0) > 3:
            scores[CognitiveState.EXPLORATION] += 2

        max_state = max(scores, key=scores.get)
        if scores[max_state] == 0:
            return CognitiveState.ROUTINE
        return max_state

    def _calculate_totem_weights(self, state: CognitiveState) -> Dict[str, float]:
        """计算五路图腾的激活权重"""
        base_weights = {
            "confucius": 0.2,
            "simon": 0.2,
            "guanyin": 0.2,
            "liuyuxi": 0.2,
            "huineng": 0.2
        }
        state_boost = {
            CognitiveState.ETHICAL_DILEMMA: {"confucius": 0.6},
            CognitiveState.RESOURCE_CONSTRAINT: {"simon": 0.6},
            CognitiveState.CRISIS: {"guanyin": 0.6},
            CognitiveState.SOCIAL_BINDING: {"liuyuxi": 0.6},
            CognitiveState.EXPLORATION: {"huineng": 0.6}
        }
        if state in state_boost:
            for totem, boost in state_boost[state].items():
                base_weights[totem] += boost
        exp_scores = {k: np.exp(v) for k, v in base_weights.items()}
        total = sum(exp_scores.values())
        return {k: v / total for k, v in exp_scores.items()}

    def _select_pipeline(self, weights: Dict[str, float], state: CognitiveState) -> str:
        """基于权重选择处理管道"""
        max_totem = max(weights, key=weights.get)
        if state == CognitiveState.CRISIS and weights["guanyin"] > 0.4:
            return "risk_analysis"
        if state == CognitiveState.ETHICAL_DILEMMA and weights["confucius"] > 0.4:
            return "ethical_audit"
        if state == CognitiveState.RESOURCE_CONSTRAINT and weights["simon"] > 0.4:
            return "satisficing_process"
        if state == CognitiveState.EXPLORATION and weights["huineng"] > 0.4:
            return "lateral_thinking"
        if state == CognitiveState.SOCIAL_BINDING and weights["liuyuxi"] > 0.4:
            return "relationship_mode"
        return "standard_processing"

    def _generate_rationale(self, weights: Dict[str, float], state: CognitiveState) -> str:
        """生成路由理由"""
        dominant = max(weights, key=weights.get)
        return f"状态识别为 {state.value}，由 {dominant} 图腾主导 ({weights[dominant]:.0%})"
