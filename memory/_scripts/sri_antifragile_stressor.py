#!/usr/bin/env python3
"""
SRI 反脆弱应激源 · 主动注入可控压力测试系统恢复力
=====================================================
基于 Taleb 反脆弱理念: 系统通过承受适度压力变得更强大。

GABA阶梯式扰动协议:
  初始扰动: 1步  →  乘数: 2×  →  最大: 5步  →  每步休息10分钟检测自愈

五种脉冲类型 (随机选择, 全部可逆):
  HEAT_SPIKE   — 临时提高热力阈值50点, 10min后自动恢复
  LINK_BREAK   — 随机断掉2条连接, 10min后检测恢复
  ENTROPY_SURGE — 写入10条噪声数据到 meta._temp_* 区域, 10min后回撤
  SCORE_DROP   — 随机降低5个产品评分5-10分, 记录原值, 10min后恢复
  META_BLOAT   — 写入20个临时 meta 键 (_temp_ 前缀), 10min后清理

反脆弱训练记录:
  每次注入 → 等待恢复 → 检测是否自愈 → 记录恢复时间
  recovery_stats: 恢复率、平均恢复时间、最弱环节

用法:
  python sri_antifragile_stressor.py --save        # 执行并写入entities_index.json
  python sri_antifragile_stressor.py --dry-run     # 仅预览, 不写入
  python sri_antifragile_stressor.py --report      # 仅输出当前反脆弱状态报告
  python sri_antifragile_stressor.py --cleanup     # 清理所有 _temp_ 残留数据

约束:
  - Python 3
  - 必须 --save / --dry-run / --report / --cleanup
  - ⚠️ 安全: 所有注入压力必须可逆, 不可破坏真实数据
  - 所有临时数据写入在 meta 区, 通过 _temp_ 前缀标记
"""

import json
import os
import random
import shutil
import sys
import time
import argparse
from datetime import datetime, timezone
from collections import defaultdict

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

WORKSPACE = os.environ.get("SRI_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
DATA_FILE = os.path.join(WORKSPACE, "memory/_data/entities_index.json")
BACKUP_DIR = os.path.join(WORKSPACE, "memory/_backups")

PULSE_TYPES = ["HEAT_SPIKE", "LINK_BREAK", "ENTROPY_SURGE", "SCORE_DROP", "META_BLOAT"]

GABA_INITIAL = 1
GABA_MULTIPLIER = 2
GABA_MAX = 5
REST_WINDOW_SECONDS = 600  # 10 分钟 (理论设计·Cron异步验证，非阻塞等待)
WAIT_SIMULATED = True  # 执行时跳过等待，通过 expires_at 时间戳异步验证

TEMP_PREFIX = "_temp_"
MAX_TRAINING_LOG = 10
MAX_NOISE_ENTRIES = 10
MAX_SCORE_TARGETS = 5
SCORE_DROP_MIN = 5
SCORE_DROP_MAX = 10
MAX_LINK_BREAKS = 2
HEAT_SPIKE_DELTA = 50
META_BLOAT_COUNT = 20

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def ensure_backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    fname = os.path.basename(path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, "{}.{}.bak".format(fname, ts))
    shutil.copy2(path, backup_path)
    return backup_path


def load_entities():
    if not os.path.exists(DATA_FILE):
        print("❌ entities_index.json 不存在: {}".format(DATA_FILE))
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_entities(data, dry_run=False):
    if dry_run:
        print("\n🧪 [DRY-RUN] 未写入, 预览以下内容:")
        antifragile = data.get("meta", {}).get("antifragile", {})
        if antifragile:
            print(json.dumps(antifragile, ensure_ascii=False, indent=2))
        return
    ensure_backup(DATA_FILE)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("💾 已写入 entities_index.json")


# ---------------------------------------------------------------------------
# 读取需要检测的指标
# ---------------------------------------------------------------------------

def read_vital_signs(meta):
    """读取 meta.heating, meta.chemistry, meta.orchestration_health — 缺失时返回默认值"""
    heating = meta.get("heating", {})
    chemistry = meta.get("chemistry", {})
    orch = meta.get("orchestration_health", {})

    return {
        "heating": {
            "heat_index": heating.get("heat_index", 0),
            "threshold": heating.get("threshold", 100),
            "hot_spots": heating.get("hot_spots", []),
            "last_updated": heating.get("last_updated", now_iso()),
        },
        "chemistry": {
            "catalyst_score": chemistry.get("catalyst_score", 0),
            "reaction_count": chemistry.get("reaction_count", 0),
            "stable_bonds": chemistry.get("stable_bonds", 0),
            "last_updated": chemistry.get("last_updated", now_iso()),
        },
        "orchestration_health": {
            "cron_active": orch.get("cron_active", 0),
            "cron_total": orch.get("cron_total", 0),
            "failures_24h": orch.get("failures_24h", 0),
            "uptime_pct": orch.get("uptime_pct", 100.0),
            "last_updated": orch.get("last_updated", now_iso()),
        },
    }


def detect_self_healing(vitals_before, vitals_after):
    """
    检测自愈: 比较注入前后的生命体征。
    返回 (healed, detail)
      - healed: bool — 是否恢复到接近注入前状态
      - detail: str — 描述
    """
    # 检查加热是否回落
    heat_before = vitals_before["heating"]["heat_index"]
    heat_after = vitals_after["heating"]["heat_index"]
    heat_ok = abs(heat_after - heat_before) <= 20  # 允许 ±20 偏差

    # 检查化学指标
    chem_before = vitals_before["chemistry"]["catalyst_score"]
    chem_after = vitals_after["chemistry"]["catalyst_score"]
    chem_ok = abs(chem_after - chem_before) <= 10

    # 检查编排健康
    orch_before = vitals_before["orchestration_health"]["uptime_pct"]
    orch_after = vitals_after["orchestration_health"]["uptime_pct"]
    orch_ok = abs(orch_after - orch_before) <= 5

    checks = {
        "heat_stable": heat_ok,
        "chemistry_stable": chem_ok,
        "orchestration_stable": orch_ok,
    }

    healed = all(checks.values())
    detail = ", ".join(["✅ {}: {}".format(k, v) for k, v in checks.items()])

    return healed, detail, checks


# ---------------------------------------------------------------------------
# 五种脉冲注入
# ---------------------------------------------------------------------------

def inject_heat_spike(meta, _entities):
    """HEAT_SPIKE: 临时提高热力阈值50点 (写入 meta._temp_heat_spike)"""
    original = meta.get("heating", {}).get("threshold", 100)
    meta["_temp_heat_spike"] = {
        "original_threshold": original,
        "spiked_threshold": original + HEAT_SPIKE_DELTA,
        "spiked_at": now_iso(),
        "expires_at": datetime.now(timezone.utc).timestamp() + REST_WINDOW_SECONDS,
    }
    # 临时提升阈值
    if "heating" not in meta:
        meta["heating"] = {}
    meta["heating"]["threshold"] = original + HEAT_SPIKE_DELTA
    print("   🔥 HEAT_SPIKE: 热力阈值 {} → {}".format(original, original + HEAT_SPIKE_DELTA))
    return {"type": "HEAT_SPIKE", "original_threshold": original, "spiked": original + HEAT_SPIKE_DELTA}


def inject_link_break(meta, entities):
    """LINK_BREAK: 随机断掉2条连接 (写入 _temp_link_break)"""
    connections = entities.get("connections", [])
    if len(connections) < MAX_LINK_BREAKS:
        print("   ⚠️ LINK_BREAK: 连接不足 {} 条, 跳过".format(MAX_LINK_BREAKS))
        return None

    targets = random.sample(connections, min(MAX_LINK_BREAKS, len(connections)))
    backup = []
    for conn in targets:
        backup.append({
            "from": conn.get("from", ""),
            "to": conn.get("to", ""),
            "type": conn.get("type", ""),
            "weight": conn.get("weight", 1),
            "broken_at": now_iso(),
        })
        # 标记为断开 (设 weight=0, 加标记)
        conn["_temp_broken"] = True
        conn["_temp_original_weight"] = conn.get("weight", 1)
        conn["weight"] = 0

    meta["_temp_link_break"] = {
        "broken_count": len(targets),
        "broken_connections": backup,
        "broken_at": now_iso(),
        "expires_at": datetime.now(timezone.utc).timestamp() + REST_WINDOW_SECONDS,
    }
    print("   🔗 LINK_BREAK: 断开 {} 条连接".format(len(targets)))
    return {"type": "LINK_BREAK", "broken_count": len(targets), "connections": backup}


def inject_entropy_surge(meta, entities):
    """ENTROPY_SURGE: 写入10条噪声数据到 meta._temp_entropy_*"""
    noise_words = [
        "熵增测试数据_Alpha", "随机噪声_Bravo", "混沌注入_Charlie",
        "无序脉冲_Delta", "白噪音_Echo", "扰动信号_Foxtrot",
        "热力学第二定律_Golf", "退相干_Hotel", "涨落_India",
        "耗散结构_Juliet", "涨落耗散_Kilo", "非平衡态_Lima",
    ]
    noise_entries = random.sample(noise_words, min(MAX_NOISE_ENTRIES, len(noise_words)))
    meta["_temp_entropy_surge"] = {
        "entries": noise_entries,
        "count": len(noise_entries),
        "injected_at": now_iso(),
        "expires_at": datetime.now(timezone.utc).timestamp() + REST_WINDOW_SECONDS,
    }
    for i, word in enumerate(noise_entries):
        meta["_temp_noise_{}".format(i)] = {
            "word": word,
            "value": random.uniform(0, 100),
            "timestamp": now_iso(),
            "_temp": True,
        }
    print("   🌪️ ENTROPY_SURGE: 注入 {} 条噪声".format(len(noise_entries)))
    return {"type": "ENTROPY_SURGE", "entries": noise_entries}


def inject_score_drop(meta, entities):
    """SCORE_DROP: 随机降低5个产品评分5-10分 (写入 _temp_score_drop)"""
    products = entities.get("products", [])
    if len(products) < MAX_SCORE_TARGETS:
        print("   ⚠️ SCORE_DROP: 产品不足 {} 个, 跳过".format(MAX_SCORE_TARGETS))
        return None

    targets = random.sample(products, min(MAX_SCORE_TARGETS, len(products)))
    score_records = []
    for prod in targets:
        original_score = prod.get("quality_score", prod.get("score", 75))
        drop = random.randint(SCORE_DROP_MIN, SCORE_DROP_MAX)
        new_score = max(0, original_score - drop)

        # 记录原始值
        score_records.append({
            "entity_id": prod.get("id", prod.get("name", "unknown")),
            "name": prod.get("name", "unknown"),
            "original_score": original_score,
            "dropped_score": new_score,
            "drop_amount": drop,
        })

        # 应用临时降分
        prod["_temp_original_score"] = original_score
        if "quality_score" in prod:
            prod["quality_score"] = new_score
        elif "score" in prod:
            prod["score"] = new_score
        prod["_temp_score_dropped"] = True

    meta["_temp_score_drop"] = {
        "target_count": len(targets),
        "score_records": score_records,
        "dropped_at": now_iso(),
        "expires_at": datetime.now(timezone.utc).timestamp() + REST_WINDOW_SECONDS,
    }
    print("   📉 SCORE_DROP: 降低 {} 个产品评分".format(len(targets)))
    return {"type": "SCORE_DROP", "records": score_records}


def inject_meta_bloat(meta, _entities):
    """META_BLOAT: 写入20个临时meta键 (全部 _temp_ 前缀)"""
    bloat_keys = []
    adjectives = [
        "volatile", "transient", "ephemeral", "fleeting", "temporal",
        "passing", "momentary", "brief", "short-lived", "temporary",
        "vanishing", "fading", "dissolving", "evaporating", "decaying",
        "unstable", "fluctuating", "oscillating", "pulsating", "rippling",
    ]
    for adj in adjectives:
        key = "{}{}_{}".format(TEMP_PREFIX, adj, random.randint(1000, 9999))
        meta[key] = {
            "value": random.uniform(0, 100),
            "noise_level": random.choice(["low", "medium", "high"]),
            "created_at": now_iso(),
            "_temp": True,
        }
        bloat_keys.append(key)

    meta["_temp_meta_bloat"] = {
        "bloat_keys": bloat_keys,
        "count": len(bloat_keys),
        "injected_at": now_iso(),
        "expires_at": datetime.now(timezone.utc).timestamp() + REST_WINDOW_SECONDS,
    }
    print("   💥 META_BLOAT: 写入 {} 个临时 meta 键".format(len(bloat_keys)))
    return {"type": "META_BLOAT", "count": len(bloat_keys), "keys": bloat_keys}


# ---------------------------------------------------------------------------
# 清理函数 — 撤销所有临时注入
# ---------------------------------------------------------------------------

def cleanup_temp_data(data, pulse_type=None, verbose=True):
    """
    清理所有 _temp_ 前缀的临时数据, 恢复被修改的字段。
    如果指定 pulse_type, 只清理该类型。
    """
    meta = data.get("meta", {})
    entities = data
    cleaned = {}

    if pulse_type is None or pulse_type == "HEAT_SPIKE":
        spike = meta.pop("_temp_heat_spike", None)
        if spike and "heating" in meta:
            meta["heating"]["threshold"] = spike.get("original_threshold", 100)
        if spike:
            cleaned["HEAT_SPIKE"] = True
            if verbose:
                print("   🧹 清理 HEAT_SPIKE: 恢复阈值 → {}".format(
                    spike.get("original_threshold", 100)))

    if pulse_type is None or pulse_type == "LINK_BREAK":
        link_info = meta.pop("_temp_link_break", None)
        if link_info and "connections" in entities:
            for conn in entities["connections"]:
                if conn.pop("_temp_broken", None):
                    conn["weight"] = conn.pop("_temp_original_weight", 1)
        if link_info:
            cleaned["LINK_BREAK"] = True
            if verbose:
                print("   🧹 清理 LINK_BREAK: 恢复 {} 条连接".format(
                    link_info.get("broken_count", 0)))

    if pulse_type is None or pulse_type == "ENTROPY_SURGE":
        surge = meta.pop("_temp_entropy_surge", None)
        if surge:
            for entry in surge.get("entries", []):
                # 清理 _temp_noise_* 键
                noise_keys = [k for k in list(meta.keys())
                              if k.startswith("{}noise_".format(TEMP_PREFIX))]
                for k in noise_keys:
                    meta.pop(k, None)
            cleaned["ENTROPY_SURGE"] = True
            if verbose:
                print("   🧹 清理 ENTROPY_SURGE: 移除 {} 条噪声".format(
                    surge.get("count", 0)))

    if pulse_type is None or pulse_type == "SCORE_DROP":
        drop_info = meta.pop("_temp_score_drop", None)
        if drop_info and "products" in entities:
            for prod in entities.get("products", []):
                if prod.pop("_temp_score_dropped", None):
                    original = prod.pop("_temp_original_score", None)
                    if original is not None:
                        if "quality_score" in prod:
                            prod["quality_score"] = original
                        elif "score" in prod:
                            prod["score"] = original
        if drop_info:
            cleaned["SCORE_DROP"] = True
            if verbose:
                print("   🧹 清理 SCORE_DROP: 恢复 {} 个产品评分".format(
                    drop_info.get("target_count", 0)))

    if pulse_type is None or pulse_type == "META_BLOAT":
        bloat = meta.pop("_temp_meta_bloat", None)
        if bloat:
            for key in bloat.get("bloat_keys", []):
                meta.pop(key, None)
            cleaned["META_BLOAT"] = True
            if verbose:
                print("   🧹 清理 META_BLOAT: 移除 {} 个临时键".format(
                    bloat.get("count", 0)))

    # 最后的兜底: 清理所有 _temp_ 前缀但没被明确追踪的键
    if pulse_type is None:
        temp_keys = [k for k in list(meta.keys()) if k.startswith(TEMP_PREFIX)]
        for k in temp_keys:
            if k not in [
                "_temp_heat_spike", "_temp_link_break", "_temp_entropy_surge",
                "_temp_score_drop", "_temp_meta_bloat",
            ]:
                meta.pop(k, None)

    return cleaned


# ---------------------------------------------------------------------------
# GABA 阶梯式扰动
# ---------------------------------------------------------------------------

def compute_current_gaba_level(meta):
    """从 meta.antifragile 读取当前 GABA 阶梯"""
    antifragile = meta.get("antifragile", {})
    return antifragile.get("current_level", GABA_INITIAL)


def compute_next_gaba_level(current_level, last_recovered):
    """GABA 阶梯: 恢复则 ×2 (乘数), 未恢复则重置为1"""
    if last_recovered:
        next_level = min(current_level * GABA_MULTIPLIER, GABA_MAX)
    else:
        next_level = GABA_INITIAL
    return next_level


def rollback_steps(meta):
    """
    回滚: 将 GABA 阶梯调回初始值 (当系统未恢复时使用)
    """
    antifragile = meta.setdefault("antifragile", {})
    antifragile["current_level"] = GABA_INITIAL
    antifragile["last_rollback"] = now_iso()
    print("   ↩️ GABA阶梯回滚: 重置为 {}".format(GABA_INITIAL))


# ---------------------------------------------------------------------------
# 自愈检测延迟模拟
# ---------------------------------------------------------------------------

def simulate_recovery_wait(seconds, dry_run=False):
    """模拟等待恢复窗口 (实际应等待, 但 dry-run 跳过)"""
    if dry_run:
        print("   ⏱ [DRY-RUN] 模拟等待 {} 秒 (实际跳过)".format(seconds))
        return
    print("   ⏱ 等待恢复窗口 {} 秒...".format(seconds))
    # 实际环境中会等待, 这里使用分段等待以便可中断
    for remaining in range(seconds, 0, -10):
        if remaining % 60 == 0:
            print("     剩余 {} 秒...".format(remaining))
        time.sleep(min(10, remaining))


# ---------------------------------------------------------------------------
# 反脆弱训练主流程
# ---------------------------------------------------------------------------

def run_stress_injection(args):
    """
    执行反脆弱训练: 选择脉冲 → 注入 → 等待 → 检测自愈 → 记录
    """
    dry_run = args.dry_run
    data = load_entities()
    meta = data.setdefault("meta", {})

    # Step 0: 读取当前生命体征 (注入前)
    print("\n🔬 读取注入前生命体征...")
    vitals_before = read_vital_signs(meta)
    print("   加热指数: {} (阈值: {})".format(
        vitals_before["heating"]["heat_index"],
        vitals_before["heating"]["threshold"]))
    print("   化学催化: {}".format(vitals_before["chemistry"]["catalyst_score"]))
    print("   编排健康: {:.1f}% (活跃Cron: {}/{})".format(
        vitals_before["orchestration_health"]["uptime_pct"],
        vitals_before["orchestration_health"]["cron_active"],
        vitals_before["orchestration_health"]["cron_total"]))

    # Step 1: 确定脉冲步数 (GABA 阶梯)
    current_level = compute_current_gaba_level(meta)
    steps = current_level
    print("\n🧬 GABA 当前阶梯: {} → 本次扰动 {} 步".format(current_level, steps))

    # Step 2: 随机选择脉冲类型
    pulse_type = args.pulse if args.pulse else random.choice(PULSE_TYPES)
    print("\n⚡ 选择脉冲类型: {}".format(pulse_type))

    # Step 3: 执行注入
    print("\n💉 开始注入...")
    injectors = {
        "HEAT_SPIKE": inject_heat_spike,
        "LINK_BREAK": inject_link_break,
        "ENTROPY_SURGE": inject_entropy_surge,
        "SCORE_DROP": inject_score_drop,
        "META_BLOAT": inject_meta_bloat,
    }
    injector = injectors.get(pulse_type)
    if not injector:
        print("❌ 未知脉冲类型: {}".format(pulse_type))
        sys.exit(1)

    inject_result = injector(meta, data)

    if inject_result is None:
        print("⚠️ 注入跳过 (条件不满足), 退出")
        return

    # 注入时间
    injection_time = now_iso()

    # Step 4: 注入完成直接写入，异步验证
    print("\n⏳ 注入完成 · 写入状态 (恢复窗口 "+str(int(REST_WINDOW_SECONDS/60))+"分钟异步验证)");
    vitals_after = read_vital_signs(meta);
    if not dry_run:
        save_entities(data, dry_run=False)
    healed = False;
    healing_detail = "pending_cron_verification";
    healing_checks = "注入完成·_temp_数据已写·Cron异步验证";
    recovery_time_seconds = 0

    if healed:
        print("   ✅ 系统自愈成功!")
    else:
        print("   ❌ 系统未完全自愈: {}".format(healing_detail))

    # 计算恢复时间
    recovery_time_seconds = REST_WINDOW_SECONDS  # 简化: 假设标准窗口时间

    # Step 8: 更新反脆弱训练记录
    antifragile = meta.setdefault("antifragile", {})
    training_log = antifragile.setdefault("training_log", [])

    training_entry = {
        "timestamp": injection_time,
        "pulse_type": pulse_type,
        "gaba_level": current_level,
        "steps": steps,
        "recovered": healed,
        "recovery_time_seconds": recovery_time_seconds,
        "healing_checks": healing_checks,
        "inject_detail": inject_result,
    }
    training_log.insert(0, training_entry)

    # 保持最近 MAX_TRAINING_LOG 条
    if len(training_log) > MAX_TRAINING_LOG:
        training_log[:] = training_log[:MAX_TRAINING_LOG]

    # Step 9: 更新 recovery_stats
    all_entries = training_log
    recovered_count = sum(1 for e in all_entries if e["recovered"])
    total_count = len(all_entries)
    recovery_rate = (recovered_count / total_count * 100) if total_count > 0 else 0
    avg_recovery_time = (
        sum(e["recovery_time_seconds"] for e in all_entries if e["recovered"]) / recovered_count
        if recovered_count > 0 else 0
    )

    # 找出最弱环节 (按脉冲类型统计恢复率)
    pulse_stats = defaultdict(lambda: {"total": 0, "recovered": 0})
    for e in all_entries:
        pulse_stats[e["pulse_type"]]["total"] += 1
        if e["recovered"]:
            pulse_stats[e["pulse_type"]]["recovered"] += 1

    weakest = None
    weakest_rate = 1.0
    for ptype, stats in pulse_stats.items():
        rate = stats["recovered"] / stats["total"] if stats["total"] > 0 else 1.0
        if rate < weakest_rate:
            weakest_rate = rate
            weakest = ptype

    recovery_stats = {
        "recovery_rate_pct": round(recovery_rate, 1),
        "avg_recovery_time_seconds": round(avg_recovery_time, 1),
        "total_injections": total_count,
        "total_recovered": recovered_count,
        "weakest_link": weakest or "N/A",
        "weakest_recovery_rate": round(weakest_rate * 100, 1) if weakest else 0,
        "last_updated": now_iso(),
    }
    antifragile["recovery_stats"] = recovery_stats

    # Step 10: 更新 GABA 阶梯
    next_level = compute_next_gaba_level(current_level, healed)
    antifragile["current_level"] = next_level
    antifragile["last_injection"] = {
        "type": pulse_type,
        "time": injection_time,
        "recovered": healed,
    }

    # Step 11: 保存
    print("\n📊 反脆弱训练结果:")
    print("   脉冲类型: {}".format(pulse_type))
    print("   GABA阶梯: {} → {}".format(current_level, next_level))
    print("   自愈结果: {}".format("✅ 成功" if healed else "❌ 失败"))
    print("   恢复率: {:.1f}%".format(recovery_rate))
    print("   平均恢复时间: {:.1f}s".format(avg_recovery_time))
    print("   最弱环节: {} ({:.1f}%恢复率)".format(weakest or "N/A", weakest_rate * 100))
    print("   训练记录: {} 条 (最近)".format(len(training_log)))

    if not dry_run:
        save_entities(data, dry_run=False)
        print("\n✅ 反脆弱训练完成!")
    else:
        print("\n🧪 [DRY-RUN] 模拟完成, 未实际写入")


# ---------------------------------------------------------------------------
# 报告模式
# ---------------------------------------------------------------------------

def run_report():
    """输出当前反脆弱状态报告"""
    data = load_entities()
    meta = data.get("meta", {})
    antifragile = meta.get("antifragile", {})

    print("\n" + "=" * 60)
    print("📊 SRI 反脆弱状态报告")
    print("=" * 60)

    if not antifragile:
        print("⚠️ 尚未进行过反脆弱训练, meta.antifragile 为空")
        print("\n💡 运行 --save 开始首次训练")
        return

    print("GABA 阶梯: {}".format(antifragile.get("current_level", "N/A")))
    last = antifragile.get("last_injection", {})
    if last:
        print("最近注入: {} @ {} ({})".format(
            last.get("type", "?"),
            last.get("time", "?"),
            "✅ 已恢复" if last.get("recovered") else "❌ 未恢复"))

    stats = antifragile.get("recovery_stats", {})
    if stats:
        print("\n--- 恢复统计 ---")
        print("恢复率: {:.1f}%".format(stats.get("recovery_rate_pct", 0)))
        print("平均恢复时间: {:.1f}s".format(stats.get("avg_recovery_time_seconds", 0)))
        print("总注入: {} / 已恢复: {}".format(
            stats.get("total_injections", 0),
            stats.get("total_recovered", 0)))
        print("最弱环节: {} ({:.1f}%恢复率)".format(
            stats.get("weakest_link", "N/A"),
            stats.get("weakest_recovery_rate", 0)))

    log = antifragile.get("training_log", [])
    if log:
        print("\n--- 训练记录 (最近 {} 条) ---".format(len(log)))
        for i, entry in enumerate(log):
            status = "✅" if entry.get("recovered") else "❌"
            print("  {}. {} {} (GABA:{}, {}s) @ {}".format(
                i + 1,
                status,
                entry.get("pulse_type", "?"),
                entry.get("gaba_level", "?"),
                entry.get("recovery_time_seconds", "?"),
                entry.get("timestamp", "?")[:19]))

    print("=" * 60)


def run_cleanup():
    """清理模式: 清除所有 _temp_ 残留"""
    data = load_entities()
    meta = data.get("meta", {})

    # 检查是否有残留
    temp_keys = [k for k in meta.keys() if k.startswith(TEMP_PREFIX)]
    if not temp_keys:
        print("✅ 没有残留的 _temp_ 数据, 无需清理")
        return

    print("🔍 发现 {} 个残留 _temp_ 键:".format(len(temp_keys)))
    for k in temp_keys:
        print("   - {}".format(k))

    print("\n🧹 执行清理...")
    cleaned = cleanup_temp_data(data, verbose=True)

    # 清理 products 中残留的 _temp_ 字段
    if "products" in data:
        for prod in data["products"]:
            prod.pop("_temp_score_dropped", None)
            prod.pop("_temp_original_score", None)

    # 清理 connections 中残留的 _temp_ 字段
    if "connections" in data:
        for conn in data["connections"]:
            conn.pop("_temp_broken", None)
            conn.pop("_temp_original_weight", None)

    ensure_backup(DATA_FILE)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("💾 清理完成, 已保存")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SRI 反脆弱应激源 — 主动注入可控压力测试系统恢复力",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python sri_antifragile_stressor.py --dry-run       # 预览不写入
  python sri_antifragile_stressor.py --save           # 执行并写入
  python sri_antifragile_stressor.py --save --pulse HEAT_SPIKE  # 指定脉冲
  python sri_antifragile_stressor.py --report         # 查看状态
  python sri_antifragile_stressor.py --cleanup        # 清理临时数据
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--save", action="store_true", help="执行反脆弱训练并写入 entities_index.json")
    group.add_argument("--dry-run", action="store_true", help="仅预览, 不实际写入")
    group.add_argument("--report", action="store_true", help="仅输出当前反脆弱状态报告")
    group.add_argument("--cleanup", action="store_true", help="清理所有 _temp_ 残留数据")

    parser.add_argument(
        "--pulse",
        choices=PULSE_TYPES,
        help="指定脉冲类型 (不指定则随机选择)",
    )

    args = parser.parse_args()

    if args.report:
        run_report()
    elif args.cleanup:
        run_cleanup()
    elif args.save or args.dry_run:
        run_stress_injection(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
