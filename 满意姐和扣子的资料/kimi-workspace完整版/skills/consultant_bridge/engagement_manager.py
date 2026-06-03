"""
Consultant Bridge - 外援桥接系统
管理系统对外援（知识/技术）的接待、请求生成、结果内化与知识入库
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from defense_base_components import BaseComponent
from typing import Dict, List, Optional, Any
from datetime import datetime


class EngagementManager(BaseComponent):
    """
    外援 engagement 生命周期管理
    """

    CONSULTANT_TYPES = {
        "knowledge": {
            "name": "知识外援",
            "domain": "理论思考、知识收集、框架梳理、跨学科连接",
            "trigger_scenarios": [
                "需要引入新理论或跨学科视角",
                "现有知识框架无法解释观察到的现象",
                " token 预算紧张但需要深度研究",
                "需要人类专家的真实经验和直觉判断",
            ],
        },
        "technical": {
            "name": "技术外援",
            "domain": "技术难题攻关、架构升级、工程化规范、代码评审",
            "trigger_scenarios": [
                "技术债务积累到需要外部视角评估",
                "需要引入新的技术栈或工具链",
                "系统性能/安全/可维护性达到瓶颈",
                "需要建立可量化的技术评估体系",
                "自动化测试/部署/监控需要升级",
            ],
        },
    }

    def __init__(self):
        super().__init__("engagement_manager")
        self.active_requests = []

    def should_escalate(self, task: Dict[str, Any]) -> Optional[str]:
        """
        判定当前任务是否应优先寻求外援。
        返回 'knowledge' | 'technical' | None
        """
        complexity = task.get("complexity", "P2")
        domain = task.get("domain", "")
        token_budget = task.get("token_budget", 50000)
        estimated_tokens = task.get("estimated_tokens", token_budget)
        internal_exhausted = task.get("internal_attempts", 0) >= 2
        novel_theory_required = task.get("novel_theory_required", False)
        tech_stack = task.get("tech_stack", "")

        # 知识外援触发条件
        if novel_theory_required or domain in ("哲学", "经济学", "心理学", "组织行为", "决策科学"):
            return "knowledge"
        if estimated_tokens > token_budget * 0.8 and domain in ("研究", "框架设计", "方法论"):
            return "knowledge"

        # 技术外援触发条件
        if tech_stack or domain in ("软件工程", "架构", "性能优化", "安全审计", "DevOps"):
            return "technical"
        if complexity == "P0" and internal_exhausted:
            return "technical"
        if task.get("needs_external_audit", False):
            return "technical"

        return None

    def create_request(self, req_type: str, task_id: str, background: str, specific_asks: List[str], deliverables: List[str]) -> Dict[str, Any]:
        """生成标准化的外援请求单"""
        template = self.CONSULTANT_TYPES.get(req_type, {})
        request = {
            "task_id": task_id,
            "type": req_type,
            "type_name": template.get("name", req_type),
            "created_at": self.get_timestamp(),
            "background": background,
            "specific_asks": specific_asks,
            "expected_deliverables": deliverables,
            "status": "pending_dispatch",
        }
        self.active_requests.append(request)
        return request

    def ingest_feedback(self, request_id: str, feedback: str, evaluator: str = "蓝军+满意姐") -> Dict[str, Any]:
        """
        接收外援反馈后，生成内化任务单。
        """
        return {
            "request_id": request_id,
            "feedback_summary": feedback[:500],
            "ingestion_steps": [
                "1. 由蓝军进行对抗性审阅（事实核查+逻辑漏洞+假设检验）",
                "2. 由满意姐进行情感/伦理/适配性评估",
                "3. 将可验证的结论写入对应SKILL.md或AGENTS.md",
                "4. 将方法论更新到 cognitive_ecosystem/evolution/ 或 theory-miner/",
                "5. 将不可验证但高价值的假设放入'research_hypotheses'队列待验证",
                "6. 生成一条 MEMORY.md 指针，指向内化后的物理文件",
            ],
            "evaluator": evaluator,
            "timestamp": self.get_timestamp(),
        }
