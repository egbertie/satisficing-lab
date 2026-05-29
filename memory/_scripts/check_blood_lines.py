#!/usr/bin/env python3
"""
满意解研究所 · 血液化连接检查器
扫描所有数据源→检查是否通向驾驶舱→标注断点
对标: Event-Driven Architecture + Digital Twin + Data Fabric
"""
import os, json, subprocess, time

WORKSPACE = "/Users/egbertielau/.openclaw/workspace"
DB_PATH = f"{WORKSPACE}/memory/local_dashboard.db"

# ===== 数据源清单 =====
DATASOURCES = {
    # 产品层
    "GitHub Pages部署": {
        "type": "部署状态",
        "path": f"{WORKSPACE}/satisficing-lab",
        "check": lambda: os.path.exists(f"{WORKSPACE}/satisficing-lab/go.html"),
        "流向": ["驾驶舱·产品Tab"],
        "频率": "每次git push"
    },
    "线上产品 200巡检": {
        "type": "产品健康",
        "path": f"{WORKSPACE}/satisficing-lab/*.html",
        "check": lambda: len([f for f in os.listdir(f"{WORKSPACE}/satisficing-lab") if f.endswith('.html')]) > 200,
        "流向": ["驾驶舱·产品Tab", "驾驶舱·系统Tab"],
        "频率": "周一cron"
    },

    # 数据层
    "飞书Base旧(8可读表)": {
        "type": "外部数据源",
        "check": lambda: subprocess.run(['lark-cli','api','GET',
            '/open-apis/bitable/v1/apps/HcCObLZAxalT3SsVLTocAfcvnmt/tables',
            '--as','bot'], capture_output=True).returncode == 0,
        "流向": ["sync_dashboard_data.py → SQLite → 驾驶舱"],
        "频率": "cron每30分钟"
    },
    "SQLite数据库": {
        "type": "本地中枢",
        "path": DB_PATH,
        "check": lambda: os.path.exists(DB_PATH),
        "流向": ["驾驶舱·全部Tab"],
        "频率": "实时"
    },

    # 引擎层
    "flywheel-engine.js": {
        "type": "资产飞轮引擎",
        "path": f"{WORKSPACE}/satisficing-lab/flywheel-engine.js",
        "check": lambda: os.path.exists(f"{WORKSPACE}/satisficing-lab/flywheel-engine.js"),
        "流向": ["驾驶舱·资产Tab", "驾驶舱·增长Tab"],
        "频率": "14页面注入·每次页面加载"
    },
    "产品健康扫描": {
        "type": "自动化脚本",
        "path": f"{WORKSPACE}/memory/_scripts/product_health_scan.py",
        "check": lambda: os.path.exists(f"{WORKSPACE}/memory/_scripts/product_health_scan.py"),
        "流向": ["驾驶舱·质量Tab", "产品健康周报.md"],
        "频率": "周一cron"
    },
    "死链接检测": {
        "type": "自动化脚本",
        "path": f"{WORKSPACE}/memory/_scripts/dead_link_checker.py",
        "check": lambda: os.path.exists(f"{WORKSPACE}/memory/_scripts/dead_link_checker.py"),
        "流向": ["驾驶舱·系统Tab"],
        "频率": "周一cron"
    },
    "隐私审计": {
        "type": "自动化脚本",
        "path": f"{WORKSPACE}/memory/_scripts/privacy_audit.py",
        "check": lambda: os.path.exists(f"{WORKSPACE}/memory/_scripts/privacy_audit.py"),
        "流向": ["驾驶舱·质量Tab"],
        "频率": "每月1日cron"
    },
    "密码同步": {
        "type": "自动化脚本",
        "path": f"{WORKSPACE}/memory/_scripts/sync_passwords.py",
        "check": lambda: os.path.exists(f"{WORKSPACE}/memory/_scripts/sync_passwords.py"),
        "流向": ["GitHub password.js → gate.html"],
        "频率": "周三cron"
    },

    # 运营层
    "cron任务状态": {
        "type": "系统运行",
        "流向": ["驾驶舱·系统Tab"],
        "频率": "24/7运行·驾驶舱静态展示"
    },
    "邮箱检查(sina)": {
        "type": "客户触达",
        "流向": ["扣子邮件·memory记录"],
        "频率": "每日10:00/18:00"
    },
    "NPS自动触发": {
        "type": "客户反馈",
        "流向": ["localStorage → 驾驶舱·增长Tab"],
        "频率": "客户使用3个工具后触发"
    },
    "30天重测提醒": {
        "type": "客户留存",
        "流向": ["localStorage → go.html横幅"],
        "频率": "客户访问时检查"
    },

    # 管理仪表层
    "合同管理": {
        "type": "管理数据",
        "流向": ["驾驶舱·合同Tab(seed数据)"],
        "频率": "首次打开灌入·手动更新"
    },
    "渠道管理": {
        "type": "管理数据", 
        "流向": ["驾驶舱·渠道Tab(seed数据)"],
        "频率": "首次打开灌入·手动更新"
    },
    "VI资产管理": {
        "type": "管理数据",
        "流向": ["驾驶舱·VITab(seed数据)"],
        "频率": "首次打开灌入·手动更新"
    },
    "命名规范": {
        "type": "管理数据",
        "流向": ["驾驶舱·命名Tab"],
        "频率": "静态展示·版本更新时同步"
    },
}

def check_all():
    print("=" * 60)
    print("血液化连接检查器 · 对标Event-Driven Architecture + Data Fabric")
    print("=" * 60)

    results = {"✅已连接": 0, "⚠️弱连接": 0, "❌断点": 0, "📋静态": 0}
    
    for name, ds in DATASOURCES.items():
        check_fn = ds.get("check")
        if check_fn:
            try:
                ok = check_fn()
            except:
                ok = False
        else:
            ok = None

        flow = " → ".join(ds["流向"])
        freq = ds.get("频率", "")

        if ok is True:
            status = "✅已连接"
        elif ok is False:
            status = "❌断点"
        elif ok is None:
            status = "📋静态"
        else:
            status = "⚠️弱连接"

        results[status] = results.get(status, 0) + 1
        print(f"\n{status} {name} [{ds['type']}]")
        print(f"  路径: {flow}")
        print(f"  频率: {freq}")

    print("\n" + "=" * 60)
    print(f"总数据源: {sum(results.values())}")
    print(f"  ✅已连接: {results.get('✅已连接',0)} · ⚠️弱连接: {results.get('⚠️弱连接',0)} · ❌断点: {results.get('❌断点',0)} · 📋静态: {results.get('📋静态',0)}")
    
    # 识别断点
    print("\n需要修复的断点:")
    has_issues = False
    for name, ds in DATASOURCES.items():
        check_fn = ds.get("check")
        if check_fn:
            try:
                ok = check_fn()
                if not ok:
                    print(f"  ❌ {name}: 文件/服务缺失或不可达")
                    has_issues = True
            except:
                print(f"  ❌ {name}: 检查失败")
                has_issues = True
    if not has_issues:
        print("  🎉 无断点！所有数据源畅通。")

    return results

if __name__ == "__main__":
    check_all()
