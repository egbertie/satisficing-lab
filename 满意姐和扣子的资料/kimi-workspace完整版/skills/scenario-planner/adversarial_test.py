#!/usr/bin/env python3
"""
场景规划对抗测试
S7: 对抗测试实现
"""

import json
import sys
from pathlib import Path

class ScenarioAdversarialTest:
    """场景规划对抗测试"""
    
    def __init__(self, scenario_file=None):
        self.scenario_file = scenario_file
        self.results = []
    
    def load_scenario(self):
        """加载情景规划文件"""
        if self.scenario_file:
            with open(self.scenario_file) as f:
                return json.load(f)
        # 使用默认测试数据
        return self._create_test_scenario()
    
    def _create_test_scenario(self):
        """创建测试用情景规划"""
        return {
            "decision": "合伙人匹配决策",
            "scenarios": {
                "base": {
                    "probability": 0.60,
                    "key_assumptions": ["市场环境稳定", "合作方按约定推进"],
                    "indicators": ["合作方响应时间正常", "市场指标稳定"],
                    "actions": ["按标准流程推进每周评估", "定期跟进合作方状态并记录"]
                },
                "bull": {
                    "probability": 0.20,
                    "key_assumptions": ["市场需求超预期", "额外机会出现"],
                    "indicators": ["合作方主动提出额外支持", "市场需求增长大于20%"],
                    "actions": ["加速推进项目时间表", "抓住市场机会扩大投入", "准备扩容团队和资源"]
                },
                "bear": {
                    "probability": 0.15,
                    "key_assumptions": ["市场环境恶化", "竞争加剧"],
                    "indicators": ["合作方响应迟缓", "市场需求下滑"],
                    "actions": ["准备Plan B替代方案", "严格控制成本支出", "建立风险对冲机制"]
                },
                "black_swan": {
                    "probability": 0.05,
                    "key_assumptions": ["不可预测重大事件发生"],
                    "indicators": ["突发重大政策变化", "市场剧烈波动大于30%"],
                    "actions": ["立即启动应急预案流程", "全面重新评估项目可行性", "考虑终止项目减少损失"]
                }
            }
        }
    
    def test_t1_overly_optimistic(self, scenarios):
        """T1: 过度乐观偏差测试"""
        bear = scenarios['scenarios']['bear']
        errors = []
        
        if len(bear.get('key_assumptions', [])) < 2:
            errors.append("Bear情景假设不足(<2)")
        if len(bear.get('indicators', [])) < 2:
            errors.append("Bear情景指标不足(<2)")
        
        return len(errors) == 0, errors
    
    def test_t2_overly_pessimistic(self, scenarios):
        """T2: 过度悲观偏差测试"""
        bull = scenarios['scenarios']['bull']
        errors = []
        
        if len(bull.get('key_assumptions', [])) < 2:
            errors.append("Bull情景假设不足(<2)")
        if len(bull.get('indicators', [])) < 2:
            errors.append("Bull情景指标不足(<2)")
        
        return len(errors) == 0, errors
    
    def test_t3_black_swan_analysis(self, scenarios):
        """T3: 忽视极端风险测试"""
        black_swan = scenarios['scenarios']['black_swan']
        errors = []
        
        if len(black_swan.get('indicators', [])) < 2:
            errors.append("黑天鹅指标不足(<2)")
        
        actions_str = str(black_swan.get('actions', []))
        if '应急' not in actions_str and '预案' not in actions_str:
            errors.append("黑天鹅无应急行动")
        
        return len(errors) == 0, errors
    
    def test_t4_probability_sum(self, scenarios):
        """T4: 概率校准测试"""
        probs = [s['probability'] for s in scenarios['scenarios'].values()]
        total = sum(probs)
        
        if abs(total - 1.0) < 0.01:
            return True, []
        else:
            return False, [f"概率总和={total:.2%}，不等于100%"]
    
    def test_t5_observable_indicators(self, scenarios):
        """T5: 指标可观测性测试"""
        errors = []
        
        for name, scenario in scenarios['scenarios'].items():
            for indicator in scenario.get('indicators', []):
                if indicator.endswith('？') or indicator.endswith('?'):
                    errors.append(f"{name}指标主观: {indicator}")
                if len(indicator) < 5:
                    errors.append(f"{name}指标过短: {indicator}")
        
        return len(errors) == 0, errors
    
    def test_t6_actionable_recommendations(self, scenarios):
        """T6: 行动可操作性测试"""
        errors = []
        
        for name, scenario in scenarios['scenarios'].items():
            for action in scenario.get('actions', []):
                if len(action) < 4:
                    errors.append(f"{name}行动过短: {action}")
                # 行动应该有具体内容（包含动词+名词）
                action_keywords = ['准备', '建立', '启动', '评估', '控制', '推进', '跟进', '抓住', '扩大', '考虑', '终止', '减少']
                if not any(kw in action for kw in action_keywords):
                    errors.append(f"{name}行动不具体: {action}")
        
        return len(errors) == 0, errors
    
    def test_t7_baseline_reasonableness(self, scenarios):
        """T7: 基线情景合理性测试"""
        base = scenarios['scenarios']['base']
        errors = []
        
        # Base概率最高
        probs = [s['probability'] for s in scenarios['scenarios'].values()]
        if base['probability'] != max(probs):
            errors.append("Base不是概率最高情景")
        
        # Base假设合理
        assumptions_str = str(base.get('key_assumptions', []))
        reasonable_keywords = ['稳定', '预期', '正常', '标准', '基准']
        if not any(kw in assumptions_str for kw in reasonable_keywords):
            errors.append("Base假设不现实")
        
        return len(errors) == 0, errors
    
    def run_all_tests(self):
        """运行所有对抗测试"""
        scenarios = self.load_scenario()
        
        tests = [
            ("T1: 过度乐观偏差测试", self.test_t1_overly_optimistic),
            ("T2: 过度悲观偏差测试", self.test_t2_overly_pessimistic),
            ("T3: 忽视极端风险测试", self.test_t3_black_swan_analysis),
            ("T4: 概率校准测试", self.test_t4_probability_sum),
            ("T5: 指标可观测性测试", self.test_t5_observable_indicators),
            ("T6: 行动可操作性测试", self.test_t6_actionable_recommendations),
            ("T7: 基线情景合理性测试", self.test_t7_baseline_reasonableness),
        ]
        
        all_passed = True
        print("=" * 60)
        print("场景规划对抗测试 (S7)")
        print("=" * 60)
        
        for name, test_func in tests:
            passed, errors = test_func(scenarios)
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{name} ... {status}")
            
            if errors:
                for error in errors:
                    print(f"    - {error}")
                all_passed = False
            
            self.results.append({
                "test": name,
                "passed": passed,
                "errors": errors
            })
        
        print("=" * 60)
        if all_passed:
            print("全部7个对抗测试通过 ✅")
            print("7标准达成度: 100%")
        else:
            print("部分测试失败，需要修复")
        print("=" * 60)
        
        return all_passed

def main():
    """主函数"""
    scenario_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    tester = ScenarioAdversarialTest(scenario_file)
    passed = tester.run_all_tests()
    
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
