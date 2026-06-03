"""
---
KIA-CODE: 知识入库代码级闭环
Asset: manual_approval_system.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次四

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (协作与认知系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 人工审批系统
  - 关联: 关键决策审批
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 风险控制
  - 产品映射: 孔子-伦理审查
  - 运营映射: 协作与认知优化

---
"""

#!/usr/bin/env python3
# manual_approval_system.py - 手动实现审批系统
# 功能: 当Agent想要手动实现时，必须经过审批流程
# 创建时间: 2026-04-04
# 版本: 1.0

import json
import sys
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

class ManualApprovalSystem(BaseComponent):
    """
    负向反馈：手动实现需要额外审批
    增加手动实现的"摩擦成本"，引导优先使用skill
    """
    
    # 需要审批的手动实现场景
    APPROVAL_REQUIRED_SCENARIOS = [
        'docx_parsing',
        'web_fetch',
        'file_search',
        'data_processing',
        'image_processing',
        'api_call'
    ]
    
    # 例外情况（不需要审批）
    EXCEPTION_CASES = [
        'skill不可用',
        'skill功能不满足需求',
        '性能要求特殊',
        '安全限制'
    ]
    
    def __init__(self):
        super().__init__('manual_approval')
        self.metrics = MetricsCollector('approval_system')
        self.approval_queue = f"{self.workspace}/.approval_queue.jsonl"
        self.approval_history = f"{self.workspace}/.approval_history.jsonl"
    
    def request_approval(self, task_description: str, 
                        manual_approach: str,
                        reason: str,
                        available_skills: list = None) -> Dict:
        """
        请求手动实现审批
        """
        print("\n" + "=" * 70)
        print("🔒 【负向反馈】手动实现审批申请")
        print("=" * 70)
        
        # 检测是否需要审批
        scenario = self._detect_scenario(task_description)
        
        print(f"\n📋 任务描述: {task_description[:80]}...")
        print(f"🔧 手动实现: {manual_approach[:80]}...")
        print(f"📝 申请理由: {reason}")
        
        # 显示可用skills（如果有）
        if available_skills:
            print(f"\n💡 检测到可用skills:")
            for skill in available_skills[:3]:
                print(f"   • {skill}")
            print(f"\n⚠️  注意: 存在可用skill时，手动实现申请更难通过")
        
        # 生成审批ID
        approval_id = f"APR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(task_description) % 10000}"
        
        # 评估申请
        evaluation = self._evaluate_request(task_description, manual_approach, 
                                           reason, available_skills, scenario)
        
        print(f"\n📊 自动评估结果:")
        print(f"   场景: {scenario}")
        print(f"   风险等级: {evaluation['risk_level']}")
        print(f"   建议: {evaluation['recommendation']}")
        
        if evaluation['auto_approve']:
            print(f"\n✅ 自动审批通过")
            self._record_approval(approval_id, 'AUTO_APPROVED', evaluation)
            return {
                'approval_id': approval_id,
                'status': 'APPROVED',
                'type': 'AUTO',
                'reason': evaluation['recommendation']
            }
        else:
            print(f"\n⏸️  需要人工审批")
            print(f"   审批ID: {approval_id}")
            print(f"   请说明为什么不能用skill完成此任务")
            
            # 加入审批队列
            self._add_to_queue(approval_id, task_description, manual_approach, 
                              reason, evaluation)
            
            return {
                'approval_id': approval_id,
                'status': 'PENDING',
                'type': 'MANUAL_REVIEW',
                'estimated_wait': '等待用户响应'
            }
    
    def _detect_scenario(self, task_description: str) -> str:
        """检测任务场景"""
        desc_lower = task_description.lower()
        
        if 'docx' in desc_lower or 'document' in desc_lower:
            return 'docx_parsing'
        elif 'web' in desc_lower or 'http' in desc_lower or 'url' in desc_lower:
            return 'web_fetch'
        elif 'file' in desc_lower and 'search' in desc_lower:
            return 'file_search'
        elif 'data' in desc_lower or 'csv' in desc_lower or 'excel' in desc_lower:
            return 'data_processing'
        elif 'image' in desc_lower or 'picture' in desc_lower:
            return 'image_processing'
        elif 'api' in desc_lower:
            return 'api_call'
        
        return 'general'
    
    def _evaluate_request(self, task: str, manual: str, reason: str,
                         skills: list, scenario: str) -> Dict:
        """评估申请"""
        # 基础评估
        score = 50  # 基础分50
        
        # 如果有可用skills，大幅减分
        if skills and len(skills) > 0:
            score -= 30 * len(skills)
        
        # 如果理由是例外情况，加分
        for exception in self.EXCEPTION_CASES:
            if exception in reason:
                score += 25
        
        # 如果场景是高风险，减分
        if scenario in self.APPROVAL_REQUIRED_SCENARIOS:
            score -= 20
        
        # 判定结果
        if score >= 70:
            return {
                'risk_level': 'LOW',
                'recommendation': '理由充分，建议通过',
                'auto_approve': True,
                'score': score
            }
        elif score >= 40:
            return {
                'risk_level': 'MEDIUM',
                'recommendation': '需要进一步说明',
                'auto_approve': False,
                'score': score
            }
        else:
            return {
                'risk_level': 'HIGH',
                'recommendation': '强烈建议使用skill',
                'auto_approve': False,
                'score': score
            }
    
    def _add_to_queue(self, approval_id: str, task: str, manual: str,
                     reason: str, evaluation: Dict):
        """加入审批队列"""
        entry = {
            'approval_id': approval_id,
            'timestamp': datetime.now().isoformat(),
            'task': task[:100],
            'manual_approach': manual[:100],
            'reason': reason,
            'evaluation': evaluation,
            'status': 'PENDING'
        }
        
        with open(self.approval_queue, 'a') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        self.metrics.record(action='approval_pending', approval_id=approval_id)
    
    def _record_approval(self, approval_id: str, status: str, evaluation: Dict):
        """记录审批结果"""
        entry = {
            'approval_id': approval_id,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'evaluation': evaluation
        }
        
        with open(self.approval_history, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        self.metrics.record(action=f'approval_{status.lower()}', 
                          approval_id=approval_id)
    
    def approve(self, approval_id: str, approver: str = "user") -> Dict:
        """人工批准"""
        print(f"\n✅ 审批通过: {approval_id}")
        print(f"   批准人: {approver}")
        
        self._update_queue_status(approval_id, 'APPROVED', approver)
        
        return {
            'approval_id': approval_id,
            'status': 'APPROVED',
            'message': '可以执行手动实现'
        }
    
    def reject(self, approval_id: str, reject_reason: str, 
              approver: str = "user") -> Dict:
        """人工拒绝"""
        print(f"\n❌ 审批拒绝: {approval_id}")
        print(f"   拒绝原因: {reject_reason}")
        print(f"   拒绝人: {approver}")
        
        self._update_queue_status(approval_id, 'REJECTED', approver, reject_reason)
        
        return {
            'approval_id': approval_id,
            'status': 'REJECTED',
            'reason': reject_reason,
            'message': '请使用skill完成任务'
        }
    
    def _update_queue_status(self, approval_id: str, status: str,
                            approver: str, reason: str = None):
        """更新队列状态"""
        # 简化处理：直接记录到历史
        entry = {
            'approval_id': approval_id,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'approver': approver,
            'reason': reason
        }
        
        with open(self.approval_history, 'a') as f:
            f.write(json.dumps(entry) + '\n')

# 便捷函数
def request_manual_approval(task: str, manual: str, reason: str, 
                           skills: list = None) -> Dict:
    """快速请求审批"""
    system = ManualApprovalSystem()
    return system.request_approval(task, manual, reason, skills)

if __name__ == '__main__':
    # 测试
    result = request_manual_approval(
        task="我需要解析docx文件",
        manual="用zipfile手动解析",
        reason="skill功能不满足需求",
        skills=["feishu-fetch-doc"]
    )
    print(f"\n结果: {result}")
