#!/usr/bin/env python3
"""
SRI 自校准引擎 v1.0
====================
设定点动态调谐 + 漂移检测 + 周期性重校准

原理:
  系统不止被调控 —— 系统观察调控效果，自动校准设定点。
  这是第二阶控制论的实践: 控制者观察自己的控制行为，调整控制参数。

功能:
  1. 从 entities_index.json 的 meta 区域读取当前热力、调控历史、化学统计
  2. 多时间尺度历史窗口分析 (24h / 72h / 7d)
  3. 基于历史中位数计算新设定点 (low=中位数的50%, high=中位数的150%)
  4. 漂移检测: 当前热力 vs 目标窗口 → OVERHEAT / UNDERHEAT / STABLE
  5. 周期性重校准: 距上次校准超过2h → 自动触发
  6. --save: 写入 entities_index.json → meta.autocalibration
  7. --dry-run: 仅输出不写入

被编排器 orchestrator 的阶段 13 (autocalibrate) 调用。
"""

import json
import os
import statistics
from datetime import datetime, timezone, timedelta

# ============================================================
# 配置
# ============================================================
WORKSPACE = os.environ.get('SRI_WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
DATA_FILE = os.path.join(WORKSPACE, 'memory/_data/entities_index.json')

# 设定点硬约束
SETPOINT_LOW_MIN = 100
SETPOINT_LOW_MAX = 800
SETPOINT_HIGH_MIN = 300
SETPOINT_HIGH_MAX = 2000

# 历史窗口配置 (小时)
HISTORY_WINDOWS = {
    '24h': 24,
    '72h': 72,
    '7d': 168,
}

# 校准冷却时间
RECALIBRATION_COOLDOWN_HOURS = 2

# 漂移检测阈值 (偏移比例)
DRIFT_THRESHOLD = 0.20  # 20%

# 历史窗口最小样本量
MIN_SAMPLES_PER_WINDOW = 5


# ============================================================
# 加载数据
# ============================================================
def load_data():
    """加载 entities_index.json"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================
# 历史窗口分析
# ============================================================
def collect_window_samples(tuning_history, window_hours, now):
    """
    从 tuning_history 中提取指定时间窗口内的调控样本。

    Parameters
    ----------
    tuning_history : list[dict]
        调控历史记录列表，每条含 'timestamp' 和 'heat_after' 字段
    window_hours : int
        时间窗口大小 (小时)
    now : datetime
        当前时间 (UTC)

    Returns
    -------
    list[float]
        窗口内有效的 heat_after 值列表
    """
    cutoff = now - timedelta(hours=window_hours)
    samples = []
    for record in tuning_history:
        # 解析时间戳
        ts_str = record.get('timestamp', '')
        try:
            # 处理多种ISO格式
            ts_str_clean = ts_str.replace('Z', '+00:00')
            if 'T' in ts_str_clean:
                ts = datetime.fromisoformat(ts_str_clean)
            else:
                # 尝试只解析日期部分
                ts = datetime.fromisoformat(ts_str_clean + 'T00:00:00+00:00')
        except (ValueError, TypeError):
            continue

        # 确保时区感知比较
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        if ts < cutoff:
            continue

        heat_val = record.get('heat_after')
        if heat_val is not None and isinstance(heat_val, (int, float)) and heat_val > 0:
            samples.append(float(heat_val))

    return samples


def analyze_window(samples, label):
    """
    对样本窗口进行统计分析。

    Returns
    -------
    dict or None
        包含 median, std, min, max, count, label 的统计结果
        如果样本数不足则返回 None
    """
    if len(samples) < MIN_SAMPLES_PER_WINDOW:
        return None

    # 排序后计算统计量
    sorted_samples = sorted(samples)
    n = len(sorted_samples)

    return {
        'label': label,
        'count': n,
        'median': statistics.median(sorted_samples),
        'std': statistics.stdev(sorted_samples) if n >= 2 else 0.0,
        'min': sorted_samples[0],
        'max': sorted_samples[-1],
        'range': sorted_samples[-1] - sorted_samples[0],
        'p25': sorted_samples[int(n * 0.25)],
        'p75': sorted_samples[int(n * 0.75)],
    }


def select_best_window(window_results):
    """
    从多个时间窗口中选择最佳者。

    选择策略:
      1. 优先选样本量≥MIN_SAMPLES_PER_WINDOW的窗口
      2. 样本量多的优于少的
      3. 样本量相同时，标准差小的 (波动小的) 优于大的

    Returns
    -------
    dict or None
        最佳窗口的分析结果
    """
    candidates = [w for w in window_results if w is not None]

    if not candidates:
        return None

    # 按 (样本量降序, 标准差升序 或 0) 排序
    candidates.sort(key=lambda w: (-w['count'], w.get('std', 0)))

    return candidates[0]


# ============================================================
# 设定点计算
# ============================================================
def compute_setpoint(best_window):
    """
    基于历史中位数计算新设定点。

    规则:
      - low  = 历史中位数的 50%
      - high = 历史中位数的 150%
      - 硬约束: low ∈ [100, 800], high ∈ [300, 2000]

    Parameters
    ----------
    best_window : dict
        最佳历史窗口的分析结果 (含 'median' 字段)

    Returns
    -------
    tuple[float, float]
        (setpoint_low, setpoint_high)
    """
    median_heat = best_window['median']

    raw_low = median_heat * 0.50
    raw_high = median_heat * 1.50

    setpoint_low = max(SETPOINT_LOW_MIN, min(SETPOINT_LOW_MAX, raw_low))
    setpoint_high = max(SETPOINT_HIGH_MIN, min(SETPOINT_HIGH_MAX, raw_high))

    # 额外保护: low 绝对不能超过 high
    if setpoint_low >= setpoint_high:
        setpoint_low = max(SETPOINT_LOW_MIN, setpoint_high - 100)

    return round(setpoint_low, 1), round(setpoint_high, 1)


def compute_fallback_setpoint():
    """
    无历史数据时的回退设定点。

    使用宽泛但受保护的默认值:
      - low:  200 (历史中位400的50%)
      - high: 600 (历史中位400的150%)
    """
    return 200.0, 600.0


# ============================================================
# 漂移检测
# ============================================================
def detect_drift(current_heat, setpoint_low, setpoint_high):
    """
    检测当前热力是否偏离目标设定点窗口。

    Parameters
    ----------
    current_heat : float
        当前系统热力值
    setpoint_low : float
        设定点窗口下界
    setpoint_high : float
        设定点窗口上界

    Returns
    -------
    tuple[bool, str, float]
        (drift_detected, drift_direction, deviation_ratio)
        direction: 'OVERHEAT' | 'UNDERHEAT' | 'STABLE'
    """
    if setpoint_high <= 0:
        # 无效设定点
        return False, 'STABLE', 0.0

    if current_heat > setpoint_high:
        deviation = (current_heat - setpoint_high) / setpoint_high
        if deviation > DRIFT_THRESHOLD:
            return True, 'OVERHEAT', round(deviation, 3)
        else:
            return False, 'OVERHEAT_MINOR', round(deviation, 3)

    elif current_heat < setpoint_low:
        deviation = (setpoint_low - current_heat) / setpoint_low
        if deviation > DRIFT_THRESHOLD:
            return True, 'UNDERHEAT', round(deviation, 3)
        else:
            return False, 'UNDERHEAT_MINOR', round(deviation, 3)

    else:
        return False, 'STABLE', 0.0


# ============================================================
# 周期性重校准检查
# ============================================================
def should_recalibrate(last_calibration_time, now):
    """
    判断是否需要触发周期性重校准。

    Parameters
    ----------
    last_calibration_time : str or None
        上次校准的 ISO 时间戳
    now : datetime
        当前时间

    Returns
    -------
    tuple[bool, float or None]
        (需要校准, 距上次校准的小时数)
    """
    if not last_calibration_time:
        return True, None

    try:
        ts_str = last_calibration_time.replace('Z', '+00:00')
        last_ts = datetime.fromisoformat(ts_str)
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return True, None

    elapsed = (now - last_ts).total_seconds() / 3600.0
    return elapsed >= RECALIBRATION_COOLDOWN_HOURS, round(elapsed, 1)


# ============================================================
# 主流程
# ============================================================
def run_autocalibration(dry_run=False):
    """
    执行完整的自校准流程。

    流程:
      1. 加载数据 → 提取 meta.heating / meta._tuning_history / meta.chemistry
      2. 多窗口历史分析 (24h / 72h / 7d)
      3. 选定最佳窗口 → 计算设定点
      4. 漂移检测
      5. 周期性重校准检查
      6. 写入或预览结果

    Returns
    -------
    dict
        校准报告
    """
    now = datetime.now(timezone.utc)

    # ---- 1. 加载数据 ----
    data = load_data()
    meta = data.get('meta', {})

    heating = meta.get('heating', {})
    if isinstance(heating, dict):
        current_heat = float(heating.get('total_heat', 0))
    else:
        current_heat = 0.0

    tuning_history = meta.get('_tuning_history', [])
    if not isinstance(tuning_history, list):
        tuning_history = []

    chemistry = meta.get('chemistry', {})
    if not isinstance(chemistry, dict):
        chemistry = {}

    last_autocal = meta.get('autocalibration', {})

    # ---- 2. 历史窗口分析 ----
    window_results = []
    for label, hours in HISTORY_WINDOWS.items():
        samples = collect_window_samples(tuning_history, hours, now)
        result = analyze_window(samples, label)
        window_results.append(result)

    # ---- 3. 选定最佳窗口 & 计算设定点 ----
    best_window = select_best_window(window_results)

    if best_window is not None:
        setpoint_low, setpoint_high = compute_setpoint(best_window)
        history_sample_count = best_window['count']
        window_used = best_window['label']
        window_stats = {
            'median': best_window['median'],
            'std': round(best_window['std'], 1),
            'min': best_window['min'],
            'max': best_window['max'],
            'count': best_window['count'],
        }
    else:
        setpoint_low, setpoint_high = compute_fallback_setpoint()
        history_sample_count = 0
        window_used = 'default'
        window_stats = {
            'median': None,
            'std': None,
            'min': None,
            'max': None,
            'count': 0,
        }

    # ---- 4. 漂移检测 ----
    drift_detected, drift_direction, drift_deviation = detect_drift(
        current_heat, setpoint_low, setpoint_high
    )

    # ---- 5. 周期性重校准检查 ----
    need_recal, hours_since = should_recalibrate(
        last_autocal.get('calibration_timestamp'), now
    )

    # ---- 6. 构建校准结果 ----
    calibration_result = {
        'setpoint_low': setpoint_low,
        'setpoint_high': setpoint_high,
        'drift_detected': drift_detected,
        'drift_direction': drift_direction,
        'drift_deviation': drift_deviation,
        'calibration_timestamp': now.isoformat(),
        'trigger': 'periodic' if need_recal else 'manual',
        'hours_since_last_calibration': hours_since,
        'current_heat': round(current_heat, 1),
        'history_window': window_used,
        'history_sample_count': history_sample_count,
        'window_stats': window_stats,
        # 所有窗口的概览 (供调试和日志)
        'all_windows': {
            wr['label']: {
                'count': wr['count'],
                'median': wr['median'],
                'std': round(wr['std'], 1),
            }
            for wr in window_results
            if wr is not None
        },
        # 化学统计摘要
        'chemistry_summary': {
            'last_reacted': chemistry.get('last_reacted'),
            'total_reactions': chemistry.get('total_reactions', 0),
        },
    }

    # ---- 7. 写入或预览 ----
    if not dry_run:
        meta['autocalibration'] = calibration_result

        # 追加一条轻量校准记录到 _tuning_history
        # 这样后续自校准可以追踪自身的校准历史
        tuning_record = {
            'type': 'autocalibration',
            'timestamp': now.isoformat(),
            'calibration_low': setpoint_low,
            'calibration_high': setpoint_high,
            'heat_before': round(current_heat, 1),
            'heat_after': round(current_heat, 1),
            'window_used': window_used,
            'samples': history_sample_count,
            'drift': drift_direction,
        }
        tuning_history.append(tuning_record)
        if len(tuning_history) > 100:
            tuning_history = tuning_history[-100:]
        meta['_tuning_history'] = tuning_history

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return calibration_result


# ============================================================
# 输出
# ============================================================
def print_report(report):
    """打印格式化的校准报告"""
    print("=" * 64)
    print("🎚️  SRI 自校准引擎 · 设定点动态调谐")
    print("=" * 64)
    print(f"时间: {report['calibration_timestamp'][:19]}")
    print(f"触发: {report['trigger']}")

    if report['hours_since_last_calibration'] is not None:
        print(f"距上次校准: {report['hours_since_last_calibration']}h")
    else:
        print("距上次校准: 首次校准")

    print()
    print(f"当前热力: {report['current_heat']}")
    print(f"历史窗口: {report['history_window']} (样本={report['history_sample_count']})")

    if report['window_stats']['median'] is not None:
        print(f"  历史中位数: {report['window_stats']['median']}")
        print(f"  历史标准差: {report['window_stats']['std']}")
        print(f"  历史范围: {report['window_stats']['min']} → {report['window_stats']['max']}")
    else:
        print("  无足够历史数据 · 使用默认设定点")

    print(f"\n📐 设定点: {report['setpoint_low']} → {report['setpoint_high']}")

    # 漂移
    drift_icon = '⚠️' if report['drift_detected'] else '✅'
    print(f"\n{drift_icon} 漂移检测: {report['drift_direction']}")
    if report['drift_detected']:
        print(f"  偏差比例: {report['drift_deviation'] * 100:.1f}%")

    # 多窗口概览
    if report.get('all_windows'):
        print("\n📊 多窗口历史对比:")
        for label, stats in report['all_windows'].items():
            status = '✅' if stats['count'] >= MIN_SAMPLES_PER_WINDOW else '⚠️ '
            print(f"  {status} {label}: {stats['count']}样本 "
                  f"中位={stats['median']} σ={stats['std']}")

    # 化学摘要
    cs = report.get('chemistry_summary', {})
    if cs.get('last_reacted'):
        print(f"\n⚗️  化学: 上次反应 {cs['last_reacted'][:19]} · "
              f"共{cs['total_reactions']}次反应")


# ============================================================
# CLI 入口
# ============================================================
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='SRI 自校准引擎: 设定点动态调谐 + 漂移检测 + 周期性重校准'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--save',
        action='store_true',
        help='执行校准并写入 entities_index.json'
    )
    group.add_argument(
        '--dry-run',
        action='store_true',
        help='仅预览校准结果，不写入文件'
    )

    args = parser.parse_args()

    if args.save:
        report = run_autocalibration(dry_run=False)
        print_report(report)
        print("\n[FIN-CAL] ✅ 校准完成 · 已写入 entities_index.json")
    elif args.dry_run:
        report = run_autocalibration(dry_run=True)
        print_report(report)
        print("\n[FIN-CAL] 👁️ 预览模式 · 未写入文件")
