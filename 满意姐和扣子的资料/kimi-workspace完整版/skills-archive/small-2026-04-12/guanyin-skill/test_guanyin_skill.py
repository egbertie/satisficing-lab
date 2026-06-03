#!/usr/bin/env python3
"""
测试GUANYIN Skill
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/guanyin-skill')

from guanyin_skill import GuanyinSkill, EnvironmentData, EnvironmentSignal, ResponseStrategy

def test_accelerate_scenario():
    """测试加速推进场景"""
    guanyin = GuanyinSkill()
    data = EnvironmentData(
        market_trend=8.5,
        team_morale=8.0,
        risk_level=3.0,
        opportunity_score=9.0,
        resource_availability=7.0
    )
    
    insight = guanyin.sense_environment(data)
    
    assert insight.recommended_strategy == ResponseStrategy.ACCELERATE
    assert insight.confidence >= 70
    assert "形势" in insight.overall_situation
    
    print("✅ 加速推进场景测试通过")

def test_retreat_scenario():
    """测试策略收缩场景"""
    guanyin = GuanyinSkill()
    data = EnvironmentData(
        market_trend=3.0,
        team_morale=4.0,
        risk_level=8.5,
        opportunity_score=3.0,
        resource_availability=3.5
    )
    
    insight = guanyin.sense_environment(data)
    
    assert insight.recommended_strategy == ResponseStrategy.RETREAT
    assert any("高风险" in s for s in insight.key_signals)
    
    print("✅ 策略收缩场景测试通过")

def test_signal_extraction():
    """测试信号提取"""
    guanyin = GuanyinSkill()
    data = EnvironmentData(
        market_trend=8.0,
        team_morale=4.0,
        signals=[
            (EnvironmentSignal.OPPORTUNITY, "新市场开放", 9)
        ]
    )
    
    insight = guanyin.sense_environment(data)
    
    assert len(insight.key_signals) >= 2  # 至少市场信号和显式信号
    assert any("新市场" in s for s in insight.key_signals)
    
    print("✅ 信号提取测试通过")

def test_light_asset_advice():
    """测试轻资产建议"""
    guanyin = GuanyinSkill()
    data = EnvironmentData(
        resource_availability=4.0,
        risk_level=7.0
    )
    
    insight = guanyin.sense_environment(data)
    
    assert "轻资产" in insight.light_asset_advice or "资源" in insight.light_asset_advice
    
    print("✅ 轻资产建议测试通过")

if __name__ == "__main__":
    print("测试GUANYIN Skill...")
    print("=" * 50)
    
    try:
        test_accelerate_scenario()
        test_retreat_scenario()
        test_signal_extraction()
        test_light_asset_advice()
        
        print("=" * 50)
        print("✅ 所有4个测试通过")
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)
