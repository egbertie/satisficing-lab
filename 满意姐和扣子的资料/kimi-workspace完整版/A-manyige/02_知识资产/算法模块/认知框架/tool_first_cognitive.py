#!/usr/bin/env python3
# tool_first_cognitive.py - 认知重构框架
# 功能: 强制"工具优先"认知模式，改变默认行为
# 创建时间: 2026-04-04
# 版本: 1.0

import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

class ToolFirstCognitiveFramework(BaseComponent):
    """
    认知框架：强制"查询-匹配"前置
    改变Agent默认行为：从"让我写代码"变为"让我找工具"
    """
    
    # 认知锚点：任何任务开始前的强制自问
    MANDATORY_SELF_QUESTIONS = [
        "这个需求是否有现成的skill可以完成？",
        "feishu/skills/目录下是否有匹配的工具？",
        "我是否在用Python重复实现已有的功能？",
        "上次类似任务用了什么skill？"
    ]
    
    # 常见手动实现陷阱
    COMMON_TRAPS = {
        'docx_parsing': {
            'manual': '用zipfile/xml.etree手动解析docx',
            'skill': 'feishu-fetch-doc skill',
            'severity': 'HIGH'
        },
        'file_search': {
            'manual': '用os.walk手动遍历文件',
            'skill': '文件系统skill',
            'severity': 'MEDIUM'
        },
        'data_processing': {
            'manual': '用纯Python处理复杂数据',
            'skill': 'pandas/numpy skill',
            'severity': 'MEDIUM'
        },
        'web_fetch': {
            'manual': '用requests+bs4手动爬取',
            'skill': 'web_fetch/kimi_fetch skill',
            'severity': 'HIGH'
        }
    }
    
    def __init__(self):
        super().__init__('tool_first_cognitive')
        self.metrics = MetricsCollector('cognitive_framework')
        self.cognitive_log = f"{self.workspace}/.cognitive_log"
        
    def start_task(self, task_description: str) -> Dict:
        """
        任务开始前的强制认知检查
        返回: 是否允许继续，以及建议使用的skill
        """
        print("🔵 【认知层】工具优先检查启动")
        print("=" * 60)
        
        # 记录任务
        self.metrics.record(action='task_start', description=task_description[:50])
        
        # 强制自问
        answers = self._mandatory_self_questions()
        
        # 检测陷阱
        traps = self._detect_traps(task_description)
        
        # 生成建议
        recommendations = self._generate_recommendations(task_description, traps)
        
        # 决策
        decision = self._make_decision(answers, traps, recommendations)
        
        # 记录日志
        self._log_cognitive_process(task_description, answers, traps, decision)
        
        print("=" * 60)
        return decision
    
    def _mandatory_self_questions(self) -> Dict[str, str]:
        """强制自问环节"""
        answers = {}
        
        print("\n📋 强制自问（必须回答）:")
        for i, question in enumerate(self.MANDATORY_SELF_QUESTIONS, 1):
            print(f"\nQ{i}: {question}")
            # 在实际交互中这里会等待回答
            # 在自动化流程中，这里会基于历史数据和skill清单自动判断
            answer = self._auto_answer_question(question)
            answers[f"Q{i}"] = answer
            print(f"A{i}: {answer}")
        
        return answers
    
    def _auto_answer_question(self, question: str) -> str:
        """基于系统状态自动回答问题"""
        if "skill" in question.lower():
            # 检查可用skills
            skills = self._list_available_skills()
            return f"可用skills: {len(skills)}个 - {', '.join(skills[:3])}..."
        elif "重复" in question:
            return "需要代码审查来确认"
        elif "上次" in question:
            return self._get_last_similar_skill()
        return "需要人工确认"
    
    def _list_available_skills(self) -> List[str]:
        """列出可用skills"""
        # 从skill目录读取
        import os
        skill_files = []
        skills_dir = f"{self.workspace}/skills"
        if os.path.exists(skills_dir):
            for root, dirs, files in os.walk(skills_dir):
                for f in files:
                    if f.endswith('.py'):
                        skill_files.append(f.replace('.py', ''))
        return skill_files[:10]
    
    def _detect_traps(self, task_description: str) -> List[Dict]:
        """检测常见手动实现陷阱"""
        detected = []
        task_lower = task_description.lower()
        
        for trap_id, trap_info in self.COMMON_TRAPS.items():
            # 检测关键词
            keywords = trap_info['manual'].lower().split()
            if any(kw in task_lower for kw in keywords):
                detected.append({
                    'trap_id': trap_id,
                    'description': trap_info['manual'],
                    'recommended_skill': trap_info['skill'],
                    'severity': trap_info['severity']
                })
                print(f"\n⚠️  检测到陷阱: {trap_id}")
                print(f"   手动实现: {trap_info['manual']}")
                print(f"   推荐skill: {trap_info['skill']}")
        
        return detected
    
    def _generate_recommendations(self, task: str, traps: List[Dict]) -> List[str]:
        """生成使用建议"""
        recommendations = []
        
        if traps:
            recommendations.append("⚠️ 检测到手动实现倾向，请优先考虑使用skill")
            for trap in traps:
                recommendations.append(f"   → 使用 {trap['recommended_skill']} 替代手动实现")
        else:
            recommendations.append("✅ 未检测到明显的手动实现陷阱")
        
        return recommendations
    
    def _make_decision(self, answers: Dict, traps: List[Dict], 
                       recommendations: List[str]) -> Dict:
        """做出决策"""
        # 如果有高危陷阱，建议阻断
        high_severity_traps = [t for t in traps if t['severity'] == 'HIGH']
        
        if high_severity_traps:
            return {
                'allow_continue': False,
                'action': 'BLOCK',
                'reason': f'检测到{len(high_severity_traps)}个高危手动实现陷阱',
                'recommendations': recommendations,
                'required_action': '使用推荐的skill或申请例外审批'
            }
        elif traps:
            return {
                'allow_continue': True,
                'action': 'WARN',
                'reason': f'检测到{len(traps)}个手动实现倾向',
                'recommendations': recommendations,
                'required_action': '请优先考虑使用skill'
            }
        else:
            return {
                'allow_continue': True,
                'action': 'PASS',
                'reason': '未检测到手动实现倾向',
                'recommendations': recommendations,
                'required_action': '继续执行任务'
            }
    
    def _log_cognitive_process(self, task: str, answers: Dict, 
                               traps: List[Dict], decision: Dict):
        """记录认知过程"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task': task[:100],
            'answers': answers,
            'traps_detected': len(traps),
            'decision': decision['action'],
            'reason': decision['reason']
        }
        
        with open(self.cognitive_log, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _get_last_similar_skill(self) -> str:
        """获取上次类似任务使用的skill"""
        try:
            with open(self.cognitive_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return f"上次使用: {last_entry.get('decision', 'unknown')}"
        except:
            pass
        return "无历史记录"

# 便捷函数
def check_task(task_description: str) -> Dict:
    """快速检查任务"""
    framework = ToolFirstCognitiveFramework()
    return framework.start_task(task_description)

if __name__ == '__main__':
    # 测试
    test_task = "我需要解析一个docx文件提取内容"
    result = check_task(test_task)
    print(f"\n决策结果: {result}")
