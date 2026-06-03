#!/usr/bin/env python3
"""
蓝军全量Skill审计工具
按新标准（≥150行、10+测试、Token评估）逐一检查
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

SKILLS_DIR = "/root/.openclaw/workspace/skills"
REPORT_FILE = "/root/.openclaw/workspace/reports/blue-army-skill-audit-20260328.json"

# 高标准要求
HIGH_STANDARD = {
    'min_lines': 150,
    'min_tests': 10,
    'requires_token_assessment': True,
    'requires_test_function': True,
    'requires_cli_test': True,
}

@dataclass
class SkillAuditResult:
    skill_name: str
    skill_md_exists: bool
    py_file_exists: bool
    lines_of_code: int
    has_run_tests: bool
    has_cli_test: bool
    test_passed: Optional[bool]
    has_token_assessment: bool
    issues: List[str]
    status: str  # 'PASS', 'FAIL', 'CRITICAL'

def audit_skill(skill_path: Path) -> SkillAuditResult:
    """审计单个Skill"""
    skill_name = skill_path.name
    issues = []
    
    # 检查SKILL.md
    skill_md = skill_path / 'SKILL.md'
    skill_md_exists = skill_md.exists()
    
    # 查找主.py文件
    py_files = list(skill_path.glob('*.py'))
    py_file_exists = len(py_files) > 0
    
    if not py_file_exists:
        return SkillAuditResult(
            skill_name=skill_name,
            skill_md_exists=skill_md_exists,
            py_file_exists=False,
            lines_of_code=0,
            has_run_tests=False,
            has_cli_test=False,
            test_passed=None,
            has_token_assessment=False,
            issues=['No Python file found'],
            status='CRITICAL'
        )
    
    # 取最大的.py文件作为主文件
    main_py = max(py_files, key=lambda f: f.stat().st_size)
    
    # 统计行数
    with open(main_py, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines_of_code = len(content.splitlines())
    
    # 检查是否有run_tests函数
    has_run_tests = 'def run_tests' in content
    
    # 检查是否有--test CLI参数
    has_cli_test = "'--test'" in content or '"--test"' in content or 'args.test' in content
    
    # 检查Token评估
    has_token_assessment = any(keyword in content.lower() for keyword in 
        ['token', 'cost', 'estimate', 'consumption'])
    
    # 尝试运行测试
    test_passed = None
    if has_cli_test and lines_of_code > 50:
        try:
            result = subprocess.run(
                ['python3', str(main_py), '--test'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(skill_path)
            )
            test_passed = result.returncode == 0
        except:
            test_passed = False
    
    # 判定问题
    if lines_of_code < HIGH_STANDARD['min_lines']:
        issues.append(f"Code too short: {lines_of_code} < {HIGH_STANDARD['min_lines']} lines")
    
    if not has_run_tests:
        issues.append("Missing run_tests function")
    
    if not has_cli_test:
        issues.append("Missing --test CLI parameter")
    
    if not has_token_assessment:
        issues.append("Missing Token consumption assessment")
    
    if test_passed is False:
        issues.append("Tests failed")
    
    # 判定状态
    if not py_file_exists or not skill_md_exists:
        status = 'CRITICAL'
    elif len(issues) >= 3:
        status = 'FAIL'
    elif len(issues) > 0:
        status = 'PARTIAL'
    else:
        status = 'PASS'
    
    return SkillAuditResult(
        skill_name=skill_name,
        skill_md_exists=skill_md_exists,
        py_file_exists=py_file_exists,
        lines_of_code=lines_of_code,
        has_run_tests=has_run_tests,
        has_cli_test=has_cli_test,
        test_passed=test_passed,
        has_token_assessment=has_token_assessment,
        issues=issues,
        status=status
    )

def run_audit():
    """运行全量审计"""
    print("=" * 70)
    print("蓝军全量Skill高标准审计")
    print(f"标准: ≥{HIGH_STANDARD['min_lines']}行, ≥{HIGH_STANDARD['min_tests']}测试, Token评估")
    print("=" * 70)
    
    skills_dir = Path(SKILLS_DIR)
    results = []
    
    # 遍历所有Skill目录
    for skill_path in sorted(skills_dir.iterdir()):
        if skill_path.is_dir() and not skill_path.name.startswith('.'):
            print(f"\n审计: {skill_path.name}")
            result = audit_skill(skill_path)
            results.append(result)
            
            # 简要输出
            status_icon = {'PASS': '✓', 'PARTIAL': '△', 'FAIL': '✗', 'CRITICAL': '💀'}
            print(f"  {status_icon.get(result.status, '?')} {result.status}")
            print(f"    代码: {result.lines_of_code}行")
            print(f"    run_tests: {'✓' if result.has_run_tests else '✗'}")
            print(f"    --test: {'✓' if result.has_cli_test else '✗'}")
            print(f"    Token评估: {'✓' if result.has_token_assessment else '✗'}")
            if result.issues:
                print(f"    问题: {', '.join(result.issues[:2])}")
    
    # 统计
    pass_count = sum(1 for r in results if r.status == 'PASS')
    partial_count = sum(1 for r in results if r.status == 'PARTIAL')
    fail_count = sum(1 for r in results if r.status == 'FAIL')
    critical_count = sum(1 for r in results if r.status == 'CRITICAL')
    
    print("\n" + "=" * 70)
    print("审计汇总")
    print("=" * 70)
    print(f"总Skill数: {len(results)}")
    print(f"✓ 通过: {pass_count}")
    print(f"△ 部分达标: {partial_count}")
    print(f"✗ 不达标: {fail_count}")
    print(f"💀 严重问题: {critical_count}")
    print(f"通过率: {pass_count}/{len(results)} ({100*pass_count//len(results)}%)")
    
    # 保存报告
    report = {
        'audit_time': '2026-03-28',
        'standard': HIGH_STANDARD,
        'summary': {
            'total': len(results),
            'pass': pass_count,
            'partial': partial_count,
            'fail': fail_count,
            'critical': critical_count
        },
        'results': [
            {
                'skill_name': r.skill_name,
                'status': r.status,
                'lines': r.lines_of_code,
                'has_run_tests': r.has_run_tests,
                'has_cli_test': r.has_cli_test,
                'has_token': r.has_token_assessment,
                'test_passed': r.test_passed,
                'issues': r.issues
            }
            for r in results
        ]
    }
    
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n报告已保存: {REPORT_FILE}")
    
    # 输出不达标清单
    if fail_count + critical_count > 0:
        print("\n" + "=" * 70)
        print("需优化的Skill清单（FAIL/CRITICAL）")
        print("=" * 70)
        for r in results:
            if r.status in ('FAIL', 'CRITICAL'):
                print(f"\n{r.skill_name}")
                print(f"  状态: {r.status}")
                print(f"  问题: {r.issues}")

if __name__ == '__main__':
    run_audit()
