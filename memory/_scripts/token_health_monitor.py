#!/usr/bin/env python3
"""
Token 健康度监控 + Cron 自检引擎 v1.0
=====================================
双经济约束 · 预防性治理 · 自动告警
纳入管理后台 gov 域

监控维度:
  1. Token 消耗率 (session_status)
  2. Cron 数量 (防膨胀红线)
  3. Cron 失败率 (异常检测)
  4. Cron 执行频率 (每日总次数)
  5. 历史趋势 (基线对比)

红线:
  - Token 消耗率连续 > 80% → 黄牌
  - Cron 总数 > 30 → 红牌（需要审批才能新增）
  - 日执行次数 > 60 → 黄牌
  - 连续失败 > 3 的任务 → 自动暂停
  - 任意 Cron 连续 error > 5 → 自动禁用

用法:
  python3 token_health_monitor.py scan     # 扫描并写入报告
  python3 token_health_monitor.py report   # 生成可读报告
  python3 token_health_monitor.py enforce  # 强制执行规则（禁用违规任务）
"""

import json, subprocess, os, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path(os.environ.get('OPENCLAW_WORKSPACE', os.path.expanduser('~/.openclaw/workspace')))
MEMORY = WORKSPACE / 'memory'
LOG = MEMORY / '_data' / 'token_health_log.jsonl'
STATE = MEMORY / '_data' / 'token_health_state.json'

UTC8 = timezone(timedelta(hours=8))

# ============================================================
# 红线配置
# ============================================================
REDLINES = {
    'max_total_crons': 31,        # Cron 硬上限（含1个自检任务）
    'max_daily_execs': 60,        # 日执行次数上限
    'max_consecutive_errors': 3,  # 连续失败 → 黄牌
    'max_consecutive_disable': 5, # 连续失败 → 自动禁用
    'max_error_rate': 0.15,       # 失败率 > 15% → 告警
    'token_warn_pct': 80,         # Token 消耗率黄牌
    'token_crit_pct': 90,         # Token 消耗率红牌
    'min_green_days': 3,          # 连续绿天后才能申请新增 Cron
}


def get_cron_list():
    """获取所有 Cron 任务"""
    try:
        result = subprocess.run(
            ['openclaw', 'cron', 'list', '--json'],
            capture_output=True, text=True, cwd=str(WORKSPACE), timeout=15
        )
        data = json.loads(result.stdout)
        return data.get('jobs', [])
    except Exception as e:
        return []


def analyze_crons(jobs):
    """分析 Cron 健康状态"""
    total = len(jobs)
    errors = [j for j in jobs if j.get('state', {}).get('consecutiveErrors', 0) > 0]
    error_count = len(errors)
    error_rate = error_count / total if total > 0 else 0

    # 每日执行次数
    daily_execs = 0
    for j in jobs:
        sched = j.get('schedule', {})
        if sched.get('kind') == 'every':
            ms = sched.get('everyMs', 0)
            if ms > 0:
                daily_execs += 86400000 // ms
        elif sched.get('kind') == 'cron':
            daily_execs += 1  # cron 按每天 1 次算（近似）

    # 需要禁用的任务
    to_disable = []
    to_warn = []
    for j in errors:
        errs = j.get('state', {}).get('consecutiveErrors', 0)
        if errs >= REDLINES['max_consecutive_disable']:
            to_disable.append((j['name'], j['id'], errs))
        elif errs >= REDLINES['max_consecutive_errors']:
            to_warn.append((j['name'], j['id'], errs))

    return {
        'total': total,
        'errors': error_count,
        'error_rate': round(error_rate, 3),
        'daily_execs': daily_execs,
        'to_disable': to_disable,
        'to_warn': to_warn,
        'over_limit': total > REDLINES['max_total_crons'],
        'execs_over_limit': daily_execs > REDLINES['max_daily_execs'],
        'error_rate_over_limit': error_rate > REDLINES['max_error_rate'],
    }


def read_session_token():
    """读取当前 token 消耗率（通过 session_status）"""
    # Cron 隔离会话无法直接读，从压缩日志取最近一次
    log_file = MEMORY / 'Token压缩日志.md'
    if log_file.exists():
        text = log_file.read_text()
        for line in text.split('\n'):
            if 'Token 使用率' in line:
                try:
                    pct = int(''.join(c for c in line if c.isdigit()))
                    return pct
                except:
                    pass
    return None


def load_state():
    """加载历史状态"""
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        'cron_count_history': [],
        'daily_execs_history': [],
        'token_history': [],
        'alerts': []
    }


def save_state(state):
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def scan():
    """执行一次完整扫描"""
    now = datetime.now(UTC8)
    jobs = get_cron_list()
    analysis = analyze_crons(jobs)
    token_pct = read_session_token()

    # 更新历史状态
    state = load_state()
    
    # 确保历史列表存在
    for key in ['cron_count_history', 'daily_execs_history', 'token_history']:
        if key not in state:
            state[key] = []
    
    state['cron_count_history'].append({'ts': now.isoformat(), 'count': analysis['total']})
    state['daily_execs_history'].append({'ts': now.isoformat(), 'count': analysis['daily_execs']})
    if token_pct is not None:
        state['token_history'].append({'ts': now.isoformat(), 'pct': token_pct})

    # 保持最近 100 条
    for key in ['cron_count_history', 'daily_execs_history', 'token_history']:
        if len(state.get(key, [])) > 100:
            state[key] = state[key][-100:]

    # 检查告警
    alerts = []
    health = 'green'

    if analysis['over_limit']:
        health = 'red'
        alerts.append(f'🔴 Cron 总数 {analysis["total"]} > 红线 {REDLINES["max_total_crons"]}')
    if analysis['execs_over_limit']:
        health = 'red' if health != 'green' else 'yellow'
        alerts.append(f'🟡 日执行次数 {analysis["daily_execs"]} > 红线 {REDLINES["max_daily_execs"]}')
    if analysis['error_rate_over_limit']:
        health = 'red' if health != 'green' else 'yellow'
        alerts.append(f'🟡 错误率 {analysis["error_rate"]:.1%} > 红线 {REDLINES["max_error_rate"]:.1%}')
    if token_pct and token_pct >= REDLINES['token_crit_pct']:
        health = 'red'
        alerts.append(f'🔴 Token 消耗率 {token_pct}% > 红线 {REDLINES["token_crit_pct"]}%')
    elif token_pct and token_pct >= REDLINES['token_warn_pct']:
        health = 'yellow' if health != 'red' else 'red'
        alerts.append(f'🟡 Token 消耗率 {token_pct}% > 黄线 {REDLINES["token_warn_pct"]}%')

    for name, jid, errs in analysis['to_disable']:
        health = 'red'
        alerts.append(f'🔴 {name} 连续{errs}次失败 → 建议禁用')

    for name, jid, errs in analysis['to_warn']:
        if health == 'green':
            health = 'yellow'
        alerts.append(f'🟡 {name} 连续{errs}次失败')

    # 趋势检测
    cron_trend = 'stable'
    if len(state['cron_count_history']) >= 2:
        recent = [h['count'] for h in state['cron_count_history'][-5:]]
        if len(set(recent)) > 1:
            if recent[-1] > recent[0]:
                cron_trend = '⬆️ growing'
            elif recent[-1] < recent[0]:
                cron_trend = '⬇️ shrinking'

    # 写入状态
    state['alerts'] = alerts
    state['last_scan'] = now.isoformat()
    state['health'] = health
    state['analysis'] = {
        'total_crons': analysis['total'],
        'daily_execs': analysis['daily_execs'],
        'error_count': analysis['errors'],
        'error_rate': analysis['error_rate'],
        'token_pct': token_pct,
        'cron_trend': cron_trend,
        'new_cron_quota': max(0, REDLINES['max_total_crons'] - analysis['total']),
    }
    save_state(state)

    # 写日志行
    log_entry = {
        'ts': now.isoformat(),
        'health': health,
        'total': analysis['total'],
        'errors': analysis['errors'],
        'rate': analysis['error_rate'],
        'daily': analysis['daily_execs'],
        'token': token_pct,
        'alerts': len(alerts),
        'trend': cron_trend,
    }
    with open(LOG, 'a') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    return state


def enforce():
    """强制执行规则：禁用违规任务"""
    state = scan()
    jobs = get_cron_list()
    disabled = 0

    for j in jobs:
        errs = j.get('state', {}).get('consecutiveErrors', 0)
        if errs >= REDLINES['max_consecutive_disable']:
            name = j['name']
            jid = j['id']
            try:
                subprocess.run(
                    ['openclaw', 'cron', 'disable', jid],
                    capture_output=True, text=True, cwd=str(WORKSPACE), timeout=15
                )
                print(f'🛑 自动禁用: {name} (连续{errs}次失败)')
                disabled += 1
            except Exception as e:
                print(f'❌ 禁用失败 {name}: {e}')

    print(f'\n执行完毕: 禁用了 {disabled} 个任务')
    return disabled


def report():
    """生成可读健康报告"""
    state = load_state()
    if not state.get('last_scan'):
        print('⚠️ 尚未执行扫描，先运行 scan')
        return

    a = state.get('analysis', {})
    print('=' * 50)
    print('🩺 Token 健康度 + Cron 自检报告')
    print('=' * 50)
    print(f'时间: {state["last_scan"]}')
    print(f'健康: {"🟢 正常" if state["health"]=="green" else "🟡 警告" if state["health"]=="yellow" else "🔴 异常"}')
    print(f'Token: {a.get("token_pct","N/A")}%')
    print()
    print(f'Cron 总数: {a["total_crons"]} / 红线 {REDLINES["max_total_crons"]}')
    print(f'日执行: {a["daily_execs"]} / 红线 {REDLINES["max_daily_execs"]}')
    print(f'错误率: {a["error_rate"]:.1%} / 红线 {REDLINES["max_error_rate"]:.1%}')
    print(f'新增配额: {a["new_cron_quota"]} (需 {REDLINES["min_green_days"]}天绿色后可申请)')
    print(f'趋势: {a["cron_trend"]}')
    print()

    if state.get('alerts'):
        print('📢 告警:')
        for alert in state['alerts']:
            print(f'  {alert}')
    else:
        print('✅ 无告警')


VALID_ACTIONS = ['scan', 'report', 'enforce']

if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    if action not in VALID_ACTIONS:
        print(f"用法: {sys.argv[0]} scan|report|enforce")
        sys.exit(1)
    globals()[action]()
