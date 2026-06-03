"""
project_operation_playbook.py
一堂·复盘营项目运营管理方法论资产

来源:
- 复盘营 13 个 PDF 课程（业务里程碑/科学决策/业务拆解/时间管理/科学成长/知识管理/苦练基本功/科学复盘/解决方案/商业模式/项目壁垒/人生红点/最佳转化率）
- 一堂相关音频转录与商业模式画布资料

版本: V1.0
生成时间: 2026-04-09
处理流程: 文件内化标准作业流程 V1.0（批量提取 → 结构化 → 代码化 → 测试验证 →  runner 注册）
作者: 蓝军 Skeptor-7 + 满意姐 (基于一堂项目运营与复盘方法论体系)

说明:
本资产将一堂复盘营的核心方法论抽象为一套可运行的项目运营管理工具箱。
覆盖从 0→1 业务探索、商业模式验证、团队时间管理、知识管理到科学复盘的完整闭环。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta


class MilestoneStage(Enum):
    EXPLORATION = "探索期"        # 0-1 验证
    GROWTH = "增长期"             # 规模化
    MATURITY = "成熟期"           # 盈利优化
    TRANSITION = "转型期"         # 第二曲线


class DecisionType(Enum):
    GO = "GO-推进"
    NO_GO = "NO_GO-放弃"
    DEFER = "DEFER-推迟"
    EXPERIMENT = "EXPERIMENT-小步实验"


class TimeQuadrant(Enum):
    Q1_IMPORTANT_URGENT = "重要且紧急"
    Q2_IMPORTANT_NOT_URGENT = "重要不紧急"
    Q3_NOT_IMPORTANT_URGENT = "紧急不重要"
    Q4_NOT_IMPORTANT_NOT_URGENT = "不重要不紧急"


class ReviewFrequency(Enum):
    DAILY = "日复盘"
    WEEKLY = "周复盘"
    MONTHLY = "月复盘"
    MILESTONE = "里程碑复盘"


@dataclass
class Milestone:
    name: str
    target_date: str
    success_criteria: List[str]
    stage: MilestoneStage
    is_achieved: bool = False


@dataclass
class DecisionLog:
    decision_id: str
    context: str
    options: List[str]
    chosen_option: str
    roi_estimate: Dict[str, float]      # 投入/产出/时间成本
    decision_type: DecisionType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskItem:
    name: str
    quadrant: TimeQuadrant
    estimated_hours: float
    deadline: Optional[str] = None
    is_done: bool = False


@dataclass
class BusinessModelCanvas:
    customer_segments: str = ""
    value_propositions: str = ""
    channels: str = ""
    customer_relationships: str = ""
    revenue_streams: str = ""
    key_resources: str = ""
    key_activities: str = ""
    key_partnerships: str = ""
    cost_structure: str = ""


@dataclass
class ProjectReview:
    review_type: ReviewFrequency
    what_done: List[str]
    what_learned: List[str]
    what_next: List[str]
    red_dot_insight: str = ""  # 人生红点/核心洞察
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ProjectOperationPlaybook:
    """
    一堂复盘营项目运营管理方法论引擎。
    封装业务里程碑、五步法拆解、科学决策、时间管理、知识管理、科学复盘六大模块。
    """

    # 一堂五步法核心框架（一堂创业/项目管理基础）
    FIVE_STEP_FRAMEWORK = {
        1: {"name": "用户洞察", "key_question": "谁是我的核心用户？他们有什么痛点？"},
        2: {"name": "解决方案", "key_question": "我的产品/服务如何解决这个痛点？"},
        3: {"name": "商业模式", "key_question": "如何持续赚钱？收入来源和成本结构是什么？"},
        4: {"name": "增长壁垒", "key_question": "如何获取用户？我的护城河和壁垒是什么？"},
        5: {"name": "项目壁垒", "key_question": "为什么是我做？核心优势和资源匹配度如何？"},
    }

    # 复盘四问（科学复盘模板）
    REVIEW_FOUR_QUESTIONS = [
        "目标是什么？（Goal）",
        "结果是什么？（Result）",
        "差距在哪里？（Gap）",
        "下一步做什么？（Action）",
    ]

    # 科学成长飞轮（刻意练习 + 反馈闭环）
    GROWTH_FLYWHEEL = [
        "设定明确目标",
        "设计练习任务",
        "获取即时反馈",
        "修正错误模式",
        "复盘提炼规律",
    ]

    # 知识管理三层架构
    KNOWLEDGE_ARCHITECTURE = {
        "input": "信息输入层（课程/书籍/对话/实践）",
        "process": "加工内化层（笔记/模型/代码/测试）",
        "output": "行动输出层（决策/产品/文章/教学）",
    }

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.milestones: List[Milestone] = []
        self.decisions: List[DecisionLog] = []
        self.tasks: List[TaskItem] = []
        self.reviews: List[ProjectReview] = []
        self.knowledge_base: Dict[str, str] = {}

    # ==================== 模块1: 业务里程碑 ====================
    def add_milestone(self, name: str, target_date: str, success_criteria: List[str], stage: MilestoneStage):
        ms = Milestone(name=name, target_date=target_date, success_criteria=success_criteria, stage=stage)
        self.milestones.append(ms)
        return ms

    def milestone_check(self, milestone_name: str, actual_results: List[str]) -> Dict:
        """里程碑达成度检查。"""
        ms = next((m for m in self.milestones if m.name == milestone_name), None)
        if not ms:
            return {"error": "Milestone not found"}
        met = [c for c in ms.success_criteria if any(c.lower() in r.lower() for r in actual_results)]
        ratio = len(met) / len(ms.success_criteria) if ms.success_criteria else 0.0
        status = "✅ 达成" if ratio >= 1.0 else "🟡 部分达成" if ratio >= 0.5 else "🔴 未达标"
        return {
            "milestone": milestone_name,
            "stage": ms.stage.value,
            "criteria_total": len(ms.success_criteria),
            "criteria_met": len(met),
            "achievement_ratio": round(ratio, 2),
            "status": status,
            "unmet_criteria": [c for c in ms.success_criteria if c not in met],
        }

    # ==================== 模块2: 科学决策 ====================
    def make_decision(self, context: str, options: List[str], chosen: str,
                      investment: float, expected_return: float, time_cost_hours: float) -> DecisionLog:
        roi = expected_return / investment if investment > 0 else 0.0
        decision_type = self._classify_decision(roi, time_cost_hours)
        log = DecisionLog(
            decision_id=f"D-{len(self.decisions)+1:03d}",
            context=context,
            options=options,
            chosen_option=chosen,
            roi_estimate={"investment": investment, "expected_return": expected_return, "roi": round(roi, 2), "time_cost_hours": time_cost_hours},
            decision_type=decision_type,
        )
        self.decisions.append(log)
        return log

    def _classify_decision(self, roi: float, time_cost_hours: float) -> DecisionType:
        if roi >= 3.0 and time_cost_hours < 40:
            return DecisionType.GO
        if roi < 1.0:
            return DecisionType.NO_GO
        if time_cost_hours > 160:
            return DecisionType.EXPERIMENT
        return DecisionType.GO if roi >= 1.5 else DecisionType.DEFER

    # ==================== 模块3: 业务拆解（五步法） ====================
    def five_step_diagnosis(self, step_answers: Dict[int, str]) -> Dict:
        """
        基于一堂五步法对项目进行诊断。
        step_answers: {1: "用户洞察回答", 2: "解决方案回答", ...}
        """
        gaps = []
        for step_num, info in self.FIVE_STEP_FRAMEWORK.items():
            answer = step_answers.get(step_num, "").strip()
            if len(answer) < 20:
                gaps.append(f"第{step_num}步「{info['name']}」回答过短，需深入思考：{info['key_question']}")
        score = max(0, 100 - len(gaps) * 20)
        return {
            "score": score,
            "gaps": gaps,
            "framework": self.FIVE_STEP_FRAMEWORK,
            "next_action": "优先补齐 gaps 中的第一步" if gaps else "五步法完整，进入验证/增长阶段",
        }

    # ==================== 模块4: 时间管理 ====================
    def add_task(self, name: str, quadrant: TimeQuadrant, estimated_hours: float, deadline: Optional[str] = None):
        t = TaskItem(name=name, quadrant=quadrant, estimated_hours=estimated_hours, deadline=deadline)
        self.tasks.append(t)
        return t

    def time_audit(self) -> Dict:
        """时间分配审计，识别 Q2 投入比例。"""
        total_hours = sum(t.estimated_hours for t in self.tasks if not t.is_done)
        q2_hours = sum(t.estimated_hours for t in self.tasks if t.quadrant == TimeQuadrant.Q2_IMPORTANT_NOT_URGENT and not t.is_done)
        ratio = q2_hours / total_hours if total_hours > 0 else 0.0
        return {
            "total_pending_hours": round(total_hours, 1),
            "q2_hours": round(q2_hours, 1),
            "q2_ratio": round(ratio, 2),
            "assessment": "优秀" if ratio >= 0.4 else "良好" if ratio >= 0.25 else "需优化",
            "advice": "增加 Q2（重要不紧急）任务投入，减少 Q3/Q4 时间黑洞。" if ratio < 0.25 else "保持当前时间结构。",
        }

    # ==================== 模块5: 知识管理 ====================
    def add_knowledge(self, topic: str, insight: str):
        self.knowledge_base[topic] = insight
        return {"topic": topic, "stored": True}

    def knowledge_output_check(self) -> Dict:
        """检查知识是否形成了有效输出闭环。"""
        count = len(self.knowledge_base)
        return {
            "knowledge_topics": count,
            "architecture": self.KNOWLEDGE_ARCHITECTURE,
            "healthcheck": "建议将每个 topic 转化为一个可执行的决策或代码资产。" if count > 5 else "继续积累输入。",
        }

    # ==================== 模块6: 科学复盘 ====================
    def conduct_review(self, review_type: ReviewFrequency, what_done: List[str],
                       what_learned: List[str], what_next: List[str], red_dot_insight: str = "") -> ProjectReview:
        review = ProjectReview(
            review_type=review_type,
            what_done=what_done,
            what_learned=what_learned,
            what_next=what_next,
            red_dot_insight=red_dot_insight,
        )
        self.reviews.append(review)
        return review

    def review_summary(self) -> Dict:
        """汇总所有复盘记录。"""
        return {
            "total_reviews": len(self.reviews),
            "by_type": {rt.value: sum(1 for r in self.reviews if r.review_type == rt) for rt in ReviewFrequency},
            "latest_red_dot": self.reviews[-1].red_dot_insight if self.reviews else "",
            "four_questions_template": self.REVIEW_FOUR_QUESTIONS,
        }

    # ==================== 模块7: 商业模式画布 ====================
    def build_business_model(self, canvas: BusinessModelCanvas) -> Dict:
        empty_fields = [k for k, v in canvas.__dict__.items() if not v.strip()]
        completeness = (9 - len(empty_fields)) / 9.0
        return {
            "completeness": round(completeness, 2),
            "empty_fields": empty_fields,
            "canvas": canvas.__dict__,
            "status": "完整" if completeness >= 0.8 else "待完善",
        }

    # ==================== 模块8: 项目壁垒评估 ====================
    def moat_assessment(self, factors: Dict[str, float]) -> Dict:
        """
        评估项目壁垒强度。
        factors 示例: {"技术壁垒": 0.6, "网络效应": 0.2, "品牌认知": 0.4, "成本优势": 0.3, "规模效应": 0.1}
        """
        total = sum(factors.values())
        avg = total / len(factors) if factors else 0.0
        strongest = max(factors.items(), key=lambda x: x[1]) if factors else ("无", 0)
        return {
            "avg_moat_score": round(avg, 2),
            "strongest_moat": strongest[0],
            "assessment": "高壁垒" if avg >= 0.6 else "中等壁垒" if avg >= 0.4 else "低壁垒-需快速验证或寻找差异化",
            "factors": factors,
        }

    # ==================== 模块9: 最佳转化率优化 ====================
    def conversion_optimizer(self, funnel: Dict[str, int]) -> Dict:
        """
        分析漏斗各层转化率。
        funnel 示例: {"曝光": 10000, "点击": 500, "注册": 100, "付费": 10}
        """
        steps = list(funnel.items())
        rates = []
        for i in range(1, len(steps)):
            rate = steps[i][1] / steps[i-1][1] if steps[i-1][1] > 0 else 0.0
            rates.append({"from": steps[i-1][0], "to": steps[i][0], "conversion_rate": round(rate, 4)})
        overall = steps[-1][1] / steps[0][1] if steps[0][1] > 0 else 0.0
        weakest = min(rates, key=lambda x: x["conversion_rate"]) if rates else None
        return {
            "overall_conversion": round(overall, 4),
            "step_rates": rates,
            "weakest_link": weakest,
            "priority_action": f"优先优化<{weakest['from']} → {weakest['to']}>环节" if weakest else "数据不足",
        }

    # ==================== 模块10: 人生红点探索 ====================
    def red_dot_discovery(self, passion_areas: List[str], market_needs: List[str], personal_edges: List[str]) -> Dict:
        """
        人生红点 = 热爱 ∩ 市场需求 ∩ 个人优势。
        """
        intersection = set(passion_areas) & set(market_needs) & set(personal_edges)
        return {
            "red_dot_candidates": list(intersection),
            "passion_areas": passion_areas,
            "market_needs": market_needs,
            "personal_edges": personal_edges,
            "guidance": "聚焦红点交集领域，长期积累形成不可替代性。" if intersection else "扩大交集：要么培养热爱，要么打磨优势，要么寻找市场需求对接点。",
        }

    def export_project_health_report(self) -> Dict:
        """导出项目健康诊断报告。"""
        return {
            "project_name": self.project_name,
            "generated_at": datetime.now().isoformat(),
            "milestones": {"total": len(self.milestones), "achieved": sum(1 for m in self.milestones if m.is_achieved)},
            "decisions": {"total": len(self.decisions), "latest_5": [d.__dict__ for d in self.decisions[-5:]]},
            "tasks": self.time_audit(),
            "knowledge": self.knowledge_output_check(),
            "reviews": self.review_summary(),
        }
