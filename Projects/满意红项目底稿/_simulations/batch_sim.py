#!/usr/bin/env python3
"""批量模拟数据运行·自动生成5赛道对比报告"""
import subprocess, json, glob, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sim_files = sorted(glob.glob("sim_*.json"))

print("=" * 65)
print("  五维决策评分引擎 · 批量模拟诊断")
print("  5赛道 × 基线+30天 = 10次诊断")
print("=" * 65)

results = {}
for sf in sim_files:
    sector = sf.replace("sim_", "").replace(".json", "")
    # 基线
    r = subprocess.run(["python3", "scoring_engine_v3.0.py", "--json", sf], capture_output=True, text=True)
    t = r.stdout
    i = t.find('{')
    depth = 0
    for j in range(i, len(t)):
        if t[j] == '{': depth += 1
        elif t[j] == '}':
            depth -= 1
            if depth == 0:
                d = json.loads(t[i:j+1])
                results[sector] = d['summary']
                break
    
    # 检查是否有30天随访
    followup_file = f"sim_{sector}_30d.json"
    if os.path.exists(followup_file):
        r2 = subprocess.run(["python3", "scoring_engine_v3.0.py", "--json", followup_file], capture_output=True, text=True)
        t2 = r2.stdout
        i2 = t2.find('{')
        depth2 = 0
        for j2 in range(i2, len(t2)):
            if t2[j2] == '{': depth2 += 1
            elif t2[j2] == '}':
                depth2 -= 1
                if depth2 == 0:
                    d2 = json.loads(t2[i2:j2+1])
                    results[f"{sector}_30d"] = d2['summary']
                    break

print()
print(f"{'赛道':<12} {'基线均分':>6} {'基线骑士':>20} {'30天均分':>6} {'30天骑士':>20} {'趋势':>6}")
print("-" * 75)
for sector in ["量子计算", "芯片", "eVTOL", "机器人", "出海"]:
    base = results.get(sector, {})
    follow = results.get(f"{sector}_30d", {})
    if base:
        base_avg = base.get('average', '?')
        base_knights = base.get('gottman', '?').split(':')[-1].strip()
        follow_avg = follow.get('average', '-') if follow else '-'
        follow_knights = follow.get('gottman', '-').split(':')[-1].strip() if follow else '-'
        trend = '↑' if (isinstance(follow_avg, (int, float)) and isinstance(base_avg, (int, float)) and follow_avg > base_avg) else ('↓' if (isinstance(follow_avg, (int, float)) and isinstance(base_avg, (int, float)) and follow_avg < base_avg) else '-')
        print(f"{sector:<12} {base_avg:>6} {base_knights:>20} {str(follow_avg):>6} {str(follow_knights):>20} {trend:>6}")

print()
print("管线就绪: 真实数据到达后·替换sim_*.json即可")
