"""
满意尺 - 意图契约系统
"""

from typing import Dict, Any, Optional


class IntentContract:
    """
    4.2 意图契约
    在复杂任务启动前，必须给出：
    1. 理解重述
    2. 目标状态
    3. 成功标准
    4. 边界条件
    阻塞规则：用户未确认，不得进入执行阶段
    """

    def build_contract(self, user_request: str, complexity: str = "auto") -> Dict[str, Any]:
        """
        自动生成意图契约
        complexity: P0/P1任务默认需要契约；P2/P3可选
        """
        contract = {
            "understanding": f"我看到的任务是：{user_request[:120]}..." if len(user_request) > 120 else f"我看到的任务是：{user_request}",
            "target_state": "完成后，相关文件/代码/报告将按约定路径存放，并通过基础验证。",
            "success_criteria": "1) 可运行的实现或完整的文档 2) 基础自检通过 3) 物理路径明确",
            "boundaries": "不修改SOUL.md/USER.md/AGENTS.md等bootstrap文件；不执行未确认的对外操作；无外部API时自动降级。",
            "confirmed": False,
            "blocking": complexity in ("P0", "P1", "auto"),
        }
        return contract

    def confirm(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """用户确认契约"""
        contract["confirmed"] = True
        contract["blocking"] = False
        return contract

    def is_ready_to_execute(self, contract: Optional[Dict[str, Any]]) -> bool:
        """检查是否可以进入执行阶段"""
        if contract is None:
            return True
        if not contract.get("blocking", False):
            return True
        return contract.get("confirmed", False)
