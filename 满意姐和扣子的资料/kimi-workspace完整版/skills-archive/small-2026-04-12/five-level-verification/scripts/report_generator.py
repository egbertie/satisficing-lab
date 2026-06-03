#!/usr/bin/env python3
"""
Report Generator
生成格式化的验证报告
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


class ReportGenerator:
    """验证报告生成器"""
    
    def __init__(self, verification_result: Dict):
        self.result = verification_result
    
    def generate_markdown(self) -> str:
        """生成Markdown格式报告"""
        skill = self.result.get("skill", "Unknown")
        timestamp = self.result.get("timestamp", datetime.now().isoformat())
        overall = self.result.get("overall_level", "L0")
        results = self.result.get("results", {})
        summary = self.result.get("summary", {})
        next_steps = self.result.get("next_steps", [])
        
        report = f"""# Five-Level Verification Report

**Skill**: `{skill}`  
**验证时间**: {timestamp}  
**总体级别**: {overall}  
**标准版本**: 7-Standard-v5

---

## 验证结果摘要

| 级别 | 名称 | 状态 | 得分 |
|------|------|------|------|
"""
        
        for level in ["L1", "L2", "L3", "L4", "L5"]:
            if level in results:
                r = results[level]
                status = "✅ 通过" if r.get("passed") else "❌ 未通过"
                if level == "L5" and r.get("requires_manual"):
                    status = "⚠️  需人工"
                score = r.get("score", 0)
                name = r.get("name", level)
                report += f"| {level} | {name} | {status} | {score}% |\n"
        
        report += "\n---\n\n## 详细检查项\n\n"
        
        for level in ["L1", "L2", "L3", "L4", "L5"]:
            if level in results:
                r = results[level]
                report += f"### {level}: {r.get('name', level)}\n\n"
                
                checks = r.get("checks", {})
                if checks:
                    report += "| 检查项 | 状态 |\n"
                    report += "|--------|------|\n"
                    for check, passed in checks.items():
                        status = "✅" if passed else "❌"
                        report += f"| {check} | {status} |\n"
                
                if "warnings" in r:
                    report += "\n**警告**:\n"
                    for w in r["warnings"]:
                        report += f"- ⚠️ {w}\n"
                
                report += "\n"
        
        # 问题列表
        issues = summary.get("issues", [])
        if issues:
            report += "---\n\n## 发现的问题\n\n"
            for i, issue in enumerate(issues, 1):
                report += f"{i}. {issue}\n"
            report += "\n"
        
        # 修复建议
        recommendations = summary.get("recommendations", [])
        if recommendations:
            report += "---\n\n## 修复建议\n\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
            report += "\n"
        
        # 下一步
        if next_steps:
            report += "---\n\n## 下一步行动\n\n"
            for step in next_steps:
                report += f"- [ ] {step}\n"
            report += "\n"
        
        # 标准符合性
        if "S5_compliance" in results:
            s5 = results["S5_compliance"]
            report += "---\n\n## S5: 标准一致性验证\n\n"
            report += f"**符合度**: {s5.get('score', 0)}%\n\n"
            
            compliance = s5.get("compliance", {})
            report += "| 标准 | 状态 |\n"
            report += "|------|------|\n"
            for std, passed in compliance.items():
                status = "✅" if passed else "❌"
                report += f"| {std} | {status} |\n"
            report += "\n"
        
        report += f"""---

*报告生成时间: {datetime.now().isoformat()}*  
*Five-Level Verification System V5.0*
"""
        
        return report
    
    def generate_html(self) -> str:
        """生成HTML格式报告"""
        skill = self.result.get("skill", "Unknown")
        overall = self.result.get("overall_level", "L0")
        
        # 根据级别确定颜色
        color_map = {
            "L1": "#ff6b6b",
            "L2": "#feca57",
            "L3": "#48dbfb",
            "L4": "#1dd1a1",
            "L5": "#5f27cd"
        }
        color = color_map.get(overall, "#95a5a6")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Verification Report - {skill}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid {color}; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; font-weight: 600; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        .level-badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-weight: bold; }}
        .status-pass {{ color: #27ae60; }}
        .status-fail {{ color: #e74c3c; }}
        .status-warn {{ color: #f39c12; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .summary {{ background: linear-gradient(135deg, {color}20, {color}05); padding: 20px; border-radius: 10px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>🔍 Five-Level Verification Report</h1>
    
    <div class="summary">
        <h2>摘要</h2>
        <p><strong>Skill:</strong> <code>{skill}</code></p>
        <p><strong>总体级别:</strong> <span class="level-badge" style="background-color: {color}20; color: {color};">{overall}</span></p>
        <p><strong>验证时间:</strong> {self.result.get("timestamp", "N/A")}</p>
    </div>
"""
        
        # 添加详细结果
        html += "    <h2>详细结果</h2>\n    <table>\n"
        html += "        <tr><th>级别</th><th>名称</th><th>状态</th><th>得分</th></tr>\n"
        
        for level in ["L1", "L2", "L3", "L4", "L5"]:
            if level in self.result.get("results", {}):
                r = self.result["results"][level]
                status_class = "status-pass" if r.get("passed") else "status-fail"
                status_text = "通过" if r.get("passed") else "未通过"
                if level == "L5" and r.get("requires_manual"):
                    status_class = "status-warn"
                    status_text = "需人工"
                
                html += f"        <tr><td>{level}</td><td>{r.get('name', level)}</td>"
                html += f"<td class='{status_class}'>{status_text}</td>"
                html += f"<td>{r.get('score', 0)}%</td></tr>\n"
        
        html += "    </table>\n"
        
        # 添加问题
        issues = self.result.get("summary", {}).get("issues", [])
        if issues:
            html += "    <h2>⚠️ 发现的问题</h2>\n    <ol>\n"
            for issue in issues:
                html += f"        <li>{issue}</li>\n"
            html += "    </ol>\n"
        
        html += "</body>\n</html>"
        
        return html
    
    def save(self, output_dir: str = "./reports"):
        """保存报告"""
        os.makedirs(output_dir, exist_ok=True)
        skill = self.result.get("skill", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON
        json_path = os.path.join(output_dir, f"{skill}_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(self.result, f, indent=2, ensure_ascii=False)
        
        # Markdown
        md_path = os.path.join(output_dir, f"{skill}_{timestamp}.md")
        with open(md_path, 'w') as f:
            f.write(self.generate_markdown())
        
        # HTML
        html_path = os.path.join(output_dir, f"{skill}_{timestamp}.html")
        with open(html_path, 'w') as f:
            f.write(self.generate_html())
        
        return {
            "json": json_path,
            "markdown": md_path,
            "html": html_path
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="生成验证报告")
    parser.add_argument("--input", required=True, help="验证结果JSON文件")
    parser.add_argument("--format", default="all", 
                       choices=["json", "markdown", "html", "all"])
    parser.add_argument("--output", default="./reports", help="输出目录")
    
    args = parser.parse_args()
    
    with open(args.input, 'r') as f:
        result = json.load(f)
    
    generator = ReportGenerator(result)
    
    if args.format == "all":
        paths = generator.save(args.output)
        print("报告已生成:")
        for fmt, path in paths.items():
            print(f"  [{fmt.upper()}] {path}")
    elif args.format == "markdown":
        print(generator.generate_markdown())
    elif args.format == "html":
        print(generator.generate_html())


if __name__ == "__main__":
    main()
