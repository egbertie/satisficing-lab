#!/usr/bin/env python3
"""
KIA Batch Processor - 知识入库全闭环批处理引擎
版本: 1.0
日期: 2026-04-12

对指定目录下的全部 Markdown 文档执行标准化 KIA-Loop：
清点 -> 提取 -> 查重 -> 定级 -> 卡片化/血液化 -> 索引 -> 报告

使用方式:
  python3 scripts/kia-batch-processor.py
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE / "A-manyige/知识库/kia-batch-2026-04-12"
DOCS_DIRS = [
    WORKSPACE / "A-satisficing-v27",
    WORKSPACE / "B-egbertie-view",
    WORKSPACE / "research",
    WORKSPACE / "docs",
]

# 分类规则：路径/文件名正则 -> tier
tier_rules = [
    # Tier 0: 必须深度血液化
    (r"李泽湘|黎红雷|方翊沣|陈国祥|谢宝剑|许若圣|罗汉|专家档案|数字替身", "T0"),
    (r"deep_insight|深度洞察|血液化|内化映射|第一性原理|满意解理论|知识体系", "T0"),
    (r"research/.*deep|research/.*insight|academic_foundation|external_response", "T0"),
    (r"文件处理标准|文件内化标准|编号决策协议|节点报告双位置|知识入库全闭环", "T0"),
    # Tier 1: 标准 KIA 卡片
    (r"README|INDEX|index|手册|指南|模板|SOP|V1\.[0-9]|V[0-9]\.[0-9]", "T1"),
    (r"产品.*手册|案例库|运营文档|工作空间|资源配置|项目状态|核心理论", "T1"),
    (r"决策框架|方法论|资产飞轮|经验挖掘|产品体系", "T1"),
    # Tier 2: 归档摘要（Working/草稿/待确认/旧版本）
    (r"Working|草稿|draft|待确认|待阅|旧版|deprecated|archive", "T2"),
]

def classify_tier(filepath):
    rel = str(filepath.relative_to(WORKSPACE))
    for pattern, tier in tier_rules:
        if re.search(pattern, rel, re.I):
            return tier
    return "T1"  # 默认标准卡片

def extract_title(content, filepath):
    lines = content.splitlines()
    # 优先 H1
    for line in lines[:20]:
        if line.startswith("# "):
            return line[2:].strip()
    # 次选 frontmatter title
    if lines and lines[0].strip() == "---":
        for line in lines[1:20]:
            if line.strip() == "---":
                break
            m = re.match(r'^title:\s*(.+)', line)
            if m:
                return m.group(1).strip()
    # 回退文件名
    return filepath.stem

def extract_summary(content, max_lines=8):
    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("-")]
    return " ".join(lines[:max_lines])[:300]

def content_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

def generate_kia_card(doc):
    tier = doc["tier"]
    lines = [
        f"# KIA-{doc['id']} | {doc['title']}",
        f"**来源**: `{doc['source']}`  ",
        f"**级别**: {tier}  **字数**: {doc['chars']:,}  **入库时间**: {doc['processed_at']}",
        f"**内容指纹**: `{doc['hash']}`",
        "",
        "## 核心摘要",
        doc['summary'],
        "",
    ]
    if tier == "T0":
        lines += [
            "## 血液化映射",
            "- **适用场景**: _待补充_",
            "- **可复用模块**: _待补充_",
            "- **与12类型案例库关联**: _待补充_",
            "- **与五路图腾关联**: _待补充_",
            "- **下一步行动**: _待补充_",
            "",
            "## 原始内容",
            f"见源文件: `{doc['source']}`",
        ]
    else:
        lines += [
            "## 定位与用法",
            "- **文档类型**: _待补充_",
            "- **快速入口**: 直接查阅源文件。",
        ]
    return "\n".join(lines)

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    registry = []
    hash_seen = {}
    dup_count = 0
    stats = {"T0": 0, "T1": 0, "T2": 0, "dup": 0}

    for base_dir in DOCS_DIRS:
        if not base_dir.exists():
            continue
        for filepath in sorted(base_dir.rglob("*.md")):
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            h = content_hash(content)
            if h in hash_seen:
                dup_count += 1
                stats["dup"] += 1
                continue
            hash_seen[h] = str(filepath.relative_to(WORKSPACE))

            tier = classify_tier(filepath)
            stats[tier] += 1

            doc = {
                "id": f"{tier}-{len(registry)+1:04d}",
                "source": str(filepath.relative_to(WORKSPACE)),
                "title": extract_title(content, filepath),
                "chars": len(content),
                "hash": h,
                "tier": tier,
                "summary": extract_summary(content),
                "processed_at": datetime.now().isoformat(),
            }
            registry.append(doc)

            # 落盘 KIA 卡片
            card_path = OUTPUT_DIR / f"{doc['id']}.md"
            card_path.write_text(generate_kia_card(doc), encoding="utf-8")

    # 主索引
    registry_path = OUTPUT_DIR / "registry.json"
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    # 总报告
    t0_items = [d for d in registry if d["tier"] == "T0"]
    report_lines = [
        f"# KIA 批量入库全景报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 执行统计",
        f"- **处理文档总数**: {len(registry)} 份",
        f"- **去重剔除**: {dup_count} 份",
        f"- **T0 深度血液化**: {stats['T0']} 份",
        f"- **T1 标准卡片**: {stats['T1']} 份",
        f"- **T2 归档摘要**: {stats['T2']} 份",
        "",
        "## T0 高价值文档清单（需补充血液化内容）",
    ]
    for doc in t0_items:
        report_lines.append(f"- `{doc['id']}` [{doc['title']}]({doc['source']})")
    report_lines += [
        "",
        "## KIA-Loop 状态",
        "- [x] 接收清点",
        "- [x] 轻量提取",
        "- [x] 查重去冗",
        "- [x]  tier 分级",
        "- [x] 卡片化/血液化骨架生成",
        "- [ ] 高价值文档深度内容补完（T0）",
        "- [ ] Git 归档锁定",
        "",
        f"输出目录: `{OUTPUT_DIR.relative_to(WORKSPACE)}`",
    ]
    report_path = OUTPUT_DIR / "KIA--batch-report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"[KIA Batch] 完成")
    print(f"  注册文档: {len(registry)}")
    print(f"  去重剔除: {dup_count}")
    print(f"  T0/T1/T2: {stats['T0']}/{stats['T1']}/{stats['T2']}")
    print(f"  输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
