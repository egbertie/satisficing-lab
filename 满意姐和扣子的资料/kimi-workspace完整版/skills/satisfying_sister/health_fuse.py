"""
满意尺 - 健康与熔断系统
实现Token熔断、相似输出检测、置信度怀疑模式、超时机制
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from defense_base_components import BaseComponent
from typing import Dict, List, Any, Optional
import time
import difflib


class HealthFuse(BaseComponent):
    """
    14.4 熔断与健康机制
    """

    def __init__(self):
        super().__init__("health_fuse")
        self.output_history = []
        self.low_confidence_count = 0

    def check_token_budget(self, used: int, budget: int) -> Dict[str, Any]:
        """Token超预算200% → 自动暂停"""
        ratio = used / budget if budget > 0 else 0
        if ratio > 2.0:
            return {
                "triggered": True,
                "level": "🔴高危",
                "message": f"Token已用 {used}/{budget}（{ratio*100:.0f}%），超预算200%。建议暂停或压缩上下文。",
                "action": "PAUSE",
            }
        elif ratio > 1.5:
            return {
                "triggered": True,
                "level": "🟡中危",
                "message": f"Token已用 {used}/{budget}（{ratio*100:.0f}%），接近上限。",
                "action": "WARN",
            }
        return {"triggered": False, "level": "🟢", "message": "Token预算正常", "action": "CONTINUE"}

    def check_similarity(self, new_output: str, threshold: float = 0.80) -> Dict[str, Any]:
        """连续3次相似输出（>80%）→ 强制退出"""
        self.output_history.append(new_output)
        if len(self.output_history) > 3:
            self.output_history.pop(0)

        if len(self.output_history) == 3:
            # 简单基于共同子串比例判断
            s1, s2, s3 = self.output_history
            sim12 = self._simple_similarity(s1, s2)
            sim23 = self._simple_similarity(s2, s3)
            if sim12 > threshold and sim23 > threshold:
                return {
                    "triggered": True,
                    "level": "🔴高危",
                    "message": "连续3次输出相似度>80%，强制退出当前任务，请求外部视角。",
                    "action": "EXIT",
                }
        return {"triggered": False, "level": "🟢", "message": "输出多样性正常", "action": "CONTINUE"}

    def _simple_similarity(self, a: str, b: str) -> float:
        """基于difflib.SequenceMatcher的相似度（更快更稳）"""
        if not a or not b:
            return 0.0
        return difflib.SequenceMatcher(None, a, b).ratio()

    def check_confidence(self, confidence: float) -> Dict[str, Any]:
        """置信度<0.5的论断>3个 → 进入怀疑模式"""
        if confidence < 0.5:
            self.low_confidence_count += 1
        else:
            self.low_confidence_count = max(0, self.low_confidence_count - 1)

        if self.low_confidence_count > 3:
            return {
                "triggered": True,
                "level": "🟡中危",
                "message": "连续出现多个低置信度论断，进入怀疑模式。",
                "action": "SUSPICIOUS",
                "note": "此处存疑",
            }
        return {"triggered": False, "level": "🟢", "message": "置信度正常", "action": "CONTINUE"}

    def wrap_with_timeout(self, func, timeout: int = 300):
        """为函数添加超时保护（基于信号的简化版，主要用于说明）"""
        import signal

        def handler(signum, frame):
            raise TimeoutError(f"函数执行超过{timeout}秒，已强制退出")

        old_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)
        try:
            result = func()
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        return result
