#!/usr/bin/env python3
"""
标准自检框架 - Standard Self-Check Framework
统一的S1-S7标准检查器，适用于所有Skills

使用方法:
    python3 standard_self_check.py <skill_path>
    
示例:
    python3 standard_self_check.py ../quality-assurance
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class CheckResult:
    """检查结果数据类"""
    standard: str
    name: str
    passed: bool
    message: str
    details: List[str]
    score: float  # 0.0 - 1.0

class StandardSelfChecker:
    """5/7标准自检器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.results: List[CheckResult] = []
        self.passed_count = 0
        self.failed_count = 0
        
    def _read_skill_md(self) -> Optional[str]:
        """读取SKILL.md内容"""
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            return skill_md.read_text(encoding='utf-8')
        return None
    
    def _read_config(self) -> Optional[Dict]:
        """读取配置文件"""
        config_files = ['config.yaml', 'config.json', 'cron.json']
        for cf in config_files:
            config_path = self.skill_path / cf
            if config_path.exists():
                try:
                    if cf.endswith('.yaml'):
                        import yaml
                        return yaml.safe_load(config_path.read_text())
                    else:
                        return json.loads(config_path.read_text())
                except:
                    continue
        return None
    
    def check_s1_input(self) -> CheckResult:
        """S1: 输入规范检查"""
        details = []
        score = 0.0
        
        content = self._read_skill_md()
        if not content:
            return CheckResult("S1", "输入规范", False, "SKILL.md不存在", [], 0.0)
        
        # 检查输入定义
        if 'S1' in content or '输入' in content:
            details.append("✓ 输入章节存在")
            score += 0.3
        
        # 检查输入参数定义
        if re.search(r'\|.*参数.*\|.*类型.*\|', content):
            details.append("✓ 参数表格定义")
            score += 0.4
        
        # 检查示例输入
        if '输入示例' in content or 'Example Input' in content:
            details.append("✓ 输入示例存在")
            score += 0.3
        
        passed = score >= 0.6
        return CheckResult(
            "S1", "输入规范", passed,
            f"输入规范完整性: {score*100:.0f}%",
            details, score
        )
    
    def check_s2_processing(self) -> CheckResult:
        """S2: 处理流程检查"""
        details = []
        score = 0.0
        
        content = self._read_skill_md()
        if not content:
            return CheckResult("S2", "处理流程", False, "SKILL.md不存在", [], 0.0)
        
        # 检查处理流程章节
        if 'S2' in content or '处理' in content or 'Processing' in content:
            details.append("✓ 处理流程章节存在")
            score += 0.3
        
        # 检查流程图或步骤
        if '```' in content and ('流程' in content or 'step' in content.lower()):
            details.append("✓ 流程代码块存在")
            score += 0.4
        
        # 检查处理逻辑描述
        if len(re.findall(r'^[0-9]+[\.\、]', content)) >= 3:
            details.append("✓ 步骤化描述存在")
            score += 0.3
        
        passed = score >= 0.6
        return CheckResult(
            "S2", "处理流程", passed,
            f"处理流程完整性: {score*100:.0f}%",
            details, score
        )
    
    def check_s3_output(self) -> CheckResult:
        """S3: 输出定义检查"""
        details = []
        score = 0.0
        
        content = self._read_skill_md()
        if not content:
            return CheckResult("S3", "输出定义", False, "SKILL.md不存在", [], 0.0)
        
        # 检查输出章节
        if 'S3' in content or '输出' in content or 'Output' in content:
            details.append("✓ 输出章节存在")
            score += 0.3
        
        # 检查输出格式定义
        if re.search(r'```(json|yaml|xml)', content):
            details.append("✓ 输出格式示例")
            score += 0.4
        
        # 检查输出表格
        if '输出项' in content or 'output' in content.lower():
            details.append("✓ 输出项定义")
            score += 0.3
        
        passed = score >= 0.6
        return CheckResult(
            "S3", "输出定义", passed,
            f"输出定义完整性: {score*100:.0f}%",
            details, score
        )
    
    def check_s4_automation(self) -> CheckResult:
        """S4: 自动化触发检查"""
        details = []
        score = 0.0
        
        # 检查cron配置
        cron_file = self.skill_path / "cron.json"
        if cron_file.exists():
            details.append("✓ cron.json配置存在")
            score += 0.5
        
        # 检查脚本可执行性
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            scripts = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh"))
            if scripts:
                details.append(f"✓ 发现 {len(scripts)} 个脚本")
                score += 0.3
        
        # 检查触发方式说明
        content = self._read_skill_md()
        if content and ('触发' in content or '自动化' in content or 'cron' in content.lower()):
            details.append("✓ 触发方式文档化")
            score += 0.2
        
        passed = score >= 0.5
        return CheckResult(
            "S4", "自动化触发", passed,
            f"自动化配置完整性: {score*100:.0f}%",
            details, score
        )
    
    def check_s5_validation(self) -> CheckResult:
        """S5: 验证方法检查"""
        details = []
        score = 0.0
        
        content = self._read_skill_md()
        if not content:
            return CheckResult("S5", "验证方法", False, "SKILL.md不存在", [], 0.0)
        
        # 检查S5章节
        if 'S5' in content or '验证' in content:
            details.append("✓ 验证章节存在")
            score += 0.3
        
        # 检查检查清单
        if '- [' in content or '检查项' in content:
            details.append("✓ 检查清单存在")
            score += 0.4
        
        # 检查测试脚本
        tests_dir = self.skill_path / "tests"
        if tests_dir.exists():
            details.append("✓ 测试目录存在")
            score += 0.3
        
        passed = score >= 0.6
        return CheckResult(
            "S5", "验证方法", passed,
            f"验证方法完整性: {score*100:.0f}%",
            details, score
        )
    
    def check_s6_limitations(self) -> CheckResult:
        """S6: 局限标注检查"""
        details = []
        score = 0.0
        
        content = self._read_skill_md()
        if not content:
            return CheckResult("S6", "局限标注", False, "SKILL.md不存在", [], 0.0)
        
        # 检查S6章节
        if 'S6' in content or '局限' in content or 'Limitations' in content:
            details.append("✓ 局限章节存在")
            score += 0.4
        
        # 检查至少2个局限点
        limitations = re.findall(r'^[\s]*[-\*][\s]*(.+局限.+|.+限制.+|.+不足.+)', content, re.MULTILINE)
        if len(limitations) >= 2:
            details.append(f"✓ 发现 {len(limitations)} 个局限标注")
            score += 0.6
        elif len(limitations) >= 1:
            details.append(f"⚠ 仅发现 {len(limitations)} 个局限标注")
            score += 0.3
        
        passed = score >= 0.5
        return CheckResult(
            "S6", "局限标注", passed,
            f"局限标注完整性: {score*100:.0f}%",
            details, score
        )
    
    def check_s7_adversarial(self) -> CheckResult:
        """S7: 对抗测试检查"""
        details = []
        score = 0.0
        
        content = self._read_skill_md()
        
        # 检查S7章节
        if content and ('S7' in content or '对抗' in content or 'Adversarial' in content):
            details.append("✓ 对抗测试章节存在")
            score += 0.4
        
        # 检查对抗测试脚本
        adv_scripts = [
            self.skill_path / "scripts" / "adversarial_test.py",
            self.skill_path / "tests" / "test_adversarial.py"
        ]
        for script in adv_scripts:
            if script.exists():
                details.append(f"✓ 对抗测试脚本: {script.name}")
                score += 0.6
                break
        
        # 检查测试用例定义
        test_cases = [
            self.skill_path / "tests" / "adversarial_test_cases.yaml",
            self.skill_path / "tests" / "adversarial_cases.json"
        ]
        for tc in test_cases:
            if tc.exists():
                details.append(f"✓ 测试用例定义: {tc.name}")
                score += 0.3
                break
        
        passed = score >= 0.5
        return CheckResult(
            "S7", "对抗测试", passed,
            f"对抗测试完整性: {score*100:.0f}%",
            details, score
        )
    
    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("="*70)
        print(f"🔍 标准自检框架 v1.0")
        print(f"   Skill: {self.skill_path.name}")
        print("="*70)
        
        checks = [
            self.check_s1_input,
            self.check_s2_processing,
            self.check_s3_output,
            self.check_s4_automation,
            self.check_s5_validation,
            self.check_s6_limitations,
            self.check_s7_adversarial,
        ]
        
        for check_func in checks:
            result = check_func()
            self.results.append(result)
            
            status = "✅" if result.passed else "❌"
            print(f"\n[{result.standard}] {result.name} {status}")
            print(f"   {result.message}")
            for detail in result.details:
                print(f"   {detail}")
            
            if result.passed:
                self.passed_count += 1
            else:
                self.failed_count += 1
        
        return self.failed_count == 0
    
    def generate_report(self, output_path: Optional[str] = None):
        """生成检查报告"""
        total = len(self.results)
        pass_rate = self.passed_count / total if total > 0 else 0
        
        report = {
            "skill_name": self.skill_path.name,
            "skill_path": str(self.skill_path),
            "check_time": str(Path().stat().st_mtime),
            "standard": "5/7标准",
            "summary": {
                "total": total,
                "passed": self.passed_count,
                "failed": self.failed_count,
                "pass_rate": f"{pass_rate*100:.1f}%",
                "certified": self.failed_count == 0
            },
            "details": [asdict(r) for r in self.results]
        }
        
        # 输出到控制台
        print("\n" + "="*70)
        print("📊 自检报告汇总")
        print("="*70)
        print(f"   通过: {self.passed_count}/{total}")
        print(f"   失败: {self.failed_count}/{total}")
        print(f"   通过率: {pass_rate*100:.1f}%")
        
        if self.failed_count == 0:
            print("\n🎉 恭喜! 该Skill已通过所有标准检查!")
        else:
            print(f"\n⚠️  有 {self.failed_count} 项标准未通过")
        
        # 保存到文件
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = self.skill_path / "reports" / "self_check_report.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 报告已保存: {output_path}")
        return report


def main():
    if len(sys.argv) < 2:
        print("用法: python3 standard_self_check.py <skill_path>")
        print("示例: python3 standard_self_check.py ../quality-assurance")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    if not os.path.exists(skill_path):
        print(f"错误: 路径不存在: {skill_path}")
        sys.exit(1)
    
    checker = StandardSelfChecker(skill_path)
    passed = checker.run_all_checks()
    checker.generate_report()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
