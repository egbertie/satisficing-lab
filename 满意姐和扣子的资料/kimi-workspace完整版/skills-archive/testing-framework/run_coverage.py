#!/usr/bin/env python3
"""
覆盖率报告生成器 - S3标准实现

功能:
- 生成多格式覆盖率报告（HTML/XML/JSON）
- 检查覆盖率阈值
- 趋势分析
- 未覆盖代码高亮

使用方法:
    python run_coverage.py                    # 生成默认报告
    python run_coverage.py --threshold 80     # 设置阈值
    python run_coverage.py --skill zero_idle  # 单Skill报告
    python run_coverage.py --trend            # 显示趋势
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent
REPORTS_DIR = PROJECT_ROOT / "reports"
COVERAGE_DIR = REPORTS_DIR / "coverage"
HISTORY_FILE = REPORTS_DIR / "coverage_history.json"

DEFAULT_THRESHOLD = 80


def run_command(cmd: List[str], cwd: Path = None) -> Tuple[int, str, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "命令超时"
    except Exception as e:
        return 1, "", str(e)


def generate_coverage(skill: str = None, output_dir: Path = None) -> Dict[str, Any]:
    """生成覆盖率报告"""
    output_dir = output_dir or COVERAGE_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    workspace_skills = str(Path("/root/.openclaw/workspace/skills"))
    
    print("=" * 60)
    print("生成覆盖率报告")
    print("=" * 60)
    
    # 构建pytest命令
    cmd = [
        "python3", "-m", "pytest",
        "tests/",
        f"--cov={workspace_skills}",
        f"--cov-report=html:{output_dir}",
        f"--cov-report=xml:{REPORTS_DIR / 'coverage.xml'}",
        f"--cov-report=json:{REPORTS_DIR / 'coverage.json'}",
        "--cov-report=term-missing",
        "-q"
    ]
    
    if skill:
        marker_map = {
            "zero_idle": "zero_idle",
            "zero-idle": "zero_idle",
            "token_budget": "token_budget",
            "token-budget": "token_budget",
            "blue_sentinel": "blue_sentinel",
            "blue-sentinel": "blue_sentinel"
        }
        marker = marker_map.get(skill.lower(), skill.lower())
        cmd.extend(["-m", marker])
        
        # 按 skill 精确指定源码路径，避免被未测试模块稀释
        skill_dir_map = {
            "zero_idle": "zero-idle-enforcer",
            "zero-idle": "zero-idle-enforcer",
            "token_budget": "token-budget-enforcer",
            "token-budget": "token-budget-enforcer",
            "blue_sentinel": "blue-sentinel",
            "blue-sentinel": "blue-sentinel"
        }
        skill_dir = skill_dir_map.get(skill.lower())
        if skill_dir:
            cmd[cmd.index(f"--cov={workspace_skills}")] = f"--cov={workspace_skills}/{skill_dir}"
        print(f"仅生成 {skill} 的覆盖率报告")
    
    returncode, stdout, stderr = run_command(cmd)
    
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    
    # 解析覆盖率数据
    coverage_data = parse_coverage_json(REPORTS_DIR / "coverage.json")
    
    # 生成摘要
    summary = {
        "timestamp": datetime.now().isoformat(),
        "skill": skill or "all",
        "success": returncode == 0,
        "line_coverage": coverage_data.get("line_coverage", 0),
        "branch_coverage": coverage_data.get("branch_coverage", 0),
        "function_coverage": coverage_data.get("function_coverage", 0),
        "total_lines": coverage_data.get("total_lines", 0),
        "missed_lines": coverage_data.get("missed_lines", 0)
    }
    
    # 保存摘要
    summary_file = REPORTS_DIR / "coverage_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n报告已生成:")
    print(f"  - HTML报告: {output_dir}/index.html")
    print(f"  - XML报告: {REPORTS_DIR / 'coverage.xml'}")
    print(f"  - JSON报告: {REPORTS_DIR / 'coverage.json'}")
    print(f"  - 摘要: {summary_file}")
    
    return summary


def parse_coverage_json(json_path: Path) -> Dict[str, Any]:
    """解析覆盖率JSON文件"""
    if not json_path.exists():
        return {
            "line_coverage": 0,
            "branch_coverage": 0,
            "function_coverage": 0,
            "total_lines": 0,
            "missed_lines": 0
        }
    
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        
        # 计算总体覆盖率
        totals = data.get("totals", {})
        return {
            "line_coverage": totals.get("covered_lines", 0) / max(totals.get("num_statements", 1), 1) * 100,
            "branch_coverage": totals.get("covered_branches", 0) / max(totals.get("num_branches", 1), 1) * 100,
            "function_coverage": 0,  # pytest-cov不直接提供
            "total_lines": totals.get("num_statements", 0),
            "missed_lines": totals.get("missing_lines", 0)
        }
    except Exception as e:
        print(f"解析覆盖率JSON失败: {e}", file=sys.stderr)
        return {
            "line_coverage": 0,
            "branch_coverage": 0,
            "function_coverage": 0,
            "total_lines": 0,
            "missed_lines": 0
        }


def check_threshold(threshold: int, skill: str = None) -> bool:
    """检查覆盖率是否达到阈值"""
    print("=" * 60)
    print(f"检查覆盖率阈值: {threshold}%")
    print("=" * 60)
    
    summary_file = REPORTS_DIR / "coverage_summary.json"
    
    if not summary_file.exists():
        print("未找到覆盖率摘要，先生成报告...")
        generate_coverage(skill)
    
    with open(summary_file, "r") as f:
        summary = json.load(f)
    
    line_coverage = summary.get("line_coverage", 0)
    
    if line_coverage >= threshold:
        print(f"✅ 覆盖率达标: {line_coverage:.2f}% >= {threshold}%")
        return True
    else:
        print(f"❌ 覆盖率未达标: {line_coverage:.2f}% < {threshold}%")
        print(f"   缺失行数: {summary.get('missed_lines', 0)}")
        return False


def show_trend():
    """显示覆盖率趋势"""
    print("=" * 60)
    print("覆盖率趋势")
    print("=" * 60)
    
    if not HISTORY_FILE.exists():
        print("暂无历史数据")
        return
    
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    
    if len(history) < 2:
        print("历史数据不足（需要至少2次记录）")
        return
    
    print(f"{'日期':<20} {'行覆盖率':<10} {'分支覆盖率':<10} {'变化':<10}")
    print("-" * 60)
    
    prev_line = None
    for entry in history[-10:]:  # 显示最近10次
        line_cov = entry.get("line_coverage", 0)
        branch_cov = entry.get("branch_coverage", 0)
        timestamp = entry.get("timestamp", "")[:19]
        
        change = ""
        if prev_line is not None:
            delta = line_cov - prev_line
            change = f"{delta:+.2f}%"
        
        print(f"{timestamp:<20} {line_cov:>8.2f}% {branch_cov:>8.2f}% {change:<10}")
        prev_line = line_cov


def save_to_history(summary: Dict[str, Any]):
    """保存到历史记录"""
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    
    history.append(summary)
    
    # 只保留最近100条
    history = history[-100:]
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def generate_uncovered_report():
    """生成未覆盖代码报告"""
    print("=" * 60)
    print("未覆盖代码分析")
    print("=" * 60)
    
    json_path = REPORTS_DIR / "coverage.json"
    if not json_path.exists():
        print("未找到覆盖率数据")
        return
    
    with open(json_path, "r") as f:
        data = json.load(f)
    
    uncovered = []
    for file_path, file_data in data.get("files", {}).items():
        missing_lines = file_data.get("missing_lines", [])
        if missing_lines:
            uncovered.append({
                "file": file_path,
                "missing_lines": missing_lines,
                "missing_count": len(missing_lines)
            })
    
    # 按缺失行数排序
    uncovered.sort(key=lambda x: x["missing_count"], reverse=True)
    
    print(f"\n未覆盖文件数: {len(uncovered)}")
    print(f"{'文件':<50} {'未覆盖行数':<10}")
    print("-" * 60)
    
    for item in uncovered[:20]:  # 显示前20个
        file_name = item["file"][-47:]  # 截断显示
        print(f"{file_name:<50} {item['missing_count']:<10}")
    
    # 保存详细报告
    report_file = REPORTS_DIR / "uncovered_lines.json"
    with open(report_file, "w") as f:
        json.dump(uncovered, f, indent=2)
    
    print(f"\n详细报告: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description="覆盖率报告生成器"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"覆盖率阈值 (默认: {DEFAULT_THRESHOLD}%)"
    )
    parser.add_argument(
        "--skill",
        type=str,
        help="指定Skill生成报告"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(COVERAGE_DIR),
        help="输出目录"
    )
    parser.add_argument(
        "--trend",
        action="store_true",
        help="显示覆盖率趋势"
    )
    parser.add_argument(
        "--uncovered",
        action="store_true",
        help="生成未覆盖代码报告"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="仅检查阈值，不生成报告"
    )
    
    args = parser.parse_args()
    
    if args.trend:
        show_trend()
        return
    
    if args.uncovered:
        generate_uncovered_report()
        return
    
    if args.check:
        passed = check_threshold(args.threshold, args.skill)
        sys.exit(0 if passed else 1)
        return
    
    # 生成报告
    summary = generate_coverage(args.skill, Path(args.output))
    save_to_history(summary)
    
    # 检查阈值
    passed = summary.get("line_coverage", 0) >= args.threshold
    
    if not passed:
        print(f"\n⚠️  覆盖率未达到阈值 {args.threshold}%")
        sys.exit(1)
    
    print(f"\n✅ 覆盖率检查通过: {summary.get('line_coverage', 0):.2f}%")


if __name__ == "__main__":
    main()
