"""
外援代码集成测试
验证所有外援组件能正常工作
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'reference'))

from simon_agent import HerbertSimonAgent
from pentad_extractor import RuleEngine
from five_totems_part1 import LiuYuxiAgent, GuanZizaiAgent, SimonTotemAdapter
from five_totems_part2 import ConfuciusAgent, HuiNengAgent, ConflictResolver


def test_simon_agent():
    """测试司马贺满意解Agent"""
    agent = HerbertSimonAgent()
    scenario = {
        'scenario': '寻找硬科技项目合伙人',
        'constraints': ['有产业资源', '全职投入', '接受较低估值'],
        'founder_profile': '技术背景，首次创业，资金有限',
        'risk_preference': 'moderate',
        'candidates': [
            {'name': 'A', 'experience': '10年销售', 'network': '强', 'equity_expectation': '高', 'availability': 'full_time'},
            {'name': 'B', 'experience': '5年产品', 'network': '中', 'equity_expectation': '中', 'availability': 'full_time'},
            {'name': 'C', 'experience': '8年投资', 'network': '强', 'equity_expectation': '低', 'availability': 'full_time'}
        ]
    }
    result = agent.decide(scenario)
    assert result['process_metadata']['satisfactory_count'] == 3
    assert result['recommendation']['action'] == 'select_best_in_satisfactory'
    print('✓ test_simon_agent passed')


def test_pentad_extractor():
    """测试五元组提取器"""
    engine = RuleEngine()
    test_text = '''深圳AI芯片项目，创始人张博士，技术背景强但缺乏商业经验。
    寻找商业合伙人，通过朋友介绍认识了李总（前华为销售总监）。
    经过3个月磨合，双方在股权分配上产生分歧，最终合作失败。
    反思：技术创始人应更早明确股权架构，避免后期纠纷。'''
    
    hints = engine.pre_extract(test_text)
    assert len(hints['situation']) > 0
    assert len(hints['judgment']) > 0
    assert len(hints['outcome']) > 0
    assert len(hints['reflection']) > 0
    print('✓ test_pentad_extractor passed')


def test_five_totems():
    """测试五图腾Agent"""
    founder_values = ['长期主义', '技术理想', '公平分享']
    founder_profile = {
        'background': 'tech',
        'decision_style': 'analytical',
        'stress_response': 'steady',
        'management_style': 'hands_off'
    }
    candidate_profile = {
        'values_expression': '相信长期价值，愿意与团队共同成长',
        'track_record': '连续创业者，成功退出经验，诚信记录良好',
        'collaboration_style': '强调协作沟通，尊重团队决策',
        'conflict_resolution': '倾向于协商解决',
        'decision_style': 'analytical',
        'stress_response': 'steady',
        'autonomy_need': 'medium',
        'innovation_ability': '模式创新',
        'problem_solving_record': '多次重新定义产品方向',
        'breakthrough_cases': ['首创XX模式'],
        'failure_experience': '从失败中学到很多，成长显著',
        'experience': '8年'
    }
    
    # 刘禹锡
    liuyuxi = LiuYuxiAgent()
    result = liuyuxi.evaluate(founder_values, candidate_profile)
    assert 'score' in result
    assert 'recommendation' in result
    
    # 观自在
    guanzizai = GuanZizaiAgent()
    result = guanzizai.evaluate(founder_profile, candidate_profile)
    assert 'score' in result
    
    # 孔子
    confucius = ConfuciusAgent()
    result = confucius.evaluate(founder_values, candidate_profile)
    assert 'score' in result
    
    # 慧能
    huineng = HuiNengAgent()
    result = huineng.evaluate(founder_profile, candidate_profile)
    assert 'score' in result
    
    print('✓ test_five_totems passed')


def test_conflict_resolver():
    """测试冲突消解器"""
    resolver = ConflictResolver()
    evaluations = {
        'liuyuxi': {'score': 0.8, 'analysis': '德馨良好', 'recommendation': '积极'},
        'simon': {'score': 0.9, 'analysis': '满意解', 'recommendation': '可接受'},
        'guanzizai': {'score': 0.7, 'analysis': '直觉兼容', 'recommendation': '积极'},
        'confucius': {'score': 0.85, 'analysis': '五常良好', 'recommendation': '积极'},
        'huineng': {'score': 0.6, 'analysis': '创新一般', 'recommendation': '可接受'}
    }
    scenario = {'context': '测试场景', 'constraints': []}
    result = resolver.resolve(evaluations, scenario)
    assert 'consensus_score' in result
    assert result['conflicts_detected'] == 0  # 无大冲突
    print('✓ test_conflict_resolver passed')


if __name__ == '__main__':
    print('=== 外援代码集成测试 ===')
    test_simon_agent()
    test_pentad_extractor()
    test_five_totems()
    test_conflict_resolver()
    print()
    print('=== 所有测试通过！===')
