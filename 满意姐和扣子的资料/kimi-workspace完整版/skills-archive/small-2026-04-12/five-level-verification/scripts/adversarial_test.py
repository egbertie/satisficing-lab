#!/usr/bin/env python3
"""
S7: Adversarial Testing Module
对抗测试 - 故意植入错误测试各级发现率
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# 对抗测试用例定义
ADVERSARIAL_TESTS = {
    "L1": [
        {
            "name": "missing_skill_md",
            "description": "删除SKILL.md文件",
            "error_type": "文件缺失",
            "target_level": "L1"
        },
        {
            "name": "missing_config",
            "description": "删除config.yaml文件",
            "error_type": "配置缺失",
            "target_level": "L1"
        },
        {
            "name": "empty_skill_md",
            "description": "创建空的SKILL.md",
            "error_type": "空文件",
            "target_level": "L1"
        }
    ],
    "L2": [
        {
            "name": "python_syntax_error",
            "description": "植入Python语法错误",
            "error_type": "语法错误",
            "target_level": "L2",
            "payload": "def broken(\n    pass\n"
        },
        {
            "name": "json_syntax_error",
            "description": "植入JSON格式错误",
            "error_type": "JSON错误",
            "target_level": "L2",
            "payload": '{"key": value}'
        },
        {
            "name": "yaml_indent_error",
            "description": "植入YAML缩进错误",
            "error_type": "YAML错误",
            "target_level": "L2",
            "payload": "key:\n  subkey: value\n wrong_indent: bad"
        }
    ],
    "L3": [
        {
            "name": "missing_import",
            "description": "植入不存在的导入",
            "error_type": "导入错误",
            "target_level": "L3",
            "payload": "import nonexistent_module_xyz123\n"
        },
        {
            "name": "runtime_error",
            "description": "植入运行时错误",
            "error_type": "运行时错误",
            "target_level": "L3",
            "payload": "raise Exception('Test error')\n"
        }
    ],
    "L4": [
        {
            "name": "missing_env_var",
            "description": "依赖缺失的环境变量",
            "error_type": "配置缺失",
            "target_level": "L4",
            "payload": "import os\nos.environ['REQUIRED_VAR']\n"
        },
        {
            "name": "invalid_config",
            "description": "无效的配置结构",
            "error_type": "配置错误",
            "target_level": "L4"
        }
    ],
    "L5": [
        {
            "name": "logic_error",
            "description": "植入逻辑错误",
            "error_type": "逻辑错误",
            "target_level": "L5",
            "payload": "# 错误的算法\ndef calculate(a, b):\n    return a - b  # 应该是加法\n"
        },
        {
            "name": "performance_issue",
            "description": "性能问题",
            "error_type": "性能缺陷",
            "target_level": "L5"
        }
    ]
}


class AdversarialTester:
    """对抗测试执行器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.skill_name = os.path.basename(skill_path)
        self.results = {}
    
    def run_all_tests(self) -> Dict:
        """运行所有对抗测试"""
        print(f"🧪 开始对抗测试: {self.skill_name}")
        print("=" * 60)
        
        for level in ["L1", "L2", "L3", "L4", "L5"]:
            level_tests = ADVERSARIAL_TESTS.get(level, [])
            self.results[level] = []
            
            for test in level_tests:
                result = self._run_single_test(level, test)
                self.results[level].append(result)
        
        return self._generate_summary()
    
    def _run_single_test(self, level: str, test: Dict) -> Dict:
        """运行单个对抗测试"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 复制原始Skill
            test_path = os.path.join(tmpdir, self.skill_name)
            shutil.copytree(self.skill_path, test_path)
            
            # 植入错误
            self._inject_error(test_path, test)
            
            # 运行验证
            detected, actual_level = self._verify_error(test_path, level)
            
            return {
                "name": test["name"],
                "description": test["description"],
                "target_level": level,
                "detected": detected,
                "detected_at": actual_level,
                "success": detected and actual_level == level
            }
    
    def _inject_error(self, path: str, test: Dict):
        """植入错误"""
        error_type = test.get("error_type")
        
        if error_type == "文件缺失":
            target = os.path.join(path, "SKILL.md" if "skill_md" in test["name"] else "config.yaml")
            if os.path.exists(target):
                os.remove(target)
                
        elif error_type == "空文件":
            target = os.path.join(path, "SKILL.md")
            with open(target, "w") as f:
                f.write("")
                
        elif error_type in ["语法错误", "导入错误", "运行时错误"]:
            target = os.path.join(path, "scripts", "test_error.py")
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w") as f:
                f.write(test.get("payload", ""))
                
        elif error_type == "JSON错误":
            target = os.path.join(path, "test.json")
            with open(target, "w") as f:
                f.write(test.get("payload", "{}"))
                
        elif error_type == "YAML错误":
            target = os.path.join(path, "test.yaml")
            with open(target, "w") as f:
                f.write(test.get("payload", ""))
    
    def _verify_error(self, path: str, expected_level: str) -> Tuple[bool, str]:
        """验证错误是否被正确检测"""
        sys.path.insert(0, os.path.dirname(__file__))
        from verify import FiveLevelVerifier
        
        verifier = FiveLevelVerifier(self.skill_name)
        verifier.skill_path = path
        
        # 逐级验证
        for level in ["L1", "L2", "L3", "L4", "L5"]:
            passed, _ = getattr(verifier, f"verify_{level}")()
            if not passed:
                return True, level
            if level == expected_level:
                break
        
        return False, "未检测"
    
    def _generate_summary(self) -> Dict:
        """生成测试总结"""
        detection_matrix = {}
        
        for level in ["L1", "L2", "L3", "L4", "L5"]:
            level_results = self.results.get(level, [])
            total = len(level_results)
            detected = sum(1 for r in level_results if r.get("detected"))
            correct_level = sum(1 for r in level_results if r.get("success"))
            
            detection_matrix[level] = {
                "total_tests": total,
                "detected": detected,
                "correct_level": correct_level,
                "detection_rate": round(detected / total * 100, 1) if total > 0 else 0,
                "accuracy": round(correct_level / total * 100, 1) if total > 0 else 0
            }
        
        summary = {
            "skill": self.skill_name,
            "test_date": str(datetime.now()) if 'datetime' in dir() else "N/A",
            "detection_matrix": detection_matrix,
            "overall_score": round(
                sum(r["accuracy"] for r in detection_matrix.values()) / 5, 1
            ),
            "details": self.results
        }
        
        # 打印报告
        self._print_report(summary)
        
        return summary
    
    def _print_report(self, summary: Dict):
        """打印对抗测试报告"""
        print("\n📊 对抗测试结果")
        print("-" * 60)
        print(f"{'级别':<8} {'测试数':<8} {'发现数':<8} {'发现率':<10} {'准确度':<10}")
        print("-" * 60)
        
        for level in ["L1", "L2", "L3", "L4", "L5"]:
            m = summary["detection_matrix"][level]
            print(f"{level:<8} {m['total_tests']:<8} {m['detected']:<8} "
                  f"{m['detection_rate']:<9}% {m['accuracy']:<9}%")
        
        print("-" * 60)
        print(f"总体准确度: {summary['overall_score']}%")
        
        # 判定
        if summary['overall_score'] >= 80:
            print("🎯 判定: 优秀 - 各级发现率达标")
        elif summary['overall_score'] >= 60:
            print("⚠️  判定: 及格 - 部分级别需改进")
        else:
            print("❌ 判定: 不合格 - 需要大幅改进")


def main():
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="对抗测试 (S7)")
    parser.add_argument("--skill", required=True, help="测试的Skill路径")
    parser.add_argument("--level", help="仅测试指定级别")
    parser.add_argument("--output", help="输出报告文件")
    
    args = parser.parse_args()
    
    tester = AdversarialTester(args.skill)
    results = tester.run_all_tests()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n📝 报告已保存: {args.output}")
    
    # 返回码
    sys.exit(0 if results['overall_score'] >= 60 else 1)


if __name__ == "__main__":
    main()
