#!/usr/bin/env python3
"""
对抗测试执行器 - S7标准实现

功能:
- 通过故意破坏代码验证测试的鲁棒性
- 注入各种类型的bug
- 检测测试是否能捕获这些bug
- 生成对抗测试报告

使用方法:
    python adversarial_test.py --mode all        # 运行所有对抗测试
    python adversarial_test.py --mode boundary   # 仅边界破坏
    python adversarial_test.py --skill zero_idle # 针对特定Skill
"""

import os
import sys
import json
import re
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile

PROJECT_ROOT = Path(__file__).parent
SKILLS_DIR = PROJECT_ROOT.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_FILE = REPORTS_DIR / "adversarial_report.json"


class InjectionType(Enum):
    """注入类型"""
    BOUNDARY_BREAK = "boundary_break"
    COMPARISON_FLIP = "comparison_flip"
    ARITHMETIC_CHANGE = "arithmetic_change"
    RETURN_VALUE_TAMPER = "return_value_tamper"
    EXCEPTION_OMIT = "exception_omit"


@dataclass
class Injection:
    """注入记录"""
    id: str
    skill: str
    type: str
    file: str
    line: int
    original: str
    modified: str
    description: str


@dataclass
class InjectionResult:
    """注入结果"""
    injection: Injection
    detected: bool
    failed_tests: List[str]
    duration: float


class AdversarialTester:
    """对抗测试器"""
    
    def __init__(self):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.results: List[InjectionResult] = []
        self.temp_dir: Optional[Path] = None
    
    def setup_temp_env(self) -> Path:
        """创建临时测试环境"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="adversarial_test_"))
        
        # 复制项目到临时目录
        shutil.copytree(PROJECT_ROOT, self.temp_dir / "testing-framework", ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".pytest_cache", "reports"
        ))
        
        return self.temp_dir
    
    def cleanup(self):
        """清理临时环境"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def find_target_files(self, skill: str = None) -> List[Path]:
        """查找目标文件"""
        targets = []
        
        skills_to_test = []
        if skill:
            skills_to_test.append(skill)
        else:
            skills_to_test = ["zero-idle-enforcer", "token-budget-enforcer", "blue-sentinel"]
        
        for skill_name in skills_to_test:
            skill_dir = SKILLS_DIR / skill_name
            if skill_dir.exists():
                for py_file in skill_dir.rglob("*.py"):
                    if not py_file.name.startswith("test_") and py_file.name != "__init__.py":
                        targets.append(py_file)
        
        return targets
    
    def inject_boundary_break(self, file_path: Path) -> List[Injection]:
        """注入边界破坏"""
        injections = []
        content = file_path.read_text()
        lines = content.split('\n')
        
        # 查找边界值（如 7200, 3600 等）
        boundary_pattern = re.compile(r'(\s*if\s+.*?[<>=!]+\s*)(\d+)(\s*:?)')
        
        for i, line in enumerate(lines, 1):
            match = boundary_pattern.search(line)
            if match:
                original_val = int(match.group(2))
                # 边界+1破坏
                modified_val = original_val + 1
                modified_line = boundary_pattern.sub(rf'\g<1>{modified_val}\g<3>', line)
                
                if modified_line != line:
                    injections.append(Injection(
                        id=f"ADV-BB-{len(injections)+1:03d}",
                        skill=file_path.parent.name,
                        type=InjectionType.BOUNDARY_BREAK.value,
                        file=str(file_path),
                        line=i,
                        original=line.strip(),
                        modified=modified_line.strip(),
                        description=f"将边界值 {original_val} 改为 {modified_val}"
                    ))
        
        return injections
    
    def inject_comparison_flip(self, file_path: Path) -> List[Injection]:
        """注入比较运算符翻转"""
        injections = []
        content = file_path.read_text()
        lines = content.split('\n')
        
        # 比较运算符替换
        flips = [
            (' == ', ' != '),
            (' != ', ' == '),
            (' > ', ' < '),
            (' < ', ' > '),
            (' >= ', ' <= '),
            (' <= ', ' >= '),
        ]
        
        for i, line in enumerate(lines, 1):
            for orig, repl in flips:
                if orig in line:
                    modified_line = line.replace(orig, repl, 1)
                    if modified_line != line:
                        injections.append(Injection(
                            id=f"ADV-CF-{len(injections)+1:03d}",
                            skill=file_path.parent.name,
                            type=InjectionType.COMPARISON_FLIP.value,
                            file=str(file_path),
                            line=i,
                            original=line.strip(),
                            modified=modified_line.strip(),
                            description=f"将 '{orig.strip()}' 改为 '{repl.strip()}'"
                        ))
                        break  # 每行只注入一次
        
        return injections
    
    def inject_return_value_tamper(self, file_path: Path) -> List[Injection]:
        """注入返回值篡改"""
        injections = []
        content = file_path.read_text()
        lines = content.split('\n')
        
        # 查找return语句
        return_pattern = re.compile(r'(\s*return\s+)(True|False|None|\d+|\'[^\']*\'|\"[^\"]*\")')
        
        replacements = {
            'True': 'False',
            'False': 'True',
            'None': '"tampered"',
        }
        
        for i, line in enumerate(lines, 1):
            match = return_pattern.search(line)
            if match:
                original_val = match.group(2)
                if original_val in replacements:
                    modified_val = replacements[original_val]
                    modified_line = return_pattern.sub(rf'\g<1>{modified_val}', line)
                    
                    if modified_line != line:
                        injections.append(Injection(
                            id=f"ADV-RV-{len(injections)+1:03d}",
                            skill=file_path.parent.name,
                            type=InjectionType.RETURN_VALUE_TAMPER.value,
                            file=str(file_path),
                            line=i,
                            original=line.strip(),
                            modified=modified_line.strip(),
                            description=f"将return {original_val} 改为 return {modified_val}"
                        ))
        
        return injections
    
    def apply_injection(self, injection: Injection, temp_dir: Path):
        """应用注入到临时文件"""
        # 计算临时文件路径
        rel_path = Path(injection.file).relative_to(SKILLS_DIR.parent)
        temp_file = temp_dir / "testing-framework" / rel_path
        
        if not temp_file.exists():
            return False
        
        content = temp_file.read_text()
        lines = content.split('\n')
        
        # 替换指定行
        if 0 < injection.line <= len(lines):
            if lines[injection.line - 1].strip() == injection.original:
                lines[injection.line - 1] = lines[injection.line - 1].replace(
                    injection.original, injection.modified
                )
                temp_file.write_text('\n'.join(lines))
                return True
        
        return False
    
    def run_tests_on_injection(self, injection: Injection, temp_dir: Path) -> Tuple[bool, List[str]]:
        """在注入后的代码上运行测试"""
        import time
        start_time = time.time()
        
        # 运行测试
        cmd = [
            "python", "-m", "pytest",
            str(temp_dir / "testing-framework" / "tests"),
            "-v",
            "--tb=no",
            "-q"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir / "testing-framework"
            )
            
            duration = time.time() - start_time
            detected = result.returncode != 0
            
            # 解析失败的测试
            failed_tests = []
            if detected:
                for line in result.stdout.split('\n'):
                    if 'FAILED' in line:
                        test_name = line.split()[0] if line.split() else "unknown"
                        failed_tests.append(test_name)
            
            return detected, failed_tests, duration
        except subprocess.TimeoutExpired:
            return True, ["timeout"], 60.0
        except Exception as e:
            return False, [str(e)], 0.0
    
    def run_adversarial_tests(
        self,
        mode: str = "all",
        skill: str = None,
        max_injections: int = 50
    ) -> Dict[str, Any]:
        """运行对抗测试"""
        print("=" * 60)
        print("对抗测试 - 验证测试鲁棒性")
        print("=" * 60)
        
        # 设置临时环境
        print("\n📁 设置临时测试环境...")
        temp_dir = self.setup_temp_env()
        
        try:
            # 查找目标文件
            target_files = self.find_target_files(skill)
            print(f"🔍 找到 {len(target_files)} 个目标文件")
            
            # 生成注入
            all_injections: List[Injection] = []
            
            for file_path in target_files:
                if mode in ["all", "boundary"]:
                    all_injections.extend(self.inject_boundary_break(file_path))
                if mode in ["all", "comparison"]:
                    all_injections.extend(self.inject_comparison_flip(file_path))
                if mode in ["all", "return"]:
                    all_injections.extend(self.inject_return_value_tamper(file_path))
            
            # 限制注入数量
            all_injections = all_injections[:max_injections]
            
            print(f"💉 生成 {len(all_injections)} 个注入点")
            
            # 执行注入和测试
            results = []
            detected_count = 0
            
            for i, injection in enumerate(all_injections, 1):
                print(f"\n[{i}/{len(all_injections)}] 测试注入: {injection.id}")
                print(f"   类型: {injection.type}")
                print(f"   位置: {injection.file}:{injection.line}")
                print(f"   操作: {injection.description}")
                
                # 重新创建临时环境（避免累积注入）
                self.cleanup()
                temp_dir = self.setup_temp_env()
                
                # 应用注入
                if self.apply_injection(injection, temp_dir):
                    # 运行测试
                    detected, failed_tests, duration = self.run_tests_on_injection(injection, temp_dir)
                    
                    result = InjectionResult(
                        injection=injection,
                        detected=detected,
                        failed_tests=failed_tests,
                        duration=duration
                    )
                    results.append(result)
                    
                    status = "✅ 已检测" if detected else "❌ 未检测"
                    print(f"   结果: {status}")
                    
                    if detected:
                        detected_count += 1
                else:
                    print(f"   结果: ⚠️ 注入失败")
            
            # 计算检测率
            detection_rate = (detected_count / len(results) * 100) if results else 0
            
            print("\n" + "=" * 60)
            print("对抗测试结果")
            print("=" * 60)
            print(f"总注入数: {len(results)}")
            print(f"已检测: {detected_count}")
            print(f"未检测: {len(results) - detected_count}")
            print(f"检测率: {detection_rate:.1f}%")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_injections": len(results),
                "detected": detected_count,
                "missed": len(results) - detected_count,
                "detection_rate": round(detection_rate, 1),
                "injections": [
                    {
                        "id": r.injection.id,
                        "skill": r.injection.skill,
                        "type": r.injection.type,
                        "description": r.injection.description,
                        "detected": r.detected,
                        "failed_tests": r.failed_tests,
                        "duration": r.duration
                    }
                    for r in results
                ]
            }
        
        finally:
            self.cleanup()
    
    def generate_report(self, results: Dict[str, Any]):
        """生成对抗测试报告"""
        # JSON报告
        with open(REPORT_FILE, "w") as f:
            json.dump({"adversarial_test": results}, f, indent=2)
        
        # Markdown报告
        md_file = REPORTS_DIR / "adversarial_report.md"
        with open(md_file, "w") as f:
            f.write("# 对抗测试报告\n\n")
            f.write(f"测试时间: {results['timestamp']}\n\n")
            f.write("## 摘要\n\n")
            f.write(f"- 总注入数: {results['total_injections']}\n")
            f.write(f"- 已检测: {results['detected']}\n")
            f.write(f"- 未检测: {results['missed']}\n")
            f.write(f"- **检测率: {results['detection_rate']}%**\n\n")
            
            f.write("## 详细结果\n\n")
            f.write("| ID | Skill | 类型 | 检测状态 | 失败的测试 |\n")
            f.write("|----|-------|------|----------|------------|\n")
            
            for inj in results['injections']:
                status = "✅" if inj['detected'] else "❌"
                failed = ", ".join(inj['failed_tests'][:3]) if inj['detected'] else "-"
                f.write(f"| {inj['id']} | {inj['skill']} | {inj['type']} | {status} | {failed} |\n")
            
            if results['missed'] > 0:
                f.write("\n## 未检测的注入（需要改进测试）\n\n")
                for inj in results['injections']:
                    if not inj['detected']:
                        f.write(f"- {inj['id']}: {inj['description']}\n")
        
        return REPORT_FILE


def main():
    parser = argparse.ArgumentParser(description="对抗测试执行器")
    parser.add_argument(
        "--mode",
        choices=["all", "boundary", "comparison", "return"],
        default="all",
        help="注入类型"
    )
    parser.add_argument("--skill", type=str, help="指定Skill")
    parser.add_argument("--max", type=int, default=50, help="最大注入数")
    parser.add_argument("--threshold", type=int, default=90, help="检测率阈值")
    
    args = parser.parse_args()
    
    tester = AdversarialTester()
    results = tester.run_adversarial_tests(
        mode=args.mode,
        skill=args.skill,
        max_injections=args.max
    )
    
    # 生成报告
    report_path = tester.generate_report(results)
    print(f"\n📄 报告已生成: {report_path}")
    print(f"   Markdown: {REPORTS_DIR / 'adversarial_report.md'}")
    
    # 检查阈值
    if results['detection_rate'] < args.threshold:
        print(f"\n❌ 检测率 {results['detection_rate']}% 低于阈值 {args.threshold}%")
        print("   建议：增强测试严格性")
        sys.exit(1)
    else:
        print(f"\n✅ 检测率 {results['detection_rate']}% 达到阈值 {args.threshold}%")


if __name__ == "__main__":
    main()
