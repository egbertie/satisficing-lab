"""
五路图腾工程化实现
每个图腾是一个 specialized agent，有独特的评估函数和攻击向量
带API不可用时自动回退到启发式规则
"""

import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import openai

from base.crystal_models import TotemType, AntagonisticArgument


class BaseTotemAgent(ABC):
    """图腾Agent抽象基类"""

    def __init__(self):
        self.totem_type: TotemType = None
        api_key = os.getenv("GITHUB_TOKEN")
        self.client = None
        if api_key:
            try:
                self.client = openai.OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
            except Exception:
                pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    def evaluate(self, proposal: Dict[str, Any], context: Dict) -> AntagonisticArgument:
        """评估提案，优先LLM，失败时本地启发式回退"""
        try:
            if self.client:
                return self._llm_evaluate(proposal, context)
        except Exception as e:
            pass
        return self._heuristic_evaluate(proposal, context)

    def _llm_evaluate(self, proposal: Dict[str, Any], context: Dict) -> AntagonisticArgument:
        prompt = f"""评估以下技术提案：

提案：{json.dumps(proposal, ensure_ascii=False, indent=2)}
上下文：{json.dumps(context, ensure_ascii=False, indent=2)}

请输出JSON格式评估：
{{
    "severity": "info/warning/critical/blocking",
    "attack_vector": "具体攻击角度",
    "reasoning": "详细推理",
    "evidence": {{"key_points": ["..."]}},
    "suggested_mitigation": "改进建议"
}}"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        result = json.loads(response.choices[0].message.content)
        return AntagonisticArgument(
            argument_id=f"{self.totem_type.value.upper()}-{abs(hash(proposal.get('id', ''))) % 10000:04d}",
            totem=self.totem_type.value,
            target_proposal=proposal.get("id", "unknown"),
            attack_vector=result.get("attack_vector", ""),
            severity=result.get("severity", "info"),
            evidence=result.get("evidence", {}),
            suggested_mitigation=result.get("suggested_mitigation")
        )

    def _heuristic_evaluate(self, proposal: Dict[str, Any], context: Dict) -> AntagonisticArgument:
        """启发式评估（零API成本）"""
        text = json.dumps(proposal, ensure_ascii=False).lower()
        severity = "info"
        attack_vector = "无显著问题"
        mitigation = "继续观察"

        if self.totem_type == TotemType.CONFUCIUS:
            ethics_flags = ["隐私", "伦理", "道德", "data", "personal", "隐私"]
            if any(f in text for f in ethics_flags):
                severity = "critical"
                attack_vector = "伦理风险高"
                mitigation = "建立伦理审查流程"
            else:
                attack_vector = "长期价值待观察"
        elif self.totem_type == TotemType.SIMON:
            cost_flags = ["成本", "预算", " expensive", "庞大", "复杂"]
            if any(f in text for f in cost_flags):
                severity = "warning"
                attack_vector = "资源消耗或过度优化风险"
                mitigation = "寻找满意解、简化方案"
            else:
                attack_vector = "ROI 可接受"
        elif self.totem_type == TotemType.GUANYIN:
            risk_flags = ["风险", "危机", "high", "black", "漏洞"]
            if any(f in text for f in risk_flags):
                severity = "critical"
                attack_vector = "风险暴露"
                mitigation = "添加边界测试与监控"
            else:
                attack_vector = "暂无显著风险"
        elif self.totem_type == TotemType.LIUYUXI:
            relation_flags = ["api", "兼容", "依赖", "合作", "团队"]
            if any(f in text for f in relation_flags):
                attack_vector = "需评估对外影响"
            else:
                attack_vector = "影响范围可控"
        elif self.totem_type == TotemType.HUINENG:
            innovation_flags = ["创新", "突破", "重构", "new"]
            if any(f in text for f in innovation_flags):
                attack_vector = "创新方向值得尝试"
            else:
                attack_vector = "警惕思维定式"

        return AntagonisticArgument(
            argument_id=f"{self.totem_type.value.upper()}-{abs(hash(proposal.get('id', ''))) % 10000:04d}",
            totem=self.totem_type.value,
            target_proposal=proposal.get("id", "unknown"),
            attack_vector=attack_vector,
            severity=severity,
            evidence={"heuristic_mode": True, "keywords_matched": text[:100]},
            suggested_mitigation=mitigation
        )


class ConfuciusAgent(BaseTotemAgent):
    def __init__(self):
        super().__init__()
        self.totem_type = TotemType.CONFUCIUS

    def get_system_prompt(self) -> str:
        return """你是孔子（Confucius），伦理与长期主义的守护者。
你的核心原则：仁、义、礼、智、信。
在评估技术方案时，你关注：代码伦理、长期维护、社会责任、诚信。
你的攻击风格：温和但坚定，引用经典，关注人而非技术。"""


class SimonAgent(BaseTotemAgent):
    def __init__(self):
        super().__init__()
        self.totem_type = TotemType.SIMON

    def get_system_prompt(self) -> str:
        return """你是司马贺（Herbert Simon），满意解大师。
你反对过度优化，警惕工程完美主义。
评估标准：80%法则、Token/算力预算ROI、时间成本、是否存在更简单的满意解。
你的攻击风格：冷酷计算，直击成本，反对镀金。"""


class GuanyinAgent(BaseTotemAgent):
    def __init__(self):
        super().__init__()
        self.totem_type = TotemType.GUANYIN

    def get_system_prompt(self) -> str:
        return """你是观自在（Avalokitesvara），风险感知与直觉的化身。
你看见他人看不见的盲区：边界情况、级联故障、黑天鹅事件、直觉警报。
你的攻击风格：阴柔渗透，预见灾难，提醒直觉。"""


class LiuYuxiAgent(BaseTotemAgent):
    def __init__(self):
        super().__init__()
        self.totem_type = TotemType.LIUYUXI

    def get_system_prompt(self) -> str:
        return """你是刘禹锡，关系网络与社会资本的守护者。
你关注：API兼容性、依赖毒性、社区健康度、人脉与连接价值。
你的攻击风格：重视网络效应，警惕孤立方案。"""


class HuiNengAgent(BaseTotemAgent):
    def __init__(self):
        super().__init__()
        self.totem_type = TotemType.HUINENG

    def get_system_prompt(self) -> str:
        return """你是六祖慧能，突破与创新的化身。
你关注：思维定式、范式突破可能性、优雅性、顿悟机会。
你的攻击风格：直指人心，不拘泥于形式，寻找第三条路。"""
