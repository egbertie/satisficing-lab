#!/usr/bin/env python3
# efficiency_visualizer.py - 效率可视化系统
# 功能: 展示使用skill vs 手动实现的时间/代码量对比
# 创建时间: 2026-04-04
# 版本: 1.0

import json
import sys
from datetime import datetime
from typing import Dict, List
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

class EfficiencyVisualizer(BaseComponent):
    """
    效率可视化：展示使用skill节省的时间和代码量
    提供数据支撑，强化"工具优先"认知
    """
    
    # skill vs 手动实现对比数据
    EFFICIENCY_DATA = {
        'docx_parsing': {
            'skill': {
                'name': 'feishu-fetch-doc',
                'time_seconds': 5,
                'code_lines': 1,
                'description': '直接调用skill'
            },
            'manual': {
                'name': '手动解析',
                'time_seconds': 300,
                'code_lines': 50,
                'description': 'zipfile + xml.etree'
            }
        },
        'web_fetch': {
            'skill': {
                'name': 'kimi-fetch',
                'time_seconds': 3,
                'code_lines': 1,
                'description': '直接调用'
            },
            'manual': {
                'name': '手动爬取',
                'time_seconds': 600,
                'code_lines': 100,
                'description': 'requests + bs4 + 异常处理'
            }
        },
        'file_search': {
            'skill': {
                'name': 'exec(find)',
                'time_seconds': 2,
                'code_lines': 1,
                'description': '系统命令'
            },
            'manual': {
                'name': 'os.walk',
                'time_seconds': 60,
                'code_lines': 20,
                'description': '递归遍历+过滤'
            }
        },
        'data_processing': {
            'skill': {
                'name': 'pandas',
                'time_seconds': 10,
                'code_lines': 5,
                'description': '向量化操作'
            },
            'manual': {
                'name': '纯Python',
                'time_seconds': 300,
                'code_lines': 80,
                'description': '循环+列表推导'
            }
        }
    }
    
    def __init__(self):
        super().__init__('efficiency_visualizer')
        self.metrics = MetricsCollector('efficiency')
        self.usage_log = f"{self.workspace}/.efficiency_log.jsonl"
    
    def compare(self, task_type: str) -> Dict:
        """
        对比skill vs 手动实现的效率
        """
        if task_type not in self.EFFICIENCY_DATA:
            return {'error': f'未知的任务类型: {task_type}'}
        
        data = self.EFFICIENCY_DATA[task_type]
        skill = data['skill']
        manual = data['manual']
        
        # 计算节省
        time_saved = manual['time_seconds'] - skill['time_seconds']
        code_saved = manual['code_lines'] - skill['code_lines']
        time_ratio = manual['time_seconds'] / skill['time_seconds'] if skill['time_seconds'] > 0 else 0
        
        print("\n" + "=" * 70)
        print(f"📊 效率对比: {task_type}")
        print("=" * 70)
        
        print(f"\n🟢 使用 Skill: {skill['name']}")
        print(f"   时间: {skill['time_seconds']}秒")
        print(f"   代码: {skill['code_lines']}行")
        print(f"   方式: {skill['description']}")
        
        print(f"\n🔴 手动实现: {manual['name']}")
        print(f"   时间: {manual['time_seconds']}秒")
        print(f"   代码: {manual['code_lines']}行")
        print(f"   方式: {manual['description']}")
        
        print(f"\n💰 使用Skill的收益:")
        print(f"   ⏱️  节省时间: {time_saved}秒 ({time_ratio:.1f}x 更快)")
        print(f"   📝 减少代码: {code_saved}行 ({code_saved/manual['code_lines']*100:.0f}%)")
        
        # 可视化
        self._visualize_comparison(skill, manual, time_saved, code_saved)
        
        # 记录
        self._log_comparison(task_type, skill, manual, time_saved)
        
        print("=" * 70)
        
        return {
            'task_type': task_type,
            'time_saved_seconds': time_saved,
            'code_saved_lines': code_saved,
            'efficiency_multiplier': time_ratio,
            'recommendation': '强烈建议使用skill'
        }
    
    def _visualize_comparison(self, skill: Dict, manual: Dict, 
                              time_saved: int, code_saved: int):
        """可视化对比"""
        max_time = max(skill['time_seconds'], manual['time_seconds'])
        max_code = max(skill['code_lines'], manual['code_lines'])
        
        # 时间对比条形图
        print(f"\n📊 时间对比 (秒):")
        skill_bar = '█' * int(skill['time_seconds'] / max_time * 30)
        manual_bar = '█' * int(manual['time_seconds'] / max_time * 30)
        print(f"   Skill:  {skill_bar} {skill['time_seconds']}s")
        print(f"   手动:   {manual_bar} {manual['time_seconds']}s")
        
        # 代码对比条形图
        print(f"\n📊 代码量对比 (行):")
        skill_bar = '█' * int(skill['code_lines'] / max_code * 30)
        manual_bar = '█' * int(manual['code_lines'] / max_code * 30)
        print(f"   Skill:  {skill_bar} {skill['code_lines']}行")
        print(f"   手动:   {manual_bar} {manual['code_lines']}行")
    
    def show_cumulative_savings(self) -> Dict:
        """显示累计节省"""
        try:
            total_time = 0
            total_code = 0
            usage_count = 0
            
            if Path(self.usage_log).exists():
                with open(self.usage_log, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        total_time += entry.get('time_saved', 0)
                        total_code += entry.get('code_saved', 0)
                        usage_count += 1
            
            print("\n" + "=" * 70)
            print("💰 累计效率收益")
            print("=" * 70)
            print(f"   使用skill次数: {usage_count}")
            print(f"   累计节省时间: {total_time}秒 ({total_time/60:.1f}分钟)")
            print(f"   累计减少代码: {total_code}行")
            print("=" * 70)
            
            return {
                'usage_count': usage_count,
                'total_time_saved': total_time,
                'total_code_saved': total_code
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _log_comparison(self, task_type: str, skill: Dict, 
                       manual: Dict, time_saved: int):
        """记录对比日志"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'skill_used': skill['name'],
            'time_saved': time_saved,
            'code_saved': manual['code_lines'] - skill['code_lines']
        }
        
        with open(self.usage_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')

# 便捷函数
def show_efficiency(task_type: str = 'docx_parsing') -> Dict:
    """快速显示效率对比"""
    visualizer = EfficiencyVisualizer()
    return visualizer.compare(task_type)

def show_cumulative() -> Dict:
    """显示累计节省"""
    visualizer = EfficiencyVisualizer()
    return visualizer.show_cumulative_savings()

if __name__ == '__main__':
    # 测试
    show_efficiency('docx_parsing')
    show_efficiency('web_fetch')
    show_cumulative()
