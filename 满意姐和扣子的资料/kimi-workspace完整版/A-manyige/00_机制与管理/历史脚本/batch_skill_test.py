#!/usr/bin/env python3
"""
batch_skill_test.py - 批量Skill测试
一次执行所有测试，减少调用次数
"""

import subprocess
import sys
from pathlib import Path

def run_all_tests():
    """批量运行所有核心Skill测试"""
    skills_dir = Path("/root/.openclaw/workspace/skills")
    
    skills = [
        ("checkpoint-manager", "test_checkpoint_manager.py"),
        ("blackboard-manager", "test_blackboard_manager.py"),
        ("worker-orchestrator", "test_worker_orchestrator.py"),
        ("blue-army-auditor", "test_blue_army_auditor.py"),
        ("secret-manager", "test_secret_manager.py"),
        ("disaster-recovery-auditor", "test_disaster_recovery_auditor.py"),
    ]
    
    results = []
    total_passed = 0
    total_tests = 0
    
    print("=" * 60)
    print("批量Skill测试")
    print("=" * 60)
    
    for skill_name, test_file in skills:
        skill_path = skills_dir / skill_name
        test_path = skill_path / test_file
        
        if not test_path.exists():
            print(f"⚠️  {skill_name}: 测试文件不存在")
            results.append((skill_name, 0, 0, False))
            continue
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 解析测试结果
            output = result.stdout + result.stderr
            
            # 查找 "Ran X tests" 和 "OK" 或 "FAILED"
            import re
            test_match = re.search(r'Ran (\d+) tests?', output)
            ok_match = 'OK' in output or result.returncode == 0
            
            if test_match:
                test_count = int(test_match.group(1))
                total_tests += test_count
                
                if ok_match:
                    total_passed += test_count
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
            else:
                test_count = 0
                status = "⚠️  UNKNOWN"
            
            print(f"{status} | {skill_name:25} | {test_count} tests")
            results.append((skill_name, test_count, test_count if ok_match else 0, ok_match))
            
        except Exception as e:
            print(f"❌ {skill_name}: 执行错误 - {e}")
            results.append((skill_name, 0, 0, False))
    
    print("=" * 60)
    print(f"总计: {total_passed}/{total_tests} 测试通过")
    print("=" * 60)
    
    return all(r[3] for r in results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
