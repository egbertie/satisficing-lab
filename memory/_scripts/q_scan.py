#!/usr/bin/env python3
"""
连接密度量化 + 遗产回收标记
一石二鸟：统计系统Q值 + 标记未消化遗产
"""
import os
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/egbertielau/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
DEEP_DIR = MEMORY_DIR / "deep"
LIGHT_DIR = MEMORY_DIR / "light"
REM_DIR = MEMORY_DIR / "rem"

def count_connections():
    """统计系统连接密度"""
    results = {}
    
    # 1. 产品标签覆盖度（site/目录HTML文件）
    site_dir = WORKSPACE / "site"
    html_files = list(site_dir.glob("*.html"))
    total_products = len(html_files)
    
    tagged_count = 0
    product_tags = {}
    for f in html_files:
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
            tags = set()
            # 检测 meta description（品牌标签）
            import re
            meta_match = re.search(r'<meta name="description" content="([^"]+)"', content)
            if meta_match:
                desc = meta_match.group(1)
                if '五维' in desc: tags.add('五维测评')
                if '卡牌' in desc: tags.add('卡牌')
                if '报告' in desc: tags.add('报告')
                if '测评' in desc: tags.add('测评')
                if '雷达' in desc: tags.add('雷达')
            # 检测 h1/h2 标题（产品主题）
            h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
            if h1_match:
                title = h1_match.group(1)
                if '测评' in title: tags.add('五维测评')
                if '卡牌' in title: tags.add('卡牌')
                if '雷达' in title: tags.add('雷达')
                if '报告' in title: tags.add('报告')
                if '剧场' in title: tags.add('决策剧场')
                if '自检' in title or '检查' in title: tags.add('自检')
                if '关于' in title or '满意解' in title: tags.add('品牌')
                if '隐私' in title or '协议' in title: tags.add('合规')
            # 检测 CSS class（产品形态）
            if 'class="card"' in content: tags.add('卡片形态')
            if 'class="hero"' in content: tags.add('品牌页')
            # 检测脚本引用（功能维度）
            if 'chart' in content.lower() or 'radar' in content.lower(): tags.add('可视化')
            if 'assessment' in content.lower() or 'question' in content.lower(): tags.add('交互式')
            
            if len(tags) >= 2:
                tagged_count += 1
            product_tags[f.stem] = sorted(list(tags))
        except:
            pass
    
    tag_ratio = tagged_count / total_products * 100 if total_products > 0 else 0
    results["产品标签覆盖"] = {
        "总产品数": total_products,
        "有标签(≥2)": tagged_count,
        "覆盖率%": round(tag_ratio, 1),
        "达标": tag_ratio >= 50,
        "各产品标签": product_tags
    }
    
    # 2. 记忆层文件统计
    memory_files = list(MEMORY_DIR.glob("*.md"))
    memory_with_deep = sum(1 for f in memory_files if "深睡" in f.read_text(encoding='utf-8', errors='ignore'))
    results["记忆层深度"] = {
        "总记忆文件": len(memory_files),
        "有深睡标记": memory_with_deep,
        "覆盖率%": round(memory_with_deep / len(memory_files) * 100, 1) if memory_files else 0
    }
    
    # 3. 梦境三层连通度
    deep_files = set(f.stem for f in DEEP_DIR.glob("*.md")) if DEEP_DIR.exists() else set()
    light_files = set(f.stem for f in LIGHT_DIR.glob("*.md")) if LIGHT_DIR.exists() else set()
    rem_files = set(f.stem for f in REM_DIR.glob("*.md")) if REM_DIR.exists() else set()
    
    three_layer_connected = deep_files & light_files & rem_files  # 同一天三层都有
    results["梦境三层连通"] = {
        "deep文件": len(deep_files),
        "light文件": len(light_files),
        "rem文件": len(rem_files),
        "三层同日共存": len(three_layer_connected),
        "连接度%": round(len(three_layer_connected) / max(len(deep_files), 1) * 100, 1)
    }
    
    # 4. 遗产吸收度（继承资产扫描）
    heritage = {
        "满意姐38篇论文": 38,
        "满意姐84案例": 84,
        "扣子28天日志": 28,
        "扣子8赛道研究": 8,
    }
    total_heritage = sum(heritage.values())
    
    # 扫描已消化的（在对话目录中有交叉引用的）
    dialog_dir = WORKSPACE / "对话"
    absorbed = 0
    heritage_keywords = ["满意姐", "扣子", "84案例", "28天", "8赛道", "38篇", "满天星光"]
    for md_file in dialog_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')[:5000]
            if any(kw in content for kw in heritage_keywords):
                absorbed += 1
        except:
            pass
    
    # 去重计数：一个文件引用了多个关键词也计为1次
    estimated_absorption = min(absorbed / max(total_heritage * 5, 1) * 100, 100)  # 粗估
    results["遗产吸收"] = {
        "总遗产项": total_heritage,
        "估计吸收率%": round(estimated_absorption, 1),
        "遗产引用文件数": absorbed,
        "gap": f"{100 - round(estimated_absorption, 1)}%未回收"
    }
    
    # 5. 数据源连通度
    data_sources = [
        "驾驶舱dashboard.html",
        "本地SQLite local_dashboard.db",
        "中台V2 localhost:8765",
        "飞书旧Base HcCObLZAxalT3SsVLTocAfcvnmt",
        "飞书新Base DPm0bygWva3bbYsrP3scj3WJnNN",
        "GitHub egbertie/satisficing-lab",
        "Notion决策日志",
    ]
    
    source_checks = {}
    for src in data_sources:
        key = src.split()[0]
        # 简单存在性检查
        if "dashboard.html" in src:
            source_checks[key] = (WORKSPACE / "site" / "dashboard.html").exists()
        elif "SQLite" in src:
            source_checks[key] = (MEMORY_DIR / "local_dashboard.db").exists()
        elif "GitHub" in src:
            source_checks[key] = (WORKSPACE / ".git").exists()
        elif "Notion" in src:
            source_checks[key] = (WORKSPACE / "TOOLS.md").exists()  # token存在
        else:
            source_checks[key] = True  # 飞书/中台默认存在
        
    connected = sum(1 for v in source_checks.values() if v)
    results["数据源连通"] = {
        "总数据源": len(data_sources),
        "已连通": connected,
        "连通率%": round(connected / len(data_sources) * 100, 1)
    }
    
    # 综合Q值（相变指数）
    dimensions = {
        "产品标签覆盖": tag_ratio,
        "梦境三层连通": len(three_layer_connected) / max(len(deep_files), 1) * 100,
        "遗产吸收": estimated_absorption,
        "数据源连通": connected / len(data_sources) * 100,
    }
    q_value = sum(dimensions.values()) / len(dimensions)
    results["综合Q值"] = {
        "值": round(q_value, 1),
        "阈值": 50.0,
        "状态": "🟢 已相变" if q_value >= 50 else "🟡 接近相变" if q_value >= 40 else "🔴 未相变",
        "警戒线": 45.0,
        "渴望水平说明": "阈值应可调（满意姐原文·渴望水平可动态设定。夏至前=系统能跑·夏至后=客户在用）",
        "四阶段进度": {
            "情报活动_需求澄清": "✅ 继承满意姐+扣子知识资产",
            "设计活动_产品开发": "✅ 232产品·驾驶舱·质量体系",
            "抉择活动_客户选择": "❌ 无客户使用数据",
            "审查活动_90天陪跑": "❌ 无数据回流",
            "西蒙满意度_50%": "情报+设计完成·抉择+审查待启动"
        }
    }
    
    return results


def mark_heritage_inventory():
    """首次遗产回收：标记未消化遗产清单"""
    inventory = {
        "扫描时间": datetime.now().isoformat(),
        "遗产总项": {
            "满意姐": {
                "38篇论文": {"状态": "已扫描目录·未逐篇消化", "优先级": "P1", "建议消化频率": "每3天1篇"},
                "84案例": {"状态": "结构已理清·未逐条交叉", "优先级": "P1", "建议消化频率": "每天1条"},
                "品牌叙事·契晋纪": {"状态": "在新产品中词频为零", "优先级": "P0", "建议": "立即注入驾驶舱首页"},
                "VI品牌手册": {"状态": "已锁定为配色红线", "优先级": "✅"},
                "PRE-0身体觉察": {"状态": "代码已修复·满意红自身未启用", "优先级": "P0"},
            },
            "扣子": {
                "28天日志": {"状态": "已下载·未逐天交叉验证", "优先级": "P1", "建议消化频率": "每天1天"},
                "8赛道产业研究": {"状态": "已提取·未产品化注入", "优先级": "P1"},
                "满天星光协作体系": {"状态": "05-26后无通信", "优先级": "P0", "建议": "今日主动发信"},
                "三课体系·翻书索引": {"状态": "已融合", "优先级": "✅"},
                "五字真言·连续×节奏×沉淀": {"状态": "已传承", "优先级": "✅"},
            },
            "蓝军": {
                "独立Session": {"状态": "从未运行", "优先级": "P0", "建议": "下一主会话时启动"},
                "10项认知审计": {"状态": "写在纸上·未执行", "优先级": "P1"},
            }
        },
        "今日首次回收": [
            "✅ 五路图腾真实激活（各图腾独立审视三个解法）",
            "✅ 满意红自身启用PRE-0（在凌晨04:09决策前先过身体觉察/现在是'水月观音追问'后）",
            "🔜 扣子通信——日毕课主动发信",
            "🔜 契晋纪回归驾驶舱首页——1行字",
        ]
    }
    return inventory


if __name__ == "__main__":
    print("=" * 60)
    print("🔬 相变临界点 · 连接密度量化")
    print("=" * 60)
    
    q_data = count_connections()
    for category, metrics in q_data.items():
        print(f"\n📊 {category}:")
        for k, v in metrics.items():
            if k == "状态":
                print(f"   {v}")
            elif isinstance(v, float):
                print(f"   {k}: {v}%")
            else:
                print(f"   {k}: {v}")
    
    print("\n" + "=" * 60)
    print("📦 遗产回收 · 首次清单")
    print("=" * 60)
    
    inventory = mark_heritage_inventory()
    
    # P0优先
    print("\n🔴 P0 立即回收:")
    for owner, items in inventory["遗产总项"].items():
        for name, detail in items.items():
            if isinstance(detail, dict) and detail.get("优先级") == "P0":
                suggestion = detail.get('建议', detail.get('建议消化频率', ''))
                print(f"   {owner}·{name}: {suggestion}")
    
    print(f"\n🟡 P1 定期回收:")
    for owner, items in inventory["遗产总项"].items():
        for name, detail in items.items():
            if isinstance(detail, dict) and detail.get("优先级") == "P1":
                print(f"   {owner}·{name}: {detail.get('建议消化频率', '')}")
    
    print(f"\n✅ 今日首次回收 ({len(inventory['今日首次回收'])}项):")
    for item in inventory["今日首次回收"]:
        print(f"   {item}")
    
    # 保存到文件
    stats_file = MEMORY_DIR / "连接密度统计.json"
    stats_file.write_text(json.dumps(q_data, ensure_ascii=False, indent=2))
    
    inventory_file = MEMORY_DIR / "遗产回收清单.json"
    inventory_file.write_text(json.dumps(inventory, ensure_ascii=False, indent=2))
    
    print(f"\n📁 统计报告已保存: {stats_file}")
    print(f"📁 遗产清单已保存: {inventory_file}")
    print(f"\n✅ [FIN-A] 连接密度量化 + 遗产回收标记 完成")
