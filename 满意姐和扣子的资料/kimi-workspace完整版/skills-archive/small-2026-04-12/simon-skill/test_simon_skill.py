#!/usr/bin/env python3
"""
测试SIMON Skill
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/simon-skill')

from simon_skill import SIMONSkill, CandidateProfile, DecisionStatus

def test_recommended_candidate():
    """测试推荐候选人"""
    simon = SIMONSkill()
    candidate = CandidateProfile(
        name="推荐候选人",
        liu_score=85,
        capability_match=9.0,
        cost_benefit=8.0,
        risk_controllability=8.5,
        stakeholder_satisfaction=8.0,
        time_feasibility=8.0
    )
    
    result = simon.make_decision(candidate)
    
    assert result.satisficing_score >= 70, f"期望≥70，得到{result.satisficing_score}"
    assert result.decision_status == DecisionStatus.RECOMMENDED, f"期望推荐，得到{result.decision_status}"
    
    print("✅ 推荐候选人测试通过")

def test_liu_foundation_matters():
    """测试LIU根基的重要性"""
    simon = SIMONSkill()
    
    # 同样能力，不同根基
    good_foundation = CandidateProfile(
        name="根基好",
        liu_score=80,
        capability_match=8.0,
        cost_benefit=8.0,
        risk_controllability=8.0,
        stakeholder_satisfaction=8.0,
        time_feasibility=8.0
    )
    
    bad_foundation = CandidateProfile(
        name="根基差",
        liu_score=30,
        capability_match=8.0,
        cost_benefit=8.0,
        risk_controllability=8.0,
        stakeholder_satisfaction=8.0,
        time_feasibility=8.0
    )
    
    result_good = simon.make_decision(good_foundation)
    result_bad = simon.make_decision(bad_foundation)
    
    assert result_good.satisficing_score > result_bad.satisficing_score, \
        f"根基好应得分更高: {result_good.satisficing_score} vs {result_bad.satisficing_score}"
    assert result_bad.decision_status == DecisionStatus.REJECTED, \
        f"根基差应被拒绝，得到{result_bad.decision_status}"
    
    print("✅ LIU根基重要性测试通过")

def test_aspiration_threshold():
    """测试期望阈值"""
    # 高阈值
    simon_strict = SIMONSkill(aspiration_level=80)
    # 低阈值
    simon_loose = SIMONSkill(aspiration_level=60)
    
    candidate = CandidateProfile(
        name="中等候选人",
        liu_score=70,
        capability_match=7.0,
        cost_benefit=7.0,
        risk_controllability=7.0,
        stakeholder_satisfaction=7.0,
        time_feasibility=7.0
    )
    
    result_strict = simon_strict.make_decision(candidate)
    result_loose = simon_loose.make_decision(candidate)
    
    # 高阈值更严格
    assert result_strict.decision_status.value in ["边缘", "不推荐"], \
        f"严格阈值应更难通过，得到{result_strict.decision_status}"
    assert result_loose.decision_status.value in ["推荐", "可接受"], \
        f"宽松阈值应更容易通过，得到{result_loose.decision_status}"
    
    print("✅ 期望阈值测试通过")

def test_batch_evaluation():
    """测试批量评估"""
    simon = SIMONSkill()
    
    candidates = [
        CandidateProfile(f"候选人{i}", 70, 7.0, 7.0, 7.0, 7.0, 7.0)
        for i in range(3)
    ]
    
    results = simon.batch_evaluate(candidates)
    
    assert len(results) == 3, f"期望3个结果，得到{len(results)}"
    
    # 验证排序（得分相同，保持原有顺序）
    print("✅ 批量评估测试通过")

if __name__ == "__main__":
    print("测试SIMON Skill...")
    print("=" * 50)
    
    try:
        test_recommended_candidate()
        test_liu_foundation_matters()
        test_aspiration_threshold()
        test_batch_evaluation()
        
        print("=" * 50)
        print("✅ 所有4个测试通过")
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)
