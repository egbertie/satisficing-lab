#!/usr/bin/env python3
"""
运行时验证模块 - Runtime Verification
蓝军审计SOP V1.2 新增维度
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, List

class RuntimeVerifier:
    """运行时验证器"""
    
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.results = []
        
    def verify_python_runs(self, file_name: str) -> Tuple[bool, str]:
        """验证Python文件能实际运行"""
        file_path = self.skill_path / file_name
        if not file_path.exists():
            return False, f"文件不存在: {file_name}"
        
        try:
            # 尝试导入（不执行main）
            result = subprocess.run(
                [sys.executable, "-c", f"import sys; sys.path.insert(0, '{self.skill_path}'); exec(open('{file_path}').read().split('if __name__')[0])"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "导入成功"
            else:
                return False, f"导入失败: {result.stderr.decode()[:100]}"
        except Exception as e:
            return False, f"运行异常: {str(e)}"
    
    def verify_test_runs(self, file_name: str) -> Tuple[bool, str]:
        """验证测试能实际运行"""
        file_path = self.skill_path / file_name
        try:
            result = subprocess.run(
                [sys.executable, str(file_path), "--test"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, "测试通过"
            else:
                return False, f"测试失败: {result.stdout.decode()[-200:]}"
        except Exception as e:
            return False, f"测试异常: {str(e)}"
    
    def verify_cron_runnable(self, script_path: Path) -> Tuple[bool, str]:
        """验证Cron脚本可运行"""
        if not script_path.exists():
            return False, "脚本不存在"
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0 or b"usage" in result.stderr.lower():
                return True, "脚本可执行"
            return False, "脚本执行失败"
        except Exception as e:
            return False, f"执行异常: {str(e)}"
    
    def full_verification(self) -> dict:
        """完整运行时验证"""
        results = {
            "skill_name": self.skill_path.name,
            "runtime_pass": False,
            "tests": []
        }
        
        # 1. 验证主要Python文件
        py_files = list(self.skill_path.glob("*.py"))
        if py_files:
            main_file = max(py_files, key=lambda p: p.stat().st_size)
            passed, msg = self.verify_python_runs(main_file.name)
            results["tests"].append({
                "name": f"python_runs:{main_file.name}",
                "passed": passed,
                "message": msg
            })
        
        # 2. 验证测试运行
        if py_files:
            main_file = max(py_files, key=lambda p: p.stat().st_size)
            passed, msg = self.verify_test_runs(main_file.name)
            results["tests"].append({
                "name": f"test_runs:{main_file.name}",
                "passed": passed,
                "message": msg
            })
        
        # 3. 判断整体
        all_passed = all(t["passed"] for t in results["tests"])
        results["runtime_pass"] = all_passed
        
        return results


if __name__ == "__main__":
    import json
    skill_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    verifier = RuntimeVerifier(skill_path)
    results = verifier.full_verification()
    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.exit(0 if results["runtime_pass"] else 1)
