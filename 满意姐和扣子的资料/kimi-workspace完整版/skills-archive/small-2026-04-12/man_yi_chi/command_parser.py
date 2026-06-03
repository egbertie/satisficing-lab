"""
满意尺 - 五段式指令解析器
"""

import re
from typing import Dict, Optional, Any


class CommandParser:
    """
    4.1 五段式指令结构解析器
    [角色] {当前激活的角色}
    [上下文] {项目背景，限100字}
    [输入] {具体任务/问题}
    [约束] {输出限制，如字数/格式/Token预算}
    [阻塞条件] {未完成前禁止继续的条件}
    """

    SEGMENTS = ["角色", "上下文", "输入", "约束", "阻塞条件"]

    def parse(self, text: str) -> Dict[str, Any]:
        """解析五段式指令"""
        result = {seg: "" for seg in self.SEGMENTS}
        result["is_five_segment"] = False
        result["raw"] = text

        # 检测是否使用了五段式结构
        for seg in self.SEGMENTS:
            # 支持 [角色] 和 【角色】 两种形式
            pattern = rf"[\[【]{seg}[\]】]\s*(.*?)(?=[\[【](?:{'|'.join(self.SEGMENTS)})[\]】]|\Z)"
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                result[seg] = matches[-1].strip()
                result["is_five_segment"] = True

        return result

    def validate(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """验证五段式完整性"""
        filled = sum(1 for seg in self.SEGMENTS if parsed.get(seg))
        return {
            "valid": filled >= 3,  # 至少3个段填写算有效
            "filled_segments": filled,
            "missing_segments": [seg for seg in self.SEGMENTS if not parsed.get(seg)],
        }
