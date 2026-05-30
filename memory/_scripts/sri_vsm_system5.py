#!/usr/bin/env python3
"""
SRI VSM System 5 — 策略/身份层治理审计
==========================================
Viable System Model (VSM) 的第五层：身份与策略审计。

从 entities_index.json 读取 meta.orchestration_health 与其他策略元数据，
生成 identity 审计、政策违规扫描、治理健康分。

用法:
    python sri_vsm_system5.py [--dry-run | --save] [--index PATH]
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── 常量 ────────────────────────────────────────────────
_CORE_ENTITY_KEYS = [
    "products",
    "customers",
    "connections",
    "customer_profiles",
    "tasks",
    "decisions",
    "living_rules",
    "documents",
    "workflows",
    "events",
]

# 哪些域被视作「必须有数」的核心域
_REQUIRED_DOMAINS = [
    "products",
    "customers",
    "connections",
    "customer_profiles",
    "tasks",
    "decisions",
    "living_rules",
]

# 超过此天数未更新 → 视为过期实体
_STALE_THRESHOLD_DAYS = 7

# 治理健康分权重
_WEIGHT_IDENTITY = 0.35
_WEIGHT_FRESHNESS = 0.25
_WEIGHT_COVERAGE = 0.25
_WEIGHT_FLOWS = 0.15

# ── CLI ──────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="VSM System 5 — 身份/策略层治理审计")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="仅输出审计结果，不写回文件")
    mode.add_argument("--save", action="store_true", help="审计后写回 entities_index.json")
    parser.add_argument("--index", type=str, default=None,
                        help="entities_index.json 路径 (默认自动探测)")
    return parser.parse_args()


def discover_index(script_dir: Path) -> Path:
    """自动探测 entities_index.json 位置"""
    candidates = [
        Path.cwd() / "entities_index.json",
        script_dir.parent.parent / "entities_index.json",
        script_dir.parent / "_data" / "entities_index.json",
        script_dir.parent.parent / "_data" / "entities_index.json",
    ]
    for cand in candidates:
        if cand.exists():
            return cand
    # 兜底：直接用 memory/_data/
    fallback = script_dir.parent.parent / "_data" / "entities_index.json"
    return fallback


# ── 数据加载 ────────────────────────────────────────────
def load_index(path: Path) -> dict:
    """加载 entities_index.json"""
    print(f"📂 加载索引: {path}")
    if not path.exists():
        print(f"❌ 文件不存在: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ── 审计: 身份完整性 ───────────────────────────────────
def audit_identity(data: dict) -> dict:
    """
    检查核心实体数是否完整。
    从 meta.breakdown 中读取各实体计数，计算完整性得分。
    """
    meta = data.get("meta", {})
    breakdown = meta.get("breakdown", {})

    audit = {}
    total_present = 0
    total_core = len(_CORE_ENTITY_KEYS)

    for key in _CORE_ENTITY_KEYS:
        count = breakdown.get(key, 0)
        audit[key] = count
        if count > 0:
            total_present += 1

    # 总体得分：核心实体有数的比例 × 100
    identity_score = int((total_present / total_core) * 100) if total_core > 0 else 0

    # 关键域检查
    missing_required = [k for k in _REQUIRED_DOMAINS if breakdown.get(k, 0) == 0]

    audit["score"] = identity_score
    if missing_required:
        audit["missing_required"] = missing_required

    return audit


# ── 审计: 政策违规 ──────────────────────────────────────
def audit_policy_violations(data: dict) -> list:
    """
    扫描政策违规：
    - stale_entity: 超过 N 天未更新的实体
    - zero_coverage: 覆盖率为 0 的域
    - orphan_entities: 孤儿实体 (meta.anti_island 中的检查)
    """
    violations = []
    meta = data.get("meta", {})
    now = datetime.now(timezone.utc)

    # 1. 过期实体：检查 meta.updated 是否超过了阈值
    updated_str = meta.get("updated")
    if updated_str:
        try:
            # 处理多种 ISO 格式
            updated_str_clean = updated_str.replace("+08:00", "+0800")
            if "T" in updated_str_clean:
                updated_dt = datetime.fromisoformat(updated_str_clean)
                if updated_dt.tzinfo is None:
                    updated_dt = updated_dt.replace(tzinfo=timezone.utc)
                days_since = (now - updated_dt).days
                if days_since > _STALE_THRESHOLD_DAYS:
                    violations.append({
                        "type": "stale_entity",
                        "entity": "entities_index.json (meta.updated)",
                        "days": days_since,
                        "detail": f"整体索引超过 {days_since} 天未更新 (阈值: {_STALE_THRESHOLD_DAYS} 天)"
                    })
        except (ValueError, TypeError):
            pass

    # 2. 覆盖率为 0 的域
    breakdown = meta.get("breakdown", {})
    for domain in _CORE_ENTITY_KEYS:
        count = breakdown.get(domain, -1)
        if count == 0:
            violations.append({
                "type": "zero_coverage",
                "entity": domain,
                "days": 0,
                "detail": f"域 '{domain}' 实体数为 0，覆盖缺失"
            })

    # 3. 孤岛检查
    anti_island = meta.get("anti_island", {})
    if anti_island.get("orphan_products", 0) > 0:
        violations.append({
            "type": "orphan_entities",
            "entity": "products",
            "count": anti_island["orphan_products"],
            "detail": f"{anti_island['orphan_products']} 个孤儿产品"
        })
    if anti_island.get("dead_links", 0) > 0:
        violations.append({
            "type": "dead_links",
            "entity": "connections",
            "count": anti_island["dead_links"],
            "detail": f"{anti_island['dead_links']} 个死链"
        })
    if anti_island.get("zombie_tasks", 0) > 0:
        violations.append({
            "type": "zombie_tasks",
            "entity": "tasks",
            "count": anti_island["zombie_tasks"],
            "detail": f"{anti_island['zombie_tasks']} 个僵尸任务"
        })

    # 4. living_rules 状态违规
    lr_status = meta.get("living_rules_status", {})
    if lr_status.get("broken", 0) > 0:
        violations.append({
            "type": "broken_rules",
            "entity": "living_rules",
            "count": lr_status["broken"],
            "detail": f"{lr_status['broken']} 条生物规则已断裂"
        })

    # 5. flywheel 告警
    flywheel = meta.get("flywheel", {})
    flywheel_alerts = flywheel.get("alerts", [])
    for alert in flywheel_alerts:
        if alert.get("severity") == "error":
            violations.append({
                "type": "flywheel_error",
                "entity": alert.get("type", "unknown"),
                "detail": alert.get("detail", "")
            })

    # 6. content_assets 覆盖率为0 (特殊关注)
    content_assets = breakdown.get("content_assets", -1)
    if content_assets == 0:
        violations.append({
            "type": "zero_coverage",
            "entity": "content_assets",
            "days": 0,
            "detail": "内容资产 (content_assets) 覆盖率为 0"
        })

    return violations


# ── 审计: 治理健康分 ────────────────────────────────────
def audit_governance_pulse(data: dict, identity_audit: dict, violations: list) -> int:
    """
    计算治理健康分 (0-100)。

    维度:
    - 身份完整性 (35%): identity_audit.score
    - 新鲜度 (25%): 是否有过期实体
    - 覆盖率 (25%): 零覆盖域的比例
    - 流模型 (15%): flow_model 层激活情况
    """
    meta = data.get("meta", {})

    # 1. 身份完整性分
    identity_score = identity_audit.get("score", 0)

    # 2. 新鲜度分: 每有一个过期违规扣分
    stale_violations = [v for v in violations if v.get("type") == "stale_entity"]
    freshness_penalty = min(len(stale_violations) * 15, 50)
    freshness_score = max(100 - freshness_penalty, 0)

    # 3. 覆盖率分: 零覆盖域越多扣分越多
    zero_cov = [v for v in violations if v.get("type") == "zero_coverage"]
    coverage_penalty = min(len(zero_cov) * 20, 60)
    coverage_score = max(100 - coverage_penalty, 0)

    # 4. 流模型分: 基于 flow_model 层激活
    flow_model = meta.get("flow_model", {})
    layers_activated = flow_model.get("layers_activated", 0)
    flow_complete = flow_model.get("complete_chain_verified", False)
    if flow_complete and layers_activated >= 5:
        flow_score = 100
    elif layers_activated >= 4:
        flow_score = 80
    elif layers_activated >= 3:
        flow_score = 60
    elif layers_activated >= 2:
        flow_score = 40
    elif layers_activated >= 1:
        flow_score = 20
    else:
        flow_score = 0

    # 加权汇总
    pulse = int(
        identity_score * _WEIGHT_IDENTITY
        + freshness_score * _WEIGHT_FRESHNESS
        + coverage_score * _WEIGHT_COVERAGE
        + flow_score * _WEIGHT_FLOWS
    )
    pulse = max(min(pulse, 100), 0)
    return pulse


# ── 状态摘要 ────────────────────────────────────────────
def determine_vsm_state(violations: list, governance_pulse: int) -> str:
    """根据违规数和健康分判定状态"""
    critical_types = {"orphan_entities", "dead_links", "flywheel_error"}
    warning_types = {"stale_entity", "zero_coverage", "broken_rules", "zombie_tasks"}

    has_critical = any(v.get("type") in critical_types for v in violations)
    has_warning = any(v.get("type") in warning_types for v in violations)

    if governance_pulse >= 90 and not has_critical:
        return "✅ 健康"
    elif governance_pulse >= 70:
        return "⚠️ 警告"
    elif governance_pulse >= 40:
        return "🔶 注意"
    else:
        return "🔴 严重"


# ── 主审计逻辑 ──────────────────────────────────────────
def run_audit(data: dict) -> dict:
    """执行完整审计，返回结果字典"""
    print("🔍 VSM System 5 审计中...\n")

    # 1. 身份完整性审计
    print("  [1/3] 身份完整性审计...")
    identity_audit = audit_identity(data)
    print(f"        products={identity_audit.get('products', '?')}, "
          f"customers={identity_audit.get('customers', '?')}, "
          f"connections={identity_audit.get('connections', '?')}, "
          f"score={identity_audit['score']}")
    if "missing_required" in identity_audit:
        print(f"        ⚠️ 核心域缺失: {', '.join(identity_audit['missing_required'])}")

    # 2. 政策违规扫描
    print("  [2/3] 政策违规扫描...")
    violations = audit_policy_violations(data)
    if violations:
        print(f"        发现 {len(violations)} 条违规:")
        for v in violations:
            icon = "🔴" if v.get("type") in ("orphan_entities", "dead_links", "flywheel_error") else "🟡"
            print(f"        {icon} [{v['type']}] {v.get('entity', '?')} → {v.get('detail', v.get('days', '?'))}")
    else:
        print("        ✅ 无违规")

    # 3. 治理健康分
    print("  [3/3] 治理健康分...")
    governance_pulse = audit_governance_pulse(data, identity_audit, violations)
    print(f"        pulse={governance_pulse}/100")

    # 状态判定
    vsm_state = determine_vsm_state(violations, governance_pulse)
    print(f"\n  📊 状态: {vsm_state}")

    # 组装结果
    now_iso = datetime.now(timezone.utc).isoformat()
    result = {
        "vsm_state": vsm_state,
        "identity_audit": identity_audit,
        "policy_violations": violations,
        "governance_pulse": governance_pulse,
        "timestamp": now_iso,
    }
    return result


# ── 输出格式化 ──────────────────────────────────────────
def print_report(result: dict):
    """打印格式化的审计报告"""
    state = result["vsm_state"]
    pulse = result["governance_pulse"]
    identity = result["identity_audit"]
    violations = result["policy_violations"]

    print("\n" + "=" * 60)
    print("  🏛️  VSM SYSTEM 5 — 治理审计报告")
    print("=" * 60)

    # 状态横幅
    state_colors = {
        "✅ 健康": "🟢",
        "⚠️ 警告": "🟡",
        "🔶 注意": "🟠",
        "🔴 严重": "🔴",
    }
    prefix = state_colors.get(state, "⚪")
    print(f"\n  {prefix} 系统状态: {state}")
    print(f"  📊 治理健康分: {pulse}/100")
    print(f"  🕐 审计时间: {result['timestamp']}")

    # 身份审计
    print(f"\n  ── 身份完整性 ──")
    print(f"  得分: {identity.get('score', '?')}/100")
    for key in _CORE_ENTITY_KEYS:
        val = identity.get(key, "?")
        icon = "✅" if val and val > 0 else "❌"
        print(f"    {icon} {key}: {val}")
    if "missing_required" in identity:
        print(f"  ⚠️ 核心域缺失: {', '.join(identity['missing_required'])}")

    # 违规
    print(f"\n  ── 政策违规 ({len(violations)}) ──")
    if violations:
        for i, v in enumerate(violations, 1):
            print(f"    {i}. [{v['type']}] {v.get('entity', '?')} — {v.get('detail', v.get('days', '?'))}")
    else:
        print("    ✅ 无违规")

    # 评分计算说明
    print(f"\n  ── 评分计算 ──")
    print(f"    身份完整性 ({int(_WEIGHT_IDENTITY*100)}%): {identity.get('score', 0)}")
    print(f"    新鲜度     ({int(_WEIGHT_FRESHNESS*100)}%): 基于过期实体数")
    print(f"    覆盖率     ({int(_WEIGHT_COVERAGE*100)}%): 基于零覆盖域数")
    print(f"    流模型     ({int(_WEIGHT_FLOWS*100)}%): 基于层激活")
    print(f"    总计 = {pulse}/100")

    print("\n" + "=" * 60)
    print("  审计完成。\n")


# ── 写回 ────────────────────────────────────────────────
def save_result(path: Path, data: dict, result: dict):
    """将审计结果写入 entities_index.json → meta.vsm_system5"""
    print(f"💾 写回审计结果到 {path} ...")

    # 写入 vsm_system5 字段
    if "meta" not in data:
        data["meta"] = {}
    data["meta"]["vsm_system5"] = result

    # 同时更新时间戳
    data["meta"]["updated"] = datetime.now(timezone(timedelta(hours=8))).strftime(
        "%Y-%m-%dT%H:%M:%S+08:00"
    )

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print("   ✅ 写入完成")


# ── 入口 ────────────────────────────────────────────────
def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent

    # 确定索引文件路径
    if args.index:
        index_path = Path(args.index)
    else:
        index_path = discover_index(script_dir)

    # 加载数据
    data = load_index(index_path)

    # 执行审计
    result = run_audit(data)

    # 打印报告
    print_report(result)

    # 保存
    if args.save:
        save_result(index_path, data, result)
    else:
        print("🔍 --dry-run: 以上结果未写入 entities_index.json")

    # 返回码
    pulse = result["governance_pulse"]
    if pulse < 40:
        sys.exit(2)  # 严重
    elif pulse < 70:
        sys.exit(1)  # 警告
    else:
        sys.exit(0)  # 健康


if __name__ == "__main__":
    main()
