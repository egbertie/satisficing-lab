#!/usr/bin/env python3
# efficiency_points_system.py - 效率积分系统
# 功能: 使用skill获得积分，手动实现扣积分
# 创建时间: 2026-04-04
# 版本: 1.0

import json
import sys
from datetime import datetime
from typing import Dict, List
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

class EfficiencyPointsSystem(BaseComponent):
    """
    正向强化：使用skill获得效率积分
    通过游戏化激励，培养工具优先习惯
    """
    
    # 积分规则
    POINTS_RULES = {
        'use_skill': {
            'base': 10,
            'description': '使用skill完成任务'
        },
        'use_appropriate_skill': {
            'base': 20,
            'description': '选择最适合的skill'
        },
        'save_time': {
            'per_minute': 5,
            'description': '每分钟节省时间'
        },
        'reduce_code': {
            'per_10_lines': 3,
            'description': '每减少10行代码'
        },
        'manual_without_approval': {
            'penalty': -50,
            'description': '未经审批手动实现'
        },
        'manual_with_approval': {
            'penalty': -10,
            'description': '经审批手动实现（ still discouraged）'
        }
    }
    
    # 等级系统
    LEVELS = {
        0: {'name': '新手', 'icon': '🌱'},
        100: {'name': '学徒', 'icon': '🌿'},
        300: {'name': '熟练工', 'icon': '🌳'},
        600: {'name': '专家', 'icon': '⭐'},
        1000: {'name': '大师', 'icon': '👑'},
        2000: {'name': '传奇', 'icon': '🏆'}
    }
    
    def __init__(self):
        super().__init__('points_system')
        self.metrics = MetricsCollector('efficiency_points')
        self.points_file = f"{self.workspace}/.efficiency_points.json"
        self.history_file = f"{self.workspace}/.points_history.jsonl"
        self._init_points()
    
    def _init_points(self):
        """初始化积分记录"""
        if not Path(self.points_file).exists():
            data = {
                'total_points': 0,
                'current_streak': 0,  # 连续使用skill次数
                'best_streak': 0,
                'skills_used': {},
                'last_update': datetime.now().isoformat()
            }
            self._save_points(data)
    
    def _load_points(self) -> Dict:
        """加载积分"""
        with open(self.points_file, 'r') as f:
            return json.load(f)
    
    def _save_points(self, data: Dict):
        """保存积分"""
        with open(self.points_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _add_history(self, event: str, points: int, details: str):
        """添加历史记录"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'points': points,
            'details': details
        }
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def award_points(self, event_type: str, details: str = "", 
                     extra_data: Dict = None) -> Dict:
        """
        奖励积分
        """
        data = self._load_points()
        
        # 计算积分
        points = 0
        if event_type == 'use_skill':
            points = self.POINTS_RULES['use_skill']['base']
            
            # 连续使用奖励
            data['current_streak'] += 1
            if data['current_streak'] > data['best_streak']:
                data['best_streak'] = data['current_streak']
            
            # 连续奖励
            streak_bonus = min(data['current_streak'] * 2, 20)  # 最高20
            points += streak_bonus
            
        elif event_type == 'save_time':
            minutes = extra_data.get('minutes', 0) if extra_data else 0
            points = minutes * self.POINTS_RULES['save_time']['per_minute']
            
        elif event_type == 'reduce_code':
            lines = extra_data.get('lines', 0) if extra_data else 0
            points = (lines // 10) * self.POINTS_RULES['reduce_code']['per_10_lines']
        
        # 更新总分
        data['total_points'] += points
        data['last_update'] = datetime.now().isoformat()
        
        # 记录skill使用
        if event_type == 'use_skill' and extra_data:
            skill_name = extra_data.get('skill_name', 'unknown')
            data['skills_used'][skill_name] = data['skills_used'].get(skill_name, 0) + 1
        
        self._save_points(data)
        self._add_history(event_type, points, details)
        
        # 显示奖励
        print(f"\n🎉 获得积分: +{points}")
        print(f"   事件: {self.POINTS_RULES.get(event_type, {}).get('description', event_type)}")
        print(f"   详情: {details}")
        
        if data['current_streak'] > 1:
            print(f"   🔥 连续使用skill: {data['current_streak']}次 (+{min(data['current_streak']*2, 20)}连续奖励)")
        
        print(f"   💰 总积分: {data['total_points']}")
        
        # 检查升级
        level_info = self._check_level_up(data['total_points'])
        if level_info:
            print(f"\n🆙 等级提升: {level_info['old_level']} → {level_info['new_level']}")
            print(f"   {level_info['icon']} 恭喜成为{level_info['new_level']}！")
        
        return {
            'points_awarded': points,
            'total_points': data['total_points'],
            'streak': data['current_streak'],
            'level_up': level_info
        }
    
    def deduct_points(self, event_type: str, details: str = "") -> Dict:
        """
        扣除积分
        """
        data = self._load_points()
        
        points = self.POINTS_RULES.get(event_type, {}).get('penalty', -10)
        
        # 更新总分
        data['total_points'] = max(0, data['total_points'] + points)  # 最低0
        data['current_streak'] = 0  # 重置连续
        data['last_update'] = datetime.now().isoformat()
        
        self._save_points(data)
        self._add_history(event_type, points, details)
        
        print(f"\n⚠️  积分扣除: {points}")
        print(f"   事件: {self.POINTS_RULES.get(event_type, {}).get('description', event_type)}")
        print(f"   详情: {details}")
        print(f"   💰 总积分: {data['total_points']}")
        
        return {
            'points_deducted': points,
            'total_points': data['total_points'],
            'streak_reset': True
        }
    
    def _check_level_up(self, total_points: int) -> Dict:
        """检查是否升级"""
        # 找到当前等级
        current_level = '新手'
        current_icon = '🌱'
        
        for threshold, info in sorted(self.LEVELS.items()):
            if total_points >= threshold:
                current_level = info['name']
                current_icon = info['icon']
        
        # 检查下一级
        next_level = None
        for threshold, info in sorted(self.LEVELS.items()):
            if total_points < threshold:
                next_level = info
                break
        
        return {
            'old_level': current_level,
            'new_level': current_level,  # 简化处理
            'icon': current_icon,
            'next_level': next_level['name'] if next_level else '已满级',
            'points_to_next': threshold - total_points if next_level else 0
        }
    
    def show_status(self) -> Dict:
        """显示当前状态"""
        data = self._load_points()
        level_info = self._check_level_up(data['total_points'])
        
        print("\n" + "=" * 70)
        print("🏆 效率积分系统")
        print("=" * 70)
        print(f"\n   当前等级: {level_info['icon']} {level_info['new_level']}")
        print(f"   总积分: {data['total_points']}")
        print(f"   连续使用skill: {data['current_streak']}次")
        print(f"   最高连续: {data['best_streak']}次")
        print(f"\n   使用skill次数:")
        for skill, count in sorted(data['skills_used'].items(), 
                                   key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {skill}: {count}次")
        
        if level_info['next_level'] != '已满级':
            print(f"\n   📈 距离下一级还需: {level_info['points_to_next']}分")
        
        print("=" * 70)
        
        return {
            'level': level_info['new_level'],
            'total_points': data['total_points'],
            'streak': data['current_streak'],
            'skills_used': data['skills_used']
        }

# 便捷函数
def award_skill_points(skill_name: str, time_saved: int = 0) -> Dict:
    """奖励skill使用积分"""
    system = EfficiencyPointsSystem()
    return system.award_points('use_skill', f'使用skill: {skill_name}',
                               {'skill_name': skill_name, 'minutes': time_saved})

def show_points_status() -> Dict:
    """显示积分状态"""
    system = EfficiencyPointsSystem()
    return system.show_status()

if __name__ == '__main__':
    # 测试
    show_points_status()
    award_skill_points('feishu-fetch-doc', time_saved=5)
    award_skill_points('kimi-search', time_saved=3)
    show_points_status()
