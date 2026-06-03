#!/usr/bin/env python3
"""
测试CONFUCIUS Skill
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/confucius-skill')

from confucius_skill import ConfuciusSkill, PartnerProfile, GovernanceLevel

def test_excellent_partner():
    """测试优秀合伙人"""
    confucius = ConfuciusSkill()
    partner = PartnerProfile(
        name="优秀合伙人",
        benevolence=8.5,
        righteousness=8.0,
        propriety=8.5,
        wisdom=8.0,
        trustworthiness=9.0,
        cultural_alignment=8.5
    )
    
    result = confucius.evaluate_ethical_governance(partner)
    
    assert result.overall_ethical_score >= 80
    assert result.governance_level in [GovernanceLevel.EXCELLENT, GovernanceLevel.GOOD]
    assert result.trustworthiness_rating >= 90
    
    print("✅ 优秀合伙人测试通过")

def test_violation_penalty():
    """测试违规惩罚"""
    confucius = ConfuciusSkill()
    
    # 无违规
    clean_partner = PartnerProfile(
        name="干净合伙人",
        benevolence=7.0,
        trustworthiness=7.0,
        ethical_violations=[]
    )
    
    # 有违规
    dirty_partner = PartnerProfile(
        name="问题合伙人",
        benevolence=7.0,
        trustworthiness=7.0,
        ethical_violations=["违规1", "违规2"]
    )
    
    result_clean = confucius.evaluate_ethical_governance(clean_partner)
    result_dirty = confucius.evaluate_ethical_governance(dirty_partner)
    
    assert result_dirty.overall_ethical_score < result_clean.overall_ethical_score
    assert result_dirty.conflict_resolution is not None
    
    print("✅ 违规惩罚测试通过")

def test_trustworthiness_calculation():
    """测试可信度计算"""
    confucius = ConfuciusSkill()
    partner = PartnerProfile(
        name="测试合伙人",
        trustworthiness=9.0,  # 高诚信
        cultural_alignment=8.0
    )
    
    result = confucius.evaluate_ethical_governance(partner)
    
    # 高诚信应该带来高可信度
    assert result.trustworthiness_rating > result.overall_ethical_score
    
    print("✅ 可信度计算测试通过")

def test_five_virtues_balance():
    """测试五常平衡"""
    confucius = ConfuciusSkill()
    partner = PartnerProfile(
        name="平衡合伙人",
        benevolence=7.0,
        righteousness=7.0,
        propriety=7.0,
        wisdom=7.0,
        trustworthiness=7.0
    )
    
    result = confucius.evaluate_ethical_governance(partner)
    
    # 所有五常应该都有分数
    assert len(result.five_virtues_score) == 5
    for virtue, score in result.five_virtues_score.items():
        assert score == 70.0, f"{virtue}期望70，得到{score}"
    
    print("✅ 五常平衡测试通过")

if __name__ == "__main__":
    print("测试CONFUCIUS Skill...")
    print("=" * 50)
    
    try:
        test_excellent_partner()
        test_violation_penalty()
        test_trustworthiness_calculation()
        test_five_virtues_balance()
        
        print("=" * 50)
        print("✅ 所有4个测试通过")
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)
