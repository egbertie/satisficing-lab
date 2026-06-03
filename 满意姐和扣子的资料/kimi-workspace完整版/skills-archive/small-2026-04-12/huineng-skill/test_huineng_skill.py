#!/usr/bin/env python3
"""
测试HUINENG Skill
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/huineng-skill')

from huineng_skill import HuinengSkill, InsightItem, ActionPriority

def test_insight_synthesis():
    """测试洞察综合"""
    huineng = HuinengSkill()
    insights = [
        InsightItem("LIU", "根基优秀", 80, 7),
        InsightItem("SIMON", "决策可行", 75, 6),
        InsightItem("GUANYIN", "机会良好", 70, 8)
    ]
    
    synthesis = huineng.synthesize_insights(insights)
    
    assert "LIU" in synthesis
    assert "SIMON" in synthesis
    assert "根基优秀" in synthesis
    
    print("✅ 洞察综合测试通过")

def test_breakthrough_identification():
    """测试突破点识别"""
    huineng = HuinengSkill()
    
    # 有高紧迫性洞察
    insights_with_breakthrough = [
        InsightItem("TEST", "高紧迫洞察", 80, 9)
    ]
    
    breakthrough = huineng.identify_breakthrough(insights_with_breakthrough)
    assert breakthrough is not None
    assert "关键突破" in breakthrough
    
    # 无高紧迫性洞察
    insights_no_breakthrough = [
        InsightItem("TEST", "普通洞察", 80, 5)
    ]
    
    no_breakthrough = huineng.identify_breakthrough(insights_no_breakthrough)
    assert no_breakthrough is None
    
    print("✅ 突破点识别测试通过")

def test_action_generation():
    """测试行动生成"""
    huineng = HuinengSkill()
    insights = [
        InsightItem("LIU", "高置信高紧迫", 90, 9),
        InsightItem("SIMON", "普通", 70, 5)
    ]
    
    plan = huineng.generate_action_plan(insights)
    
    assert len(plan.action_sequence) >= 2
    assert plan.total_effort > 0
    assert 30 <= plan.success_probability <= 95
    
    # 高优先级行动在前
    priorities = [a.priority for a in plan.action_sequence]
    assert priorities[0] in [ActionPriority.CRITICAL, ActionPriority.HIGH]
    
    print("✅ 行动生成测试通过")

def test_priority_calculation():
    """测试优先级计算"""
    huineng = HuinengSkill()
    
    critical = InsightItem("TEST", "关键", 90, 9)  # 81分
    high = InsightItem("TEST", "高", 80, 7)       # 56分
    low = InsightItem("TEST", "低", 50, 3)        # 15分
    
    assert huineng._determine_priority(critical) == ActionPriority.CRITICAL
    assert huineng._determine_priority(high) == ActionPriority.HIGH
    assert huineng._determine_priority(low) == ActionPriority.LOW
    
    print("✅ 优先级计算测试通过")

if __name__ == "__main__":
    print("测试HUINENG Skill...")
    print("=" * 50)
    
    try:
        test_insight_synthesis()
        test_breakthrough_identification()
        test_action_generation()
        test_priority_calculation()
        
        print("=" * 50)
        print("✅ 所有4个测试通过")
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)
