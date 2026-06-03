#!/usr/bin/env python3
"""
统一防御系统
整合所有机制的中央控制器
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace')

from skill_conditioning import SkillConditioningSystem
from decision_solidifier import DecisionSolidifier
from repetition_inhibitor import RepetitionInhibitor

class UnifiedDefenseSystem:
    def __init__(self):
        self.scs = SkillConditioningSystem()
        self.solidifier = DecisionSolidifier()
        self.inhibitor = RepetitionInhibitor()
        self.workspace = "/root/.openclaw/workspace"
    
    def pre_flight_check(self, operation: str) -> bool:
        """操作前全面检查"""
        print("🔍 执行预检...")
        
        # 1. Skill条件反射检查
        if not self.scs.pre_operation_intercept(operation):
            print("❌ Skill反射检查失败")
            return False
        
        # 2. 重复抑制检查
        if not self.inhibitor.before_asking(operation):
            print("❌ 重复抑制检查触发")
            return False
        
        print("✅ 预检通过")
        return True
    
    def post_operation_processing(self, conversation: str, question: str = None, answer: str = None):
        """操作后处理"""
        print("\n📝 执行后处理...")
        
        # 1. 决策即时固化
        self.solidifier.solidify_immediately(conversation, "session")
        
        # 2. 记录查询
        if question:
            self.inhibitor.record_query(question, answer)
        
        print("✅ 后处理完成")
    
    def get_system_status(self) -> dict:
        """获取系统状态"""
        weak_reflexes = self.scs.get_weak_reflexes()
        
        return {
            'weak_reflexes_count': len(weak_reflexes),
            'weak_reflexes': weak_reflexes[:3],  # 显示前3个
            'memory_index_exists': os.path.exists(f"{self.workspace}/memory/.decision_index.json"),
            'query_history_exists': os.path.exists(f"{self.workspace}/.query_history.json")
        }

if __name__ == "__main__":
    uds = UnifiedDefenseSystem()
    
    print("=" * 60)
    print("🔴 统一防御系统 - 功能测试")
    print("=" * 60)
    
    # 测试1: 预检
    print("\n[测试1] 操作预检")
    test_op = "需要解析一个docx文件"
    result = uds.pre_flight_check(test_op)
    print(f"结果: {'✅ 通过' if result else '❌ 失败'}")
    
    # 测试2: 决策固化
    print("\n[测试2] 决策固化")
    test_conv = "用户要求：必须先完成Skill盘点，禁止手动实现代码"
    uds.post_operation_processing(test_conv)
    
    # 测试3: 系统状态
    print("\n[测试3] 系统状态")
    status = uds.get_system_status()
    print(f"弱反射数量: {status['weak_reflexes_count']}")
    print(f"记忆索引: {'✅' if status['memory_index_exists'] else '❌'}")
    print(f"查询历史: {'✅' if status['query_history_exists'] else '❌'}")
    
    print("\n" + "=" * 60)
    print("✅ 统一防御系统测试完成")
    print("=" * 60)
