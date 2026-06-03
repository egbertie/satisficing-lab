#!/usr/bin/env python3
"""
运行时验证脚本
验证所有Skill可运行，生成验证报告

质量第一：实际运行验证，非静态检查
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 待验证的Skill列表
SKILLS_TO_VERIFY = [
    ("checkpoint-manager", "checkpoint_manager.py"),
    ("blackboard-manager", "blackboard_manager.py"),
    ("worker-orchestrator", "worker_orchestrator.py"),
]


def verify_skill(skill_name: str, module_name: str) -> Tuple[bool, str]:
    """
    验证单个Skill
    
    Returns:
        (成功, 消息)
    """
    skill_path = Path(f"~/.openclaw/workspace/skills/{skill_name}").expanduser()
    module_path = skill_path / module_name
    
    # 检查文件存在
    if not module_path.exists():
        return False, f"模块文件不存在: {module_path}"
    
    # 尝试导入
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(skill_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, f"导入成功"
    except Exception as e:
        return False, f"导入失败: {e}"


def run_skill_tests(skill_name: str) -> Tuple[bool, str]:
    """运行Skill测试"""
    skill_path = Path(f"~/.openclaw/workspace/skills/{skill_name}").expanduser()
    test_file = skill_path / f"test_{skill_name.replace('-', '_')}.py"
    
    if not test_file.exists():
        return False, "测试文件不存在"
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode == 0:
            return True, "测试通过"
        else:
            return False, f"测试失败:\n{result.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return False, "测试超时"
    except Exception as e:
        return False, f"运行测试失败: {e}"


def generate_verification_report() -> Dict:
    """生成验证报告"""
    report = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "skills": [],
        "summary": {"passed": 0, "failed": 0, "total": 0},
    }
    
    for skill_name, module_name in SKILLS_TO_VERIFY:
        # 验证导入
        import_success, import_msg = verify_skill(skill_name, module_name)
        
        # 运行测试（如果有）
        test_success, test_msg = run_skill_tests(skill_name) if import_success else (False, "导入失败，跳过测试")
        
        skill_report = {
            "name": skill_name,
            "import": {"success": import_success, "message": import_msg},
            "test": {"success": test_success, "message": test_msg},
            "overall": import_success and test_success,
        }
        
        report["skills"].append(skill_report)
        report["summary"]["total"] += 1
        
        if skill_report["overall"]:
            report["summary"]["passed"] += 1
        else:
            report["summary"]["failed"] += 1
    
    return report


def main():
    """主函数"""
    print("🔍 运行Skill运行时验证...")
    print()
    
    report = generate_verification_report()
    
    # 输出结果
    for skill in report["skills"]:
        status = "✅" if skill["overall"] else "❌"
        print(f"{status} {skill['name']}")
        print(f"   导入: {'✅' if skill['import']['success'] else '❌'} {skill['import']['message']}")
        print(f"   测试: {'✅' if skill['test']['success'] else '❌'} {skill['test']['message']}")
        print()
    
    # 汇总
    summary = report["summary"]
    print(f"📊 验证完成: {summary['passed']}/{summary['total']} 通过")
    
    # 保存报告
    import json
    from pathlib import Path
    
    report_dir = Path("~/.openclaw/workspace/diary/verification").expanduser()
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"verification-{__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 报告保存: {report_file}")
    
    # 返回码
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    exit(main())
