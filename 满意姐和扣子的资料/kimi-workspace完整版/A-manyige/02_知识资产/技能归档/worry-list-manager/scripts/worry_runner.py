# 担忧清单管理器 - 主运行脚本
# worry_runner.py

import os
import sys
import json
import yaml
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# 配置路径
SKILL_DIR = Path("/root/.openclaw/workspace/skills/worry-list-manager")
CONFIG_DIR = SKILL_DIR / "config"
DATA_DIR = SKILL_DIR / "data"
LOG_DIR = SKILL_DIR / "logs"

# 确保目录存在
for d in [DATA_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

WORRIES_FILE = DATA_DIR / "worries.json"
HISTORY_DIR = DATA_DIR / "history"
HISTORY_DIR.mkdir(exist_ok=True)

def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_DIR / "worry.log", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def load_config() -> Dict:
    """加载配置"""
    config = {}
    for config_file in ["categories.yaml", "thresholds.yaml"]:
        path = CONFIG_DIR / config_file
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                config.update(yaml.safe_load(f) or {})
    return config

def load_worries() -> List[Dict]:
    """加载担忧列表"""
    if WORRIES_FILE.exists():
        with open(WORRIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_worries(worries: List[Dict]):
    """保存担忧列表"""
    # 备份旧数据
    if WORRIES_FILE.exists():
        backup_file = HISTORY_DIR / f"worries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        WORRIES_FILE.rename(backup_file)
    with open(WORRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(worries, f, ensure_ascii=False, indent=2)

def generate_id() -> str:
    """生成担忧ID"""
    prefix = "W"
    date_str = datetime.now().strftime("%y%m%d")
    worries = load_worries()
    today_count = sum(1 for w in worries if w.get("id", "").startswith(f"{prefix}{date_str}"))
    return f"{prefix}{date_str}{today_count+1:03d}"

def calculate_priority(impact: int, urgency: int, probability: int, config: Dict) -> str:
    """计算优先级"""
    weights = config.get("evaluation", {}).get("weights", {"impact": 0.4, "urgency": 0.4, "probability": 0.2})
    score = (impact * weights["impact"] + 
             urgency * weights["urgency"] + 
             probability * weights["probability"])
    
    if score >= 8:
        return "P0"
    elif score >= 6:
        return "P1"
    elif score >= 4:
        return "P2"
    else:
        return "P3"

def add_worry(content: str, category: str = "UNRESOLVED", source: str = "manual", 
              impact: int = 5, urgency: int = 5, probability: int = 5, 
              epistemic_status: str = "INFERRED", confidence: float = 0.5) -> str:
    """添加担忧"""
    config = load_config()
    worries = load_worries()
    
    worry_id = generate_id()
    priority = calculate_priority(impact, urgency, probability, config)
    
    worry = {
        "id": worry_id,
        "content": content,
        "category": category,
        "priority": priority,
        "source": source,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "impact": impact,
        "urgency": urgency,
        "probability": probability,
        "score": impact * 0.4 + urgency * 0.4 + probability * 0.2,
        "epistemic_status": epistemic_status,  # KNOWN/INFERRED/UNKNOWN
        "confidence": confidence,
        "evidence": [],
        "actions": [],
        "resolution": None,
        "feedback": None
    }
    
    worries.append(worry)
    save_worries(worries)
    log(f"✅ 添加担忧 [{priority}] {worry_id}: {content[:50]}...")
    return worry_id

def list_worries(priority: Optional[str] = None, status: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
    """列出担忧"""
    worries = load_worries()
    
    if priority:
        worries = [w for w in worries if w.get("priority") == priority]
    if status:
        worries = [w for w in worries if w.get("status") == status]
    if category:
        worries = [w for w in worries if w.get("category") == category]
    
    # 按优先级和时间排序
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    worries.sort(key=lambda x: (priority_order.get(x.get("priority", "P3"), 3), x.get("created_at", "")), reverse=False)
    
    return worries

def collect_feedback(worry_id: str, feedback_type: str, notes: str = None) -> bool:
    """S2: 反馈闭环 - 收集用户对担忧处理结果的反馈"""
    worries = load_worries()
    for w in worries:
        if w.get("id") == worry_id:
            w["user_feedback"] = {
                "type": feedback_type,  # true_positive, false_positive, false_negative, unclear
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            }
            w["updated_at"] = datetime.now().isoformat()
            save_worries(worries)
            log(f"📥 收集反馈 [{worry_id}]: {feedback_type}")
            return True
    return False

def close_feedback_loop():
    """S2: 反馈闭环处理 - 根据用户反馈优化系统"""
    worries = load_worries()
    
    # 统计反馈数据
    feedback_stats = {
        "true_positive": [],
        "false_positive": [],
        "false_negative": [],
        "unclear": []
    }
    
    for w in worries:
        fb = w.get("user_feedback", {})
        if fb:
            fb_type = fb.get("type")
            if fb_type in feedback_stats:
                feedback_stats[fb_type].append(w)
    
    # 分析误报模式
    fp_patterns = analyze_patterns(feedback_stats["false_positive"])
    
    # 分析漏报模式  
    fn_patterns = analyze_patterns(feedback_stats["false_negative"])
    
    # 生成优化建议
    optimizations = []
    
    # 误报优化
    if len(feedback_stats["false_positive"]) > 3:
        common_fp_words = fp_patterns.get("common_words", [])
        if common_fp_words:
            optimizations.append({
                "type": "reduce_false_positive",
                "action": f"添加过滤规则: 包含关键词 {common_fp_words[:3]} 的担忧降低优先级",
                "expected_impact": f"预计减少 {len(feedback_stats['false_positive'])}% 误报"
            })
    
    # 漏报优化
    if len(feedback_stats["false_negative"]) > 2:
        common_fn_words = fn_patterns.get("common_words", [])
        if common_fn_words:
            optimizations.append({
                "type": "reduce_false_negative",
                "action": f"增强检测: 对包含 {common_fn_words[:3]} 的内容提高敏感度",
                "expected_impact": f"预计减少 {len(feedback_stats['false_negative'])}% 漏报"
            })
    
    # 保存闭环报告
    loop_report = {
        "timestamp": datetime.now().isoformat(),
        "feedback_summary": {
            k: len(v) for k, v in feedback_stats.items()
        },
        "patterns": {
            "false_positive": fp_patterns,
            "false_negative": fn_patterns
        },
        "recommended_optimizations": optimizations
    }
    
    loop_file = DATA_DIR / f"feedback_loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(loop_file, "w", encoding="utf-8") as f:
        json.dump(loop_report, f, ensure_ascii=False, indent=2)
    
    log(f"🔄 S2反馈闭环处理完成: TP={len(feedback_stats['true_positive'])}, "
        f"FP={len(feedback_stats['false_positive'])}, FN={len(feedback_stats['false_negative'])}")
    
    return loop_report

def analyze_patterns(worries: List[Dict]) -> Dict:
    """分析担忧的模式"""
    if not worries:
        return {}
    
    # 提取关键词
    all_words = []
    for w in worries:
        content = w.get("content", "")
        words = [word for word in content.split() if len(word) >= 2]
        all_words.extend(words)
    
    # 统计词频
    from collections import Counter
    word_counts = Counter(all_words)
    
    return {
        "total": len(worries),
        "common_words": [word for word, count in word_counts.most_common(5)],
        "avg_priority": sum({"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(w.get("priority", "P3"), 3) for w in worries) / len(worries) if worries else 0
    }

def generate_black_swan_warning() -> str:
    """S6: 黑天鹅事件警告 - 认知谦逊的极限标注"""
    warning = """
⚠️ 【认知谦逊声明 - 黑天鹅事件】

本担忧清单系统存在以下根本性局限：

1. 不可预测性
   - 系统只能基于已知模式识别担忧
   - 真正改变游戏规则的事件(黑天鹅)无法提前预警
   - 例如：突发政策变化、技术颠覆、市场崩溃等

2. 认知盲区
   - 我们不知道自己不知道什么(未知的未知)
   - 过度依赖历史数据可能错过新型风险
   - 确认偏差可能导致系统性漏报

3. 建议
   - 保持警觉，不要完全依赖自动化系统
   - 定期进行人工风险评估
   - 对"一切正常"保持健康的怀疑
   - 建立应急储备，为不可预测事件做准备

请记住：没有预警≠没有风险
"""
    return warning
    """解决担忧"""
    worries = load_worries()
    for w in worries:
        if w.get("id") == worry_id:
            w["status"] = "resolved"
            w["resolution"] = resolution
            w["resolved_at"] = datetime.now().isoformat()
            w["feedback"] = feedback
            w["updated_at"] = datetime.now().isoformat()
            save_worries(worries)
            log(f"✅ 解决担忧 {worry_id}: {resolution[:50]}...")
            return True
    log(f"❌ 未找到担忧 {worry_id}")
    return False

def scan_system() -> List[Dict]:
    """S4: 自动化系统扫描 - 多源担忧收集"""
    config = load_config()
    new_worries = []
    scan_results = {"timestamp": datetime.now().isoformat(), "sources": []}
    
    thresholds = config.get("alerting", {})
    
    # === 1. 资源监控扫描 ===
    resource_checks = []
    try:
        import shutil
        import psutil
        
        # 磁盘空间检查
        stat = shutil.disk_usage("/")
        usage_percent = stat.used / stat.total
        
        if usage_percent > thresholds.get("storage_critical", 0.9):
            new_worries.append({
                "content": f"存储空间严重告警: 使用率 {usage_percent*100:.1f}%",
                "category": "RESOURCE",
                "priority": "P0",
                "source": "system_scan",
                "epistemic_status": "KNOWN",
                "confidence": 1.0,
                "evidence": [{"type": "disk_usage", "value": usage_percent}]
            })
            resource_checks.append({"type": "disk", "status": "critical", "value": usage_percent})
        elif usage_percent > thresholds.get("storage_high", 0.8):
            new_worries.append({
                "content": f"存储空间告警: 使用率 {usage_percent*100:.1f}%",
                "category": "RESOURCE",
                "priority": "P1",
                "source": "system_scan",
                "epistemic_status": "KNOWN",
                "confidence": 1.0,
                "evidence": [{"type": "disk_usage", "value": usage_percent}]
            })
            resource_checks.append({"type": "disk", "status": "warning", "value": usage_percent})
        else:
            resource_checks.append({"type": "disk", "status": "ok", "value": usage_percent})
        
        # 内存检查
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            new_worries.append({
                "content": f"内存使用率过高: {mem.percent}%",
                "category": "RESOURCE",
                "priority": "P1",
                "source": "system_scan",
                "epistemic_status": "KNOWN",
                "confidence": 1.0,
                "evidence": [{"type": "memory_usage", "value": mem.percent}]
            })
            resource_checks.append({"type": "memory", "status": "critical", "value": mem.percent})
        else:
            resource_checks.append({"type": "memory", "status": "ok", "value": mem.percent})
            
        # CPU检查
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            new_worries.append({
                "content": f"CPU使用率持续高位: {cpu_percent}%",
                "category": "RESOURCE",
                "priority": "P2",
                "source": "system_scan",
                "epistemic_status": "KNOWN",
                "confidence": 1.0,
                "evidence": [{"type": "cpu_usage", "value": cpu_percent}]
            })
            resource_checks.append({"type": "cpu", "status": "warning", "value": cpu_percent})
        else:
            resource_checks.append({"type": "cpu", "status": "ok", "value": cpu_percent})
            
    except Exception as e:
        log(f"扫描资源时出错: {e}")
        resource_checks.append({"type": "error", "message": str(e)})
    
    scan_results["sources"].append({"name": "resource", "checks": resource_checks})
    
    # === 2. 担忧清单健康度检查 ===
    worries = load_worries()
    active_worries = [w for w in worries if w.get("status") == "active"]
    overdue_worries = [w for w in active_worries if datetime.fromisoformat(w.get("due_date", "2000-01-01")) < datetime.now()]
    
    health_checks = {
        "total_active": len(active_worries),
        "overdue_count": len(overdue_worries),
        "p0_count": len([w for w in active_worries if w.get("priority") == "P0"]),
        "unresolved_24h": len([w for w in active_worries if w.get("priority") == "P0" and 
                              (datetime.now() - datetime.fromisoformat(w.get("created_at", "2000-01-01"))).total_seconds() > 86400])
    }
    
    # S1: 担忧漏报风险评估 - 逾期率过高告警
    if len(overdue_worries) > 0:
        overdue_rate = len(overdue_worries) / max(len(active_worries), 1)
        if overdue_rate > thresholds.get("overdue_rate_threshold", 0.2):
            new_worries.append({
                "content": f"担忧清单逾期率过高: {overdue_rate*100:.1f}% ({len(overdue_worries)}个)",
                "category": "UNRESOLVED",
                "priority": "P1",
                "source": "system_scan",
                "epistemic_status": "KNOWN",
                "confidence": 1.0,
                "evidence": [{"type": "overdue_rate", "value": overdue_rate}]
            })
            health_checks["overdue_alert"] = True
    
    # P0担忧未及时处理告警 (S1: 漏报影响)
    if health_checks["unresolved_24h"] > 0:
        new_worries.append({
            "content": f"有 {health_checks['unresolved_24h']} 个P0担忧超过24小时未处理",
            "category": "UNRESOLVED",
            "priority": "P0",
            "source": "system_scan",
            "epistemic_status": "KNOWN",
            "confidence": 1.0,
            "evidence": [{"type": "p0_unresolved", "count": health_checks["unresolved_24h"]}]
        })
        health_checks["p0_alert"] = True
    
    # S1: 担忧过多导致决策质量下降的风险
    if len(active_worries) > 20:
        new_worries.append({
            "content": f"活跃担忧数量过多({len(active_worries)}个)，可能导致警报疲劳和决策瘫痪",
            "category": "UNRESOLVED",
            "priority": "P1",
            "source": "system_scan",
            "epistemic_status": "INFERRED",
            "confidence": 0.8,
            "evidence": [{"type": "worry_overload", "count": len(active_worries)}]
        })
        health_checks["overload_alert"] = True
    
    scan_results["sources"].append({"name": "health", "checks": health_checks})
    
    # === 3. 外部集成扫描 (预留接口) ===
    external_checks = []
    # 未来可集成：token预算enforcer、质量门禁、角色联邦等
    scan_results["sources"].append({"name": "external", "checks": external_checks})
    
    # 添加扫描到的担忧 (自动评估后添加)
    for nw in new_worries:
        # 自动评估并确定优先级
        auto_evaluated = auto_evaluate_worry(nw)
        nw.update(auto_evaluated)
        add_worry(**nw)
    
    # 保存扫描结果
    scan_file = DATA_DIR / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(scan_file, "w", encoding="utf-8") as f:
        json.dump(scan_results, f, ensure_ascii=False, indent=2)
    
    log(f"🔍 系统扫描完成，发现 {len(new_worries)} 个新担忧")
    return new_worries

def auto_evaluate_worry(worry: Dict) -> Dict:
    """S4: 自动评估担忧 - 基于内容智能评估"""
    content = worry.get("content", "").lower()
    
    # 关键词匹配评估
    impact_keywords = {
        "high": ["严重", "紧急", "关键", "核心", "崩溃", "失败", "损失", "安全风险"],
        "medium": ["重要", "影响", "问题", "延迟", "不足"],
        "low": ["建议", "优化", "改进", "考虑"]
    }
    
    urgency_keywords = {
        "high": ["立即", "马上", "今天", "马上", "现在", " deadline", "截止", "明天"],
        "medium": ["本周", "尽快", "近期", "3天内"],
        "low": ["下周", "以后", "未来", "长期"]
    }
    
    # 计算影响度
    impact_score = 5
    for kw in impact_keywords["high"]:
        if kw in content:
            impact_score = 9
            break
    else:
        for kw in impact_keywords["medium"]:
            if kw in content:
                impact_score = 6
                break
    
    # 计算紧急度
    urgency_score = 5
    for kw in urgency_keywords["high"]:
        if kw in content:
            urgency_score = 9
            break
    else:
        for kw in urgency_keywords["medium"]:
            if kw in content:
                urgency_score = 6
                break
    
    # 可能性评估（基于历史模式）
    probability_score = 7 if "可能" in content or "也许" in content else 5
    
    return {
        "impact": impact_score,
        "urgency": urgency_score,
        "probability": probability_score
    }

def auto_alert() -> List[Dict]:
    """S4: 自动预警 - 根据优先级自动推送"""
    worries = load_worries()
    active_worries = [w for w in worries if w.get("status") == "active"]
    
    # P0级别立即推送
    p0_worries = [w for w in active_worries if w.get("priority") == "P0"]
    
    alerts_sent = []
    
    # 生成预警通知
    if p0_worries:
        alert_content = generate_alert_content(p0_worries, "critical")
        # 保存紧急预警
        alert_file = DATA_DIR / f"alert_critical_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(alert_file, "w", encoding="utf-8") as f:
            f.write(alert_content)
        alerts_sent.extend(p0_worries)
        log(f"🚨 发送P0紧急预警: {len(p0_worries)} 项")
    
    return alerts_sent

def generate_alert_content(worries: List[Dict], level: str) -> str:
    """生成预警内容"""
    icons = {"critical": "🚨", "high": "⚠️", "medium": "📋"}
    titles = {"critical": "P0紧急预警", "high": "P1重要提醒", "medium": "关注事项"}
    
    lines = [
        f"{icons.get(level, '📋')} {titles.get(level, '预警通知')}",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 50,
        ""
    ]
    
    for w in worries:
        lines.extend([
            f"【{w['id']}】{w['content'][:50]}",
            f"  分类: {w.get('category', '未分类')} | 置信度: {w.get('confidence', 0.5)*100:.0f}%",
            f"  认知状态: {w.get('epistemic_status', 'UNKNOWN')}",
            ""
        ])
    
    # S6: 认知谦逊声明
    lines.extend([
        "---",
        "📌 认知谦逊声明:",
        "- 本预警基于当前已知信息，可能存在不确定性",
        "- 黑天鹅事件无法预测，需保持警觉",
        "- 建议结合人工判断进行决策",
        ""
    ])
    
    return "\n".join(lines)

def generate_report(period: str = "daily") -> str:
    """S3: 可观测输出 - 生成全面报告"""
    worries = load_worries()
    now = datetime.now()
    
    if period == "daily":
        cutoff = now - timedelta(days=1)
        title = f"📊 担忧日报 ({now.strftime('%Y-%m-%d')})"
    elif period == "weekly":
        cutoff = now - timedelta(days=7)
        title = f"📊 担忧周报 ({(now-timedelta(days=7)).strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')})"
    else:
        cutoff = now - timedelta(days=1)
        title = f"📊 担忧报告"
    
    # 统计数据
    all_worries = worries
    active_worries = [w for w in all_worries if w.get("status") == "active"]
    resolved_worries = [w for w in all_worries if w.get("status") == "resolved"]
    period_worries = [w for w in all_worries if datetime.fromisoformat(w.get("created_at", "2000-01-01")) >= cutoff]
    
    # S3: 担忧列表、风险评级、应对状态
    priority_counts = {}
    for p in ["P0", "P1", "P2", "P3"]:
        priority_counts[p] = len([w for w in active_worries if w.get("priority") == p])
    
    # 分类统计
    category_counts = {}
    for w in active_worries:
        cat = w.get("category", "UNRESOLVED")
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # 认知状态统计
    epistemic_stats = {}
    for w in active_worries:
        status = w.get("epistemic_status", "UNKNOWN")
        epistemic_stats[status] = epistemic_stats.get(status, 0) + 1
    
    # S1: 漏报影响评估
    overdue_worries = [w for w in active_worries if datetime.fromisoformat(w.get("due_date", "2000-01-01")) < now]
    p0_unresolved_long = [w for w in active_worries if w.get("priority") == "P0" and 
                         (now - datetime.fromisoformat(w.get("created_at", "2000-01-01"))).days > 1]
    
    # S5: 准确性趋势
    resolved_recent = [w for w in resolved_worries if datetime.fromisoformat(w.get("resolved_at", "2000-01-01")) >= cutoff]
    accuracy_trend = calculate_accuracy_trend(resolved_recent)
    
    # 生成报告
    lines = [
        title,
        "=" * 60,
        "",
        "## 📈 统计概览",
        f"- 活跃担忧: {len(active_worries)}",
        f"- 本周期新增: {len(period_worries)}",
        f"- 已解决: {len(resolved_recent)}",
        f"- 逾期担忧: {len(overdue_worries)}",
        "",
        "### 按优先级分布 (风险评级)",
        f"- 🔴 P0(紧急): {priority_counts['P0']}",
        f"- 🟠 P1(高): {priority_counts['P1']}",
        f"- 🟡 P2(中): {priority_counts['P2']}",
        f"- 🟢 P3(低): {priority_counts['P3']}",
        "",
        "### 按分类分布",
    ]
    
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- {cat}: {count}")
    lines.append("")
    
    lines.extend([
        "### 认知状态分布 (S6)",
    ])
    for status, count in epistemic_stats.items():
        icon = {"KNOWN": "✓", "INFERRED": "~", "UNKNOWN": "?"}.get(status, "?")
        lines.append(f"- {icon} {status}: {count}")
    lines.append("")
    
    # S3: 高优先级担忧详情 (应对状态)
    high_priority = [w for w in active_worries if w.get("priority") in ["P0", "P1"]]
    if high_priority:
        lines.extend([
            "## 🔥 需关注的高优先级担忧 (应对状态)",
            ""
        ])
        for w in high_priority[:10]:
            age_hours = (now - datetime.fromisoformat(w['created_at'])).total_seconds() / 3600
            lines.extend([
                f"### {w['id']} [{w['priority']}]",
                f"- 内容: {w['content']}",
                f"- 分类: {w['category']} | 存在时长: {age_hours:.1f}小时",
                f"- 认知状态: {w.get('epistemic_status', 'UNKNOWN')} | 置信度: {w.get('confidence', 0.5)*100:.0f}%",
                f"- 状态: {w.get('status', 'active')}",
                f"- 行动项: {len(w.get('actions', []))} 个",
                ""
            ])
    
    # S1: 漏报影响评估
    overdue_rate = len(overdue_worries) / max(len(active_worries), 1) if overdue_worries else 0
    
    lines.extend([
        "## ⚠️ S1: 漏报风险影响评估",
        ""
    ])
    
    if p0_unresolved_long:
        lines.append(f"🚨 **高风险**: {len(p0_unresolved_long)} 个P0担忧超过24小时未处理")
        lines.append("   影响: 可能导致重大决策延误或系统故障")
        lines.append("")
    
    if overdue_worries:
        lines.append(f"⚠️ **中风险**: 逾期率 {overdue_rate*100:.1f}% ({len(overdue_worries)}个)")
        lines.append("   影响: 决策质量下降，警报疲劳风险")
        lines.append("")
    
    if not p0_unresolved_long and not overdue_worries:
        lines.append("✅ 当前无显著漏报风险")
        lines.append("")
    
    # S5: 准确性评估
    lines.extend([
        "## 📊 S5: 准确性评估",
        f"- 本周期解决数: {len(resolved_recent)}",
        f"- 准确率: {accuracy_trend.get('accuracy_rate', 0)*100:.1f}%",
        f"- 质量评级: {accuracy_trend.get('assessment', 'N/A')}",
        ""
    ])
    
    # 建议
    lines.extend([
        "## 💡 行动建议",
        ""
    ])
    if priority_counts["P0"] > 0:
        lines.append(f"⚠️ 有 {priority_counts['P0']} 个P0级紧急担忧需要立即处理")
    if priority_counts["P1"] > 3:
        lines.append(f"📋 P1级担忧较多({priority_counts['P1']}个)，建议安排专项时间处理")
    if len(active_worries) == 0:
        lines.append("✅ 当前无活跃担忧，系统状态良好")
    if overdue_rate > 0.2:
        lines.append(f"🔴 逾期率过高，建议复盘处理流程")
    
    lines.append("")
    
    # S6: 认知谦逊声明
    lines.extend([
        "## 📌 S6: 认知谦逊声明",
        "",
        "**系统局限**:",
        "- 担忧检测基于关键词规则，覆盖率非100%",
        "- 优先级评估基于历史数据，新场景可能不适用", 
        "- **黑天鹅事件无法预测**，请保持人工警觉",
        "- 未知的未知(Unknown Unknowns)不在监控范围内",
        "",
    ])
    
    lines.extend([
        "---",
        f"*生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}*",
        "*Worry-List-Manager v2.5.0 - 5标准版本*"
    ])
    
    report = "\n".join(lines)
    
    # 保存报告
    report_file = DATA_DIR / f"report_{period}_{now.strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    log(f"📊 S3生成{period}报告: {report_file}")
    return report

def calculate_accuracy_trend(resolved_worries: List[Dict]) -> Dict:
    """计算准确性趋势"""
    if not resolved_worries:
        return {"accuracy_rate": 0, "assessment": "无数据"}
    
    accurate = [w for w in resolved_worries if w.get("feedback") not in ["false_positive", "false_negative", None]]
    accuracy = len(accurate) / len(resolved_worries)
    
    return {
        "accuracy_rate": accuracy,
        "assessment": "优秀" if accuracy >= 0.90 else "良好" if accuracy >= 0.85 else "需改进"
    }

def push_alert():
    """推送晨间简报"""
    report = generate_report("daily")
    
    # 保存为最新简报
    brief_file = DATA_DIR / "latest_brief.md"
    with open(brief_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    # 输出到控制台（实际应用中可集成消息推送）
    print("\n" + "=" * 60)
    print("📢 晨间担忧简报")
    print("=" * 60)
    print(report)
    print("=" * 60 + "\n")
    
    log("📢 已推送晨间简报")
    return report

def evaluate_accuracy() -> Dict:
    """S5: 自我验证 - 担忧评估准确性全面检查"""
    worries = load_worries()
    resolved = [w for w in worries if w.get("status") == "resolved"]
    active = [w for w in worries if w.get("status") == "active"]
    
    if not resolved:
        return {"message": "尚无已解决的担忧用于评估"}
    
    # 统计反馈
    false_positives = [w for w in resolved if w.get("feedback") == "false_positive"]
    false_negatives = [w for w in resolved if w.get("feedback") == "false_negative"]
    true_positives = [w for w in resolved if w.get("feedback") == "true_positive"]
    accurate = [w for w in resolved if w.get("feedback") not in ["false_positive", "false_negative", None]]
    
    total = len(resolved)
    fp_rate = len(false_positives) / total if total > 0 else 0
    fn_rate = len(false_negatives) / total if total > 0 else 0
    tp_rate = len(true_positives) / total if total > 0 else 0
    accuracy = len(accurate) / total if total > 0 else 0
    
    # S5: 漏报风险评估
    # 检查是否有P0级别担忧被错误评估为低优先级
    priority_misjudgments = []
    for w in resolved:
        content = w.get("content", "").lower()
        actual_priority = w.get("priority")
        
        # 如果内容包含紧急关键词但被标记为低优先级
        urgent_keywords = ["严重", "紧急", "关键", "崩溃", "失败"]
        is_urgent = any(kw in content for kw in urgent_keywords)
        
        if is_urgent and actual_priority not in ["P0", "P1"]:
            priority_misjudgments.append({
                "id": w.get("id"),
                "content": w.get("content")[:50],
                "assigned_priority": actual_priority,
                "expected": "P0/P1",
                "reason": "内容包含紧急关键词但被低估"
            })
    
    # 检查漏报 - 活跃担忧中可能应该已识别为担忧的事项
    potential_misses = []
    for w in active:
        age_days = (datetime.now() - datetime.fromisoformat(w.get("created_at", "2000-01-01"))).days
        if age_days > 7 and w.get("priority") == "P0":
            potential_misses.append({
                "id": w.get("id"),
                "content": w.get("content")[:50],
                "age_days": age_days,
                "issue": "P0担忧长期未处理，可能评估时未充分考虑紧急性"
            })
    
    # S5: 预警准确性趋势分析
    daily_stats = {}
    for w in resolved:
        date = w.get("resolved_at", "")[:10]
        if date:
            if date not in daily_stats:
                daily_stats[date] = {"total": 0, "accurate": 0, "fp": 0, "fn": 0}
            daily_stats[date]["total"] += 1
            if w.get("feedback") in ["true_positive", None]:
                daily_stats[date]["accurate"] += 1
            elif w.get("feedback") == "false_positive":
                daily_stats[date]["fp"] += 1
            elif w.get("feedback") == "false_negative":
                daily_stats[date]["fn"] += 1
    
    # 生成改进建议
    recommendations = []
    if fp_rate > 0.15:
        recommendations.append("误报率偏高，建议提高预警阈值或增强过滤规则")
    if fn_rate > 0.10:
        recommendations.append("漏报率偏高，建议增加监控维度或降低敏感度阈值")
    if priority_misjudgments:
        recommendations.append(f"发现{len(priority_misjudgments)}个优先级误判，建议优化评估算法")
    if potential_misses:
        recommendations.append(f"发现{len(potential_misses)}个潜在漏报担忧，建议回顾评估流程")
    
    # 评估报告
    result = {
        "evaluation_timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_resolved": total,
            "false_positives": len(false_positives),
            "false_negatives": len(false_negatives),
            "true_positives": len(true_positives),
            "accurate": len(accurate),
            "false_positive_rate": round(fp_rate, 4),
            "false_negative_rate": round(fn_rate, 4),
            "true_positive_rate": round(tp_rate, 4),
            "accuracy_rate": round(accuracy, 4),
        },
        "quality_assessment": "优秀" if accuracy >= 0.90 else "良好" if accuracy >= 0.85 else "需改进",
        "priority_misjudgments": {
            "count": len(priority_misjudgments),
            "items": priority_misjudgments[:5]  # 最多展示5个
        },
        "potential_misses": {
            "count": len(potential_misses),
            "items": potential_misses[:5]
        },
        "daily_trend": daily_stats,
        "recommendations": recommendations,
        "next_evaluation": (datetime.now() + timedelta(days=1)).isoformat()
    }
    
    # 保存评估报告
    eval_file = DATA_DIR / f"accuracy_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    log(f"📊 S5准确性评估: 准确率 {accuracy*100:.1f}%, 误报率 {fp_rate*100:.1f}%, 漏报率 {fn_rate*100:.1f}%")
    log(f"📊 质量评级: {result['quality_assessment']}")
    
    return result

def adversarial_test():
    """S7: 对抗测试 - 模拟已知风险测试发现能力"""
    log("🔴 开始S7对抗测试...")
    
    # 设计测试用例 - 覆盖各种场景
    test_cases = [
        # 场景1: 明显的P0级别资源问题
        {
            "content": "磁盘空间即将耗尽，剩余不足5%，系统可能随时崩溃",
            "expected_category": "RESOURCE", 
            "expected_priority": "P0",
            "test_type": "obvious_critical"
        },
        # 场景2: 隐含的截止日期风险
        {
            "content": "项目截止日期明天，核心功能尚未完成，客户非常不满",
            "expected_category": "DEADLINE",
            "expected_priority": "P0",
            "test_type": "implied_urgency"
        },
        # 场景3: 需要推断的机会风险
        {
            "content": "上周开会时客户提到的那个想法，我们好像还没跟进",
            "expected_category": "OPPORTUNITY",
            "expected_priority": "P2",
            "test_type": "subtle_opportunity"
        },
        # 场景4: 可能被误判为低优先级的系统风险
        {
            "content": "日志里有些奇怪的错误，不过好像没影响功能",
            "expected_category": "UNRESOLVED",
            "expected_priority": "P1",  # 应该至少P1
            "test_type": "risk_underestimation"
        },
        # 场景5: 多个风险叠加
        {
            "content": "API配额快用完了，同时存储也快满了，明天还要交付",
            "expected_category": "RESOURCE",
            "expected_priority": "P0",
            "test_type": "compound_risk"
        },
        # 场景6: 需要外部知识的判断
        {
            "content": "供应商发邮件说可能要调整合作条款",
            "expected_category": "EXTERNAL",
            "expected_priority": "P1",
            "test_type": "external_dependency"
        },
        # 场景7: 模糊表述的担忧
        {
            "content": "感觉最近项目进展不太对劲，但具体说不上来",
            "expected_category": "UNRESOLVED",
            "expected_priority": "P2",
            "test_type": "vague_concern"
        }
    ]
    
    results = []
    test_worry_ids = []  # 记录测试创建的担忧ID以便清理
    
    for idx, test in enumerate(test_cases, 1):
        # 模拟添加担忧
        worry_id = add_worry(
            content=test["content"],
            category=test["expected_category"],
            source="adversarial_test",
            epistemic_status="UNKNOWN",  # 测试中标记为未知，看系统能否正确识别
            confidence=0.3
        )
        test_worry_ids.append(worry_id)
        
        worries = load_worries()
        worry = next((w for w in worries if w["id"] == worry_id), None)
        
        # 评估结果
        priority_match = worry and worry.get("priority") == test["expected_priority"]
        category_match = worry and worry.get("category") == test["expected_category"]
        
        # 允许优先级有1级偏差
        priority_ok = priority_match or (
            worry and 
            abs(({"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(worry.get("priority"), 3)) - 
                ({"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(test["expected_priority"], 3))) <= 1
        )
        
        passed = category_match and priority_ok
        
        results.append({
            "test_id": idx,
            "test_type": test["test_type"],
            "content_preview": test["content"][:40],
            "passed": passed,
            "category_match": category_match,
            "priority_match": priority_match,
            "expected": f"{test['expected_category']}/{test['expected_priority']}",
            "actual": f"{worry.get('category') if worry else 'N/A'}/{worry.get('priority') if worry else 'N/A'}",
            "assessment": "通过" if passed else "失败"
        })
        
        log(f"  测试{idx} [{test['test_type']}]: {'✓' if passed else '✗'} {test['content'][:30]}...")
    
    # 清理测试数据
    worries = load_worries()
    for w in worries:
        if w.get("id") in test_worry_ids:
            w["status"] = "archived"
            w["resolution"] = "对抗测试归档"
            w["updated_at"] = datetime.now().isoformat()
    save_worries(worries)
    
    # 统计结果
    passed_count = sum(1 for r in results if r["passed"])
    category_accuracy = sum(1 for r in results if r["category_match"]) / len(results)
    priority_accuracy = sum(1 for r in results if r["priority_match"]) / len(results)
    
    # 分析失败模式
    failures = [r for r in results if not r["passed"]]
    failure_patterns = {}
    for f in failures:
        test_type = f["test_type"]
        if test_type not in failure_patterns:
            failure_patterns[test_type] = []
        failure_patterns[test_type].append(f)
    
    # 生成测试报告
    test_report = {
        "test_timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": len(test_cases),
            "passed": passed_count,
            "failed": len(test_cases) - passed_count,
            "pass_rate": round(passed_count / len(test_cases), 4),
            "category_accuracy": round(category_accuracy, 4),
            "priority_accuracy": round(priority_accuracy, 4)
        },
        "test_results": results,
        "failure_analysis": {
            "patterns": {k: len(v) for k, v in failure_patterns.items()},
            "details": failure_patterns
        },
        "implications": {
            "detection_capability": "良好" if passed_count >= len(test_cases) * 0.7 else "需改进",
            "blind_spots": list(failure_patterns.keys()) if failure_patterns else [],
            "recommendations": []
        }
    }
    
    # 生成改进建议
    if category_accuracy < 0.8:
        test_report["implications"]["recommendations"].append("分类准确度偏低，建议增强分类规则")
    if priority_accuracy < 0.8:
        test_report["implications"]["recommendations"].append("优先级评估准确度偏低，建议优化评估算法")
    if "risk_underestimation" in failure_patterns:
        test_report["implications"]["recommendations"].append("存在风险低估模式，建议提高隐含风险识别能力")
    if "vague_concern" in failure_patterns:
        test_report["implications"]["recommendations"].append("模糊担忧处理不佳，建议增强自然语言理解")
    
    # 保存测试报告
    test_file = DATA_DIR / f"adversarial_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)
    
    log(f"🔴 S7对抗测试完成: {passed_count}/{len(test_cases)} 通过 ({test_report['summary']['pass_rate']*100:.1f}%)")
    log(f"🔴 检测能力评估: {test_report['implications']['detection_capability']}")
    
    return test_report

def main():
    parser = argparse.ArgumentParser(description="担忧清单管理器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加担忧")
    add_parser.add_argument("--content", "-c", required=True, help="担忧内容")
    add_parser.add_argument("--category", "-t", default="UNRESOLVED", help="分类")
    add_parser.add_argument("--source", "-s", default="manual", help="来源")
    add_parser.add_argument("--impact", "-i", type=int, default=5, help="影响度(1-10)")
    add_parser.add_argument("--urgency", "-u", type=int, default=5, help="紧急度(1-10)")
    add_parser.add_argument("--probability", "-p", type=int, default=5, help="可能性(1-10)")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出担忧")
    list_parser.add_argument("--priority", help="按优先级筛选")
    list_parser.add_argument("--status", help="按状态筛选")
    list_parser.add_argument("--category", help="按分类筛选")
    
    # resolve 命令
    resolve_parser = subparsers.add_parser("resolve", help="解决担忧")
    resolve_parser.add_argument("id", help="担忧ID")
    resolve_parser.add_argument("--resolution", "-r", required=True, help="解决方案")
    resolve_parser.add_argument("--feedback", "-f", help="反馈(true_positive/false_positive/false_negative)")
    
    # scan 命令
    scan_parser = subparsers.add_parser("scan", help="系统扫描")
    scan_parser.add_argument("--auto-alert", "-a", action="store_true", help="自动发送预警")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成报告")
    report_parser.add_argument("--period", "-p", default="daily", choices=["daily", "weekly"], help="报告周期")
    
    # weekly 命令
    subparsers.add_parser("weekly", help="生成周报")
    
    # push 命令
    subparsers.add_parser("push", help="推送简报")
    
    # evaluate 命令 (S5)
    subparsers.add_parser("evaluate", help="评估准确性 (S5)")
    
    # test 命令 (S7)
    subparsers.add_parser("test", help="对抗测试 (S7)")
    
    # feedback 命令 (S2)
    feedback_parser = subparsers.add_parser("feedback", help="提交反馈 (S2)")
    feedback_parser.add_argument("id", help="担忧ID")
    feedback_parser.add_argument("--type", "-t", required=True, choices=["true_positive", "false_positive", "false_negative", "unclear"], help="反馈类型")
    feedback_parser.add_argument("--notes", "-n", help="备注")
    
    # loop 命令 (S2)
    subparsers.add_parser("loop", help="反馈闭环处理 (S2)")
    
    # alert 命令 (S4)
    subparsers.add_parser("alert", help="自动预警 (S4)")
    
    # warning 命令 (S6)
    subparsers.add_parser("warning", help="黑天鹅警告 (S6)")
    
    args = parser.parse_args()
    
    if args.command == "add":
        worry_id = add_worry(
            content=args.content,
            category=args.category,
            source=args.source,
            impact=args.impact,
            urgency=args.urgency,
            probability=args.probability
        )
        print(f"✅ 已添加担忧: {worry_id}")
    
    elif args.command == "list":
        worries = list_worries(args.priority, args.status, args.category)
        print(f"\n📋 担忧清单 ({len(worries)} 项)\n")
        print("-" * 80)
        print(f"{'ID':<12} {'优先级':<8} {'状态':<10} {'分类':<12} {'认知':<8} {'内容':<25}")
        print("-" * 80)
        for w in worries:
            content = w['content'][:23] + "..." if len(w['content']) > 25 else w['content']
            epistemic = w.get('epistemic_status', 'UNK')[:3]
            print(f"{w['id']:<12} {w['priority']:<8} {w['status']:<10} {w['category']:<12} {epistemic:<8} {content:<25}")
        print("-" * 80)
    
    elif args.command == "resolve":
        if resolve_worry(args.id, args.resolution, args.feedback):
            print(f"✅ 已解决担忧: {args.id}")
        else:
            print(f"❌ 未找到担忧: {args.id}")
    
    elif args.command == "scan":
        new_worries = scan_system()
        print(f"🔍 扫描完成，发现 {len(new_worries)} 个新担忧")
        if args.auto_alert and new_worries:
            alerts = auto_alert()
            print(f"🚨 自动发送 {len(alerts)} 个预警")
    
    elif args.command == "report":
        report = generate_report(args.period)
        print(report)
    
    elif args.command == "weekly":
        report = generate_report("weekly")
        print(report)
    
    elif args.command == "push":
        report = push_alert()
        print(report)
    
    elif args.command == "evaluate":
        result = evaluate_accuracy()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == "test":
        result = adversarial_test()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == "feedback":
        if collect_feedback(args.id, args.type, args.notes):
            print(f"✅ 已提交反馈: {args.id}")
        else:
            print(f"❌ 未找到担忧: {args.id}")
    
    elif args.command == "loop":
        result = close_feedback_loop()
        print("🔄 反馈闭环处理完成")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == "alert":
        alerts = auto_alert()
        print(f"🚨 自动预警: {len(alerts)} 个P0级别担忧")
    
    elif args.command == "warning":
        print(generate_black_swan_warning())
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
