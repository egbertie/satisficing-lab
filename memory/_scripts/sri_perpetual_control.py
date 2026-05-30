#!/usr/bin/env python3
"""
SRI 永续化学控制系统 v2.0
==========================
基于第二阶控制论 (Second-Order Cybernetics) + VSM (Viable System Model)

一次调控 = 检测热度→降速 (外部控制)
永续调控 = 系统观察自己的调控效果 → 调整调控策略 → 学习最优设定点

五层递归控制 (VSM):
  S1·执行层: 60条化学反应链
  S2·协调层: 编排器·断路器·优雅降级
  S3·控制层: 自限/自清/自休/自优 (第一阶)
  S4·智能层: 追踪调控效果·预测·调整设定点 (第二阶·本引擎)
  S5·策略层: 长期趋势·反脆弱训练·永续演进

反脆弱原则:
  不抵抗波动·从波动中学习
  调控失误→不是灾难·是训练数据
  越被扰动→调控越精准
"""

import json, os
from datetime import datetime, timezone

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')


def run_perpetual_control(dry_run=False):
    """永续化学控制: 第二阶·自演化·VSM嵌套"""
    now = datetime.now(timezone.utc)
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    meta = data.get('meta', {})
    governor_log = meta.get('chemical_governor', {})
    
    # ============================================
    # S2: 协调层 — 编排器健康信号
    # ============================================
    oh = meta.get('orchestration_health', {})
    health_score = oh.get('health_score', 100)
    
    # ============================================
    # S3: 控制层 — 第一阶调控 (直接调节)
    # ============================================
    heat = meta.get('heating', {}).get('total_heat', 0)
    
    # 设定点现在是动态的·不是固定的200-500
    # 第二阶根据历史调控效果来调整设定点
    tuning_history = meta.get('_tuning_history', [])
    
    # 默认设定点
    if tuning_history:
        # 从历史中学: 最近5次调控后的系统状态
        recent = tuning_history[-5:]
        stable_heats = [t.get('heat_after', 0) for t in recent if t.get('heat_after', 0) > 100]
        if stable_heats:
            # 设定点 = 历史稳定区间的中位数
            stable_heats.sort()
            setpoint_low = stable_heats[len(stable_heats)//2] - 50
            setpoint_high = stable_heats[len(stable_heats)//2] + 50
        else:
            setpoint_low, setpoint_high = 200, 500
    else:
        setpoint_low, setpoint_high = 200, 500
    
    # 调控决策
    if heat > setpoint_high:
        speed = 0.3 if heat > setpoint_high * 1.5 else 0.6
        state = 'braking'
    elif heat < setpoint_low:
        speed = 1.3 if heat < setpoint_low * 0.5 else 1.1
        state = 'heating'
    else:
        speed = 1.0
        state = 'steady'
    
    # ============================================
    # S4: 智能层 — 第二阶控制 (观察自己的调控)
    # ============================================
    
    # 追踪: 上次调控后热度变化
    prev_heat = governor_log.get('current_heat', heat)
    prev_state = governor_log.get('state', 'unknown')
    prev_speed = governor_log.get('speed_multiplier', 1.0)
    
    heat_delta = heat - prev_heat
    
    # 调控效果评估
    if prev_state == 'braking' and heat_delta < -50:
        effect = 'effective'       # 降速有效·热度成功降低
    elif prev_state == 'braking' and heat_delta >= 0:
        effect = 'ineffective'     # 降速无效·热度继续上升·需要更激进
    elif prev_state == 'heating' and heat_delta > 30:
        effect = 'effective'       # 升温有效
    elif prev_state == 'heating' and heat_delta <= 0:
        effect = 'overshoot'       # 升温过度
    else:
        effect = 'neutral'
    
    # 学习: 根据调控效果调整设定点
    if len(tuning_history) >= 3:
        recent_effects = [t.get('effect', 'neutral') for t in tuning_history[-3:]]
        # 如果连续3次 ineffective → 放宽设定点
        if recent_effects.count('ineffective') >= 2:
            setpoint_high += 50
            learning = '放宽上限·系统自然倾向高热'
        elif recent_effects.count('overshoot') >= 2:
            setpoint_low -= 30
            learning = '降低下限·系统自然倾向冷态'
        else:
            learning = '保持·设定点适应中'
    else:
        learning = '积累数据中'
    
    # ============================================
    # S5: 策略层 — 永续演进·反脆弱训练
    # ============================================
    
    # 系统的"年龄" = 总共执行的调控次数
    total_runs = len(tuning_history) + 1
    
    # 反脆弱测试: 有意引入微小扰动·观察恢复能力
    if total_runs % 10 == 0 and total_runs > 0:
        perturbation = 0.05 * (10 - (total_runs % 20) / 2)  # 逐渐减小扰动幅度
        speed *= (1 + perturbation)
        strategy = '反脆弱训练·扰动{}·测试恢复力'.format(round(perturbation, 2))
    else:
        perturbation = 0
        strategy = '稳态运行'
    
    # 永续指标
    stability_score = round(100 - abs(heat_delta) / 10, 1) if heat_delta else 100
    learning_progress = min(100, total_runs * 5)  # 每次调控+5%学习进度
    
    # ============================================
    # 保存状态
    # ============================================
    tuning_record = {
        'run': total_runs,
        'timestamp': now.isoformat(),
        'state': state,
        'speed': speed,
        'heat_before': prev_heat,
        'heat_after': heat,
        'heat_delta': heat_delta,
        'setpoint_low': setpoint_low,
        'setpoint_high': setpoint_high,
        'effect': effect,
        'learning': learning,
        'strategy': strategy,
        'health_score': health_score,
        'stability_score': stability_score,
        'learning_progress': learning_progress,
        'perturbation': perturbation,
    }
    
    tuning_history.append(tuning_record)
    if len(tuning_history) > 50:
        tuning_history = tuning_history[-50:]
    
    meta['_tuning_history'] = tuning_history
    
    # 更新调控日志 (替换·不是追加)
    meta['chemical_governor'] = {
        'version': '2.0',
        'executed_at': now.isoformat(),
        'state': state,
        'current_heat': round(heat, 1),
        'setpoint': '{}-{}'.format(setpoint_low, setpoint_high),
        'speed_multiplier': round(speed, 2),
        'effect': effect,
        'learning': learning,
        'strategy': strategy,
        'heat_delta': heat_delta,
        'stability_score': stability_score,
        'learning_progress': learning_progress,
        'total_runs': total_runs,
        'principle': '第二阶控制论·系统观察自己的调控·调整设定点·反脆弱训练'
    }
    
    if not dry_run:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return meta['chemical_governor']


def print_report(report):
    print("=" * 60)
    print("🧬 SRI 永续化学控制 · 第二阶")
    print("=" * 60)
    print("时间:", report['executed_at'][:19])
    print("版本:", report['version'])
    print(f"状态: {report['state']} · 速率: {report['speed_multiplier']}x")
    print(f"热力: {report['current_heat']} → 设定点: {report['setpoint']}")
    print(f"热变: {report['heat_delta']}")
    print(f"\n调控效果: {report['effect']}")
    print(f"学习: {report['learning']}")
    print(f"策略: {report['strategy']}")
    print(f"稳定度: {report['stability_score']}")
    print(f"学习进度: {report['learning_progress']}%")
    print(f"总调控次数: {report['total_runs']}")
    print(f"\n原则: {report['principle']}")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()
    
    report = run_perpetual_control(dry_run=not args.save)
    print_report(report)
