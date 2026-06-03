#!/usr/bin/env python3
"""
token-circuit-breaker.py - Token熔断器
整合到token-tracker-zero，增加主动熔断机制
"""
import json
from datetime import datetime
from pathlib import Path

CIRCUIT_BREAKER_CONFIG = {
    'level_1_threshold': 0.30,  # 日消耗>30%周预算
    'level_1_action': '降频50%',
    'level_2_threshold': 0.50,  # 日消耗>50%周预算
    'level_2_action': '仅保留P0',
    'level_3_threshold': 3,      # 连续异常次数
    'level_3_action': '暂停后台任务'
}

def check_and_trigger_circuit_breaker():
    """检查并触发熔断"""
    tracker_file = Path('/root/.openclaw/workspace/memory/token-zero-tracker.json')
    
    if not tracker_file.exists():
        return {'status': 'no_data'}
    
    with open(tracker_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    today_actual = data.get('summary', {}).get('today_actual', 0)
    week_budget = 1000000  # 假设周预算100万tokens（示例值）
    
    daily_ratio = today_actual / week_budget
    
    breaker_state = {
        'timestamp': datetime.now().isoformat(),
        'today_actual': today_actual,
        'daily_ratio': daily_ratio,
        'level': 0,
        'action': 'none',
        'triggered': False
    }
    
    # 检查熔断条件
    if daily_ratio > CIRCUIT_BREAKER_CONFIG['level_2_threshold']:
        breaker_state['level'] = 2
        breaker_state['action'] = CIRCUIT_BREAKER_CONFIG['level_2_action']
        breaker_state['triggered'] = True
    elif daily_ratio > CIRCUIT_BREAKER_CONFIG['level_1_threshold']:
        breaker_state['level'] = 1
        breaker_state['action'] = CIRCUIT_BREAKER_CONFIG['level_1_action']
        breaker_state['triggered'] = True
    
    # 保存熔断状态
    breaker_file = Path('/root/.openclaw/workspace/memory/token-circuit-breaker-state.json')
    with open(breaker_file, 'w', encoding='utf-8') as f:
        json.dump(breaker_state, f, indent=2, ensure_ascii=False)
    
    if breaker_state['triggered']:
        print(f"⚠️ Token熔断触发! 级别: {breaker_state['level']}, 动作: {breaker_state['action']}")
    else:
        print(f"✅ Token消耗正常: {daily_ratio:.1%}")
    
    return breaker_state

if __name__ == '__main__':
    check_and_trigger_circuit_breaker()
