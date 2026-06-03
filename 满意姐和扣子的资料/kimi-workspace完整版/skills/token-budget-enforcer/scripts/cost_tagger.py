#!/usr/bin/env python3
"""
Token成本标签系统 - Token Cost Tagging System
为每个任务自动附加Token成本预估标签

5标准合规:
- S1: 输入规范 - 任务描述→成本标签
- S2: 执行闭环 - 标签生成→附加→验证
- S3: 输出规范 - 标准化标签格式
- S4: 自动触发 - 与任务系统集成的钩子
- S5: 准确性验证 - 预估vs实际对比
- S6: 局限标注 - 预估置信度标注
- S7: 对抗测试 - 边界情况测试
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

class TokenCostTagger:
    """Token成本标签生成器"""
    
    # 任务类型关键词映射
    TASK_PATTERNS = {
        'p0_emergency': {
            'keywords': ['紧急', 'P0', '立即', '马上', '现在'],
            'base_tokens': 2000,
            'confidence': 'medium'  # 紧急任务难以预估
        },
        'research_analysis': {
            'keywords': ['研究', '分析', '调研', '报告', '评估', '总结'],
            'base_tokens': 8000,
            'confidence': 'high'
        },
        'document_generation': {
            'keywords': ['撰写', '生成', '创建', '文档', '方案', '计划'],
            'base_tokens': 6000,
            'confidence': 'high'
        },
        'code_development': {
            'keywords': ['代码', '开发', '编程', '脚本', '函数', '类'],
            'base_tokens': 5000,
            'confidence': 'high'
        },
        'data_processing': {
            'keywords': ['数据', '处理', '整理', '清洗', '统计', '计算'],
            'base_tokens': 3000,
            'confidence': 'high'
        },
        'testing_experiment': {
            'keywords': ['测试', '实验', '验证', 'A/B', '对抗'],
            'base_tokens': 4000,
            'confidence': 'low'  # 实验性任务不确定性高
        },
        'routine_operation': {
            'keywords': ['检查', '查看', '查询', '列出', '状态'],
            'base_tokens': 1500,
            'confidence': 'high'
        },
        'meeting_notes': {
            'keywords': ['会议', '纪要', '笔记', '记录', '访谈'],
            'base_tokens': 5000,
            'confidence': 'medium'
        }
    }
    
    # 复杂度乘数
    COMPLEXITY_INDICATORS = {
        'high': {
            'keywords': ['详细', '完整', '全面', '深度', '详尽', '综合'],
            'multiplier': 2.0
        },
        'medium': {
            'keywords': ['简要', '简单', '基础', '初步'],
            'multiplier': 0.7
        }
    }
    
    def __init__(self):
        self.tags_file = Path(__file__).parent.parent / 'data' / 'cost_tags.json'
        self.tags_file.parent.mkdir(parents=True, exist_ok=True)
        self.tags_history = self._load_history()
    
    def _load_history(self) -> list:
        """加载历史标签记录"""
        if self.tags_file.exists():
            with open(self.tags_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """保存标签历史"""
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump(self.tags_history[-100:], f, ensure_ascii=False, indent=2)
    
    def classify_task(self, task_description: str) -> Tuple[str, dict]:
        """
        分类任务类型
        返回: (task_type, task_config)
        """
        task_lower = task_description.lower()
        
        for task_type, config in self.TASK_PATTERNS.items():
            for keyword in config['keywords']:
                if keyword in task_lower:
                    return task_type, config
        
        # 默认类型
        return 'routine_operation', self.TASK_PATTERNS['routine_operation']
    
    def estimate_complexity(self, task_description: str) -> float:
        """
        评估任务复杂度
        返回复杂度乘数
        """
        task_lower = task_description.lower()
        
        # 检查高复杂度指示词
        for indicator in self.COMPLEXITY_INDICATORS['high']['keywords']:
            if indicator in task_lower:
                return self.COMPLEXITY_INDICATORS['high']['multiplier']
        
        # 检查低复杂度指示词
        for indicator in self.COMPLEXITY_INDICATORS['medium']['keywords']:
            if indicator in task_lower:
                return self.COMPLEXITY_INDICATORS['medium']['multiplier']
        
        # 检查长度（长描述通常更复杂）
        word_count = len(task_description)
        if word_count > 200:
            return 1.5
        elif word_count < 50:
            return 0.8
        
        return 1.0
    
    def generate_tag(self, task_description: str, task_id: Optional[str] = None) -> dict:
        """
        生成Token成本标签
        
        S1: 输入规范 - 任务描述
        S6: 局限标注 - 置信度标注
        """
        task_type, config = self.classify_task(task_description)
        complexity_mult = self.estimate_complexity(task_description)
        
        base_tokens = config['base_tokens']
        estimated_tokens = int(base_tokens * complexity_mult)
        
        # 置信度调整
        confidence = config['confidence']
        if complexity_mult > 1.5:
            confidence = 'medium' if confidence == 'high' else 'low'
        
        # 计算置信区间
        if confidence == 'high':
            range_min, range_max = int(estimated_tokens * 0.85), int(estimated_tokens * 1.15)
        elif confidence == 'medium':
            range_min, range_max = int(estimated_tokens * 0.70), int(estimated_tokens * 1.30)
        else:  # low
            range_min, range_max = int(estimated_tokens * 0.50), int(estimated_tokens * 1.50)
        
        tag = {
            'tag_id': task_id or f"TAG-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'task_description': task_description[:100] + '...' if len(task_description) > 100 else task_description,
            'task_type': task_type,
            'estimated_tokens': estimated_tokens,
            'confidence': confidence,
            'range': {'min': range_min, 'max': range_max},
            'factors': {
                'base_tokens': base_tokens,
                'complexity_multiplier': complexity_mult,
                'type_confidence': config['confidence']
            },
            'pool_recommendation': self._recommend_pool(task_type),
            'status': 'pending'  # pending/completed
        }
        
        return tag
    
    def _recommend_pool(self, task_type: str) -> str:
        """推荐预算池"""
        pool_map = {
            'p0_emergency': 'strategic_reserve',
            'research_analysis': 'operational_budget',
            'document_generation': 'operational_budget',
            'code_development': 'operational_budget',
            'data_processing': 'operational_budget',
            'testing_experiment': 'innovation_fund',
            'routine_operation': 'operational_budget',
            'meeting_notes': 'operational_budget'
        }
        return pool_map.get(task_type, 'operational_budget')
    
    def record_actual(self, tag_id: str, actual_tokens: int) -> dict:
        """
        记录实际消耗 (S5: 准确性验证)
        """
        for tag in self.tags_history:
            if tag['tag_id'] == tag_id:
                tag['actual_tokens'] = actual_tokens
                tag['status'] = 'completed'
                tag['accuracy'] = {
                    'deviation': actual_tokens - tag['estimated_tokens'],
                    'deviation_percent': round((actual_tokens - tag['estimated_tokens']) / tag['estimated_tokens'] * 100, 2),
                    'within_range': tag['range']['min'] <= actual_tokens <= tag['range']['max']
                }
                self._save_history()
                return tag
        return None
    
    def format_tag_for_display(self, tag: dict) -> str:
        """
        格式化标签用于显示 (S3: 输出规范)
        """
        confidence_emoji = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}
        
        lines = [
            f"🏷️ Token成本标签 [{tag['tag_id']}]",
            f"   预估: {tag['estimated_tokens']:,} tokens",
            f"   区间: {tag['range']['min']:,} - {tag['range']['max']:,}",
            f"   置信: {confidence_emoji.get(tag['confidence'], '⚪')} {tag['confidence']}",
            f"   池别: {tag['pool_recommendation']}",
            f"   类型: {tag['task_type']}"
        ]
        
        if 'actual_tokens' in tag:
            accuracy = tag['accuracy']
            lines.append(f"   实际: {tag['actual_tokens']:,} tokens (偏差: {accuracy['deviation_percent']:+.1f}%)")
            if accuracy['within_range']:
                lines.append(f"   ✅ 预估准确 (在置信区间内)")
            else:
                lines.append(f"   ⚠️ 预估偏差 (超出置信区间)")
        
        return '\n'.join(lines)
    
    def tag_task(self, task_description: str, task_id: Optional[str] = None) -> str:
        """
        主入口: 为任务附加成本标签 (S2: 执行闭环, S4: 自动触发)
        """
        tag = self.generate_tag(task_description, task_id)
        self.tags_history.append(tag)
        self._save_history()
        return self.format_tag_display(tag)
    
    def format_tag_display(self, tag: dict) -> str:
        """生成标签显示字符串"""
        confidence_emoji = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}
        
        lines = [
            f"🏷️ Token成本标签 [{tag['tag_id']}]",
            f"   预估: {tag['estimated_tokens']:,} tokens",
            f"   区间: {tag['range']['min']:,} - {tag['range']['max']:,}",
            f"   置信: {confidence_emoji.get(tag['confidence'], '⚪')} {tag['confidence']}",
            f"   池别: {tag['pool_recommendation']}",
            f"   类型: {tag['task_type']}"
        ]
        
        return '\n'.join(lines)
    
    def get_accuracy_stats(self) -> dict:
        """
        获取预估准确性统计 (S5: 准确性验证)
        """
        completed = [t for t in self.tags_history if t.get('status') == 'completed']
        
        if not completed:
            return {'message': '暂无完成记录'}
        
        total = len(completed)
        within_range = sum(1 for t in completed if t['accuracy']['within_range'])
        avg_deviation = sum(t['accuracy']['deviation_percent'] for t in completed) / total
        
        return {
            'total_tasks': total,
            'within_range': within_range,
            'accuracy_rate': round(within_range / total * 100, 2),
            'avg_deviation_percent': round(avg_deviation, 2),
            'by_confidence': {
                conf: {
                    'count': sum(1 for t in completed if t['confidence'] == conf),
                    'within_range': sum(1 for t in completed if t['confidence'] == conf and t['accuracy']['within_range'])
                }
                for conf in ['high', 'medium', 'low']
            }
        }


# S7: 对抗测试
def run_adversarial_tests():
    """运行成本标签对抗测试"""
    print("=" * 60)
    print("🧪 Token成本标签系统对抗测试")
    print("=" * 60)
    
    tagger = TokenCostTagger()
    tests = [
        # (描述, 预期类型, 预期复杂度)
        ("紧急处理客户投诉", 'p0_emergency', 'high'),
        ("撰写详细市场调研报告", 'research_analysis', 'high'),
        ("简要查看系统状态", 'routine_operation', 'low'),
        ("测试新算法的A/B实验", 'testing_experiment', 'medium'),
        ("生成代码函数", 'code_development', 'medium'),
        ("", 'routine_operation', 'low'),  # 边界: 空字符串
        ("a" * 500, 'routine_operation', 'high'),  # 边界: 超长描述
    ]
    
    passed = 0
    for desc, exp_type, exp_complexity in tests:
        tag = tagger.generate_tag(desc)
        type_match = tag['task_type'] == exp_type
        
        complexity_mult = tag['factors']['complexity_multiplier']
        if exp_complexity == 'high':
            complexity_match = complexity_mult >= 1.5
        elif exp_complexity == 'low':
            complexity_match = complexity_mult <= 0.8
        else:
            complexity_match = 0.8 < complexity_mult < 1.5
        
        status = "✅ PASS" if type_match and complexity_match else "❌ FAIL"
        print(f"{status} | {desc[:30] if desc else '(空字符串)'}...")
        print(f"       类型: {tag['task_type']} (期望: {exp_type})")
        print(f"       复杂度: {complexity_mult:.1f}x")
        print(f"       预估: {tag['estimated_tokens']:,} tokens [{tag['confidence']}]")
        print()
        
        if type_match and complexity_match:
            passed += 1
    
    print(f"测试结果: {passed}/{len(tests)} 通过")
    return passed == len(tests)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_adversarial_tests()
    else:
        # 示例
        tagger = TokenCostTagger()
        test_tasks = [
            "撰写一份详细的合伙人决策沉浸营商业策划方案",
            "紧急修复生产环境bug",
            "查看当前系统状态",
            "测试Token预算熔断机制"
        ]
        
        print("🏷️ Token成本标签示例")
        print("=" * 60)
        for task in test_tasks:
            tag = tagger.generate_tag(task)
            print(tagger.format_tag_for_display(tag))
            print()
