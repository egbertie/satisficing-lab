#!/usr/bin/env python3
"""
测试运行器 - S2标准实现

功能:
- 运行所有测试或指定测试
- 支持单元/集成/端到端三级测试
- 生成测试报告
- 检查测试覆盖率
- 返回适当的退出码供CI/CD使用

使用方法:
    python run_tests.py                    # 运行单元测试
    python run_tests.py --all-levels       # 运行全部三级测试
    python run_tests.py --level unit       # 仅运行单元测试
    python run_tests.py --level integration # 仅运行集成测试
    python run_tests.py --level e2e        # 仅运行E2E测试
    python run_tests.py --critical         # 仅运行关键测试
    python run_tests.py --skill zero_idle  # 运行指定Skill测试
    python run_tests.py --coverage 80      # 检查覆盖率阈值
    python run_tests.py --report           # 生成完整报告
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# 配置
PROJECT_ROOT = Path(__file__).parent
TESTS_DIR = PROJECT_ROOT / "tests"
REPORTS_DIR = PROJECT_ROOT / "reports"
COVERAGE_THRESHOLD = 80


def run_command(cmd: List[str], cwd: Path = None) -> tuple:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "命令超时"
    except Exception as e:
        return 1, "", str(e)


def run_unit_tests(coverage_threshold: int = None, skill: str = None) -> Dict[str, Any]:
    """运行单元测试"""
    print("=" * 60)
    print("运行单元测试 (Unit Tests)")
    print("=" * 60)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/unit",
        "--verbose",
        "--tb=short",
        "-ra",
    ]
    
    if skill:
        marker_map = {
            "zero_idle": "zero_idle", "zero-idle": "zero_idle",
            "token_budget": "token_budget", "token-budget": "token_budget",
            "blue_sentinel": "blue_sentinel", "blue-sentinel": "blue_sentinel"
        }
        marker = marker_map.get(skill.lower(), skill.lower())
        cmd.extend(["-m", marker])
    
    if coverage_threshold:
        cmd.extend([
            "--cov=skills",
            f"--cov-fail-under={coverage_threshold}"
        ])
    
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print("STDERR:", stderr, file=sys.stderr)
    
    return {
        "level": "unit",
        "success": returncode == 0,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr
    }


def run_integration_tests(skill: str = None) -> Dict[str, Any]:
    """运行集成测试"""
    print("=" * 60)
    print("运行集成测试 (Integration Tests)")
    print("=" * 60)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/integration",
        "--verbose",
        "--tb=short",
        "-ra"
    ]
    
    if skill:
        marker_map = {
            "zero_idle": "zero_idle", "zero-idle": "zero_idle",
            "token_budget": "token_budget", "token-budget": "token_budget",
            "blue_sentinel": "blue_sentinel", "blue-sentinel": "blue_sentinel"
        }
        marker = marker_map.get(skill.lower(), skill.lower())
        cmd.extend(["-m", marker])
    
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print("STDERR:", stderr, file=sys.stderr)
    
    return {
        "level": "integration",
        "success": returncode == 0,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr
    }


def run_e2e_tests(skill: str = None) -> Dict[str, Any]:
    """运行端到端测试"""
    print("=" * 60)
    print("运行端到端测试 (E2E Tests)")
    print("=" * 60)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/e2e",
        "--verbose",
        "--tb=short",
        "-ra"
    ]
    
    if skill:
        marker_map = {
            "zero_idle": "zero_idle", "zero-idle": "zero_idle",
            "token_budget": "token_budget", "token-budget": "token_budget",
            "blue_sentinel": "blue_sentinel", "blue-sentinel": "blue_sentinel"
        }
        marker = marker_map.get(skill.lower(), skill.lower())
        cmd.extend(["-m", marker])
    
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print("STDERR:", stderr, file=sys.stderr)
    
    return {
        "level": "e2e",
        "success": returncode == 0,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr
    }


def run_all_levels(coverage_threshold: int = None, skill: str = None) -> Dict[str, Any]:
    """运行全部三级测试"""
    print("=" * 60)
    print("运行全部三级测试 (单元 → 集成 → E2E)")
    print("=" * 60)
    
    results = []
    
    # 1. 单元测试
    unit_result = run_unit_tests(coverage_threshold, skill)
    results.append(unit_result)
    
    if not unit_result["success"]:
        print("\n❌ 单元测试失败，停止后续测试")
        return {
            "all_levels": True,
            "success": False,
            "results": results
        }
    
    # 2. 集成测试
    integration_result = run_integration_tests(skill)
    results.append(integration_result)
    
    if not integration_result["success"]:
        print("\n❌ 集成测试失败，停止后续测试")
        return {
            "all_levels": True,
            "success": False,
            "results": results
        }
    
    # 3. E2E测试
    e2e_result = run_e2e_tests(skill)
    results.append(e2e_result)
    
    all_passed = all(r["success"] for r in results)
    
    print("\n" + "=" * 60)
    print("三级测试汇总")
    print("=" * 60)
    for r in results:
        status = "✅ 通过" if r["success"] else "❌ 失败"
        print(f"  {r['level'].upper():15} {status}")
    
    return {
        "all_levels": True,
        "success": all_passed,
        "results": results
    }


def run_critical_tests() -> Dict[str, Any]:
    """运行关键测试"""
    print("=" * 60)
    print("运行关键测试 (P0)")
    print("=" * 60)
    
    cmd = [
        "python", "-m", "pytest",
        "-m", "critical",
        "--verbose",
        "--tb=short"
    ]
    
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print("STDERR:", stderr, file=sys.stderr)
    
    return {
        "level": "critical",
        "success": returncode == 0,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr
    }


def run_skill_tests(skill_name: str, level: str = "all") -> Dict[str, Any]:
    """运行指定Skill的测试"""
    print("=" * 60)
    print(f"运行 {skill_name} 测试 (级别: {level})")
    print("=" * 60)
    
    if level == "all":
        return run_all_levels(skill=skill_name)
    elif level == "unit":
        return run_unit_tests(skill=skill_name)
    elif level == "integration":
        return run_integration_tests(skill=skill_name)
    elif level == "e2e":
        return run_e2e_tests(skill=skill_name)
    else:
        print(f"未知级别: {level}")
        return {"success": False, "error": f"Unknown level: {level}"}


def check_coverage(threshold: int = COVERAGE_THRESHOLD) -> Dict[str, Any]:
    """检查测试覆盖率"""
    print("=" * 60)
    print(f"检查测试覆盖率 (阈值: {threshold}%)")
    print("=" * 60)
    
    # 先运行测试生成覆盖率数据
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=skills",
        "--cov-report=term-missing",
        f"--cov-fail-under={threshold}",
        "-q"
    ]
    
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    
    return {
        "success": returncode == 0,
        "returncode": returncode,
        "coverage_met": returncode == 0,
        "threshold": threshold
    }


def generate_report() -> Dict[str, Any]:
    """生成测试报告"""
    print("=" * 60)
    print("生成测试报告")
    print("=" * 60)
    
    # 确保报告目录存在
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 运行测试并生成各种报告
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--html=reports/test_report.html",
        "--self-contained-html",
        "--cov=skills",
        "--cov-report=html:reports/coverage",
        "--cov-report=xml:reports/coverage.xml",
        "--json-report",
        "--json-report-file=reports/test_results.json",
        "--junitxml=reports/junit.xml"
    ]
    
    returncode, stdout, stderr = run_command(cmd)
    
    # 生成摘要报告
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "success": returncode == 0,
        "returncode": returncode
    }
    
    # 尝试读取JSON报告
    json_report_path = REPORTS_DIR / "test_results.json"
    if json_report_path.exists():
        try:
            with open(json_report_path, "r") as f:
                json_data = json.load(f)
                report_data["summary"] = json_data.get("summary", {})
                
                # 按层级统计
                if "tests" in json_data:
                    by_level = {"unit": 0, "integration": 0, "e2e": 0}
                    for test in json_data["tests"]:
                        test_path = test.get("nodeid", "")
                        if "unit/" in test_path:
                            by_level["unit"] += 1
                        elif "integration/" in test_path:
                            by_level["integration"] += 1
                        elif "e2e/" in test_path:
                            by_level["e2e"] += 1
                    report_data["by_level"] = by_level
        except:
            pass
    
    # 保存摘要报告
    summary_path = REPORTS_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n报告已生成:")
    print(f"  - HTML报告: reports/test_report.html")
    print(f"  - 覆盖率报告: reports/coverage/index.html")
    print(f"  - JSON报告: reports/test_results.json")
    print(f"  - JUnit报告: reports/junit.xml")
    print(f"  - 摘要: reports/summary.json")
    
    return report_data


def install_dependencies() -> bool:
    """安装测试依赖"""
    print("安装测试依赖...")
    
    req_file = PROJECT_ROOT / "requirements.txt"
    if not req_file.exists():
        print("警告: requirements.txt 不存在")
        return False
    
    cmd = ["pip", "install", "-q", "-r", str(req_file)]
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print(f"安装依赖失败: {stderr}", file=sys.stderr)
        return False
    
    print("依赖安装完成")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="OpenClaw Skills Testing Framework 测试运行器 (Level 5)"
    )
    
    # 测试级别选项
    level_group = parser.add_mutually_exclusive_group()
    level_group.add_argument(
        "--all-levels",
        action="store_true",
        help="运行全部三级测试（单元→集成→E2E）"
    )
    level_group.add_argument(
        "--level",
        choices=["unit", "integration", "e2e"],
        help="运行指定级别的测试"
    )
    level_group.add_argument(
        "--critical",
        action="store_true",
        help="仅运行关键测试"
    )
    
    # 其他选项
    parser.add_argument(
        "--skill",
        type=str,
        help="运行指定Skill的测试 (zero_idle, token_budget, blue_sentinel)"
    )
    parser.add_argument(
        "--coverage",
        type=int,
        metavar="THRESHOLD",
        help=f"检查覆盖率阈值 (默认: {COVERAGE_THRESHOLD}%)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成完整测试报告"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="安装测试依赖"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="运行所有单元测试（默认行为）"
    )
    
    args = parser.parse_args()
    
    # 安装依赖
    if args.install:
        if not install_dependencies():
            sys.exit(1)
        return
    
    # 确保报告目录存在
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 运行测试
    result = None
    
    if args.all_levels:
        threshold = args.coverage if args.coverage else None
        result = run_all_levels(threshold, args.skill)
    elif args.level:
        if args.level == "unit":
            result = run_unit_tests(args.coverage, args.skill)
        elif args.level == "integration":
            result = run_integration_tests(args.skill)
        elif args.level == "e2e":
            result = run_e2e_tests(args.skill)
    elif args.critical:
        result = run_critical_tests()
    elif args.skill:
        result = run_skill_tests(args.skill)
    elif args.coverage:
        result = check_coverage(args.coverage)
    elif args.report:
        result = generate_report()
    else:
        # 默认运行单元测试
        result = run_unit_tests(args.coverage, args.skill)
    
    # 返回退出码
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
