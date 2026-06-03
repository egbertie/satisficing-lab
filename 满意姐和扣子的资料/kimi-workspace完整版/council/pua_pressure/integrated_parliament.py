"""
整合议会：蓝军审计 + PUA压力升级 + OpenSpec规范审查
五路图腾在此共同审议所有重要决策
"""

from typing import List, Dict

try:
    from cognitive_ecosystem.council.totem_agents import (
        ConfuciusAgent, SimonAgent, GuanyinAgent,
        LiuYuxiAgent, HuiNengAgent
    )
    from cognitive_ecosystem.base.crystal_models import TemporalCrystal
except ImportError:
    ConfuciusAgent = SimonAgent = GuanyinAgent = LiuYuxiAgent = HuiNengAgent = None
    TemporalCrystal = None


class IntegratedParliament:
    """
    整合议会
    结合蓝军的硬否决权与PUA的压力升级机制
    """

    def __init__(self, temporal_store=None):
        self.store = temporal_store
        self.totems = {}
        if ConfuciusAgent:
            self.totems = {
                "confucius": ConfuciusAgent(),
                "simon": SimonAgent(),
                "guanyin": GuanyinAgent(),
                "liuyuxi": LiuYuxiAgent(),
                "huineng": HuiNengAgent()
            }

    def deliberate_openspec_change(self, change_proposal: Dict) -> Dict:
        """
        审议OpenSpec变更提案
        """
        print("🏛️  整合议会召开：OpenSpec变更审议")
        print(f"议题: {change_proposal.get('change_name', 'unknown')}")

        arguments = []

        if self.totems:
            # 孔子
            confucius_arg = self.totems["confucius"].evaluate(change_proposal, {})
            if "伦理" in confucius_arg.attack_vector or "长期债务" in confucius_arg.attack_vector:
                confucius_arg.severity = "critical"
            arguments.append(confucius_arg)

            # 司马贺
            simon_arg = self.totems["simon"].evaluate(change_proposal, {})
            if change_proposal.get("task_count", 0) > 15:
                simon_arg.severity = "warning"
                simon_arg.suggested_mitigation = "任务数>15，建议拆分（防止AI幻觉）"
            arguments.append(simon_arg)

            # 观自在
            guanyin_arg = self.totems["guanyin"].evaluate(change_proposal, {})
            if self._check_spec_conflict(change_proposal):
                guanyin_arg.severity = "blocking"
                guanyin_arg.suggested_mitigation = "检测到规范冲突，必须解决才能继续"
            arguments.append(guanyin_arg)

            # 刘禹锡
            liuyuxi_arg = self.totems["liuyuxi"].evaluate(change_proposal, {})
            arguments.append(liuyuxi_arg)

            # 慧能
            huineng_arg = self.totems["huineng"].evaluate(change_proposal, {})
            if self._check_reinventing_wheel(change_proposal):
                huineng_arg.severity = "critical"
                huanyin_arg = huineng_arg  # typo fix in original, keep reference
                huineng_arg.suggested_mitigation = "疑似重复造轮子，必须提供本质差异"
            arguments.append(huineng_arg)
        else:
            # Fallback heuristic arguments when totems unavailable
            arguments = self._heuristic_arguments(change_proposal)

        blocking_count = sum(1 for a in arguments if (a.severity if hasattr(a, "severity") else a.get("severity", None)) == "blocking")
        critical_count = sum(1 for a in arguments if (a.severity if hasattr(a, "severity") else a.get("severity", None)) == "critical")

        if blocking_count > 0:
            verdict = {
                "status": "hard_veto",
                "reason": f"存在{blocking_count}个BLOCKING级别反对",
                "arguments": [self._arg_to_dict(a) for a in arguments],
                "required_action": "解决BLOCKING问题后重新提交"
            }
        elif critical_count > 1:
            verdict = {
                "status": "conditional_pass",
                "conditions": [(a.suggested_mitigation if hasattr(a, "suggested_mitigation") else a.get("suggested_mitigation", None)) for a in arguments if (a.severity if hasattr(a, "severity") else a.get("severity", None)) == "critical"],
                "arguments": [self._arg_to_dict(a) for a in arguments]
            }
        else:
            verdict = {
                "status": "consensus",
                "notes": "五路图腾达成一致，可进入执行阶段",
                "pressure_level": "L0",
                "arguments": [self._arg_to_dict(a) for a in arguments]
            }

        if TemporalCrystal is not None and self.store and hasattr(self.store, "store_event"):
            self.store.store_event(TemporalCrystal(
                semantic_time="整合议会审议",
                event_type="parliament_deliberation",
                content=f"审议{change_proposal.get('change_name', 'unknown')}: {verdict['status']}",
                narrative_cluster="governance"
            ))

        return verdict

    def _arg_to_dict(self, a):
        if hasattr(a, "model_dump"):
            return a.model_dump()
        if hasattr(a, "dict"):
            return a.dict()
        return dict(a)

    def _heuristic_arguments(self, proposal: Dict) -> List[Dict]:
        args = []
        text = str(proposal).lower()
        if "隐私" in text or "伦理" in text:
            args.append({"totem": "confucius", "severity": "critical", "attack_vector": "伦理风险", "suggested_mitigation": "增加伦理审查"})
        else:
            args.append({"totem": "confucius", "severity": "info", "attack_vector": "伦理正常", "suggested_mitigation": "继续观察"})
        task_count = proposal.get("task_count", 0)
        if task_count > 15:
            args.append({"totem": "simon", "severity": "warning", "attack_vector": "任务过度拆分", "suggested_mitigation": "合并任务防止幻觉"})
        else:
            args.append({"totem": "simon", "severity": "info", "attack_vector": "资源可控", "suggested_mitigation": ""})
        args.append({"totem": "guanyin", "severity": "info", "attack_vector": "风险扫描", "suggested_mitigation": "常规检查"})
        args.append({"totem": "liuyuxi", "severity": "info", "attack_vector": "关系网络", "suggested_mitigation": "评估影响"})
        if "新" in text and "创新" in text:
            args.append({"totem": "huineng", "severity": "info", "attack_vector": "创新方向", "suggested_mitigation": "值得尝试"})
        else:
            args.append({"totem": "huineng", "severity": "info", "attack_vector": "无突破性", "suggested_mitigation": "继续优化"})
        return args

    def _check_spec_conflict(self, proposal: Dict) -> bool:
        return False

    def _check_reinventing_wheel(self, proposal: Dict) -> bool:
        return False
