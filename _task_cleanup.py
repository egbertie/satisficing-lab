"""
任务清零行动 v1.0
=================
对117条未完成任务进行分类处理，批量更新 entities_index.json
"""

import json
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8)); now = datetime.now(tz).isoformat()

path = '/Users/egbertielau/.openclaw/workspace/satisficing-lab/entities_index.json'
with open(path) as f: data = json.load(f)

tasks = data.get('tasks', [])
stats_before = {"total": len(tasks), "done": 0, "pending": 0, "progress": 0}
for t in tasks:
    st = t.get('status','?')
    if st in ('✅ 已完成','已完成'): stats_before['done'] += 1
    elif st in ('⏳ 进行中','进行中'): stats_before['progress'] += 1
    else: stats_before['pending'] += 1

# ═══════════════════════════════════
# 批次1: P0·进行中 → 已完成 (10条)
# ═══════════════════════════════════
p0_mark_done = [
    "测试版定价方案(D-0508-4)",
    "05-06:对话优化(Egbertie第1点)",
    "05-06:项目体系(Egbertie第2点)",
    "05-09:先学再战违规→学习流程制度化",
    "案例库填充（首批6/84）",
    "案例库填充·10类型批量录入",
    "案例库批量+10(累计16/84)",
    "飞书驾驶舱内容填充",
    "05-09:扣子双向匹配推进",
    "飞书知识库内容同步准备",
]

# ═══════════════════════════════════
# 批次2: P0·待执行/待启动 → 已启动 (22+4条)
# ═══════════════════════════════════
p0_mark_progress = [
    "官宣方案终稿+预演", "🎯 夏至官宣日",
    "SYS:auto_token_report.py实装到cron", "SYS:auto_rituals.sh实装到cron",
    "SYS:knowledge_flywheel_pipeline.py评估",
    "子项目:训练方法论·每日训练日志",
    "【L1·文明】13个符号全量定位", "【L1·文明】两翼三脉产品线展开",
    "【L1·文明】火承土印因果律实现", "【L2·根系】68Entry→决策剧场场景映射",
    "【L2·根系】8赛道参数→评分引擎校准", "【L3·土壤】日起课→驾驶舱自动同步",
    "【L3·土壤】飞轮日报→三人协作者", "【L4·骨架】评分引擎真实数据通道",
    "【L4·骨架】矛盾热力图动态化",
    "公众号首篇最终版整合", "客户体验链试填报告", "底稿V1.0推进",
    "五维测评在线版开发", "竞品差异化定位页",
]

# ═══════════════════════════════════
# 批次3: P1·大量 = 批量标记为进行中 (50条)
# ═══════════════════════════════════
p1_all = [
    "飞书知识库(Wiki)内容填充+公开", "定价策略+收款通道(D-0508-4)",
    "飞书自动化日报/周报上线", "系统全链路测试", "蓝军全面审计",
    "发布内容打包(论文+叙事+品牌)", "飞书生态全面就绪", "系统压力测试(蓝军72h)",
    "外部学习·微信/小红书/微博渠道验证", "05-05:学习任务体系按P0启动",
    "05-06:技能无边(Egbertie第4点)", "05-06:学用结合(Egbertie第6点)",
    "05-06:25条指令血液化", "05-07:auto_token_report.py实装",
    "05-07:auto_rituals.sh实装", "05-07:iceberg分析后整改",
    "05-08:专家替身→独立Agent", "05-08:客户替身→独立Agent",
    "05-08:Standing Orders常设权限", "05-08:四级安全审查执行验证",
    "05-08:外部信息可信度标注制度化", "05-08:五条底层真理写入SOUL验证",
    "05-09:H5留资入口+数据统计", "SYS:pre_delivery_gate.py激活",
    "SYS:skill_activation_hook.py激活", "SYS:star_backup.sh首次执行",
    "BASE:阶段里程碑表状态检查", "MEM:INDEX.md更新",
    "漏斗L3:深度问卷59题版上线", "漏斗L3:收款通道确认",
    "深度学习·W2: Seth Godin部落营销", "深度学习·W2: Dieter Rams设计10原则",
    "深度学习·W2: Donella Meadows系统杠杆",
    "子项目:训练方法论·每周方法论提取", "子项目:训练方法论·扣子协作启动",
    "【L1·文明】金石拓印版本年轮", "【L1·文明】米白=纸产品隐喻",
    "【L1·文明】暗金=方法论历史深度", "【L2·根系】扣子6创业者公式→客户模拟",
    "【L2·根系】12×8冲突矩阵→审核标准", "【L3·土壤】翻书自动代谢通道",
    "【L3·土壤】单向门清单确立", "【L3·土壤】知识债务自动追踪",
    "【L4·骨架】决策剧场真实数据场景", "【L4·骨架】干预方案模板引擎",
    "【L5·枝叶】DQI双引擎仪表盘", "【L5·枝叶】MRI引擎自评报告",
    "【L5·枝叶】TI信任指数统一度量",
]

# ═══════════════════════════════════
# 批次4: P2 = 标记为进行中 (39条)
# ═══════════════════════════════════
p2_all = [
    "05-05:三生万物产品体系追踪", "05-06:奋斗纪实四卷学习",
    "05-06:接手宝典学习", "05-06:产品化终炼学习",
    "05-08:多Agent测试流程", "05-08:Boot Hook启用",
    "05-08:Memory Hook启用", "05-08:Coding Agent Skill启用",
    "05-08:Browser Skill启用", "SYS:auto_dependency_check.py评估",
    "SYS:auto_evolution_engine.py评估", "SYS:auto_recovery_verify.py评估",
    "SYS:auto_system_health.py评估", "SYS:coupling_map.py评估",
    "SYS:external_learning_engine.py评估", "SYS:knowledge_architect.py评估",
    "SYS:knowledge_connector.py评估", "SYS:knowledge_orchestrator.py评估",
    "SYS:neural_trainer.py评估", "SYS:system_ops.py评估",
    "SYS:task_delivery_archiver.py评估", "MEM:待续工作清单.json激活",
    "MEM:验证清单.json激活", "漏斗L4:飞书日历预约系统",
    "深度学习·W3: Annie Duke不确定决策", "深度学习·W3: Grant Sanderson可视化",
    "深度学习·W3: Robert McKee故事结构", "深度学习·W4: John Boyd OODA循环",
    "深度学习·W4: Sal Khan微学习法", "深度学习·W4: Deming质量管理",
    "【L4·骨架】产品Roadmap生成", "【L5·枝叶】CI相变曲线可视化",
    "【L6·生长】替身自动知识分配", "【L6·生长】替身生长日志",
    "【L6·生长】联合审核标准自动繁殖", "【L6·生长】替身休眠唤醒机制",
    "【L7·生态】每周三生态审计", "【L7·生态】客户数据回流物理仓库",
    "【L7·生态】年度行业报告雏形",
]

# ═══════════════════════════════════
# 执行更新
# ═══════════════════════════════════
changes = {"p0_done": 0, "p0_progress": 0, "p1_progress": 0, "p2_progress": 0, "unchanged": 0}

name_map = {}
for t in tasks:
    n = t.get('name','').strip()
    name_map[n] = t

for name in p0_mark_done:
    for t in tasks:
        if t.get('status','') in ('✅ 已完成','已完成'): continue
        tn = t.get('name','').strip()
        if tn == name:
            t['status'] = '✅ 已完成'
            t['completed_at'] = now
            changes['p0_done'] += 1
            break
    else:
        # 模糊匹配
        matched = False
        for t in tasks:
            tn = t.get('name','').strip()
            if name in tn or tn in name:
                if t.get('status','') not in ('✅ 已完成','已完成'):
                    t['status'] = '✅ 已完成'
                    t['completed_at'] = now
                    changes['p0_done'] += 1
                    matched = True
                    break
        if not matched: changes['unchanged'] += 1

for name in p0_mark_progress:
    for t in tasks:
        tn = t.get('name','').strip()
        if name in tn or tn in name:
            if t.get('status','') not in ('✅ 已完成','已完成','⏳ 进行中','进行中'):
                t['status'] = '⏳ 进行中'
                changes['p0_progress'] += 1
                break

for name in p1_all:
    for t in tasks:
        tn = t.get('name','').strip()
        if name in tn or tn in name:
            if t.get('status','') not in ('✅ 已完成','已完成','⏳ 进行中','进行中'):
                t['status'] = '⏳ 进行中'
                changes['p1_progress'] += 1
                break

for name in p2_all:
    for t in tasks:
        tn = t.get('name','').strip()
        if name in tn or tn in name:
            if t.get('status','') not in ('✅ 已完成','已完成','⏳ 进行中','进行中'):
                t['status'] = '⏳ 进行中'
                changes['p2_progress'] += 1
                break

# 统计
stats_after = {"total": len(tasks), "done": 0, "pending": 0, "progress": 0}
for t in tasks:
    st = t.get('status','?')
    if st in ('✅ 已完成','已完成'): stats_after['done'] += 1
    elif st in ('⏳ 进行中','进行中'): stats_after['progress'] += 1
    else: stats_after['pending'] += 1

# 更新meta
data['meta']['task_cleanup'] = {
    "version":"1.0","executed_at":now,
    "before":stats_before,"after":stats_after,
    "p0_done":changes['p0_done'],"p0_progress":changes['p0_progress'],
    "p1_progress":changes['p1_progress'],"p2_progress":changes['p2_progress']
}

with open(path, 'w') as f: json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 任务清零完成")
print(f"   P0→已完成: {changes['p0_done']}")
print(f"   P0→进行中: {changes['p0_progress']}")
print(f"   P1→进行中: {changes['p1_progress']}")
print(f"   P2→进行中: {changes['p2_progress']}")
print(f"   未匹配: {changes['unchanged']}")
print(f"   之前: 已完成{stats_before['done']}·进行中{stats_before['progress']}·待执行{stats_before['pending']}")
print(f"   现在: 已完成{stats_after['done']}·进行中{stats_after['progress']}·待执行{stats_after['pending']}")
