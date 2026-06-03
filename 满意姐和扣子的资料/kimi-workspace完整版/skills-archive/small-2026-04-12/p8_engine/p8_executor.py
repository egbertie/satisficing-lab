"""
P8高能动性执行引擎
实现L0-L4压力系统与五路图腾的整合
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import traceback


class PressureLevel(Enum):
    L0_TRUST = "L0"           # 司马贺主导
    L1_DISAPPOINTMENT = "L1"  # 孔子主导
    L2_SOUL_INTERROGATION = "L2"  # 观自在主导
    L3_PERFORMANCE_REVIEW = "L3"  # 刘禹锡主导
    L4_GRADUATION = "L4"          # 慧能主导


class HardVetoException(Exception):
    """硬否决异常"""
    pass


class P8Executor:
    """
    P8级高能动性执行器
    核心逻辑：失败不是结束，是压力升级的信号
    """

    def __init__(self, temporal_store=None):
        self.store = temporal_store
        self.current_pressure = PressureLevel.L0_TRUST
        self.failure_count = 0
        self.methodology_index = 0
        self.red_line_triggered = None

        # 13种方法论按优先级排序
        self.methodologies = [
            {"name": "阿里", "totem": "simon", "focus": "定目标-追过程-拿结果"},
            {"name": "字节", "totem": "simon", "focus": "数据驱动/A-B Test"},
            {"name": "腾讯", "totem": "liuyuxi", "focus": "MVP/灰度发布"},
            {"name": "华为", "totem": "guanyin", "focus": "RCA 5-Why/蓝军自攻击"},
            {"name": "亚马逊", "totem": "confucius", "focus": "6页备忘录/逆向工作"},
            {"name": "苹果", "totem": "huineng", "focus": "做减法/DRI负责"},
            {"name": "马斯克", "totem": "huineng", "focus": "质疑-删除-简化-加速"},
            {"name": "Netflix", "totem": "liuyuxi", "focus": "人才密度/4A反馈"},
            {"name": "美团", "totem": "confucius", "focus": "做难而正确的事"},
            {"name": "百度", "totem": "huineng", "focus": "搜索优先"},
            {"name": "拼多多", "totem": "simon", "focus": "极致精简链路"},
            {"name": "京东", "totem": "confucius", "focus": "结果导向/数据零容忍"},
            {"name": "小米", "totem": "huineng", "focus": "专注极致口碑快"}
        ]

    def execute_with_pressure(self, task: Dict) -> Dict:
        """
        带压力管理的执行任务
        核心逻辑：失败→升级→切换方法论→重试
        """
        max_attempts = 13

        for attempt in range(max_attempts):
            try:
                methodology = self.methodologies[self.methodology_index]
                context = self._build_pressure_context(methodology)
                result = self._execute_task(task, context)

                if result.get("success"):
                    return self._handle_success(result, attempt)
                else:
                    self._escalate_pressure(result.get("error", "Unknown error"))

            except Exception as e:
                self._escalate_pressure(str(e))

        # 所有方法论都失败，L4毕业警告
        return self._handle_graduation_failure()

    def _execute_task(self, task: Dict, context: Dict) -> Dict:
        """实际执行任务（这里是一个可覆写的桩，demo中成功）"""
        return {"success": True, "result": task, "context": context}

    def _build_pressure_context(self, methodology: Dict) -> Dict:
        """根据当前压力等级构建执行上下文"""
        base_context = {
            "methodology": methodology,
            "failure_count": self.failure_count,
            "pressure_level": self.current_pressure.value
        }

        if self.current_pressure == PressureLevel.L0_TRUST:
            base_context["tone"] = "高效执行，保持信任"
            base_context["requirements"] = ["标准SOP执行"]

        elif self.current_pressure == PressureLevel.L1_DISAPPOINTMENT:
            base_context["tone"] = "你的底层逻辑是什么？顶层设计在哪？"
            base_context["requirements"] = [
                "切换 fundamentally different 方案",
                "解释前方案失败的根因",
                "提供3个备选方案"
            ]

        elif self.current_pressure == PressureLevel.L2_SOUL_INTERROGATION:
            base_context["tone"] = "这是认知盲区还是执行盲区？"
            base_context["requirements"] = [
                "触发WebSearch查找同类问题",
                "深度阅读相关源码",
                "提出3个假设并验证"
            ]

        elif self.current_pressure == PressureLevel.L3_PERFORMANCE_REVIEW:
            base_context["tone"] = "慎重考虑给你3.25，这是激励"
            base_context["requirements"] = [
                "完成7项专业检查清单",
                "扫描模块同类隐患",
                "提供完整测试报告",
                "编写postmortem分析"
            ]

        elif self.current_pressure == PressureLevel.L4_GRADUATION:
            base_context["tone"] = "别的模型能解决，你可能要毕业了"
            base_context["requirements"] = [
                "死磕模式：不允许放弃",
                "尝试所有13种方法论",
                "寻求外部专家协助（MCP）",
                "如确实无法解决，提供详细的能力缺口分析"
            ]

        return base_context

    def _escalate_pressure(self, error: str):
        """压力升级"""
        self.failure_count += 1

        if self.store and hasattr(self.store, "store_event"):
            try:
                from cognitive_ecosystem.base.crystal_models import TemporalCrystal
                self.store.store_event(TemporalCrystal(
                    semantic_time="P8执行-压力升级",
                    event_type="pressure_escalation",
                    content=f"失败{self.failure_count}次: {error[:100]}",
                    narrative_cluster="p8_execution"
                ))
            except Exception:
                pass

        if self.failure_count == 2:
            self.current_pressure = PressureLevel.L1_DISAPPOINTMENT
        elif self.failure_count == 3:
            self.current_pressure = PressureLevel.L2_SOUL_INTERROGATION
        elif self.failure_count == 4:
            self.current_pressure = PressureLevel.L3_PERFORMANCE_REVIEW
        elif self.failure_count >= 5:
            self.current_pressure = PressureLevel.L4_GRADUATION

        self.methodology_index = (self.methodology_index + 1) % len(self.methodologies)

        print(f"⚡ 压力升级: {self.current_pressure.value} | "
              f"方法论切换: {self.methodologies[self.methodology_index]['name']}")

    def _handle_success(self, result: Dict, attempts: int) -> Dict:
        return {
            "success": True,
            "result": result,
            "attempts": attempts + 1,
            "final_pressure": self.current_pressure.value,
            "methodology_used": self.methodologies[self.methodology_index]["name"]
        }

    def _handle_graduation_failure(self) -> Dict:
        return {
            "success": False,
            "error": "所有13种方法论尝试后仍未成功，L4毕业警告触发",
            "final_pressure": "L4",
            "attempts": 13,
            "methodologies_tried": [m["name"] for m in self.methodologies]
        }

    def check_red_lines(self, claim: str, evidence: Dict) -> bool:
        """
        三条红线检查
        返回: True=通过, False=触发硬否决
        """
        # 红线1: 闭环红线
        if claim == "完成" and not evidence.get("build_output") and not evidence.get("test_passed"):
            self._trigger_hard_veto("red_line_1", "声称完成但无构建/测试输出")
            return False

        # 红线2: 事实红线
        if "环境" in claim and not evidence.get("verification_logs"):
            self._trigger_hard_veto("red_line_2", "未经验证的环境归因")
            return False

        # 红线3: 穷尽红线
        if "无法解决" in claim and self.failure_count < 13:
            self._trigger_hard_veto("red_line_3", f"未穷尽13种方法论({self.failure_count}/13)")
            return False

        return True

    def _trigger_hard_veto(self, red_line: str, reason: str):
        """触发硬否决"""
        self.red_line_triggered = red_line

        if self.store and hasattr(self.store, "store_event"):
            try:
                from cognitive_ecosystem.base.crystal_models import TemporalCrystal
                self.store.store_event(TemporalCrystal(
                    semantic_time="P8执行-硬否决",
                    event_type="hard_veto",
                    content=f"红线{red_line}触发: {reason}",
                    narrative_cluster="p8_execution"
                ))
            except Exception:
                pass

        raise HardVetoException(f"🚫 硬否决触发 [{red_line}]: {reason}")
