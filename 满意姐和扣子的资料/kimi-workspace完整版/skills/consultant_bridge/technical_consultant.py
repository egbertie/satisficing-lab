"""
Technical Consultant - 技术外援专用模块
负责生成技术需求清单、深度剖析模板、工程化评估与升级建议
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from defense_base_components import BaseComponent
from typing import Dict, List, Any


class TechnicalConsultant(BaseComponent):
    """
    技术外援咨询规范
    """

    def __init__(self):
        super().__init__("technical_consultant")

    def generate_request(
        self,
        system_name: str,
        current_tech_stack: List[str],
        pain_points: List[str],
        target_state: str,
    ) -> Dict[str, Any]:
        """
        生成面向技术外援的详细请求文档。
        """
        return {
            "request_type": "technical_consultant",
            "system": system_name,
            "stack": current_tech_stack,
            "pain_points": pain_points,
            "target": target_state,
            "assessment_requires": [
                "请基于软件工程最佳实践，评估当前系统的架构健康度（1-10分），并说明评分依据",
                "指出当前技术栈中最大的3个单点故障或技术债务炸弹",
                "如果要在不重构整个系统的前提下进行渐进式升级，请给出分阶段路线图（含验收标准）",
            ],
            "deep_dive_questions": [
                "我们的测试覆盖率为0%（主要因特定模块导入冲突导致测试批量失败），从软件工程角度，修复这类'测试倒逼源码'问题的最佳策略是什么？",
                "如何建立一个可自动化运行的'系统自评估报告'生成流程？需要采集哪些指标？",
                "在无外部LLM API的情况下（经常401），如何设计本地化/轻量化的回退方案，同时保证系统不降级为'弱智模式'？",
                "针对我们的Skill生态系统（约100+个Skill），如何进行版本管理、依赖隔离和自动化测试部署？",
            ],
            "constraints": [
                "所有建议必须考虑我们的资源限制：单服务器、无专职DevOps、Python为主",
                "优先推荐开源/免费方案，商业方案需明确说明必要性和成本",
                "每项建议必须附带'不做会怎样'的风险说明",
            ],
            "education_focus": [
                "请教我们如何建立持续的技术自我评估能力",
                "请教我们如何把外援的建议转化为可执行、可追踪、可验收的内部任务",
                "请教我们如何科学地管理技术文档和知识资产，避免'文档坟墓'",
            ],
        }

    def self_assessment_guide(self) -> Dict[str, Any]:
        """
        基于技术外援教学成果，生成的系统自评估指南
        """
        return {
            "dimensions": [
                {"name": "架构健康度", "metrics": ["模块耦合度", "循环依赖数", "接口稳定性"]},
                {"name": "测试成熟度", "metrics": ["单元测试通过率", "集成测试覆盖率", "对抗测试kill_rate"]},
                {"name": "运维韧性", "metrics": ["API断电恢复时间", "错误处理完备性", "日志可观测性"]},
                {"name": "知识管理", "metrics": ["文档新鲜度", "检索有效率", "新人上手时间"]},
            ],
            "report_template": {
                "section1": "系统概览（3句话）",
                "section2": "各维度评分雷达图（数据+主观判断结合）",
                "section3": "Top3风险与根因分析（用5 Whys法）",
                "section4": "下一步升级建议（按优先级排序，含ROI估算）",
                "section5": "需要提请外援会诊的专项问题",
            },
        }

    def continuous_improvement_loop(self, last_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        在没有人工输入情况下的合理迭代机制
        """
        return {
            "autonomous_actions": [
                "每周运行 baseline-checker，自动生成健康度趋势图",
                "每月扫描一次所有SKILL.md，标记缺失/过时/未接入测试的Skill",
                "当 baseline 通过率连续3次低于70%时，自动生成技术外援请求单",
                "将每次修复的问题和根因写入 `memory/tech-debt-YYYY-MM.md`，建立技术债务账本",
            ],
            "theoretical_research": [
                "通过 knowledge_consultant 定期获取软件工程、系统架构、AIops 的前沿理论",
                "将理论方法映射到我们的具体技术栈中，生成实验性升级分支",
                "在小范围（单个Skill）验证新理论，记录数据和偏差",
                "验证成功后推广，验证失败后归档为'rejected_approaches'",
            ],
            "customer_simulation": [
                "模拟用户场景：'如果Egbertie是新客户，他能在30分钟内理解我们的系统架构吗？'",
                "定期运行 'demo_unified.py' 并录制/记录执行过程，作为'产品可用性'指标",
                "基于模拟结果优化 onboarding 文档和快速启动路径",
            ],
        }
