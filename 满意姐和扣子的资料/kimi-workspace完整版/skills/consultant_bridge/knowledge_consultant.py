"""
Knowledge Consultant - 知识外援专用模块
负责生成知识请求模板、管理知识入库流程、持续学习追踪
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from defense_base_components import BaseComponent
from typing import Dict, List, Any


class KnowledgeConsultant(BaseComponent):
    """
    知识外援咨询规范
    """

    def __init__(self):
        super().__init__("knowledge_consultant")

    def generate_request(
        self,
        topic: str,
        current_framework: str,
        observed_gaps: List[str],
        desired_depth: str = "学术级但可落地",
    ) -> Dict[str, Any]:
        """
        生成面向知识外援的详细请求文档。
        假设外援是第一次接触我们的系统，背景必须充分、要求必须细致。
        """
        return {
            "request_type": "knowledge_consultant",
            "topic": topic,
            "background": current_framework,
            "gaps": observed_gaps,
            "depth": desired_depth,
            "questions": [
                f"关于'{topic}'，当前学术界或产业界有哪些最新且经过验证的理论进展？",
                f"这些理论与我们的现有框架'{current_framework}'之间，存在哪些可桥接或可冲突的地方？",
                "请给出至少2个可直接应用于我们系统的具体建议（要足够细致，达到'第一次接触者也能按图索骥'的程度）。",
                "如果我们要自行深入研究这个方向，推荐的阅读路径/资料/工具是什么？",
                "这个领域有哪些常见的认知陷阱或伪理论需要我们警惕？",
            ],
            "constraints": [
                "所有推荐必须附带来源（论文/书籍/权威机构报告）",
                "如果存在相互矛盾的理论，请明确列出并给出你的判断依据",
                "避免过于抽象的概念堆砌，每个概念请给出在我们的业务场景下的映射示例",
            ],
            "ingestion_plan": {
                "step1": "收到回复后，蓝军进行来源独立性和逻辑一致性审查",
                "step2": "满意姐评估情感适配性和文化兼容性（特别是儒商哲学维度）",
                "step3": "将可立即落地的建议转化为代码/文档/SKILL.md更新",
                "step4": "将理论性内容存入 theory-miner/ 并建立与现有知识图谱的链接",
                "step5": "在 MEMORY.md 中建立索引指针，便于未来检索引用",
            },
        }

    def learning_loop(self, ingested_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        知识内化后的持续学习循环
        """
        return {
            "next_questions": [
                "基于上次外援的输入，我们在实际应用中遇到了什么偏差？",
                "这些偏差是因为理论本身不适用，还是我们的 implementation 有问题？",
                "是否有新的观察可以进一步验证或证伪该理论？",
            ],
            "token_saving_notes": [
                "将外援的高价值回复提炼为'决策卡片'（≤200字），替代每次长篇复述",
                "建立'已知问题清单'，避免重复向外援询问同一类问题",
                "使用知识图谱链接替代完整文本引用",
            ],
        }
