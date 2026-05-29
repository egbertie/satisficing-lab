#!/usr/bin/env python3
"""
Q值7天追踪 · 自动记录器
每天由cron或手动调用 → 追加一条记录到Q值趋势日志
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path("/Users/egbertielau/.openclaw/workspace/memory")
Q_LOG = MEMORY_DIR / "Q值趋势日志.json"
Q_SCAN = MEMORY_DIR / "_scripts" / "q_scan.py"

def record():
    # 运行q_scan.py获取最新Q值
    result = subprocess.run(
        ["python3", str(Q_SCAN)],
        capture_output=True, text=True, timeout=30, cwd=str(MEMORY_DIR.parent)
    )
    
    # 读取保存的统计数据
    stats_file = MEMORY_DIR / "连接密度统计.json"
    if not stats_file.exists():
        print("[BLOCKED] 统计数据文件不存在")
        return
    
    stats = json.loads(stats_file.read_text(encoding='utf-8'))
    q_value = stats["综合Q值"]["值"]
    q_status = stats["综合Q值"]["状态"]
    product_coverage = stats["产品标签覆盖"]["覆盖率%"]
    dream_connect = stats["梦境三层连通"]["连接度%"]
    heritage_abs = stats["遗产吸收"]["估计吸收率%"]
    data_connect = stats["数据源连通"]["连通率%"]
    simon_phase = stats["综合Q值"]["四阶段进度"]["西蒙满意度_50%"]
    
    # 读取或创建趋势日志
    if Q_LOG.exists():
        trend = json.loads(Q_LOG.read_text(encoding='utf-8'))
    else:
        trend = {"记录": [], "说明": "每日Q值趋势追踪。连续7天数据后方可判断趋势方向"}
    
    record = {
        "时间": datetime.now().isoformat(),
        "Q值": q_value,
        "状态": q_status,
        "产品标签覆盖": product_coverage,
        "梦境三层连通": dream_connect,
        "遗产吸收": heritage_abs,
        "数据源连通": data_connect,
        "四阶段进度": simon_phase,
        "各维度": {
            k: v for k, v in stats.items() if k != "综合Q值"
        }
    }
    
    # 防重复：同一天已有记录则跳过
    today = datetime.now().strftime("%Y-%m-%d")
    existing = [r for r in trend["记录"] if r["时间"].startswith(today)]
    if existing:
        print(f"[SKIP] 今日已有记录 ({len(existing)}条)")
        return
    
    trend["记录"].append(record)
    
    # 如果有≥2条记录，计算趋势
    if len(trend["记录"]) >= 2:
        prev = trend["记录"][-2]["Q值"]
        curr = trend["记录"][-1]["Q值"]
        diff = curr - prev
        trend["最新趋势"] = {
            "上期Q值": prev,
            "本期Q值": curr,
            "变化": round(diff, 1),
            "方向": "📈 上升" if diff > 1 else "📉 下降" if diff < -1 else "➡️ 平稳"
        }
    
    Q_LOG.write_text(json.dumps(trend, ensure_ascii=False, indent=2))
    print(f"[FIN-A] Q值记录已保存 · 当前: {q_value}% · 共{len(trend['记录'])}条记录")

if __name__ == "__main__":
    record()
