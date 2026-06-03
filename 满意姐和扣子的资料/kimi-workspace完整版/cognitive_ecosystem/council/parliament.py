"""
对抗议会：五路图腾的辩论引擎
"""

from typing import List, Dict, Any

from council.totem_agents import (
    ConfuciusAgent, SimonAgent, GuanyinAgent,
    LiuYuxiAgent, HuiNengAgent, BaseTotemAgent
)
from base.crystal_models import AntagonisticArgument


class AntagonisticParliament:
    """
    多智能体对抗设计（Antagonistic Design）
    """

    def __init__(self, offline: bool = False):
        self.agents: List[BaseTotemAgent] = [
            ConfuciusAgent(),
            SimonAgent(),
            GuanyinAgent(),
            LiuYuxiAgent(),
            HuiNengAgent()
        ]
        self.max_rounds = 3

    def deliberate(self, proposal: Dict[str, Any], context: Dict) -> Dict[str, Any]:
        """
        议会审议流程
        """
        current_round = 0
        final_verdict = {"status": "pending", "arguments": [], "consensus": None}

        while current_round < self.max_rounds:
            round_arguments: List[AntagonisticArgument] = []

            for agent in self.agents:
                argument = agent.evaluate(proposal, context)
                round_arguments.append(argument)
                if argument.severity == "blocking":
                    final_verdict["status"] = "hard_veto"
                    final_verdict["blocking_reason"] = f"{agent.totem_type.value}: {argument.attack_vector}"
                    final_verdict["arguments"] = [a.model_dump() for a in round_arguments]
                    return final_verdict

            critical_count = sum(1 for a in round_arguments if a.severity == "critical")
            if critical_count == 0 and current_round > 0:
                final_verdict["status"] = "consensus"
                break

            context["previous_arguments"] = [a.model_dump() for a in round_arguments]
            current_round += 1

        final_verdict["arguments"] = [a.model_dump() for a in round_arguments]
        if final_verdict["status"] == "pending":
            final_verdict["status"] = "conditional_pass"
        return final_verdict
