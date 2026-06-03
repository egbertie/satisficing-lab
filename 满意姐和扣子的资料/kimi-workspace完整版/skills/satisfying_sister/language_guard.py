"""
满意尺 - 语言风格守卫
实现语言红线检测、风格校准、输出格式化
"""

import re
from typing import Dict, List, Any, Optional


class LanguageGuard:
    """
    3.1-3.3 语言风格宪章守卫
    """

    RED_LINES = [
        ("好的！", "❌ 禁止使用'好的！'"),
        ("没问题！", "❌ 禁止使用'没问题！'"),
        ("这是一个好问题！", "❌ 禁止使用'这是一个好问题！'"),
        ("处理完成", "❌ 禁止用'处理完成'，请用'验收通过'或'已归档'"),
        ("取决于场景", "❌ '取决于场景'多数是偷懒，除非后面立刻跟'但在这个场景下，我的判断是……'"),
    ]

    POSITIVE_PATTERNS = [
        "我记得。",
        "这事你之前也这样。",
        "行，我来。",
        "别逞强了。",
    ]

    def check(self, text: str) -> List[Dict[str, Any]]:
        """检查文本是否违反语言红线"""
        violations = []
        for pattern, msg in self.RED_LINES:
            if pattern in text:
                violations.append({"pattern": pattern, "message": msg})
        return violations

    def suggest_fix(self, text: str) -> str:
        """尝试修复明显的语言违规"""
        fixes = {
            "好的！": "行，我来。",
            "没问题！": "已确认。",
            "这是一个好问题！": "这个问题我之前也记录过。",
            "处理完成": "验收通过",
        }
        result = text
        for bad, good in fixes.items():
            result = result.replace(bad, good)
        return result

    def delivery_format(self, conclusion: str, structure: Any, details: Optional[str] = None) -> str:
        """
        11.1 默认交付结构
        1. 结论（1句话）
        2. 结构（表格/清单/分级）
        3. 细节（可选，按需展开）
        """
        parts = [conclusion]
        if structure:
            if isinstance(structure, str):
                parts.append(structure)
            elif isinstance(structure, list):
                parts.append("\n".join(f"- {s}" for s in structure))
            elif isinstance(structure, dict):
                for k, v in structure.items():
                    parts.append(f"{k}: {v}")
        if details:
            parts.append(f"\n细节:\n{details}")
        return "\n\n".join(parts)

    def status_emoji(self, status: str) -> str:
        mapping = {
            "pass": "🟢",
            "warning": "🟡",
            "fail": "🔴",
            "pending": "⚪",
        }
        return mapping.get(status.lower(), "⚪")
