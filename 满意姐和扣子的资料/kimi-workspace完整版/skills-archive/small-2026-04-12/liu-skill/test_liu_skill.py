#!/usr/bin/env python3
"""
测试LIU Skill
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/liu-skill')

from liu_skill import LIUSkill, CandidateData, TrustLevel, Recommendation

def test_excellent_candidate():
    """测试优秀候选人"""
    liu = LIUSkill()
    candidate = CandidateData(
        name="优秀候选人",
        values_alignment=9.0,
        integrity_history=8.5,
        long_term_commitment=8.0,
        cultural_fit=8.5,
        reputation_score=9.0
    )
    
    result = liu.evaluate_partner(candidate)
    
    assert result.total_score >= 85, f"期望高分，得到{result.total_score}"
    assert result.trust_level == TrustLevel.L5_FULL_TRUST, f"期望L5，得到{result.trust_level}"
    assert result.recommendation == Recommendation.RECOMMEND, f"期望推荐，得到{result.recommendation}"
    
    print("✅ 优秀候选人测试通过")

def test_risky_candidate():
    """测试有风险候选人"""
    liu = LIUSkill()
    candidate = CandidateData(
        name="风险候选人",
        values_alignment=4.0,
        integrity_history=3.5,
        long_term_commitment=4.0,
        cultural_fit=3.5,
        reputation_score=3.0,
        red_flags=["有失信记录", "合同纠纷"]
    )
    
    result = liu.evaluate_partner(candidate)
    
    assert result.total_score < 50, f"期望低分，得到{result.total_score}"
    assert result.recommendation == Recommendation.NOT_RECOMMEND, f"期望不推荐，得到{result.recommendation}"
    assert len(result.risk_warnings) >= 2, f"期望至少2个风险预警，得到{len(result.risk_warnings)}"
    
    print("✅ 风险候选人测试通过")

def test_boundary_case():
    """测试边界情况"""
    liu = LIUSkill()
    candidate = CandidateData(
        name="边界候选人",
        values_alignment=7.0,
        integrity_history=7.0,
        long_term_commitment=7.0,
        cultural_fit=7.0,
        reputation_score=7.0
    )
    
    result = liu.evaluate_partner(candidate)
    
    assert result.total_score == 70.0, f"期望70分，得到{result.total_score}"
    assert result.trust_level == TrustLevel.L4_TRUSTED, f"期望L4，得到{result.trust_level}"
    
    print("✅ 边界测试通过")

def test_report_generation():
    """测试报告生成"""
    liu = LIUSkill()
    candidate = CandidateData(name="测试人员", values_alignment=8.0)
    
    result = liu.evaluate_partner(candidate)
    report = liu.format_report(result)
    
    assert "LIU根基与信任评估报告" in report
    assert result.candidate_name in report
    assert str(result.total_score) in report
    
    print("✅ 报告生成测试通过")

if __name__ == "__main__":
    print("测试LIU Skill...")
    print("=" * 50)
    
    try:
        test_excellent_candidate()
        test_risky_candidate()
        test_boundary_case()
        test_report_generation()
        
        print("=" * 50)
        print("✅ 所有4个测试通过")
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)
