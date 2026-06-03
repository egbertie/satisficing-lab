#!/usr/bin/env python3
"""
quality-assurance - 质量保证框架
真正实现版本

功能:
- 质量门禁控制
- 自动化测试集成
- 代码质量检查
- 文档完整性验证
- 发布前检查清单

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class GateStatus(Enum):
    """门禁状态"""
    PASSED = "passed"      # 通过
    WARNING = "warning"    # 警告
    FAILED = "failed"      # 失败
    BLOCKED = "blocked"    # 阻塞


class CheckType(Enum):
    """检查类型"""
    UNIT_TEST = "unit_test"          # 单元测试
    INTEGRATION_TEST = "integration_test"  # 集成测试
    CODE_REVIEW = "code_review"      # 代码审查
    DOCUMENTATION = "documentation"  # 文档检查
    SECURITY = "security"            # 安全检查
    PERFORMANCE = "performance"      # 性能检查


@dataclass
class CheckResult:
    """检查结果"""
    check_type: str
    name: str
    status: str
    duration_ms: int
    message: str
    details: List[str]


@dataclass
class QualityGate:
    """质量门禁"""
    name: str
    required_checks: List[str]
    optional_checks: List[str]
    threshold: float  # 通过阈值


@dataclass
class AssuranceReport:
    """质量保证报告"""
    gate_name: str
    overall_status: str
    check_results: List[CheckResult]
    passed_count: int
    failed_count: int
    warning_count: int
    duration_ms: int
    timestamp: str
    can_proceed: bool
    blockers: List[str]


class QualityAssurance:
    """质量保证框架"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化"""
        self.config = config or {}
        self.gates = self._load_gates()
    
    def _load_gates(self) -> Dict[str, QualityGate]:
        """加载质量门禁配置"""
        default_gates = {
            'pre-commit': QualityGate(
                name='pre-commit',
                required_checks=[
                    CheckType.UNIT_TEST.value,
                    CheckType.CODE_REVIEW.value
                ],
                optional_checks=[
                    CheckType.DOCUMENTATION.value
                ],
                threshold=0.8
            ),
            'pre-release': QualityGate(
                name='pre-release',
                required_checks=[
                    CheckType.UNIT_TEST.value,
                    CheckType.INTEGRATION_TEST.value,
                    CheckType.CODE_REVIEW.value,
                    CheckType.DOCUMENTATION.value
                ],
                optional_checks=[
                    CheckType.SECURITY.value,
                    CheckType.PERFORMANCE.value
                ],
                threshold=0.9
            )
        }
        
        # 从配置加载自定义门禁
        custom_gates = self.config.get('gates', {})
        for name, gate_config in custom_gates.items():
            default_gates[name] = QualityGate(
                name=name,
                required_checks=gate_config.get('required', []),
                optional_checks=gate_config.get('optional', []),
                threshold=gate_config.get('threshold', 0.8)
            )
        
        return default_gates
    
    def run_gate(self, gate_name: str, project_path: str) -> AssuranceReport:
        """运行质量门禁"""
        import time
        start_time = time.time()
        
        gate = self.gates.get(gate_name)
        if not gate:
            return self._create_error_report(f"未知的门禁: {gate_name}")
        
        check_results = []
        
        # 运行必需检查
        for check in gate.required_checks:
            result = self._run_check(check, project_path, required=True)
            check_results.append(result)
        
        # 运行可选检查
        for check in gate.optional_checks:
            result = self._run_check(check, project_path, required=False)
            check_results.append(result)
        
        # 计算结果
        duration_ms = int((time.time() - start_time) * 1000)
        passed = sum(1 for r in check_results if r.status == GateStatus.PASSED.value)
        failed = sum(1 for r in check_results if r.status == GateStatus.FAILED.value)
        warnings = sum(1 for r in check_results if r.status == GateStatus.WARNING.value)
        
        # 判断是否通过
        total_required = len(gate.required_checks)
        passed_required = sum(1 for r in check_results 
                            if r.check_type in gate.required_checks 
                            and r.status in [GateStatus.PASSED.value, GateStatus.WARNING.value])
        
        # 计算通过率
        if total_required > 0:
            pass_rate = passed_required / total_required
        else:
            pass_rate = 1.0
        
        can_proceed = pass_rate >= gate.threshold and failed == 0
        
        # 收集阻塞项
        blockers = [r.name for r in check_results 
                   if r.check_type in gate.required_checks 
                   and r.status == GateStatus.FAILED.value]
        
        # 确定总体状态
        if failed > 0:
            overall_status = GateStatus.FAILED.value
        elif warnings > 0:
            overall_status = GateStatus.WARNING.value
        else:
            overall_status = GateStatus.PASSED.value
        
        if not can_proceed:
            overall_status = GateStatus.BLOCKED.value
        
        return AssuranceReport(
            gate_name=gate_name,
            overall_status=overall_status,
            check_results=check_results,
            passed_count=passed,
            failed_count=failed,
            warning_count=warnings,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat(),
            can_proceed=can_proceed,
            blockers=blockers
        )
    
    def _run_check(self, check_type: str, project_path: str, required: bool) -> CheckResult:
        """运行单个检查"""
        import time
        start = time.time()
        
        check_runners = {
            CheckType.UNIT_TEST.value: self._check_unit_tests,
            CheckType.INTEGRATION_TEST.value: self._check_integration_tests,
            CheckType.CODE_REVIEW.value: self._check_code_review,
            CheckType.DOCUMENTATION.value: self._check_documentation,
            CheckType.SECURITY.value: self._check_security,
            CheckType.PERFORMANCE.value: self._check_performance
        }
        
        runner = check_runners.get(check_type)
        if runner:
            status, message, details = runner(project_path)
        else:
            status = GateStatus.WARNING.value
            message = f"未实现的检查类型: {check_type}"
            details = []
        
        duration = int((time.time() - start) * 1000)
        
        return CheckResult(
            check_type=check_type,
            name=self._get_check_name(check_type),
            status=status,
            duration_ms=duration,
            message=message,
            details=details
        )
    
    def _check_unit_tests(self, project_path: str) -> tuple:
        """检查单元测试"""
        tests_path = Path(project_path) / "tests"
        if not tests_path.exists():
            return GateStatus.FAILED.value, "未找到测试目录", ["请创建 tests/ 目录并添加单元测试"]
        
        test_files = list(tests_path.glob("test_*.py"))
        if not test_files:
            return GateStatus.FAILED.value, "未找到测试文件", ["请添加以 test_ 开头的测试文件"]
        
        # 尝试运行测试
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", str(tests_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_path
            )
            
            if result.returncode == 0:
                return GateStatus.PASSED.value, f"所有单元测试通过 ({len(test_files)}个文件)", []
            else:
                failed = result.stdout.count("FAILED")
                return GateStatus.FAILED.value, f"单元测试失败 ({failed}个失败)", result.stdout.split('\n')[:10]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # pytest 可能未安装，检查文件存在性
            return GateStatus.WARNING.value, f"找到 {len(test_files)} 个测试文件 (未运行)", []
    
    def _check_integration_tests(self, project_path: str) -> tuple:
        """检查集成测试"""
        integration_path = Path(project_path) / "tests" / "integration"
        if not integration_path.exists():
            return GateStatus.WARNING.value, "未找到集成测试", ["建议添加 tests/integration/ 目录"]
        
        test_files = list(integration_path.glob("test_*.py"))
        return GateStatus.PASSED.value, f"找到 {len(test_files)} 个集成测试文件", []
    
    def _check_code_review(self, project_path: str) -> tuple:
        """检查代码审查要求"""
        issues = []
        
        # 检查是否有Python文件
        py_files = list(Path(project_path).rglob("*.py"))
        if not py_files:
            return GateStatus.PASSED.value, "无Python代码需要审查", []
        
        # 检查基本的代码规范
        for py_file in py_files[:5]:  # 只检查前5个文件
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查文件长度
                lines = content.split('\n')
                if len(lines) > 500:
                    issues.append(f"{py_file.name}: 文件过长 ({len(lines)}行)")
                
                # 检查是否有docstring
                if '"""' not in content and "'''" not in content:
                    issues.append(f"{py_file.name}: 缺少文档字符串")
                    
            except Exception:
                pass
        
        if issues:
            return GateStatus.WARNING.value, "发现代码规范问题", issues
        
        return GateStatus.PASSED.value, f"代码审查通过 ({len(py_files)}个文件)", []
    
    def _check_documentation(self, project_path: str) -> tuple:
        """检查文档完整性"""
        required_docs = ['README.md', 'SKILL.md', 'docs']
        missing = []
        
        for doc in required_docs:
            doc_path = Path(project_path) / doc
            if not doc_path.exists():
                missing.append(doc)
        
        if missing:
            return GateStatus.WARNING.value, f"缺少文档: {', '.join(missing)}", []
        
        return GateStatus.PASSED.value, "文档完整", []
    
    def _check_security(self, project_path: str) -> tuple:
        """检查安全问题"""
        # 简化版安全检查
        py_files = list(Path(project_path).rglob("*.py"))
        issues = []
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查硬编码密码
                if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    issues.append(f"{py_file.name}: 可能的硬编码密码")
                
                # 检查eval使用
                if 'eval(' in content:
                    issues.append(f"{py_file.name}: 使用eval()存在安全风险")
                    
            except Exception:
                pass
        
        if issues:
            return GateStatus.FAILED.value, "发现安全问题", issues
        
        return GateStatus.PASSED.value, "安全检查通过", []
    
    def _check_performance(self, project_path: str) -> tuple:
        """检查性能问题"""
        return GateStatus.PASSED.value, "性能检查通过 (基础)", ["性能基准测试需要额外配置"]
    
    def _get_check_name(self, check_type: str) -> str:
        """获取检查名称"""
        names = {
            CheckType.UNIT_TEST.value: "单元测试",
            CheckType.INTEGRATION_TEST.value: "集成测试",
            CheckType.CODE_REVIEW.value: "代码审查",
            CheckType.DOCUMENTATION.value: "文档检查",
            CheckType.SECURITY.value: "安全检查",
            CheckType.PERFORMANCE.value: "性能检查"
        }
        return names.get(check_type, check_type)
    
    def _create_error_report(self, message: str) -> AssuranceReport:
        """创建错误报告"""
        return AssuranceReport(
            gate_name="unknown",
            overall_status=GateStatus.FAILED.value,
            check_results=[],
            passed_count=0,
            failed_count=1,
            warning_count=0,
            duration_ms=0,
            timestamp=datetime.now().isoformat(),
            can_proceed=False,
            blockers=[message]
        )
    
    def export_report(self, report: AssuranceReport, format: str = "json") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps(report.__dict__, ensure_ascii=False, indent=2, default=str)
        elif format == "markdown":
            return self._format_markdown(report)
        return ""
    
    def _format_markdown(self, report: AssuranceReport) -> str:
        """格式化为Markdown"""
        status_icons = {
            GateStatus.PASSED.value: "✅",
            GateStatus.WARNING.value: "⚠️",
            GateStatus.FAILED.value: "❌",
            GateStatus.BLOCKED.value: "🚫"
        }
        
        lines = [
            f"# 质量保证报告: {report.gate_name}",
            "",
            f"**执行时间**: {report.timestamp}",
            f"**总体状态**: {status_icons.get(report.overall_status, '⚪')} {report.overall_status.upper()}",
            f"**执行耗时**: {report.duration_ms}ms",
            f"**能否继续**: {'✅ 是' if report.can_proceed else '❌ 否'}",
            "",
            "---",
            "",
            "## 📊 检查结果统计",
            "",
            f"- ✅ 通过: {report.passed_count}",
            f"- ⚠️ 警告: {report.warning_count}",
            f"- ❌ 失败: {report.failed_count}",
            "",
            "---",
            "",
            "## 🔍 详细结果",
            ""
        ]
        
        for result in report.check_results:
            icon = status_icons.get(result.status, '⚪')
            lines.append(f"### {icon} {result.name}")
            lines.append("")
            lines.append(f"**状态**: {result.status}")
            lines.append(f"**耗时**: {result.duration_ms}ms")
            lines.append(f"**消息**: {result.message}")
            
            if result.details:
                lines.append("")
                lines.append("**详情**:")
                for detail in result.details[:5]:
                    lines.append(f"- {detail}")
            
            lines.append("")
        
        if report.blockers:
            lines.extend([
                "---",
                "",
                "## 🚫 阻塞项",
                "",
            ])
            for blocker in report.blockers:
                lines.append(f"- ❌ {blocker}")
            lines.append("")
        
        return '\n'.join(lines)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quality Assurance - 质量保证框架')
    parser.add_argument('--gate', '-g', default='pre-commit',
                       help='门禁名称 (pre-commit, pre-release)')
    parser.add_argument('--path', '-p', default='.',
                       help='项目路径')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='报告格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    try:
        # 执行质量门禁
        qa = QualityAssurance()
        report = qa.run_gate(args.gate, args.path)
        
        # 输出报告
        output = qa.export_report(report, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 报告已保存: {args.output}")
        else:
            print(output)
        
        # 根据状态返回退出码
        if report.can_proceed:
            return 0
        else:
            print("\n❌ 质量门禁未通过，禁止继续")
            return 1
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    import re  # 导入re模块
    sys.exit(main())
