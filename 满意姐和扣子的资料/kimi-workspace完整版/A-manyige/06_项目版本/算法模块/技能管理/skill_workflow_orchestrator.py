"""
skill_workflow_orchestrator.py
Abstracts bloodized skills into reusable workflow patterns for thinking and research.
Skills are not just mapped to decision styles — they are composed into
higher-order cognitive workflows that cover HOW we think and HOW we research.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass
from enum import Enum

LEDGER_PATH = Path("/root/.openclaw/workspace/skill_workflow_ledger.json")


class WorkflowType(str, Enum):
    STRUCTURED_ANALYSIS = "structured_analysis"          # 结构化解构一个复杂问题
    HYPOTHESIS_VALIDATION = "hypothesis_validation"      # 验证一个假设
    COMPARATIVE_EVALUATION = "comparative_evaluation"    # 多方案对比评估
    DEEP_RESEARCH = "deep_research"                      # 深度研究
    LANDSCAPE_SCANNING = "landscape_scanning"            # 竞争格局/环境扫描
    SOURCE_VERIFICATION = "source_verification"          # 信源验证
    SYNTHESIS_AND_CITATION = "synthesis_and_citation"    # 综合与引用
    CREATIVE_GENERATION = "creative_generation"          # 创造性产出
    RISK_AUDIT = "risk_audit"                            # 对抗性审计
    EXECUTION_AND_CLOSURE = "execution_and_closure"      # 执行与闭环


WORKFLOW_PATTERNS: dict[WorkflowType, dict[str, Any]] = {
    WorkflowType.STRUCTURED_ANALYSIS: {
        "description": "面对复杂问题时，不裸脑，先用框架结构化解构",
        "cognitive_organs": ["思维器官", "感知器官"],
        "steps": [
            {"phase": "界定", "action": "明确问题边界（Q1-Q3+C1-C3）", "skill_hints": ["adi-decision-engine", "afrexai-strategic-thinking", "thinking-mentor"]},
            {"phase": "拆解", "action": "将大问题拆解为可验证的子假设", "skill_hints": ["architecture-designer", "academic-deep-research"]},
            {"phase": "校准", "action": "对抗性检查逻辑跳跃和假设漏洞", "skill_hints": ["antifragile-taleb", "ai-meeting-room"]},
            {"phase": "收敛", "action": "用满意解原则收敛到可执行的结论", "skill_hints": ["egbertie_management_philosophy_embedder"]},
        ],
        "barbell_rule": "杠铃规则: Local思维框架 ≥ 60%, 感知验证 ~ 25%, LLM合成 ≤ 15%",
    },
    WorkflowType.HYPOTHESIS_VALIDATION: {
        "description": "任何论断在输出前必须经过三层验证",
        "cognitive_organs": ["感知器官", "思维器官", "代谢器官"],
        "steps": [
            {"phase": "溯源", "action": "搜索独立信源，交叉验证", "skill_hints": ["kimi-search", "tavily-search", "agent-reach", "web_search"]},
            {"phase": "边界", "action": "测试反例和边缘条件", "skill_hints": ["baseline-checker", "testing-framework"]},
            {"phase": "置信", "action": "为每个论断标注置信度", "skill_hints": ["BLUE_TEAM_CHARTER"], "note": "引用蓝军宪章的置信度标注"},
        ],
        "barbell_rule": "杠铃规则: 感知验证 ≥ 50%, 本地规则测试 ~ 35%, LLM合成 ≤ 15%",
    },
    WorkflowType.COMPARATIVE_EVALUATION: {
        "description": "多选项排序时建立可比维度，避免苹果与橘子比较",
        "cognitive_organs": ["思维器官", "感知器官"],
        "steps": [
            {"phase": "定维", "action": "与决策者共同确定评估维度与权重", "skill_hints": ["adi-decision-engine", "afrexai-strategic-thinking"]},
            {"phase": "采集", "action": "为每个选项采集同质化信息", "skill_hints": ["agent-reach", "kimi-search", "web_search"]},
            {"phase": "评分", "action": "按维度打分，敏感分析", "skill_hints": ["adi-decision-engine"]},
            {"phase": "审计", "action": "蓝军对抗性审计权重与数据", "skill_hints": ["antifragile-taleb"]},
        ],
        "barbell_rule": "杠铃规则: 本地评分模型 ≥ 50%, 感知采集 ~ 35%, LLM解释 ≤ 15%",
    },
    WorkflowType.DEEP_RESEARCH: {
        "description": "穷尽性调研，不是黑盒API包装",
        "cognitive_organs": ["感知器官", "思维器官", "记忆器官"],
        "steps": [
            {"phase": "主题拆分", "action": "将大主题拆分为2-4个子主题，每个主题2轮循环", "skill_hints": ["academic-deep-research", "deep-research"]},
            {"phase": "搜索循环1", "action": "广度扫描，获取全景", "skill_hints": ["kimi-search", "tavily-search", "agent-reach"]},
            {"phase": "搜索循环2", "action": "深度钻取，验证细节", "skill_hints": ["web_fetch", "kimi_fetch", "agent-browser"]},
            {"phase": "结构化", "action": "按证据等级分层，APA引用", "skill_hints": ["academic-deep-research"]},
            {"phase": "记忆固化", "action": "提取可复用洞察写入知识库", "skill_hints": ["file_deep_internalizer", "skill_methodology_extractor"]},
        ],
        "barbell_rule": "杠铃规则: 感知搜索+验证 ≥ 60%, 本地结构化 ~ 25%, LLM综合 ≤ 15%",
    },
    WorkflowType.LANDSCAPE_SCANNING: {
        "description": "快速获取领域全景，识别关键玩家与趋势",
        "cognitive_organs": ["感知器官", "思维器官"],
        "steps": [
            {"phase": "广角", "action": "多引擎搜索获取overview", "skill_hints": ["kimi-search", "tavily-search", "ai-news-collector"]},
            {"phase": "玩家", "action": "识别并提取关键实体", "skill_hints": ["agent-reach", "web_search"]},
            {"phase": "映射", "action": "绘制关系网络与趋势矩阵", "skill_hints": ["architecture-designer", "feishu-bitable"]},
        ],
        "barbell_rule": "杠铃规则: 感知搜索 ≥ 60%, 本地映射 ~ 25%, LLM解释 ≤ 15%",
    },
    WorkflowType.SOURCE_VERIFICATION: {
        "description": "任何事实性陈述前必须先验证信源",
        "cognitive_organs": ["感知器官", "代谢器官"],
        "steps": [
            {"phase": "独立", "action": "至少两个独立信源交叉验证", "skill_hints": ["kimi-search", "web_search", "tavily-search"]},
            {"phase": "时效", "action": "检查信息发布时间与版本", "skill_hints": ["web_fetch", "kimi_fetch"]},
            {"phase": "偏见", "action": "评估信源利益相关性与立场偏差", "skill_hints": ["antifragile-taleb"]},
        ],
        "barbell_rule": "杠铃规则: 感知验证 ≥ 70%, 本地偏见检查 ~ 15%, LLM辅助 ≤ 15%",
    },
    WorkflowType.SYNTHESIS_AND_CITATION: {
        "description": "将碎片化信息整合为可引用的结构化知识",
        "cognitive_organs": ["记忆器官", "思维器官"],
        "steps": [
            {"phase": "去重", "action": "消除重复与矛盾信息", "skill_hints": ["skill_methodology_extractor", "file_deep_internalizer"]},
            {"phase": "分层", "action": "按证据等级与相关性分类", "skill_hints": ["academic-deep-research"]},
            {"phase": "引用", "action": "生成可追溯的引用链条", "skill_hints": ["academic-deep-research", "feishu-create-doc"]},
            {"phase": "入库", "action": "写入长期知识库", "skill_hints": ["feishu-bitable", "feishu-create-doc"]},
        ],
        "barbell_rule": "杠铃规则: 本地结构化 ≥ 60%, 感知补充 ~ 25%, LLM润色 ≤ 15%",
    },
    WorkflowType.CREATIVE_GENERATION: {
        "description": "在约束条件下产出创造性方案",
        "cognitive_organs": ["思维器官", "运动器官"],
        "steps": [
            {"phase": "约束", "action": "明确硬约束与软约束", "skill_hints": ["egbertie_management_philosophy_embedder"]},
            {"phase": "发散", "action": "多视角快速生成候选方案", "skill_hints": ["ai-meeting-room", "afrexai-strategic-thinking"]},
            {"phase": "收敛", "action": "用满意解筛选可执行方案", "skill_hints": ["adi-decision-engine"]},
        ],
        "barbell_rule": "杠铃规则: 本地规则约束 ≥ 40%, 多视角生成 ~ 45%, LLM精炼 ≤ 15%",
    },
    WorkflowType.RISK_AUDIT: {
        "description": "任何重要产出发布前必须经过对抗性审计",
        "cognitive_organs": ["代谢器官", "思维器官"],
        "steps": [
            {"phase": "幻觉", "action": "检查事实性错误与过度推断", "skill_hints": ["source_verification", "agent-reach"]},
            {"phase": "盲区", "action": "识别幸存者偏差与确认偏误", "skill_hints": ["antifragile-taleb"]},
            {"phase": "数学", "action": "验证量化主张的准确性", "skill_hints": ["baseline-checker"]},
            {"phase": "否决", "action": "必须发现至少1个问题", "skill_hints": ["BLUE_TEAM_CHARTER"], "note": "蓝军硬否决权"},
        ],
        "barbell_rule": "杠铃规则: 本地规则审计 ≥ 50%, 感知验证 ~ 35%, LLM总结 ≤ 15%",
    },
    WorkflowType.EXECUTION_AND_CLOSURE: {
        "description": "将决策转化为可验证的执行结果并闭环",
        "cognitive_organs": ["运动器官", "记忆器官", "代谢器官"],
        "steps": [
            {"phase": "计划", "action": "将任务拆分为可验证的子任务", "skill_hints": ["feishu-task", "baseline-checker"]},
            {"phase": "执行", "action": "按优先级执行并记录证据", "skill_hints": ["cognitive_workload_router"]},
            {"phase": "验证", "action": "pytest/测试/人工复核", "skill_hints": ["baseline-checker", "skill_bloodization_guardian"]},
            {"phase": "归档", "action": "C1-C8 全部检查并写入 memory/Git", "skill_hints": ["egbertie_management_philosophy_embedder"]},
        ],
        "barbell_rule": "杠铃规则: 本地执行 ≥ 70%, 协调沟通 ~ 15%, LLM摘要 ≤ 15%",
    },
}


@dataclass
class WorkflowPlan:
    workflow_type: WorkflowType
    description: str
    steps: list[dict[str, Any]]
    barbell_rule: str
    estimated_llm_ratio: float


class SkillWorkflowOrchestrator:
    """
    Maps tasks to high-level cognitive workflows and returns step-by-step plans.
    Every plan enforces the three-layer architecture barbell rule.
    """

    def __init__(self) -> None:
        self.ledger_path = LEDGER_PATH
        self.ledger = self._load_ledger()

    def _load_ledger(self) -> dict[str, Any]:
        if self.ledger_path.exists():
            return json.loads(self.ledger_path.read_text(encoding="utf-8"))
        return {"workflow_runs": [], "workflow_stats": {}}

    def _save_ledger(self) -> None:
        self.ledger_path.write_text(json.dumps(self.ledger, ensure_ascii=False, indent=2), encoding="utf-8")

    def classify_task(self, task_description: str) -> WorkflowType:
        """Rule-based classification of task into workflow type."""
        td = task_description.lower()

        # EXECUTION_AND_CLOSURE indicators — high priority because they contain common words
        if any(k in td for k in [
            "pytest", "commit", "登记", "deploy", "fin",
            "执行落地", "落地执行", "闭环完成", "完成闭环"
        ]):
            return WorkflowType.EXECUTION_AND_CLOSURE
        if any(k in td for k in [
            "执行", "落地", "闭环", "implementation"
        ]):
            return WorkflowType.EXECUTION_AND_CLOSURE

        # RISK_AUDIT indicators — before comparative eval to catch "审计" / "蓝军"
        if any(k in td for k in [
            "蓝军", "审计", "audit", "对抗性", "challenge",
            "verify output"
        ]):
            return WorkflowType.RISK_AUDIT
        if "风险评估" in td:
            return WorkflowType.RISK_AUDIT
        if any(k in td for k in ["review", "检查"]):
            # Distinguish from general evaluation
            if any(audit_k in td for audit_k in ["报告", "output", "产出", "文档"]):
                return WorkflowType.RISK_AUDIT

        # DEEP_RESEARCH indicators
        if any(k in td for k in [
            "研究", "调研", "research", "深度分析", "文献综述", "competitive intelligence",
            "行业分析", "趋势", "benchmark"
        ]):
            return WorkflowType.DEEP_RESEARCH

        # LANDSCAPE_SCANNING indicators
        if any(k in td for k in [
            "扫描", "全景", "格局", "玩家", "landscape", "overview", "market map",
            "竞争格局", "ecosystem"
        ]):
            return WorkflowType.LANDSCAPE_SCANNING

        # SOURCE_VERIFICATION indicators
        if any(k in td for k in [
            "source", "fact-check", "核实", "交叉验证", "confirm",
            "信源", "溯源"
        ]):
            return WorkflowType.SOURCE_VERIFICATION
        if "验证" in td and any(src_k in td for src_k in ["出处", "来源", "信息", "事实", "真实性"]):
            return WorkflowType.SOURCE_VERIFICATION

        # COMPARATIVE_EVALUATION indicators
        if any(k in td for k in [
            "对比", "比较", "评估", "选型", "排序", "评分", "versus", "compare",
            "evaluation", "mcda", "决策", "选择"
        ]):
            return WorkflowType.COMPARATIVE_EVALUATION

        # HYPOTHESIS_VALIDATION indicators
        if any(k in td for k in [
            "假设", "验证假设", "hypothesis", "experiment", "试点",
            "验证想法"
        ]):
            return WorkflowType.HYPOTHESIS_VALIDATION
        if "测试" in td and any(hyp_k in td for hyp_k in ["想法", "假设", "理论", "观点", "假说"]):
            return WorkflowType.HYPOTHESIS_VALIDATION

        # CREATIVE_GENERATION indicators
        if any(k in td for k in [
            "创意", "设计方案", "生成", "create", "design", "brainstorm",
            "提案", "concept"
        ]):
            return WorkflowType.CREATIVE_GENERATION

        # SYNTHESIS_AND_CITATION indicators
        if any(k in td for k in [
            "综合", "整合", "synthesis", "citation", "引用", "报告",
            "write up", "总结", "归纳"
        ]):
            return WorkflowType.SYNTHESIS_AND_CITATION

        # Default: STRUCTURED_ANALYSIS
        return WorkflowType.STRUCTURED_ANALYSIS

    def plan(self, task_description: str) -> WorkflowPlan:
        wf = self.classify_task(task_description)
        pattern = WORKFLOW_PATTERNS[wf]

        # Estimate LLM ratio from barbell_rule string
        br = pattern["barbell_rule"]
        llm_ratio = 0.15
        if "llm" in br.lower():
            import re
            m = re.search(r"llm[^\d]*(\d+)%", br.lower())
            if m:
                llm_ratio = int(m.group(1)) / 100.0

        plan = WorkflowPlan(
            workflow_type=wf,
            description=pattern["description"],
            steps=pattern["steps"].copy(),
            barbell_rule=br,
            estimated_llm_ratio=llm_ratio,
        )

        import datetime as _dt
        self.ledger["workflow_runs"].append({
            "task": task_description[:200],
            "workflow": wf.value,
            "llm_ratio": llm_ratio,
            "timestamp": _dt.datetime.now().isoformat(),
        })
        self._save_ledger()
        return plan

    def health(self, n: int = 50) -> dict[str, Any]:
        runs = self.ledger.get("workflow_runs", [])[-n:]
        if not runs:
            return {"error": "No workflow runs yet."}
        from collections import Counter
        wf_counts = Counter(r["workflow"] for r in runs)
        avg_llm = sum(r["llm_ratio"] for r in runs) / len(runs)
        return {
            "sample_size": len(runs),
            "avg_llm_ratio": round(avg_llm, 2),
            "workflow_distribution": dict(wf_counts),
            "barbell_alarm": avg_llm > 0.15,
        }


def demo() -> None:
    orch = SkillWorkflowOrchestrator()
    tasks = [
        "帮我研究一下硬科技合伙人匹配服务的竞争格局",
        "验证一下稻盛和夫敬天爱人的出处",
        "对比三个方案择优",
        "把这个功能闭环并 pytest 测试",
    ]
    for t in tasks:
        p = orch.plan(t)
        print(f"\n任务: {t}")
        print(f"  工作流: {p.workflow_type.value}")
        print(f"  说明: {p.description}")
        print(f"  步骤: {[s['phase'] for s in p.steps]}")
        print(f"  杠铃规则: {p.barbell_rule}")


if __name__ == "__main__":
    demo()
