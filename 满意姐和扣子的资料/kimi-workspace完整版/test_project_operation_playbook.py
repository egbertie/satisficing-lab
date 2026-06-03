"""
test_project_operation_playbook.py
一堂·复盘营项目运营管理方法论资产测试
"""

import pytest
from project_operation_playbook import (
    ProjectOperationPlaybook,
    MilestoneStage,
    DecisionType,
    TimeQuadrant,
    ReviewFrequency,
    BusinessModelCanvas,
)


class TestMilestoneModule:
    def test_add_and_check_milestone(self):
        pb = ProjectOperationPlaybook("TestProject")
        pb.add_milestone(
            "MVP上线",
            "2026-06-01",
            ["完成核心功能", "通过内测", "获取首批100用户"],
            MilestoneStage.EXPLORATION,
        )
        result = pb.milestone_check("MVP上线", ["完成核心功能", "获取首批100用户"])
        assert result["criteria_total"] == 3
        assert result["criteria_met"] == 2
        assert result["achievement_ratio"] == 0.67
        assert "部分达成" in result["status"]


class TestDecisionModule:
    def test_make_go_decision(self):
        pb = ProjectOperationPlaybook("TestProject")
        log = pb.make_decision("是否投放广告", ["投放", "不投放"], "投放", 10000, 50000, 20)
        assert log.decision_type == DecisionType.GO
        assert log.roi_estimate["roi"] == 5.0

    def test_make_no_go_decision(self):
        pb = ProjectOperationPlaybook("TestProject")
        log = pb.make_decision("是否参加展会", ["参加", "不参加"], "参加", 50000, 30000, 80)
        assert log.decision_type == DecisionType.NO_GO

    def test_make_experiment_decision(self):
        pb = ProjectOperationPlaybook("TestProject")
        log = pb.make_decision("新品类扩张", ["扩张", "不扩张"], "扩张", 100000, 250000, 200)
        assert log.decision_type == DecisionType.EXPERIMENT


class TestFiveStepDiagnosis:
    def test_complete_five_step(self):
        pb = ProjectOperationPlaybook("TestProject")
        answers = {
            1: "中小企业主，获客成本高，缺乏系统决策方法。",
            2: "提供 AI 决策教练服务，降低合伙人匹配风险。",
            3: "按项目或按年收费，成本主要是 AI 算力和人力。",
            4: "通过内容营销和口碑裂变，壁垒是案例库和方法论。",
            5: "创始人有 22 年金融+创业双系统经验，且有认证体系。",
        }
        result = pb.five_step_diagnosis(answers)
        assert result["score"] == 100
        assert len(result["gaps"]) == 0

    def test_incomplete_five_step(self):
        pb = ProjectOperationPlaybook("TestProject")
        answers = {1: "中小企业", 2: "", 3: "赚钱", 4: "", 5: "有经验"}
        result = pb.five_step_diagnosis(answers)
        assert result["score"] < 100
        assert len(result["gaps"]) > 0


class TestTimeManagement:
    def test_time_audit(self):
        pb = ProjectOperationPlaybook("TestProject")
        pb.add_task("写PRD", TimeQuadrant.Q2_IMPORTANT_NOT_URGENT, 10)
        pb.add_task("回邮件", TimeQuadrant.Q3_NOT_IMPORTANT_URGENT, 2)
        pb.add_task("开会", TimeQuadrant.Q1_IMPORTANT_URGENT, 4)
        audit = pb.time_audit()
        assert audit["q2_hours"] == 10
        assert audit["total_pending_hours"] == 16
        assert abs(audit["q2_ratio"] - 0.625) < 0.01
        assert audit["assessment"] == "优秀"


class TestKnowledgeManagement:
    def test_knowledge_output(self):
        pb = ProjectOperationPlaybook("TestProject")
        pb.add_knowledge("ROI评估", "任何决策前计算投入产出比")
        pb.add_knowledge("里程碑", "设置3-5个可验证的业务节点")
        result = pb.knowledge_output_check()
        assert result["knowledge_topics"] == 2
        assert "积累输入" in result["healthcheck"]


class TestReviewModule:
    def test_conduct_and_summary(self):
        pb = ProjectOperationPlaybook("TestProject")
        pb.conduct_review(
            ReviewFrequency.WEEKLY,
            ["完成MVP", "获取5条用户反馈"],
            ["用户最关注价格"],
            ["调整定价策略", "优化 landing page"],
            "定价是转化率的最大杠杆",
        )
        summary = pb.review_summary()
        assert summary["total_reviews"] == 1
        assert summary["by_type"][ReviewFrequency.WEEKLY.value] == 1
        assert "定价是转化率的最大杠杆" in summary["latest_red_dot"]


class TestBusinessModelCanvas:
    def test_complete_canvas(self):
        pb = ProjectOperationPlaybook("TestProject")
        canvas = BusinessModelCanvas(
            customer_segments="硬科技初创企业创始人",
            value_propositions="合伙人匹配决策教练",
            channels="线上内容+私域+推荐",
            customer_relationships="一对一咨询+会员社群",
            revenue_streams="按项目收费+年费会员",
            key_resources="案例库+方法论+专家团队",
            key_activities="案例研究+客户访谈+课程研发",
            key_partnerships="孵化器+投资机构",
            cost_structure="人力+内容制作+营销",
        )
        result = pb.build_business_model(canvas)
        assert result["completeness"] == 1.0
        assert result["status"] == "完整"

    def test_incomplete_canvas(self):
        pb = ProjectOperationPlaybook("TestProject")
        canvas = BusinessModelCanvas(customer_segments="初创企业")
        result = pb.build_business_model(canvas)
        assert result["completeness"] < 0.5
        assert result["status"] == "待完善"


class TestMoatAssessment:
    def test_moat_assessment(self):
        pb = ProjectOperationPlaybook("TestProject")
        factors = {"技术壁垒": 0.8, "网络效应": 0.2, "品牌认知": 0.6, "成本优势": 0.3, "规模效应": 0.1}
        result = pb.moat_assessment(factors)
        assert result["avg_moat_score"] == 0.4
        assert result["strongest_moat"] == "技术壁垒"
        assert result["assessment"] == "中等壁垒"


class TestConversionOptimizer:
    def test_conversion_optimizer(self):
        pb = ProjectOperationPlaybook("TestProject")
        funnel = {"曝光": 10000, "点击": 500, "注册": 100, "付费": 10}
        result = pb.conversion_optimizer(funnel)
        assert result["overall_conversion"] == 0.001
        assert result["weakest_link"]["from"] == "曝光"
        assert result["weakest_link"]["to"] == "点击"


class TestRedDotDiscovery:
    def test_red_dot_found(self):
        pb = ProjectOperationPlaybook("TestProject")
        result = pb.red_dot_discovery(
            ["商业分析", "教育", "写作"],
            ["商业分析", "AI应用", "健康管理"],
            ["商业分析", "沟通", "系统设计"],
        )
        assert "商业分析" in result["red_dot_candidates"]
        assert "聚焦红点交集领域" in result["guidance"]

    def test_red_dot_empty(self):
        pb = ProjectOperationPlaybook("TestProject")
        result = pb.red_dot_discovery(["音乐"], ["编程"], ["体育"])
        assert len(result["red_dot_candidates"]) == 0
        assert "扩大交集" in result["guidance"]


class TestHealthReport:
    def test_export_health_report(self):
        pb = ProjectOperationPlaybook("TestProject")
        pb.add_milestone("MVP", "2026-06-01", ["功能完成"], MilestoneStage.EXPLORATION)
        pb.add_task("测试", TimeQuadrant.Q2_IMPORTANT_NOT_URGENT, 5)
        report = pb.export_project_health_report()
        assert report["project_name"] == "TestProject"
        assert report["milestones"]["total"] == 1
        assert "tasks" in report
        assert "reviews" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
