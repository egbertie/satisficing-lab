#!/usr/bin/env python3
"""
sensitive_word_guardian.py
Scans A-manyige/ docs for banned sensitive words on mainland China.
违规即写入审计报告，强行血液化脱敏规则。
"""
import os
import datetime

WORKSPACE = "/root/.openclaw/workspace"
TARGET_DIR = os.path.join(WORKSPACE, "A-manyige")
REPORT_DIR = os.path.join(TARGET_DIR, "审计")
# 用户明确要求的脱敏词库
BANNED = ["能量治疗", "宗教", "禅修", "打坐", "开光", "法术", "通灵"]
SAFE_REPLACEMENTS = {
    "能量治疗": "身心恢复",
    "宗教": "文化信仰",
    "禅修": "正念训练",
    "打坐": "静坐放松",
    "开光": "仪式祝福",
    "法术": "传统技艺",
    "通灵": "直觉感知"
}


def scan():
    violations = []
    for root, _, files in os.walk(TARGET_DIR):
        for fname in files:
            if not fname.lower().endswith((".md", ".txt", ".docx", ".doc")):
                continue
            fpath = os.path.join(root, fname)
            try:
                # Simple text read for md/txt; skip binary-like docx content
                if fname.lower().endswith(".docx"):
                    # crude scan: read as binary and decode with errors=ignore
                    with open(fpath, "rb") as f:
                        text = f.read().decode("utf-8", errors="ignore")
                else:
                    with open(fpath, "r", encoding="utf-8") as f:
                        text = f.read()
            except Exception:
                continue
            found = [w for w in BANNED if w in text]
            if found:
                violations.append((fpath, found))
    return violations


def write_report(violations):
    os.makedirs(REPORT_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = os.path.join(REPORT_DIR, f"sensitive_word_guardian_{today}.md")
    lines = [
        f"# 敏感词守护报告 ({today})",
        f"\n违规文件数: **{len(violations)}**\n",
        "| 文件路径 | 敏感词 | 推荐替换 |",
        "|----------|--------|----------|"
    ]
    for fpath, words in violations:
        recs = ", ".join(SAFE_REPLACEMENTS.get(w, "需人工脱敏") for w in words)
        lines.append(f"| {fpath} | {', '.join(words)} | {recs} |")
    lines.append("\n---\n**Action**: 立即修正上表文件中的敏感词，否则禁止对外发布。")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    v = scan()
    if v:
        p = write_report(v)
        print(f"ALERT: {len(v)} files with banned words -> {p}")
    else:
        print("OK: No banned words found in A-manyige/")


if __name__ == "__main__":
    main()
