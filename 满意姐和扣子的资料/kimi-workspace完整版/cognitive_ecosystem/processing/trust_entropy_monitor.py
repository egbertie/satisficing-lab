"""
Trust Entropy Monitor - 合伙人信任崩塌STAGE-D五阶段熵增模型
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class TrustStage(Enum):
    S1_SIGNAL_NEGLECT = "S1-信号忽视"
    S2_ATTRIBUTION_BIAS = "S2-归因偏置"
    S3_ESCALATION_OF_COMMITMENT = "S3-承诺升级"
    S4_AFFECTIVE_POLARIZATION = "S4-情感极化"
    S5_STRUCTURAL_LOCK_IN = "S5-结构锁定"


@dataclass
class StageSignal:
    stage: TrustStage
    severity: str  # green | yellow | red
    observable_evidence: List[str]
    recommendation: str


@dataclass
class TrustEntropyReport:
    current_stage: TrustStage
    stage_history: List[Dict]
    overall_entropy_score: float  # 0-100, 越高越危险
    signals: List[StageSignal]
    intervention_priority: List[str]


class TrustEntropyMonitor:
    """信任熵增监测器"""

    def __init__(self):
        self.stage_thresholds = {
            TrustStage.S1_SIGNAL_NEGLECT: {
                "metric": "回避困难对话次数/周",
                "yellow": 2,
                "red": 4,
            },
            TrustStage.S2_ATTRIBUTION_BIAS: {
                "metric": "外归因/内归因比值",
                "yellow": 2.0,
                "red": 3.5,
            },
            TrustStage.S3_ESCALATION_OF_COMMITMENT: {
                "metric": "重复失败路径投入次数",
                "yellow": 2,
                "red": 3,
            },
            TrustStage.S4_AFFECTIVE_POLARIZATION: {
                "metric": "公开指责/羞辱事件",
                "yellow": 1,
                "red": 1,
            },
            TrustStage.S5_STRUCTURAL_LOCK_IN: {
                "metric": "资产保护/法律咨询行为",
                "yellow": 1,
                "red": 1,
            },
        }

    def evaluate(self, interaction_logs: List[Dict]) -> TrustEntropyReport:
        """
        基于交互日志评估当前信任阶段。
        interaction_logs 格式: [{"type": "conversation|email|meeting", "content": "...", "participants": ["A","B"]}]
        """
        signals = []
        stage_scores = {s: 0.0 for s in TrustStage}

        # S1: 信号忽视（回避困难对话）
        avoidance_count = sum(1 for log in interaction_logs
                             if self._is_avoidance(log))
        s1_score = self._score_stage(TrustStage.S1_SIGNAL_NEGLECT, avoidance_count)
        stage_scores[TrustStage.S1_SIGNAL_NEGLECT] = s1_score
        signals.append(StageSignal(
            stage=TrustStage.S1_SIGNAL_NEGLECT,
            severity=self._severity(s1_score),
            observable_evidence=[f"过去一周回避困难对话 {avoidance_count} 次"],
            recommendation="建立制度化冲突对话机制（每周1次合伙人同步会）"
        ))

        # S2: 归因偏置（外部归因 dominate）
        attribution_ratio = self._calculate_attribution_ratio(interaction_logs)
        s2_score = self._score_stage(TrustStage.S2_ATTRIBUTION_BIAS, attribution_ratio)
        stage_scores[TrustStage.S2_ATTRIBUTION_BIAS] = s2_score
        signals.append(StageSignal(
            stage=TrustStage.S2_ATTRIBUTION_BIAS,
            severity=self._severity(s2_score),
            observable_evidence=[f"外部归因/内部归因比值 ≈ {attribution_ratio:.1f}"],
            recommendation="引入第三方中立的复盘流程，强制双方先陈述自身责任"
        ))

        # S3: 承诺升级（沉没成本效应）
        repeated_failures = self._count_repeated_failures(interaction_logs)
        s3_score = self._score_stage(TrustStage.S3_ESCALATION_OF_COMMITMENT, repeated_failures)
        stage_scores[TrustStage.S3_ESCALATION_OF_COMMITMENT] = s3_score
        signals.append(StageSignal(
            stage=TrustStage.S3_ESCALATION_OF_COMMITMENT,
            severity=self._severity(s3_score),
            observable_evidence=[f"同一失败路径被重复投入 {repeated_failures} 次"],
            recommendation="设置'止损规则'：同一策略失败2次必须强制切换方案"
        ))

        # S4: 情感极化（公开羞辱/指责）
        public_accusations = self._count_public_accusations(interaction_logs)
        s4_score = self._score_stage(TrustStage.S4_AFFECTIVE_POLARIZATION, public_accusations)
        stage_scores[TrustStage.S4_AFFECTIVE_POLARIZATION] = s4_score
        signals.append(StageSignal(
            stage=TrustStage.S4_AFFECTIVE_POLARIZATION,
            severity=self._severity(s4_score),
            observable_evidence=[f"检测到 {public_accusations} 起公开指责/羞辱事件"],
            recommendation="立即启动情感隔离：暂停共同会议，引入调解人"
        ))

        # S5: 结构锁定（退出壁垒构建）
        structural_moves = self._count_structural_lock_in(interaction_logs)
        s5_score = self._score_stage(TrustStage.S5_STRUCTURAL_LOCK_IN, structural_moves)
        stage_scores[TrustStage.S5_STRUCTURAL_LOCK_IN] = s5_score
        signals.append(StageSignal(
            stage=TrustStage.S5_STRUCTURAL_LOCK_IN,
            severity=self._severity(s5_score),
            observable_evidence=[f"检测到 {structural_moves} 项资产保护/法律咨询行为"],
            recommendation="进入危机模式：所有决策须经外部法律顾问和中立审计"
        ))

        # 确定当前主导阶段（最高分且最晚期）
        current_stage = max(stage_scores, key=lambda s: (self._stage_order(s), stage_scores[s]))
        entropy_score = min(100, sum(stage_scores.values()))

        # 干预优先级
        red_signals = [s for s in signals if s.severity == "red"]
        intervention = [s.recommendation for s in red_signals]
        if not intervention:
            intervention = [s.recommendation for s in signals if s.severity == "yellow"]
        if not intervention:
            intervention = ["信任熵处于正常范围，继续保持透明沟通机制。"]

        return TrustEntropyReport(
            current_stage=current_stage,
            stage_history=[{"stage": s.value, "score": round(v, 1)} for s, v in stage_scores.items()],
            overall_entropy_score=round(entropy_score, 1),
            signals=signals,
            intervention_priority=intervention
        )

    def _is_avoidance(self, log: Dict) -> bool:
        content = log.get("content", "")
        markers = ["下次再说", "先放一放", "这个不急", "以后讨论", "暂时跳过", " postpone "]
        return any(m in content for m in markers)

    def _calculate_attribution_ratio(self, logs: List[Dict]) -> float:
        external = sum(1 for log in logs if any(w in log.get("content", "") for w in
                         ["都是因为他", "对方的错", "外部原因", "运气不好", "环境导致"]))
        internal = sum(1 for log in logs if any(w in log.get("content", "") for w in
                         ["我的责任", "我们有问题", "内部原因", "我需要改进"]))
        return (external / max(internal, 1))

    def _count_repeated_failures(self, logs: List[Dict]) -> int:
        # 简化：关键词计数
        return sum(1 for log in logs if any(w in log.get("content", "") for w in
                   ["又失败了", "再次尝试", "第三次", "还是不行", "重蹈覆辙"]))

    def _count_public_accusations(self, logs: List[Dict]) -> int:
        return sum(1 for log in logs if any(w in log.get("content", "") for w in
                   ["公开指责", "羞辱", "你就是", "无能", "垃圾", "fail completely", "public blame"]))

    def _count_structural_lock_in(self, logs: List[Dict]) -> int:
        return sum(1 for log in logs if any(w in log.get("content", "") for w in
                   ["法律咨询", "资产转移", "股权冻结", "竞业禁止", "保护性措施", "退出条款"]))

    def _score_stage(self, stage: TrustStage, value: float) -> float:
        cfg = self.stage_thresholds[stage]
        yellow = cfg["yellow"]
        red = cfg["red"]
        if value < yellow:
            return 0.0
        if value >= red:
            return 25.0
        # 线性插值
        return ((value - yellow) / (red - yellow)) * 25.0

    def _severity(self, score: float) -> str:
        if score >= 20:
            return "red"
        if score >= 10:
            return "yellow"
        return "green"

    def _stage_order(self, stage: TrustStage) -> int:
        return list(TrustStage).index(stage)
