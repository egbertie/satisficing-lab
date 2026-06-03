#!/usr/bin/env python3
"""
自检脚本 - 验证 Skill 达到 Level 5 标准
"""

import json
import os
import sys
from pathlib import Path

# Skill 目录
SKILL_DIR = Path(__file__).parent.parent


class SelfChecker:
    """自检器"""
    
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        
    def _check(self, name: str, condition: bool, details: str = ""):
        """执行单个检查"""
        status = "✅ PASS" if condition else "❌ FAIL"
        self.checks.append({
            'name': name,
            'passed': condition,
            'details': details
        })
        
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        
        print(f"{status}: {name}")
        if details and not condition:
            print(f"       {details}")
        
        return condition
    
    def check_file_exists(self, path: str, description: str) -> bool:
        """检查文件是否存在"""
        full_path = SKILL_DIR / path
        return self._check(
            f"文件存在: {description}",
            full_path.exists(),
            f"缺少文件: {path}"
        )
    
    def check_skill_md(self) -> bool:
        """检查 SKILL.md 完整性"""
        skill_md = SKILL_DIR / "SKILL.md"
        if not skill_md.exists():
            return self._check("SKILL.md 存在", False, "SKILL.md 文件缺失")
        
        content = skill_md.read_text(encoding='utf-8')
        
        # 检查 7-S 标准
        standards = [
            ('S1', '输入API端点/监控指标/告警阈值'),
            ('S2', 'API监控（可用性→性能→错误率→配额）'),
            ('S3', '输出监控报告+异常告警+优化建议'),
            ('S4', 'cron定时自动执行监控'),
            ('S5', '监控数据准确性验证'),
            ('S6', '局限标注（无法检测业务逻辑错误）'),
            ('S7', '对抗测试（模拟API故障测试响应）')
        ]
        
        all_present = True
        for s_code, s_desc in standards:
            present = s_code in content
            self._check(f"SKILL.md 包含 {s_code}: {s_desc}", present)
            all_present = all_present and present
        
        return all_present
    
    def check_scripts(self) -> bool:
        """检查脚本完整性"""
        required_scripts = [
            ('scripts/probe.py', '探测脚本'),
            ('scripts/report.py', '报告生成脚本'),
            ('scripts/daemon.py', '守护进程'),
            ('scripts/chaos.py', '对抗测试脚本'),
            ('scripts/validate.py', '数据验证脚本'),
            ('scripts/self_check.py', '自检脚本'),
        ]
        
        all_exist = True
        for script, desc in required_scripts:
            exists = self.check_file_exists(script, desc)
            all_exist = all_exist and exists
        
        return all_exist
    
    def check_config(self) -> bool:
        """检查配置文件"""
        return self.check_file_exists('config.example.yaml', '配置模板')
    
    def check_documentation(self) -> bool:
        """检查文档完整性"""
        checks = [
            self.check_file_exists('requirements.txt', '依赖文件'),
            self.check_file_exists('manifest.json', 'Skill 元数据'),
        ]
        return all(checks)
    
    def check_executable(self) -> bool:
        """检查脚本可执行性"""
        import subprocess
        
        # 测试 probe 脚本帮助
        try:
            result = subprocess.run(
                [sys.executable, str(SKILL_DIR / 'scripts/probe.py'), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            probe_ok = result.returncode == 0 and 'usage' in result.stdout.lower()
        except Exception as e:
            probe_ok = False
        
        self._check('probe.py 可执行', probe_ok, str(e) if not probe_ok else "")
        
        # 测试 report 脚本帮助
        report_ok = False
        report_error = ""
        try:
            result = subprocess.run(
                [sys.executable, str(SKILL_DIR / 'scripts/report.py'), '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            report_ok = result.returncode == 0 and 'usage' in result.stdout.lower()
        except Exception as e:
            report_error = str(e)
        
        self._check('report.py 可执行', report_ok, report_error)
        
        return probe_ok and report_ok
    
    def check_chaos_testing(self) -> bool:
        """检查对抗测试功能"""
        chaos_script = SKILL_DIR / 'scripts/chaos.py'
        if not chaos_script.exists():
            return self._check('chaos.py 存在', False)
        
        content = chaos_script.read_text(encoding='utf-8')
        
        # 检查关键功能
        features = [
            ('timeout', '超时模拟'),
            ('latency', '延迟模拟'),
            ('error', '错误率模拟'),
            ('HTTPServer', 'HTTP服务器'),
        ]
        
        all_present = True
        for keyword, desc in features:
            present = keyword in content
            self._check(f'chaos.py 支持 {desc}', present)
            all_present = all_present and present
        
        return all_present
    
    def check_validation(self) -> bool:
        """检查数据验证功能"""
        validate_script = SKILL_DIR / 'scripts/validate.py'
        if not validate_script.exists():
            return self._check('validate.py 存在', False)
        
        content = validate_script.read_text(encoding='utf-8')
        
        # 检查验证功能
        checks = [
            ('validate_schema', '模式验证'),
            ('validate_consistency', '一致性验证'),
            ('validate_timeline', '时间线验证'),
            ('benchmark', '基准测试'),
        ]
        
        all_present = True
        for keyword, desc in checks:
            present = keyword in content
            self._check(f'validate.py 支持 {desc}', present)
            all_present = all_present and present
        
        return all_present
    
    def run_all_checks(self) -> dict:
        """运行所有检查"""
        print("="*60)
        print("🔍 vendor-api-monitor Skill 自检")
        print("="*60)
        print(f"Skill 目录: {SKILL_DIR}")
        print()
        
        # Level 5 标准检查
        print("📋 Level 5 标准检查")
        print("-"*60)
        
        self.check_skill_md()
        print()
        
        self.check_scripts()
        print()
        
        self.check_config()
        print()
        
        self.check_documentation()
        print()
        
        print("⚙️  功能检查")
        print("-"*60)
        
        self.check_executable()
        print()
        
        self.check_chaos_testing()
        print()
        
        self.check_validation()
        print()
        
        # 汇总
        print("="*60)
        print("📊 检查结果汇总")
        print("="*60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"总计: {len(self.checks)}")
        print(f"达标率: {self.passed/len(self.checks)*100:.1f}%")
        print()
        
        # Level 5 判定
        level5_requirements = [
            'S1:',
            'S2:',
            'S3:',
            'S4:',
            'S5:',
            'S6:',
            'S7:',
            '探测脚本',
            '报告生成脚本',
            '守护进程',
            '对抗测试脚本',
            '数据验证脚本',
        ]
        
        level5_met = all(
            any(req in c['name'] and c['passed'] for c in self.checks)
            for req in level5_requirements
        )
        
        if level5_met:
            print("🎉 恭喜! Skill 已达到 Level 5 标准")
        else:
            print("⚠️  Skill 尚未达到 Level 5 标准，请查看失败项")
        
        print("="*60)
        
        return {
            'passed': self.passed,
            'failed': self.failed,
            'total': len(self.checks),
            'level5_met': level5_met,
            'checks': self.checks
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Skill 自检')
    parser.add_argument('--json', '-j', action='store_true', help='JSON 输出')
    
    args = parser.parse_args()
    
    checker = SelfChecker()
    result = checker.run_all_checks()
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    sys.exit(0 if result['level5_met'] else 1)


if __name__ == '__main__':
    main()
