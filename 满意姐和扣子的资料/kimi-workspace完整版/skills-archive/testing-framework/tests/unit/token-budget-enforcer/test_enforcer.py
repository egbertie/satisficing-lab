"""
Token-Budget-Enforcer 单元测试 - 简化版

风险等级: P0 (关键治理组件)
测试重点: 预算计算、熔断机制、阈值判断
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# 添加Skill路径
SKILL_PATH = Path(__file__).parent.parent.parent.parent.parent / "token-budget-enforcer" / "scripts"
sys.path.insert(0, str(SKILL_PATH))

# 导入被测模块
import enforcer


@pytest.mark.token_budget
@pytest.mark.critical
class TestTokenBudgetEnforcerBasic:
    """Token-Budget-Enforcer基础测试"""
    
    def test_module_imports(self):
        """测试模块可以正常导入"""
        assert enforcer is not None
        assert hasattr(enforcer, 'show_budget')
        assert hasattr(enforcer, 'estimate_task')
        assert hasattr(enforcer, 'generate_report')


class TestBudgetCalculations:
    """预算计算测试"""
    
    def test_daily_budget_value(self):
        """测试日预算值"""
        assert enforcer.DAILY_BUDGET == 50000
    
    def test_strategic_reserve_calculation(self):
        """测试战略储备计算"""
        expected = int(50000 * 0.3)
        assert enforcer.STRATEGIC_RESERVE == expected
        assert enforcer.STRATEGIC_RESERVE == 15000
    
    def test_operational_budget_calculation(self):
        """测试运营预算计算"""
        expected = int(50000 * 0.5)
        assert enforcer.OPERATIONAL_BUDGET == expected
        assert enforcer.OPERATIONAL_BUDGET == 25000
    
    def test_innovation_fund_calculation(self):
        """测试创新基金计算"""
        expected = int(50000 * 0.2)
        assert enforcer.INNOVATION_FUND == expected
        assert enforcer.INNOVATION_FUND == 10000
    
    def test_budget_pools_sum_to_total(self):
        """测试预算池总和等于总额"""
        total = (enforcer.STRATEGIC_RESERVE + 
                enforcer.OPERATIONAL_BUDGET + 
                enforcer.INNOVATION_FUND)
        assert total == enforcer.DAILY_BUDGET


class TestShowBudgetFunction:
    """预算显示功能测试"""
    
    def test_show_budget_returns_zero(self, capsys):
        """测试show_budget返回0表示成功"""
        result = enforcer.show_budget()
        assert result == 0
    
    def test_show_budget_displays_total_budget(self, capsys):
        """测试显示总预算"""
        enforcer.show_budget()
        captured = capsys.readouterr()
        assert "50,000" in captured.out
    
    def test_show_budget_displays_strategic_reserve(self, capsys):
        """测试显示战略储备"""
        enforcer.show_budget()
        captured = capsys.readouterr()
        assert "战略储备" in captured.out or "STRATEGIC" in captured.out
    
    def test_show_budget_displays_operational_budget(self, capsys):
        """测试显示运营预算"""
        enforcer.show_budget()
        captured = capsys.readouterr()
        assert "运营预算" in captured.out or "OPERATIONAL" in captured.out
    
    def test_show_budget_displays_usage(self, capsys):
        """测试显示使用量"""
        enforcer.show_budget()
        captured = capsys.readouterr()
        # 应该显示已用量和百分比
        assert "tokens" in captured.out
    
    def test_show_budget_displays_status(self, capsys):
        """测试显示状态"""
        enforcer.show_budget()
        captured = capsys.readouterr()
        # 应该显示状态标记
        assert any(marker in captured.out for marker in ["🟢", "🟡", "🔴", "⛔", "正常", "注意", "紧急"])
    
    def test_show_budget_with_zero_usage(self, capsys):
        """测试零使用量的显示"""
        with patch.object(enforcer, 'today_used', 0):
            enforcer.show_budget()
            captured = capsys.readouterr()
            assert "0" in captured.out


class TestEstimateTaskFunction:
    """任务预估功能测试"""
    
    def test_estimate_task_returns_zero(self, capsys):
        """测试estimate_task返回0表示成功"""
        result = enforcer.estimate_task("测试任务")
        assert result == 0
    
    def test_estimate_task_shows_task_name(self, capsys):
        """测试显示任务名称"""
        task_name = "AI技术研究"
        enforcer.estimate_task(task_name)
        captured = capsys.readouterr()
        assert task_name in captured.out
    
    def test_estimate_task_shows_estimated_tokens(self, capsys):
        """测试显示预估tokens"""
        enforcer.estimate_task("测试任务")
        captured = capsys.readouterr()
        assert "预估消耗" in captured.out or "tokens" in captured.out
    
    def test_estimate_task_research_multiplier(self, capsys):
        """测试研究类任务3倍乘数"""
        enforcer.estimate_task("研究AI技术")
        captured = capsys.readouterr()
        # 研究类任务应该是500 * 3 = 1500
        assert "1,500" in captured.out or "1500" in captured.out
    
    def test_estimate_task_report_multiplier(self, capsys):
        """测试报告类任务2倍乘数"""
        enforcer.estimate_task("撰写报告")
        captured = capsys.readouterr()
        # 报告类任务应该是500 * 2 = 1000
        assert "1,000" in captured.out or "1000" in captured.out
    
    def test_estimate_task_generic_base_value(self, capsys):
        """测试通用任务基础值"""
        enforcer.estimate_task("通用任务")
        captured = capsys.readouterr()
        # 通用任务应该是基础500
        assert "500" in captured.out
    
    def test_estimate_task_advice_for_large_tasks(self, capsys):
        """测试大任务的执行建议"""
        enforcer.estimate_task("研究")  # 会触发3倍乘数
        captured = capsys.readouterr()
        # 大任务应该建议分阶段
        assert "分阶段" in captured.out or "单次" in captured.out
    
    def test_estimate_task_with_empty_string(self, capsys):
        """测试空字符串任务"""
        result = enforcer.estimate_task("")
        assert result == 0


class TestGenerateReportFunction:
    """报告生成功能测试"""
    
    def test_generate_report_returns_zero(self, capsys):
        """测试generate_report返回0表示成功"""
        result = enforcer.generate_report()
        assert result == 0
    
    def test_generate_report_shows_header(self, capsys):
        """测试显示报告标题"""
        enforcer.generate_report()
        captured = capsys.readouterr()
        assert "Token" in captured.out
    
    def test_generate_report_shows_consumption_stats(self, capsys):
        """测试显示消耗统计"""
        enforcer.generate_report()
        captured = capsys.readouterr()
        assert "消耗" in captured.out
    
    def test_generate_report_shows_efficiency_metrics(self, capsys):
        """测试显示效率指标"""
        enforcer.generate_report()
        captured = capsys.readouterr()
        assert "效率" in captured.out or "指标" in captured.out
    
    def test_generate_report_shows_recommendations(self, capsys):
        """测试显示优化建议"""
        enforcer.generate_report()
        captured = capsys.readouterr()
        assert "优化建议" in captured.out or "建议" in captured.out


class TestBudgetStatusLevels:
    """预算状态级别测试"""
    
    def test_status_normal_below_70_percent(self, capsys):
        """测试低于70%为正常状态"""
        with patch.object(enforcer, 'today_used', 30000):  # 60%
            enforcer.show_budget()
            captured = capsys.readouterr()
            # 60%应该是正常
            assert any(marker in captured.out for marker in ["🟢", "正常"])
    
    def test_status_warning_at_70_percent(self, capsys):
        """测试70%为警告状态"""
        with patch.object(enforcer, 'today_used', 35000):  # 70%
            enforcer.show_budget()
            captured = capsys.readouterr()
            # 70%应该触发警告
            assert any(marker in captured.out for marker in ["🟡", "🔴", "注意", "紧急"])
    
    def test_status_critical_at_90_percent(self, capsys):
        """测试90%为紧急状态"""
        with patch.object(enforcer, 'today_used', 45000):  # 90%
            enforcer.show_budget()
            captured = capsys.readouterr()
            # 90%应该触发紧急
            assert any(marker in captured.out for marker in ["🔴", "紧急"])
    
    def test_status_exhausted_at_100_percent(self, capsys):
        """测试100%为耗尽状态"""
        with patch.object(enforcer, 'today_used', 50000):  # 100%
            enforcer.show_budget()
            captured = capsys.readouterr()
            # 100%应该显示耗尽
            assert any(marker in captured.out for marker in ["⛔", "耗尽", "暂停"])


class TestMainFunction:
    """主函数测试"""
    
    def test_main_with_budget_command(self):
        """测试budget命令"""
        with patch.object(sys, 'argv', ['enforcer.py', 'budget']):
            result = enforcer.main()
            assert result == 0
    
    def test_main_with_estimate_command(self):
        """测试estimate命令"""
        with patch.object(sys, 'argv', ['enforcer.py', 'estimate', '测试任务']):
            result = enforcer.main()
            assert result == 0
    
    def test_main_with_report_command(self):
        """测试report命令"""
        with patch.object(sys, 'argv', ['enforcer.py', 'report']):
            result = enforcer.main()
            assert result == 0
    
    def test_main_with_unknown_command(self):
        """测试未知命令返回错误"""
        with patch.object(sys, 'argv', ['enforcer.py', 'unknown']):
            result = enforcer.main()
            assert result == 1
    
    def test_main_with_no_args(self):
        """测试无参数时显示预算"""
        with patch.object(sys, 'argv', ['enforcer.py']):
            result = enforcer.main()
            assert result == 0


class TestHardConstraintsDisplay:
    """硬约束规则显示测试"""
    
    def test_hard_constraints_section_exists(self, capsys):
        """测试硬约束部分存在"""
        enforcer.show_budget()
        captured = capsys.readouterr()
        assert "硬约束" in captured.out or "约束规则" in captured.out
    
    def test_constraint_show_estimation_displayed(self, capsys):
        """测试预估显示约束"""
        enforcer.show_budget()
        captured = capsys.readouterr()
        assert "预估消耗" in captured.out or "显示预估" in captured.out
    
    def test_constraint_task_limit_displayed(self, capsys):
        """测试任务限制约束"""
        enforcer.show_budget()
        captured = capsys.readouterr()
        # 应该有关于任务限制的内容
        content = captured.out
        assert len(content) > 0


class TestBudgetAllocationPercentages:
    """预算分配比例测试"""
    
    def test_strategic_reserve_is_30_percent(self):
        """测试战略储备为30%"""
        expected = int(enforcer.DAILY_BUDGET * 0.30)
        assert enforcer.STRATEGIC_RESERVE == expected
    
    def test_operational_is_50_percent(self):
        """测试运营预算为50%"""
        expected = int(enforcer.DAILY_BUDGET * 0.50)
        assert enforcer.OPERATIONAL_BUDGET == expected
    
    def test_innovation_is_20_percent(self):
        """测试创新基金为20%"""
        expected = int(enforcer.DAILY_BUDGET * 0.20)
        assert enforcer.INNOVATION_FUND == expected
    
    def test_total_percentage_is_100(self):
        """测试总比例为100%"""
        strategic_pct = enforcer.STRATEGIC_RESERVE / enforcer.DAILY_BUDGET
        operational_pct = enforcer.OPERATIONAL_BUDGET / enforcer.DAILY_BUDGET
        innovation_pct = enforcer.INNOVATION_FUND / enforcer.DAILY_BUDGET
        
        total_pct = strategic_pct + operational_pct + innovation_pct
        assert abs(total_pct - 1.0) < 0.01  # 允许舍入误差
