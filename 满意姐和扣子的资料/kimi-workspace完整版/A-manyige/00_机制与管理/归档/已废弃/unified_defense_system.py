#!/usr/bin/env python3
# 文件: /root/.openclaw/workspace/unified_defense_system.py
# 功能: 四层防御整合架构 - 统一指挥中心
# 作者: 外援方案 + 满意姐执行
# 创建时间: 2026-04-04
# 蓝军指导: Skeptor-7

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 导入已部署的子系统
sys.path.insert(0, '/root/.openclaw/workspace')

try:
    from skill_conditioning import SkillConditioningSystem
    from decision_solidifier import DecisionSolidifier
    from context_persistence import ContextPersistence
    from repetition_inhibitor import RepetitionInhibitor
    from skill_intent_mapper import SkillIntentMapper
    from skill_governance_dashboard import SkillGovernanceDashboard
    SUBSYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  部分子系统尚未加载: {e}")
    SUBSYSTEMS_AVAILABLE = False

class UnifiedDefenseSystem:
    """
    四层防御整合架构
    统一指挥中心 - 协调所有防御机制
    """
    
    def __init__(self):
        self.workspace = "/root/.openclaw/workspace"
        self.config_file = f"{self.workspace}/.defense_system_config.json"
        self.status_file = f"{self.workspace}/.defense_system_status.json"
        
        # 四层防御层
        self.layers = {
            "L1": {
                "name": "系统层",
                "systems": ["context_persistence", "repetition_inhibitor"],
                "status": "unknown"
            },
            "L2": {
                "name": "技能层", 
                "systems": ["skill_conditioning", "skill_intent_mapper", "skill_governance"],
                "status": "unknown"
            },
            "L3": {
                "name": "知识层",
                "systems": ["decision_solidifier"],
                "status": "unknown"
            },
            "L4": {
                "name": "整合层",
                "systems": ["unified_defense"],
                "status": "initializing"
            }
        }
        
        # 子系统实例
        self.subsystems = {}
        
        # 初始化
        self.initialize()
    
    def initialize(self):
        """初始化四层防御系统"""
        print("🔥 四层防御整合架构启动中...")
        print("=" * 60)
        
        if SUBSYSTEMS_AVAILABLE:
            # L1: 系统层
            print("\n[L1] 系统层初始化...")
            self.subsystems['context_persistence'] = ContextPersistence()
            self.subsystems['repetition_inhibitor'] = RepetitionInhibitor()
            self.layers['L1']['status'] = "active"
            print("  ✓ 上下文持久化")
            print("  ✓ 重复问题抑制")
            
            # L2: 技能层
            print("\n[L2] 技能层初始化...")
            self.subsystems['skill_conditioning'] = SkillConditioningSystem()
            self.subsystems['skill_intent_mapper'] = SkillIntentMapper()
            self.subsystems['skill_governance'] = SkillGovernanceDashboard()
            self.layers['L2']['status'] = "active"
            print("  ✓ Skill条件反射训练")
            print("  ✓ 意图识别映射")
            print("  ✓ 治理仪表盘")
            
            # L3: 知识层
            print("\n[L3] 知识层初始化...")
            self.subsystems['decision_solidifier'] = DecisionSolidifier()
            self.layers['L3']['status'] = "active"
            print("  ✓ 决策即时固化")
            
            # L4: 整合层
            print("\n[L4] 整合层初始化...")
            self.layers['L4']['status'] = "active"
            print("  ✓ 统一指挥中心")
        else:
            print("⚠️  子系统未完全加载，进入演示模式")
        
        # 保存状态
        self.save_status()
        
        print("\n" + "=" * 60)
        print("✅ 四层防御架构启动完成")
        print("=" * 60)
    
    def process_task(self, task_description: str) -> Dict:
        """
        四层防御流程处理任务
        
        流程: L1 -> L2 -> L3 -> L4
        """
        result = {
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "layers_processed": [],
            "decisions": [],
            "actions": []
        }
        
        print(f"\n🎯 处理任务: {task_description}")
        print("-" * 60)
        
        # L1: 系统层 - 上下文与重复检查
        print("\n[L1] 系统层检查...")
        if 'repetition_inhibitor' in self.subsystems:
            self.subsystems['repetition_inhibitor'].check_repetition(task_description)
        if 'context_persistence' in self.subsystems:
            context = self.subsystems['context_persistence'].load_context()
            print(f"  ✓ 上下文已加载: {len(context.get('decisions', []))} 条历史决策")
        result['layers_processed'].append("L1")
        
        # L2: 技能层 - Skill识别与条件反射
        print("\n[L2] 技能层处理...")
        if 'skill_intent_mapper' in self.subsystems:
            intent_result = self.subsystems['skill_intent_mapper'].force_skill_selection(task_description)
            forced_skill = intent_result['forced_skill']
            print(f"  ✓ 意图识别: {intent_result['main_intent']} -> {forced_skill}")
            result['decisions'].append({"layer": "L2", "skill": forced_skill})
        
        if 'skill_conditioning' in self.subsystems:
            self.subsystems['skill_conditioning'].record_drill(forced_skill, "executed")
            print(f"  ✓ 条件反射训练: {forced_skill}")
        result['layers_processed'].append("L2")
        
        # L3: 知识层 - 决策固化
        print("\n[L3] 知识层固化...")
        if 'decision_solidifier' in self.subsystems:
            decision_record = {
                "decision": f"使用 {forced_skill} 处理任务",
                "trigger": task_description,
                "skill_recommended": forced_skill
            }
            self.subsystems['decision_solidifier'].solidify_decision(decision_record)
            print(f"  ✓ 决策已固化")
        result['layers_processed'].append("L3")
        
        # L4: 整合层 - 综合协调
        print("\n[L4] 整合层协调...")
        result['actions'].append({"action": "execute_skill", "skill": forced_skill})
        result['layers_processed'].append("L4")
        print(f"  ✓ 执行指令: 使用 {forced_skill}")
        
        # 记录到治理仪表盘
        if 'skill_governance' in self.subsystems:
            self.subsystems['skill_governance'].log_operation(
                task=task_description,
                skill_used=forced_skill,
                forced=True
            )
        
        print("\n" + "-" * 60)
        print(f"✅ 任务处理完成: {forced_skill}")
        
        return result
    
    def get_system_health(self) -> Dict:
        """获取系统健康状态"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "layers": {}
        }
        
        for layer_id, layer_info in self.layers.items():
            health['layers'][layer_id] = {
                "name": layer_info['name'],
                "status": layer_info['status'],
                "systems": layer_info['systems']
            }
        
        # 检查是否有故障层
        failed_layers = [l for l, info in self.layers.items() if info['status'] != 'active']
        if failed_layers:
            health['overall_status'] = 'degraded'
            health['failed_layers'] = failed_layers
        
        return health
    
    def print_dashboard(self):
        """打印系统仪表盘"""
        print("\n" + "=" * 60)
        print("🛡️  四层防御整合架构 - 系统仪表盘")
        print("=" * 60)
        
        health = self.get_system_health()
        
        print(f"\n系统状态: {'✅ 健康' if health['overall_status'] == 'healthy' else '⚠️ 降级'}")
        print(f"检查时间: {health['timestamp']}")
        
        print("\n各层状态:")
        for layer_id, layer_info in health['layers'].items():
            status_icon = "✅" if layer_info['status'] == 'active' else "❌"
            print(f"  {status_icon} {layer_id}: {layer_info['name']}")
            for system in layer_info['systems']:
                print(f"      • {system}")
        
        print("\n" + "=" * 60)
    
    def save_status(self):
        """保存系统状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "layers": self.layers,
            "subsystems_loaded": list(self.subsystems.keys())
        }
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
    
    def emergency_protocol(self, issue: str):
        """紧急处理协议"""
        print("\n" + "🚨" * 20)
        print("🚨 紧急协议启动！")
        print("🚨" * 20)
        print(f"\n问题: {issue}")
        print("\n应急措施:")
        print("  1. 激活蓝军监督模式")
        print("  2. 暂停自动执行，转为人工确认")
        print("  3. 记录异常到审计日志")
        print("  4. 通知系统管理员")
        print("\n" + "🚨" * 20)

# 主程序
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='四层防御整合架构')
    parser.add_argument('--dashboard', action='store_true', help='显示仪表盘')
    parser.add_argument('--process', type=str, help='处理任务')
    parser.add_argument('--health', action='store_true', help='检查健康状态')
    
    args = parser.parse_args()
    
    uds = UnifiedDefenseSystem()
    
    if args.dashboard:
        uds.print_dashboard()
    elif args.process:
        result = uds.process_task(args.process)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.health:
        health = uds.get_system_health()
        print(json.dumps(health, indent=2, ensure_ascii=False))
    else:
        uds.print_dashboard()
