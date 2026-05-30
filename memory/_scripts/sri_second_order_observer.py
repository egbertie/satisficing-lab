#!/usr/bin/env python3
"""
sri_second_order_observer.py — 二阶控制论观察者

观察飞轮自身如何观察，构建飞轮自我模型。
遵循二阶控制论原则(SRI)：系统不仅观察世界，也观察自己的观察过程。

原理：
  一阶观察: 飞轮 → 观察 entity_index 数据 (scan/audit/health-check)
  二阶观察: 这个脚本 → 观察飞轮是如何观察的 → 构建飞轮的自我模型

输入:  entities_index.json → meta.{flywheel, orchestration_health, heating, llm_stats}
输出:  entities_index.json → meta.second_order (when --save)

Author: SRI Second-Order Observer
Version: 1.0.0
"""

import argparse
import json
import sys
import os
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ── 路径常量 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DEFAULT_INDEX_PATH = os.path.join(WORKSPACE_ROOT, "memory", "_data", "entities_index.json")
BIAS_THRESHOLD = 0.15  # 15% 偏差阈值 → 标记为观察失真

# ── 日志工具 ──────────────────────────────────────────────
def log(msg: str, level: str = "INFO", file=None):
    """统一格式的控制台日志，默认输出到 stderr 保持 stdout 留给 JSON。"""
    ts = datetime.now().strftime("%H:%M:%S")
    prefixes = {"INFO": "  ℹ️", "OK": "  ✅", "WARN": "  ⚠️", "ERR": "  ❌", "HEAD": "📐"}
    prefix = prefixes.get(level, "  ·")
    dest = file if file is not None else sys.stderr
    print(f"{prefix} [{ts}] {msg}", file=dest)


# ═══════════════════════════════════════════════════════════════
# 数据加载
# ═══════════════════════════════════════════════════════════════

def load_index(path: str) -> dict:
    """加载 entities_index.json，返回完整对象。"""
    if not os.path.exists(path):
        log(f"文件不存在: {path}", "ERR")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_index(path: str, data: dict) -> None:
    """回写 entities_index.json。"""
    with open(path, "r", encoding="utf-8") as fh:
        original = json.load(fh)
    if "meta" not in original:
        original["meta"] = {}
    original["meta"]["second_order"] = data
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(original, fh, ensure_ascii=False, indent=2)
    log(f"已写入 meta.second_order → {path}", "OK")


# ═══════════════════════════════════════════════════════════════
# 1. observation_space 构建 (6维观察空间)
# ═══════════════════════════════════════════════════════════════

def compute_reaction_yield(heating: dict) -> float:
    """化学链活链率: alive/total (living_rules_status 驱动的链活性)

    从 heating 数据反推：total_heat 是累计热量，heat_sources 是热源数量。
    活链率 = 活跃规则 / 总规则 (取自 meta.living_rules_status)
    """
    lrs = heating.get("_living_rules_status")  # 可能传入或从 meta 挂载
    if lrs is None:
        return 0.0
    total = sum(lrs.get(k, 0) for k in ("active", "dormant", "broken", "never_activated"))
    alive = lrs.get("active", 0)
    return round(alive / total, 4) if total > 0 else 0.0


def compute_heat_variance(heating: dict) -> float:
    """热力波动: 近期热力值范围 (max - min of recent heat values)。

    由于 heating 只有单一 total_heat 快照，我们使用 heat_sources 作为
    多维度热力指标来计算波动系数。
    """
    total_heat = heating.get("total_heat", 0)
    heat_sources = heating.get("heat_sources", 1)
    # 平均每源热量作为基准，max=基准*2作为假设最大值
    avg_per_source = total_heat / max(heat_sources, 1)
    variance_coeff = avg_per_source / max(total_heat, 1)  # [0, 1] 归一化波动系数
    return round(variance_coeff, 4)


def compute_link_vitality(flywheel: dict) -> float:
    """链活性百分比: 计算飞轮各 cycle 中有多少个不是 idle 状态。"""
    cycles = flywheel.get("cycles", {})
    if not cycles:
        return 0.0
    total = len(cycles)
    active = sum(1 for c in cycles.values() if c.get("status") != "idle")
    return round(active / total, 4) if total > 0 else 0.0


def compute_health_drift(orchestration_health: dict, flywheel: dict) -> float:
    """编排器健康分的变化趋势。

    比较当前的 health_score 与飞轮最近一次 health_audit_report 中的
    flow_complete 状态的语义化差值。
    - 正值: 健康分在上升（好转）
    - 负值: 健康分在下降（恶化）
    - 0: 无变化或无历史数据
    """
    current = orchestration_health.get("health_score", 100)
    audit = flywheel.get("health_audit_report", {})
    # 使用 flow_complete 作为历史参照——complete=True 暗示历史健康≈100，False≈50
    if audit.get("flow_complete"):
        previous = 100.0
    else:
        previous = 50.0
    drift = round((current - previous) / max(previous, 1), 4)
    return drift


def compute_score_decay(llm_stats: dict) -> float:
    """LLM评分衰减检测。

    比较 best.score (最高分) 与 llm_avg (平均分) 的差距，归一化。
    衰减 = (best - avg) / best，值越大说明评分分化越严重，
    可能意味着评分标准在衰减或被稀释。
    """
    avg = llm_stats.get("llm_avg", 0)
    best_score = llm_stats.get("best", {}).get("score", avg)
    if best_score <= 0:
        return 0.0
    decay = (best_score - avg) / best_score
    return round(decay, 4)


def compute_config_entropy(meta: dict) -> float:
    """配置熵: meta 键数量的增长速率。

    计算方式：从 meta 的版本/创建时间估算键增长。
    - version="3.0" → 假设从 v1.0 开始
    - 当前键数 / 版本号 → 每大版本平均键增量
    - 归一化到 [0,1]
    """
    total_keys = len(meta)
    version_str = meta.get("version", "1.0")
    try:
        major = float(version_str.split(".")[0])
    except (ValueError, IndexError):
        major = 1.0
    # 每版本平均键数，归一化 (假设最大 200 键/版本)
    avg_per_version = total_keys / max(major, 1)
    entropy = min(avg_per_version / 200.0, 1.0)
    return round(entropy, 4)


def build_observation_space(meta: dict) -> dict:
    """构建完整的 6 维观察空间快照。

    Returns:
        dict 包含 6 个维度及其值、归一化范围、语义说明。
    """
    flywheel = meta.get("flywheel", {})
    heating = meta.get("heating", {})
    lrs = meta.get("living_rules_status", {})
    orchestration_health = meta.get("orchestration_health", {})
    llm_stats = meta.get("llm_stats", {})

    # 将 living_rules_status 挂载到 heating 供 compute_reaction_yield 使用
    heating_with_lrs = dict(heating)
    heating_with_lrs["_living_rules_status"] = lrs

    observations = {
        "reaction_yield": {
            "value": compute_reaction_yield(heating_with_lrs),
            "range": [0.0, 1.0],
            "unit": "%",
            "label": "化学链活链率",
            "description": "living_rules 中 active / total 的比例",
        },
        "heat_variance": {
            "value": compute_heat_variance(heating),
            "range": [0.0, 1.0],
            "unit": "σ",
            "label": "热力波动系数",
            "description": "total_heat 与 heat_sources 的归一化波动系数",
        },
        "link_vitality": {
            "value": compute_link_vitality(flywheel),
            "range": [0.0, 1.0],
            "unit": "%",
            "label": "链活性百分比",
            "description": "飞轮 cycles 中非 idle 状态的比例",
        },
        "health_drift": {
            "value": compute_health_drift(orchestration_health, flywheel),
            "range": [-1.0, 1.0],
            "unit": "Δ",
            "label": "编排器健康漂移",
            "description": "当前 health_score 与历史参照的变化率",
        },
        "score_decay": {
            "value": compute_score_decay(llm_stats),
            "range": [0.0, 1.0],
            "unit": "ε",
            "label": "LLM评分衰减度",
            "description": "(best - avg) / best 的归一化衰减",
        },
        "config_entropy": {
            "value": compute_config_entropy(meta),
            "range": [0.0, 1.0],
            "unit": "H",
            "label": "配置熵",
            "description": "meta 键总数/版本号 的归一化增长速率",
        },
    }

    return observations


# ═══════════════════════════════════════════════════════════════
# 2. observer_bias 计算 (观察偏差)
# ═══════════════════════════════════════════════════════════════

def compute_observer_bias(meta: dict, observation_space: dict) -> dict:
    """比较飞轮自己报告的状态 vs 独立计算的状态。

    飞轮自述状态来源:
    - flywheel.capacity.rating="green" → 自述健康100%
    - flywheel.cycles.*.status → 100% 都 idle (但自己报告 rating=green)
    - orchestration_health.health_score=100 → 自述100%
    - llm_stats.coverage_pct=11.1 → 覆盖率仅11%，但 avg=74.8

    独立计算状态:
    - chain_active_rate: 链非idle比例
    - health_drift: 从 observation_space 中取
    - coverage_pct: LLM 覆盖比例
    - score_decay: LLM 评分衰减

    偏差 > BIAS_THRESHOLD (15%) → 观察失真
    """
    flywheel = meta.get("flywheel", {})
    orchestration_health = meta.get("orchestration_health", {})
    llm_stats = meta.get("llm_stats", {})

    comparisons = []

    # 1. 飞轮自述 capacity.rating="green" vs 实际链活性
    self_reported_rating = 1.0 if flywheel.get("capacity", {}).get("rating") == "green" else 0.5
    actual_link_vitality = observation_space["link_vitality"]["value"]
    bias_chain = abs(self_reported_rating - actual_link_vitality)
    comparisons.append({
        "dimension": "chain_activity",
        "label": "链活性",
        "self_reported": self_reported_rating,
        "independently_computed": actual_link_vitality,
        "bias": round(bias_chain, 4),
        "distorted": bias_chain > BIAS_THRESHOLD,
    })

    # 2. orchestration_health.health_score=100 vs 实际 health_drift 趋势
    self_reported_health = orchestration_health.get("health_score", 100) / 100.0
    # health_drift 可以是负的(恶化)，但这里我们取绝对值来比较报告的完美 vs 实际问题
    health_drift_val = observation_space["health_drift"]["value"]
    independent_health = 1.0 - max(0, min(1, abs(health_drift_val)))  # drift越大，独立健康分越低
    bias_health = abs(self_reported_health - independent_health)
    comparisons.append({
        "dimension": "health_score",
        "label": "编排器健康分",
        "self_reported": round(self_reported_health, 4),
        "independently_computed": round(independent_health, 4),
        "bias": round(bias_health, 4),
        "distorted": bias_health > BIAS_THRESHOLD,
    })

    # 3. LLM coverage_pct=11.1 vs 是否还在评分(score_decay)
    coverage_pct = llm_stats.get("coverage_pct", 0) / 100.0
    score_decay = observation_space["score_decay"]["value"]
    # 覆盖率低→自述能力低，decay高→独立评估差
    # 当 coverage 低但 decay 不高时，说明评分集中度高(偏差小)
    # 当 coverage 低且 decay 高时，说明质量在恶化(偏差大)
    independent_cov = 1.0 - score_decay  # decay越低 = 独立评估越好
    bias_llm = abs(coverage_pct - independent_cov)
    comparisons.append({
        "dimension": "llm_cognitive",
        "label": "LLM认知覆盖",
        "self_reported": round(coverage_pct, 4),
        "independently_computed": round(independent_cov, 4),
        "bias": round(bias_llm, 4),
        "distorted": bias_llm > BIAS_THRESHOLD,
    })

    # 4. heating.total_heat → 系统自称热度 vs 活链率是否匹配
    total_heat = meta.get("heating", {}).get("total_heat", 0)
    temp_grade_map = {"hot": 1.0, "warm": 0.7, "mild": 0.4, "cool": 0.2, "cold": 0.0}
    self_reported_heat = temp_grade_map.get(
        meta.get("heating", {}).get("temperature_grade", "mild"), 0.4
    )
    reaction_yield = observation_space["reaction_yield"]["value"]
    bias_heat = abs(self_reported_heat - reaction_yield)
    comparisons.append({
        "dimension": "heat_vs_activity",
        "label": "热度vs活性匹配",
        "self_reported": self_reported_heat,
        "independently_computed": reaction_yield,
        "bias": round(bias_heat, 4),
        "distorted": bias_heat > BIAS_THRESHOLD,
    })

    # 汇总偏差
    all_biases = [c["bias"] for c in comparisons]
    avg_bias = round(sum(all_biases) / len(all_biases), 4) if all_biases else 0.0
    max_bias = max(all_biases) if all_biases else 0.0
    distorted_count = sum(1 for c in comparisons if c["distorted"])
    total_distorted = distorted_count > 0

    return {
        "avg_bias": avg_bias,
        "max_bias": max_bias,
        "dimensions_compared": len(comparisons),
        "distorted_dimensions": distorted_count,
        "comparisons": comparisons,
        "overall_distorted": total_distorted,
        "threshold": BIAS_THRESHOLD,
    }


# ═══════════════════════════════════════════════════════════════
# 3. self_referential_log (自指涉日志)
# ═══════════════════════════════════════════════════════════════

def build_self_referential_log(
    meta: dict, observation_space: dict, observer_bias: dict
) -> list:
    """生成自指涉日志条目: "系统认为自己如何" vs "系统实际如何"。

    Returns:
        list of dict — 每条日志为一个自指涉对比记录。
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    log_entries = []

    # 从 observer_bias.comparisons 中提取每一条
    for comp in observer_bias.get("comparisons", []):
        entry = {
            "timestamp": now_iso,
            "dimension": comp["dimension"],
            "label": comp["label"],
            "self_view": f"系统自述: {comp['self_reported']}",
            "observer_view": f"独立观测: {comp['independently_computed']}",
            "gap": comp["bias"],
            "judgement": (
                "观察失真 ⚠️"
                if comp["distorted"]
                else "自指涉一致 ✓"
            ),
        }
        log_entries.append(entry)

    # 追加一条全局自指涉总结
    global_bias = observer_bias.get("avg_bias", 0)
    global_distorted = observer_bias.get("overall_distorted", False)

    log_entries.append({
        "timestamp": now_iso,
        "dimension": "_global",
        "label": "二阶观察全局判断",
        "self_view": f"飞轮自述: rating={meta.get('flywheel', {}).get('capacity', {}).get('rating', 'unknown')}, "
                     f"health={meta.get('orchestration_health', {}).get('health_score', '?')}",
        "observer_view": f"独立观测: 平均偏差={global_bias:.4f}, "
                         f"失真维度={observer_bias.get('distorted_dimensions', 0)}/{observer_bias.get('dimensions_compared', 0)}",
        "gap": global_bias,
        "judgement": "⚠️ 二阶观察检测到失真" if global_distorted else "✓ 飞轮自我模型准确",
    })

    return log_entries


# ═══════════════════════════════════════════════════════════════
# 4. 状态判定
# ═══════════════════════════════════════════════════════════════

def determine_state(observer_bias: dict) -> str:
    """根据观察偏差判定二阶观察状态。

    规则:
    - distorted_dimensions >= 2  → BIAS_DETECTED
    - avg_bias > BIAS_THRESHOLD   → DRIFTING
    - else                         → OK
    """
    if observer_bias.get("distorted_dimensions", 0) >= 2:
        return "BIAS_DETECTED"
    if observer_bias.get("avg_bias", 0) > BIAS_THRESHOLD:
        return "DRIFTING"
    return "OK"


# ═══════════════════════════════════════════════════════════════
# 5. 汇总与输出
# ═══════════════════════════════════════════════════════════════

def print_report(
    observation_space: dict,
    observer_bias: dict,
    self_log: list,
    state: str,
) -> None:
    """在控制台输出完整的二阶观察报告。"""

    # ── 头部 ──
    log("", "", file=sys.stderr)
    log("═" * 62, "", file=sys.stderr)
    log("  二阶控制论观察者 · Second-Order Cybernetic Observer", "HEAD", file=sys.stderr)
    log("═" * 62, "", file=sys.stderr)
    log(f"  时间: {datetime.now(timezone.utc).isoformat()}", "", file=sys.stderr)
    log(f"  偏差阈值: {BIAS_THRESHOLD * 100:.0f}%", "", file=sys.stderr)
    log("", "", file=sys.stderr)

    # ── 观察空间 ──
    state_emoji = {"OK": "🟢", "BIAS_DETECTED": "🔴", "DRIFTING": "🟡"}.get(state, "⚪")
    log(f"  观察空间 (6维)                        状态: {state_emoji} {state}", "HEAD", file=sys.stderr)
    log("─" * 62, "", file=sys.stderr)
    for dim, obs in observation_space.items():
        val = obs["value"]
        rng = obs["range"]
        unit = obs["unit"]
        label = obs["label"]
        # 可视化条形: 根据范围映射
        lo, hi = rng
        if hi > lo:
            pct = (val - lo) / (hi - lo)
        else:
            pct = 0.5
        bar_len = 20
        filled = int(pct * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  {label:<12s} [{bar}] {val:>8.4f}{unit}", file=sys.stderr)

    # ── 观察偏差 ──
    log("", "", file=sys.stderr)
    log(f"  观察偏差比较 (avg={observer_bias['avg_bias']:.4f})", "HEAD", file=sys.stderr)
    log("─" * 62, "", file=sys.stderr)
    for comp in observer_bias.get("comparisons", []):
        dim = comp["dimension"]
        flag = "⚠️ 失真" if comp["distorted"] else "✓  一致"
        self_v = comp["self_reported"]
        ind_v = comp["independently_computed"]
        bias_v = comp["bias"]
        print(f"  {flag}  {comp['label']:<10s}  自述={self_v:.4f}  独立={ind_v:.4f}  偏差={bias_v:.4f}", file=sys.stderr)

    # ── 自指涉日志摘要 ──
    log("", "", file=sys.stderr)
    log(f"  自指涉日志 ({len(self_log)} 条)", "HEAD", file=sys.stderr)
    log("─" * 62, "", file=sys.stderr)
    for entry in self_log:
        dim = entry["dimension"]
        if dim == "_global":
            continue
        jdg = entry["judgement"]
        print(f"  {jdg:<16s} {entry['label']:<10s} gap={entry['gap']:.4f}", file=sys.stderr)

    # 全局判断
    global_entry = next((e for e in self_log if e.get("dimension") == "_global"), None)
    if global_entry:
        print(f"\n  {'─' * 58}", file=sys.stderr)
        print(f"  {global_entry['judgement']}", file=sys.stderr)
        print(f"  {global_entry['observer_view']}", file=sys.stderr)

    log("", "", file=sys.stderr)
    log("═" * 62, "", file=sys.stderr)
    log("  二阶观察完成。", "OK", file=sys.stderr)


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="二阶控制论观察者 — 观察飞轮自身如何观察",
        epilog="SRI Second-Order Observer v1.0.0",
    )
    parser.add_argument(
        "--index",
        default=DEFAULT_INDEX_PATH,
        help=f"entities_index.json 路径 (默认: {DEFAULT_INDEX_PATH})",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="将观察结果写入 entities_index.json → meta.second_order",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅计算并输出，不写入文件",
    )
    args = parser.parse_args()

    # ── 互斥检查 ──
    if args.save and args.dry_run:
        log("--save 和 --dry-run 不可同时使用", "ERR")
        sys.exit(1)

    log(f"加载 entities_index.json: {args.index}", "INFO", file=sys.stderr)
    index = load_index(args.index)
    meta = index.get("meta", {})

    log("构建 6 维观察空间...", "INFO", file=sys.stderr)
    observation_space = build_observation_space(meta)

    log("计算观察偏差...", "INFO", file=sys.stderr)
    observer_bias = compute_observer_bias(meta, observation_space)

    log("生成自指涉日志...", "INFO", file=sys.stderr)
    self_log = build_self_referential_log(meta, observation_space, observer_bias)

    log("判定二阶观察状态...", "INFO", file=sys.stderr)
    state = determine_state(observer_bias)

    # ── 汇总二阶观察结果 ──
    second_order = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "state": state,
        "observation_space": {
            dim: {
                "value": obs["value"],
                "range": obs["range"],
                "unit": obs["unit"],
                "label": obs["label"],
            }
            for dim, obs in observation_space.items()
        },
        "observer_bias": {
            "avg_bias": observer_bias["avg_bias"],
            "max_bias": observer_bias["max_bias"],
            "dimensions_compared": observer_bias["dimensions_compared"],
            "distorted_dimensions": observer_bias["distorted_dimensions"],
            "overall_distorted": observer_bias["overall_distorted"],
            "threshold": observer_bias["threshold"],
            "comparisons": observer_bias["comparisons"],
        },
        "self_referential_log": self_log,
    }

    # ── 输出 ──
    print_report(observation_space, observer_bias, self_log, state)

    if args.save:
        save_index(args.index, second_order)
        log("", "", file=sys.stderr)
        log(f"二阶观察已保存: meta.second_order (state={state})", "OK", file=sys.stderr)
    elif args.dry_run:
        log("", "", file=sys.stderr)
        log(f"[DRY-RUN] 未写入文件 (state={state})", "WARN", file=sys.stderr)
    else:
        # 默认行为: 打印 JSON 到 stdout
        print(json.dumps(second_order, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
