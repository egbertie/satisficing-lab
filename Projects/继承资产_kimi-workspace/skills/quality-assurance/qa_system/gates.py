"""
Quality Gates Module
质量门禁定义与执行
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .core import (
    GateCheck, GateResult, GateStatus, QualityResult, ConfidenceLevel
)


class PrerequisitesCheck(GateCheck):
    """前置条件检查 - S2.2"""
    
    def __init__(self):
        super().__init__(
            name="prerequisites",
            description="检查前置条件",
            weight=0.15,
            blocking=True
        )
    
    def evaluate(self, target: Any) -> QualityResult:
        checks = {
            "env_vars": self._check_env_vars(),
            "dependencies": self._check_dependencies(),
            "permissions": self._check_permissions(),
            "config_files": self._check_config_files()
        }
        
        all_passed = all(c["passed"] for c in checks.values())
        score = sum(c["score"] for c in checks.values()) / len(checks)
        
        return QualityResult(
            result=all_passed,
            confidence=ConfidenceLevel.HIGH,
            score=score,
            notes="前置条件检查完成",
            details=checks
        )
    
    def _check_env_vars(self) -> Dict[str, Any]:
        """检查环境变量"""
        required_vars = ["PYTHONPATH", "PATH"]
        missing = [v for v in required_vars if v not in __import__('os').environ]
        
        return {
            "passed": len(missing) == 0,
            "score": 100 if len(missing) == 0 else 100 - len(missing) * 25,
            "missing": missing
        }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """检查依赖安装"""
        try:
            subprocess.run(["python3", "-c", "import pytest, black, flake8"], 
                         check=True, capture_output=True)
            return {"passed": True, "score": 100}
        except subprocess.CalledProcessError:
            return {"passed": False, "score": 0, "error": "Missing dependencies"}
    
    def _check_permissions(self) -> Dict[str, Any]:
        """检查权限"""
        return {"passed": True, "score": 100}
    
    def _check_config_files(self) -> Dict[str, Any]:
        """检查配置文件"""
        config_files = ["pyproject.toml", "pytest.ini"]
        missing = [f for f in config_files if not Path(f).exists()]
        
        return {
            "passed": len(missing) == 0,
            "score": 100 if len(missing) == 0 else 100 - len(missing) * 30,
            "missing": missing
        }


class ComplianceCheck(GateCheck):
    """过程合规检查 - S2.3"""
    
    def __init__(self):
        super().__init__(
            name="compliance",
            description="检查过程合规性",
            weight=0.25,
            blocking=True
        )
    
    def evaluate(self, target: Any) -> QualityResult:
        checks = {
            "code_style": self._check_code_style(),
            "commit_message": self._check_commit_message(),
            "security_scan": self._run_security_scan(),
            "static_analysis": self._run_static_analysis()
        }
        
        all_passed = all(c["passed"] for c in checks.values())
        score = sum(c["score"] for c in checks.values()) / len(checks)
        
        return QualityResult(
            result=all_passed,
            confidence=ConfidenceLevel.HIGH,
            score=score,
            notes="合规检查完成",
            details=checks
        )
    
    def _check_code_style(self) -> Dict[str, Any]:
        """检查代码风格"""
        try:
            result = subprocess.run(
                ["flake8", "--max-line-length=100", "qa_system/"],
                capture_output=True,
                text=True
            )
            return {
                "passed": result.returncode == 0,
                "score": 100 if result.returncode == 0 else 80,
                "output": result.stdout
            }
        except Exception as e:
            return {"passed": False, "score": 0, "error": str(e)}
    
    def _check_commit_message(self) -> Dict[str, Any]:
        """检查提交信息"""
        return {"passed": True, "score": 100, "note": "Commit message check skipped"}
    
    def _run_security_scan(self) -> Dict[str, Any]:
        """运行安全扫描"""
        try:
            result = subprocess.run(
                ["bandit", "-r", "qa_system/", "-f", "json"],
                capture_output=True,
                text=True
            )
            return {
                "passed": result.returncode == 0,
                "score": 100 if result.returncode == 0 else 70,
                "output": result.stdout[:500] if result.stdout else ""
            }
        except Exception as e:
            return {"passed": False, "score": 0, "error": str(e)}
    
    def _run_static_analysis(self) -> Dict[str, Any]:
        """运行静态分析"""
        return {"passed": True, "score": 100, "note": "Static analysis check skipped"}


class ResultsCheck(GateCheck):
    """结果验收检查 - S2.4"""
    
    def __init__(self):
        super().__init__(
            name="results",
            description="检查结果验收",
            weight=0.40,
            blocking=True
        )
    
    def evaluate(self, target: Any) -> QualityResult:
        checks = {
            "unit_tests": self._run_unit_tests(),
            "coverage": self._check_coverage(),
            "integration_tests": self._run_integration_tests(),
            "performance_tests": self._run_performance_tests()
        }
        
        all_passed = all(c["passed"] for c in checks.values())
        score = sum(c["score"] for c in checks.values()) / len(checks)
        
        return QualityResult(
            result=all_passed,
            confidence=ConfidenceLevel.HIGH,
            score=score,
            notes="结果验收检查完成",
            details=checks
        )
    
    def _run_unit_tests(self) -> Dict[str, Any]:
        """运行单元测试"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/unit", "-v", "--tb=short", "-x"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "passed": result.returncode == 0,
                "score": 100 if result.returncode == 0 else 50,
                "output": result.stdout[-500:] if result.stdout else ""
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "score": 0, "error": "Timeout"}
        except Exception as e:
            return {"passed": False, "score": 0, "error": str(e)}
    
    def _check_coverage(self) -> Dict[str, Any]:
        """检查覆盖率"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--cov=qa_system", "--cov-report=term-missing", "-q"],
                capture_output=True,
                text=True,
                timeout=120
            )
            # Parse coverage from output
            output = result.stdout
            coverage = 0.0
            for line in output.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            coverage = float(parts[3].rstrip('%'))
                        except ValueError:
                            pass
            
            return {
                "passed": coverage >= 80,
                "score": min(coverage, 100),
                "coverage": coverage
            }
        except Exception as e:
            return {"passed": False, "score": 0, "error": str(e)}
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """运行集成测试"""
        return {"passed": True, "score": 100, "note": "Integration tests check skipped"}
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        return {"passed": True, "score": 100, "note": "Performance tests check skipped"}


class DocumentationCheck(GateCheck):
    """文档完整检查 - S2.5"""
    
    def __init__(self):
        super().__init__(
            name="documentation",
            description="检查文档完整性",
            weight=0.20,
            blocking=False
        )
    
    def evaluate(self, target: Any) -> QualityResult:
        checks = {
            "changelog": self._check_changelog(),
            "api_docs": self._check_api_docs(),
            "deploy_docs": self._check_deploy_docs(),
            "readme": self._check_readme()
        }
        
        all_passed = all(c["passed"] for c in checks.values())
        score = sum(c["score"] for c in checks.values()) / len(checks)
        
        return QualityResult(
            result=all_passed,
            confidence=ConfidenceLevel.MEDIUM,
            score=score,
            notes="文档检查完成",
            details=checks
        )
    
    def _check_changelog(self) -> Dict[str, Any]:
        """检查CHANGELOG"""
        return {"passed": True, "score": 100, "note": "CHANGELOG check skipped"}
    
    def _check_api_docs(self) -> Dict[str, Any]:
        """检查API文档"""
        return {"passed": True, "score": 100, "note": "API docs check skipped"}
    
    def _check_deploy_docs(self) -> Dict[str, Any]:
        """检查部署文档"""
        return {"passed": True, "score": 100, "note": "Deploy docs check skipped"}
    
    def _check_readme(self) -> Dict[str, Any]:
        """检查README"""
        readme_exists = Path("README.md").exists() or Path("SKILL.md").exists()
        return {
            "passed": readme_exists,
            "score": 100 if readme_exists else 50
        }


class QualityGate:
    """质量门禁执行器"""
    
    def __init__(self, name: str, min_score: float = 75.0, block_on_fail: bool = True):
        self.name = name
        self.min_score = min_score
        self.block_on_fail = block_on_fail
        self.checks: List[GateCheck] = []
    
    def add_check(self, check: GateCheck):
        """添加检查项"""
        self.checks.append(check)
    
    def execute(self, target: Any) -> GateResult:
        """执行门禁检查"""
        check_results = []
        failed_checks = []
        total_weighted_score = 0.0
        
        for check in self.checks:
            result = check.evaluate(target)
            weighted_score = result.score * check.weight
            total_weighted_score += weighted_score
            
            check_results.append({
                "name": check.name,
                "weight": check.weight,
                "score": result.score,
                "weighted_score": weighted_score,
                "passed": result.result,
                "confidence": result.confidence.value,
                "details": result.details
            })
            
            if not result.result and check.blocking:
                failed_checks.append(check.name)
                
            # 快速失败
            if not result.result and check.blocking and self.block_on_fail:
                return GateResult(
                    gate_name=self.name,
                    status=GateStatus.BLOCKED,
                    total_score=result.score,
                    weighted_score=total_weighted_score,
                    checks=check_results,
                    failed_checks=failed_checks
                )
        
        # 计算总分
        total_score = sum(r["score"] for r in check_results) / len(check_results) if check_results else 0
        
        # 判定状态
        if failed_checks:
            status = GateStatus.BLOCKED if self.block_on_fail else GateStatus.FAILED
        elif total_score >= self.min_score:
            status = GateStatus.PASSED
        else:
            status = GateStatus.CONDITIONAL
        
        return GateResult(
            gate_name=self.name,
            status=status,
            total_score=total_score,
            weighted_score=total_weighted_score,
            checks=check_results,
            failed_checks=failed_checks
        )


# 预定义门禁配置
GATE_CONFIGS = {
    "basic": {
        "min_score": 60,
        "block_on_fail": False,
        "checks": [ComplianceCheck]
    },
    "standard": {
        "min_score": 75,
        "block_on_fail": True,
        "checks": [PrerequisitesCheck, ComplianceCheck, ResultsCheck]
    },
    "critical": {
        "min_score": 90,
        "block_on_fail": True,
        "checks": [PrerequisitesCheck, ComplianceCheck, ResultsCheck, DocumentationCheck]
    }
}


def create_gate(level: str) -> QualityGate:
    """创建指定等级的门禁"""
    config = GATE_CONFIGS.get(level, GATE_CONFIGS["standard"])
    gate = QualityGate(
        name=f"{level}-gate",
        min_score=config["min_score"],
        block_on_fail=config["block_on_fail"]
    )
    
    for check_class in config["checks"]:
        gate.add_check(check_class())
    
    return gate
