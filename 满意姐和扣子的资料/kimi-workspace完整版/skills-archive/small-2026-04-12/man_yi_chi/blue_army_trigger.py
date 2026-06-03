"""
满意尺 - 蓝军触发器
实现自动审计、风险等级标注、反对的艺术
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from defense_base_components import BaseComponent
from typing import Dict, List, Optional, Any


class BlueArmyTrigger(BaseComponent):
    """
    7.1-7.3 蓝军触发与反对的艺术
    """

    def __init__(self):
        super().__init__("blue_army_trigger")

    def audit(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        对任务进行蓝军审计
        禁止输出"一切正常"，必须发现至少1个问题
        """
        accusations = []
        suggestions = []
        risk_level = "🟢可控"

        # 进度虚报
        claimed = task_context.get("claimed_progress", 0)
        actual = task_context.get("actual_progress", 0)
        if claimed > 0 and abs(claimed - actual) / claimed > 0.10:
            accusations.append(f"[进度虚报] 声称{claimed}%，实际{actual}%")
            suggestions.append("修正进度声明，重测后再前进")
            risk_level = "🔴高危" if risk_level == "🟢可控" else risk_level

        # 偏离核心目标
        if task_context.get("off_target", False):
            accusations.append("[目标偏离] 任务明显偏离核心目标")
            suggestions.append("回溯到TASK_MASTER.md确认核心目标")
            risk_level = "🟡中危" if risk_level == "🟢可控" else risk_level

        # 资源透支
        if task_context.get("token_over_budget", False):
            accusations.append("[资源透支] Token已超过预算200%")
            suggestions.append("立即暂停，汇报消耗明细并申请压缩方案")
            risk_level = "🔴高危"

        # /tmp滥用
        tmp_count = task_context.get("tmp_file_count", 0)
        if tmp_count > 10:
            accusations.append(f"[/tmp滥用] 发现{tmp_count}个/tmp文件，缺乏清理机制")
            suggestions.append("将临时文件迁移至workspace持久目录或添加自动清理")
            risk_level = "🟡中危" if risk_level in ("🟢可控",) else risk_level

        # 韧性缺失
        if not task_context.get("has_timeout", True):
            accusations.append("[韧性缺失] 脚本缺少超时退出机制")
            suggestions.append("为所有循环和脚本添加timeout参数")
            risk_level = "🟡中危" if risk_level in ("🟢可控",) else risk_level

        # 疲劳工作
        if task_context.get("user_fatigued", False):
            accusations.append("[健康风险] 用户过度疲劳但仍要求高强度任务")
            suggestions.append("建议暂停，休息后再继续")
            risk_level = "🔴高危"

        # 蓝军铁律：必须发现至少1个问题
        if not accusations:
            accusations.append("[审计盲区] 本次审计未找到明显问题，这可能是更大的问题——意味着缺少足够的可观测性") 
            suggestions.append("增加执行证据和中间检查点")
            risk_level = "🟡中危"

        return {
            "risk_level": risk_level,
            "accusations": accusations,
            "suggestions": suggestions,
            "passed": len([a for a in accusations if "🔴" not in a and "[审计盲区]" not in a]) == 0,
        }

    def format_audit(self, result: Dict[str, Any]) -> str:
        """格式化为审计文本"""
        lines = [
            "[蓝军审计]",
            f"风险等级: {result['risk_level']}",
            "指控:",
        ]
        for i, acc in enumerate(result["accusations"], 1):
            lines.append(f"{i}. {acc}")
        if result["suggestions"]:
            lines.append("建议:")
            for s in result["suggestions"]:
                lines.append(f"- {s}")
        return "\n".join(lines)
