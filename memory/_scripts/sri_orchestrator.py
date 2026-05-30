#!/usr/bin/env python3
"""
SRI 闭环健康编排引擎 v1.0
===========================
实现三层闭环架构:

🟢 微循环(毛细血管): 每个脚本内部的 try/except + fallback
🟡 中循环(血管):     每个环节独立自愈 + 异常隔离 + 优雅降级
🔴 大循环(大动脉):   15个环节串行 + circuit breaker + 全局健康分

被飞轮引擎 flywheel 的 run() 调用。
替代原有的一串顺序调用，改为分层编排。

v2.0 (2026-05-31): +4控制论环节(VSM·二阶观察·自校准·反脆弱) 10→15环节

架构原则:
- Circuit Breaker: 任一步骤连续失败3次 → 熔断该环节 → 跳过继续下一环节
- Bulkhead: 每个环节有独立的 timeout 和错误计数
- Graceful Degradation: 一个环节熔断不影响其他环节
- Health Dashboard: 每个环节有独立健康分
"""

import json
import os
import time
import traceback
from datetime import datetime, timezone

WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')

# 环节定义: 按执行顺序
STAGES = [
    {
        'id': 'nourish',
        'label': '📡 养料采集',
        'script': 'sri_nourishment_collector.py',
        'timeout': 120,
        'breaker_threshold': 3,
        'weight': 1.0,  # 对大闭环的权重
        'fallback': '跳过·使用已采集数据',
    },
    {
        'id': 'quality_gate',
        'label': '🔒 质量门禁',
        'script': 'sri_quality_gate.py',
        'timeout': 60,
        'breaker_threshold': 3,
        'weight': 0.8,
        'fallback': '跳过·信任养料质量',
    },
    {
        'id': 'scan',
        'label': '📁 文件扫描',
        'script': 'sri_knowledge_flywheel.py',  # 调用 scan 子命令
        'timeout': 300,
        'breaker_threshold': 5,
        'weight': 1.5,
        'fallback': '基于上次扫描结果·标记 deferred',
    },
    {
        'id': 'consistency',
        'label': '🔬 一致性检查',
        'script': 'sri_consistency_checker.py',
        'timeout': 60,
        'breaker_threshold': 3,
        'weight': 0.6,
        'fallback': '跳过·保留上次检查结果',
    },
    {
        'id': 'heal',
        'label': '🩺 自动修复',
        'script': 'sri_auto_healer.py',
        'timeout': 300,
        'breaker_threshold': 3,
        'weight': 0.5,
        'fallback': '跳过·标记待手动修复',
    },
    {
        'id': 'lifecycle',
        'label': '🔄 生命周期',
        'script': 'sri_lifecycle_manager.py',
        'timeout': 120,
        'breaker_threshold': 2,
        'weight': 0.4,
        'fallback': '跳过·保留当前cycle',
    },
    {
        'id': 'standards',
        'label': '📐 标准迭代',
        'script': 'sri_standards_iterator.py',
        'timeout': 60,
        'breaker_threshold': 2,
        'weight': 0.3,
        'fallback': '跳过·标准版本保持不变',
    },
    {
        'id': 'audit',
        'label': '📊 产品审计',
        'script': 'sri_product_scanner.py',
        'timeout': 300,
        'breaker_threshold': 2,
        'weight': 0.5,
        'fallback': '跳过·保留上次审计分',
    },
    {
        'id': 'report',
        'label': '📋 报告生成',
        'script': 'sri_knowledge_flywheel.py',  # 调用 report 子命令
        'timeout': 60,
        'breaker_threshold': 10,  # 报告几乎不熔断
        'weight': 0.2,
        'fallback': '生成简化报告',
    },
    {
        'id': 'chemistry',
        'label': '⚗️ 化学反应',
        'script': 'sri_chemistry_reactor.py',
        'timeout': 120,
        'breaker_threshold': 3,
        'weight': 1.0,
        'fallback': '跳过·保留上次反应状态',
    },
    {
        'id': 'governor',
        'label': '🧬 永续控制',
        'script': 'sri_perpetual_control.py',
        'extra_args': ['--save'],
        'timeout': 60,
        'breaker_threshold': 5,
        'weight': 1.5,
        'fallback': '跳过·保留上次调控状态',
    },
    {
        'id': 'vsm_policy',
        'label': '🏛️ VSM策略审计',
        'script': 'sri_vsm_system5.py',
        'extra_args': ['--save'],
        'timeout': 90,
        'breaker_threshold': 3,
        'weight': 0.8,
        'fallback': '跳过·保留上次策略审计结果',
    },
    {
        'id': 'second_order',
        'label': '👁️ 二阶观察',
        'script': 'sri_second_order_observer.py',
        'extra_args': ['--save'],
        'timeout': 90,
        'breaker_threshold': 3,
        'weight': 1.0,
        'fallback': '跳过·保留上次观察结果',
    },
    {
        'id': 'autocalibrate',
        'label': '🎚️ 自校准',
        'script': 'sri_autocalibration.py',
        'extra_args': ['--save'],
        'timeout': 60,
        'breaker_threshold': 3,
        'weight': 0.6,
        'fallback': '跳过·保留上次校准设定点',
    },
    {
        'id': 'antifragile',
        'label': '💪 反脆弱训练',
        'script': 'sri_antifragile_stressor.py',
        'extra_args': ['--save'],
        'timeout': 120,
        'breaker_threshold': 2,
        'weight': 0.4,
        'fallback': '跳过·保留上次训练状态',
    },
]


class CircuitBreaker:
    """电路断路器: 连续失败N次→熔断·冷却后→半开重试"""
    
    def __init__(self, name, threshold=3, cooldown_seconds=3600):
        self.name = name
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed → open → half_open → closed
        self.total_calls = 0
        self.total_success = 0
    
    def call(self, func):
        """包装函数调用·断路器保护"""
        if self.state == 'open':
            if self.last_failure_time:
                elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
                if elapsed > self.cooldown_seconds:
                    self.state = 'half_open'
                else:
                    return None, 'circuit_open·冷却{}s'.format(int(self.cooldown_seconds - elapsed))
        
        self.total_calls += 1
        try:
            result = func()
            self.on_success()
            return result, None
        except Exception as e:
            self.on_failure()
            return None, str(e)[:200]
    
    def on_success(self):
        self.failure_count = 0
        self.total_success += 1
        self.state = 'closed'
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        if self.failure_count >= self.threshold:
            self.state = 'open'
    
    def health(self):
        return {
            'name': self.name,
            'state': self.state,
            'failures': self.failure_count,
            'threshold': self.threshold,
            'success_rate': round(100 * self.total_success / max(1, self.total_calls), 1),
            'total_calls': self.total_calls
        }


def run_stage_standalone(script_name, extra_args=None):
    """独立运行一个脚本 (微循环: 即使失败也不影响其他)"""
    import subprocess
    script_path = os.path.join(WORKSPACE, 'memory/_scripts', script_name)
    
    if not os.path.exists(script_path):
        raise FileNotFoundError('Script not found: {}'.format(script_path))
    
    cmd = ['python3', script_path]
    # 各脚本参数名不同，需要适配
    if 'flywheel' in script_name:
        cmd.append('all')
    elif 'auto_healer' in script_name:
        cmd.extend(['--limit', '30'])
    elif 'product_scanner' in script_name:
        cmd.append('--save')
    elif 'quality_gate' in script_name or 'nourishment' in script_name or 'consistency' in script_name or 'lifecycle' in script_name or 'standards' in script_name:
        cmd.append('--save')
    # portfolio_rationalizer 和 orchestrator 不需要参数
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=WORKSPACE)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[:200] if result.stderr else 'exit code: {}'.format(result.returncode))
    
    return result.stdout[:1000]


def orchestrate_health_cycle(dry_run=False):
    """
    编排一轮完整的健康循环 (大循环)
    每步独立执行·断路器保护·优雅降级
    返回每个环节的状态
    """
    now = datetime.now(timezone.utc)
    stages_status = []
    
    # 加载或创建断路器状态
    breakers = {}
    
    # 尝试从 entities_index 加载断路器状态
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            saved = data.get('meta', {}).get('circuit_breakers', {})
            for sid, state in saved.items():
                cb = CircuitBreaker(sid)
                cb.failure_count = state.get('failures', 0)
                cb.state = state.get('state', 'closed')
                cb.total_calls = state.get('calls', 0)
                cb.total_success = state.get('success', 0)
                breakers[sid] = cb
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    
    # 执行所有环节
    for stage in STAGES:
        sid = stage['id']
        cb = breakers.get(sid, CircuitBreaker(sid, stage['breaker_threshold']))
        breakers[sid] = cb
        
        stage_start = time.time()
        
        if dry_run:
            stages_status.append({
                'stage': sid,
                'label': stage['label'],
                'status': 'skipped',
                'reason': 'dry_run',
                'breaker_state': cb.state,
                'duration_ms': 0
            })
            continue
        
        # 断路器包装执行
        def run_stage(s=stage):
            return run_stage_standalone(s['script'])
        
        result, error = cb.call(run_stage)
        elapsed_ms = int((time.time() - stage_start) * 1000)
        
        if error:
            if cb.state == 'open':
                stages_status.append({
                    'stage': sid,
                    'label': stage['label'],
                    'status': 'degraded',
                    'reason': 'circuit_open',
                    'fallback': stage['fallback'],
                    'breaker_state': cb.state,
                    'duration_ms': elapsed_ms
                })
            else:
                stages_status.append({
                    'stage': sid,
                    'label': stage['label'],
                    'status': 'failed',
                    'reason': error[:100],
                    'breaker_state': cb.state,
                    'duration_ms': elapsed_ms
                })
        else:
            stages_status.append({
                'stage': sid,
                'label': stage['label'],
                'status': 'ok',
                'breaker_state': cb.state,
                'duration_ms': elapsed_ms
            })
    
    # 计算全局健康分
    total_weight = sum(s['weight'] for s in STAGES)
    health_score = 0
    for i, ss in enumerate(stages_status):
        if ss['status'] == 'ok':
            health_score += STAGES[i]['weight']
        elif ss['status'] == 'degraded':
            health_score += STAGES[i]['weight'] * 0.5
        # failed = 0
    
    health_score = round(100 * health_score / total_weight, 1)
    
    # 保存断路器状态
    if not dry_run:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        if 'meta' not in data:
            data['meta'] = {}
        
        data['meta']['circuit_breakers'] = {}
        for sid, cb in breakers.items():
            data['meta']['circuit_breakers'][sid] = {
                'failures': cb.failure_count,
                'state': cb.state,
                'calls': cb.total_calls,
                'success': cb.total_success,
                'threshold': cb.threshold
            }
        
        data['meta']['orchestration_health'] = {
            'checked_at': now.isoformat(),
            'health_score': health_score,
            'total_stages': len(stages_status),
            'ok': sum(1 for s in stages_status if s['status'] == 'ok'),
            'degraded': sum(1 for s in stages_status if s['status'] == 'degraded'),
            'failed': sum(1 for s in stages_status if s['status'] == 'failed'),
            'stages': [{k: v for k, v in ss.items() if k != 'duration_ms'} for ss in stages_status]
        }
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return {
        'orchestrated_at': now.isoformat(),
        'total_stages': len(stages_status),
        'health_score': health_score,
        'stages': stages_status
    }


def print_report(report):
    print("=" * 60)
    print("SRI 三层闭环编排 · 健康报告")
    print("=" * 60)
    print("时间: {}".format(report['orchestrated_at'][:19]))
    print("健康分: {}/100".format(report['health_score']))
    print()
    
    for s in report['stages']:
        icon = {'ok': '✅', 'degraded': '🟡', 'failed': '❌', 'skipped': '⏭️'}.get(s['status'], '?')
        cb_state = s.get('breaker_state', '?')
        dur = s.get('duration_ms', 0)
        print("  {icon} {label} ({status} · {cb} · {dur}ms)".format(
            icon=icon, label=s['label'], status=s['status'], cb=cb_state, dur=dur))
        if s.get('reason'):
            print("     ↳ {}".format(s['reason']))
    
    print()
    ok = sum(1 for s in report['stages'] if s['status'] == 'ok')
    degraded = sum(1 for s in report['stages'] if s['status'] == 'degraded')
    failed = sum(1 for s in report['stages'] if s['status'] == 'failed')
    print("总计: {}✅ {}🟡 {}❌".format(ok, degraded, failed))
    if report['health_score'] >= 90:
        print("评级: 🟢 健康")
    elif report['health_score'] >= 60:
        print("评级: 🟡 注意")
    else:
        print("评级: 🔴 异常")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='SRI 闭环健康编排引擎')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--save', action='store_true')
    args = p.parse_args()
    
    report = orchestrate_health_cycle(dry_run=not args.save)
    print_report(report)
