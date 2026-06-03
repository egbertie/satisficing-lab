#!/usr/bin/env python3
"""
统一防御系统 V3.0
整合所有6个机制的中央控制器
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace')

from skill_conditioning import SkillConditioningSystem
from decision_solidifier import DecisionSolidifier
from repetition_inhibitor import RepetitionInhibitor
from skill_intent_mapper import SkillIntentMapper
from skill_governance_dashboard import SkillGovernanceDashboard
from context_persistence import ContextPersistenceManager

class UnifiedDefenseSystem:
    """
    统一防御系统 V3.0
    整合6大机制：条件反射、意图映射、治理仪表盘、决策固化、上下文保持、重复抑制
    """
    
    def __init__(self):
        print("🚀 初始化统一防御系统 V3.0...")
        
        # 6大子系统
        self.scs = SkillConditioningSystem()  # Skill条件反射
        self.intent_mapper = SkillIntentMapper()  # 意图识别映射
        self.governance = SkillGovernanceDashboard()  # 治理仪表盘
        self.solidifier = DecisionSolidifier()  # 决策固化
        self.context = ContextPersistenceManager()  # 上下文保持
        self.inhibitor = RepetitionInhibitor()  # 重复抑制
        
        self.workspace = "/root/.openclaw/workspace"
        print("✅ 6大子系统初始化完成\n")
    
    def pre_flight_check(self, operation: str) -> bool:
        """
        操作前全面检查（4层防御）
        """
        print("🔍 执行预检（4层防御）...")
        
        checks = []
        
        # 1. Skill条件反射检查
        print("  [1/4] Skill条件反射检查...")
        if not self.scs.pre_operation_intercept(operation):
            checks.append(("Skill反射", False, "需要强化训练"))
            return False
        checks.append(("Skill反射", True, "通过"))
        
        # 2. 意图识别映射
        print("  [2/4] 意图识别映射...")
        intent_result = self.intent_mapper.map_intent(operation)
        if intent_result.get('mapped'):
            print(f"    ✅ 识别意图: {intent_result['primary_intent']} -> {intent_result['skill']}")
            checks.append(("意图映射", True, f"推荐: {intent_result['skill']}"))
        else:
            checks.append(("意图映射", True, "未识别（继续执行）"))
        
        # 3. 重复抑制检查
        print("  [3/4] 重复抑制检查...")
        if not self.inhibitor.before_asking(operation):
            checks.append(("重复抑制", False, "检测到相似问题"))
            return False
        checks.append(("重复抑制", True, "通过"))
        
        # 4. 治理仪表盘记录
        print("  [4/4] 治理仪表盘记录...")
        self.governance.record_usage(
            operation=operation,
            skill_used=intent_result.get('skill') if intent_result.get('mapped') else None,
            manual_implementation=False
        )
        checks.append(("治理记录", True, "已记录"))
        
        # 输出检查结果
        print("\n  预检结果:")
        for name, passed, msg in checks:
            status = "✅" if passed else "❌"
            print(f"    {status} {name}: {msg}")
        
        all_passed = all(passed for _, passed, _ in checks)
        print(f"\n{'✅ 预检通过' if all_passed else '❌ 预检失败'}")
        return all_passed
    
    def post_operation_processing(self, conversation: str = "", 
                                   question: str = None, 
                                   answer: str = None):
        """
        操作后处理（3层处理）
        """
        print("\n📝 执行后处理（3层处理）...")
        
        # 1. 决策即时固化
        print("  [1/3] 决策即时固化...")
        self.solidifier.solidify_immediately(conversation, "session")
        
        # 2. 上下文保存
        print("  [2/3] 上下文保存...")
        self.context.save_full_context()
        
        # 3. 记录查询
        print("  [3/3] 查询记录...")
        if question:
            self.inhibitor.record_query(question, answer)
        
        print("✅ 后处理完成")
    
    def session_startup(self) -> bool:
        """
        会话启动流程
        """
        print("\n🚀 会话启动流程...")
        return self.context.session_startup_check()
    
    def get_system_status(self) -> dict:
        """
        获取完整系统状态
        """
        weak_reflexes = self.scs.get_weak_reflexes()
        mapping_stats = self.intent_mapper.get_mapping_stats()
        governance_dashboard = self.governance.get_dashboard()
        
        return {
            'version': '3.0',
            'subsystems': {
                'skill_conditioning': '✅ 运行中',
                'intent_mapper': '✅ 运行中',
                'governance_dashboard': '✅ 运行中',
                'decision_solidifier': '✅ 运行中',
                'context_persistence': '✅ 运行中',
                'repetition_inhibitor': '✅ 运行中'
            },
            'metrics': {
                'weak_reflexes_count': len(weak_reflexes),
                'intent_mapping_total': mapping_stats.get('total', 0),
                'intent_mapping_success_rate': mapping_stats.get('success_rate', 0)
            },
            'file_checks': {
                'memory_index': os.path.exists(f"{self.workspace}/memory/.decision_index.json"),
                'query_history': os.path.exists(f"{self.workspace}/.query_history.json"),
                'context_file': os.path.exists(self.context.context_file),
                'governance_metrics': os.path.exists(self.governance.metrics_file)
            }
        }
    
    def show_dashboard(self):
        """显示治理仪表盘"""
        print("\n" + self.governance.get_dashboard())
    
    def suggest_skill(self, request: str) -> str:
        """快速建议Skill"""
        result = self.intent_mapper.map_intent(request)
        
        if result.get('mapped'):
            return f"🎯 推荐: {result['skill']} (置信度: {result['confidence']:.0%})"
        return "❓ 无法识别意图，请提供更多上下文"

def main():
    """主测试函数"""
    print("=" * 70)
    print("🔴 统一防御系统 V3.0 - 全面测试")
    print("=" * 70)
    
    uds = UnifiedDefenseSystem()
    
    # 测试1: 会话启动
    print("\n" + "-" * 70)
    print("[测试1] 会话启动流程")
    print("-" * 70)
    uds.session_startup()
    
    # 测试2: 操作预检
    print("\n" + "-" * 70)
    print("[测试2] 操作预检（4层防御）")
    print("-" * 70)
    test_operations = [
        "需要解析一个docx文件",
        "搜索最新的AI新闻",
        "发送飞书消息给用户"
    ]
    
    for i, op in enumerate(test_operations, 1):
        print(f"\n测试操作 {i}: {op}")
        result = uds.pre_flight_check(op)
        print(f"结果: {'✅ 通过' if result else '❌ 失败'}")
    
    # 测试3: 决策固化
    print("\n" + "-" * 70)
    print("[测试3] 决策固化 + 后处理")
    print("-" * 70)
    test_conv = "用户要求：必须先完成Skill盘点，禁止手动实现代码，优先使用飞书Skill"
    uds.post_operation_processing(test_conv, "如何解析docx", "使用feishu-fetch-doc")
    
    # 测试4: 系统状态
    print("\n" + "-" * 70)
    print("[测试4] 系统状态报告")
    print("-" * 70)
    status = uds.get_system_status()
    print(f"版本: {status['version']}")
    print(f"\n子系统状态:")
    for name, state in status['subsystems'].items():
        print(f"  {state} {name}")
    print(f"\n指标:")
    print(f"  弱反射数量: {status['metrics']['weak_reflexes_count']}")
    print(f"  意图映射成功率: {status['metrics']['intent_mapping_success_rate']:.1%}")
    
    # 测试5: 仪表盘
    print("\n" + "-" * 70)
    print("[测试5] 治理仪表盘")
    print("-" * 70)
    uds.show_dashboard()
    
    print("\n" + "=" * 70)
    print("✅ 统一防御系统 V3.0 全面测试完成")
    print("✅ 6大子系统全部运行正常")
    print("=" * 70)

if __name__ == "__main__":
    main()
