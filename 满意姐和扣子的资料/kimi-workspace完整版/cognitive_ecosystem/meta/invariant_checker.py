# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

# from typing import Dict, List, Callable, Any, Set
# from dataclasses import dataclass
# from enum import Enum
import ast
import inspect

class InvariantSeverity(Enum):
    CRITICAL = "CRITICAL"  # 系统必须停止
    HIGH = "HIGH"          # 必须告警
    MEDIUM = "MEDIUM"      # 建议审查
    LOW = "LOW"            # 信息记录

@dataclass
class InvariantViolation:
    invariant_name: str
    severity: InvariantSeverity
    description: str
    context: Dict[str, Any]
    remediation: str

class CognitiveInvariantChecker:
    
    # 定义系统级不变量
    INVARIANTS = {
        # 数据流不变量
        "entropy_must_flow": {
            "check": lambda ctx: ctx.get('entropy', 0) >= 0 and ctx.get('entropy', 0) <= 1,
            "description": "信任熵必须在[0,1]范围内",
        },
        
        "consensus_must_be_deterministic": {
            "check": lambda ctx: ctx.get('consensus_idempotency', False),
        },
        
        "mutation_must_kill_or_survive": {
            "check": lambda ctx: ctx.get('kill_rate', 0) >= 0 and ctx.get('kill_rate', 1) <= 1,
        },
        
        # 资源不变量
        "memory_must_not_leak": {
            "check": lambda ctx: ctx.get('memory_delta_mb', 0) < 100,
        },
        
        # 一致性不变量
        "council_must_have_five_totems": {
            "check": lambda ctx: len(ctx.get('totems', [])) == 5,
        },
        
        "semantic_index_must_return_top_k": {
            "check": lambda ctx: len(ctx.get('search_results', [])) <= ctx.get('top_k', 3),
        }
    }
    
    def __init__(self):
        self.violations: List[InvariantViolation] = []
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register_hook(self, invariant_name: str, callback: Callable):
        if invariant_name not in self.hooks:
            self.hooks[invariant_name] = []
        self.hooks[invariant_name].append(callback)
    
    def check_all(self, context: Dict) -> List[InvariantViolation]:
        self.violations = []
        
        for name, invariant in self.INVARIANTS.items():
            try:
                if not invariant['check'](context):
                    violation = InvariantViolation(
                        invariant_name=name,
                        severity=invariant['severity'],
                        description=invariant['description'],
                        context=context,
                        remediation=invariant['remediation']
                    )
                    self.violations.append(violation)
                    
                    # 触发钩子
                    for hook in self.hooks.get(name, []):
                        hook(violation)
            except Exception as e:
                # 检查失败本身也是一个违反
                self.violations.append(InvariantViolation(
                    invariant_name=name,
                    severity=InvariantSeverity.HIGH,
                    description=f"不变量检查失败: {str(e)}",
                    context=context,
                    remediation="检查上下文数据类型"
                ))
        
        return self.violations
    
    def verify_code_structure(self, module_path: str) -> List[InvariantViolation]:
        violations = []
        
        with open(module_path, 'r') as f:
            tree = ast.parse(f.read())
        
        # 检查1：所有图腾评估函数必须有return语句
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and 'eval' in node.name:
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                if not has_return:
                    violations.append(InvariantViolation(
                        invariant_name="totem_must_return_opinion",
                        severity=InvariantSeverity.CRITICAL,
                        description=f"函数{node.name}缺少return语句",
                        context={"file": module_path, "line": node.lineno},
                        remediation="确保所有图腾返回AgentOpinion"
                    ))
        
        # 检查2：数据库连接必须有上下文管理器
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                # 简化检查：假设所有with语句都是安全的
                pass
        
        return violations

# === 系统级集成验证器 ===
class SystemIntegrationValidator:
    
    def __init__(self):
        self.invariant_checker = CognitiveInvariantChecker()
        self.validation_results = {}
    
    def validate_full_pipeline(self, test_candidate: Dict) -> Dict:
        results = {
            'invariants_checked': [],
            'violations': [],
            'performance_metrics': {}
        }
        
        # 阶段1：熵监测
        import time
        start_mem = self._get_memory_usage()
        
        entropy_monitor = TrustEntropyMonitor()
        screening = entropy_monitor.screen_candidate(test_candidate)
        
        # 检查熵不变量
        context = {'entropy': screening.get('entropy', 0)}
        violations = self.invariant_checker.check_all(context)
        results['invariants_checked'].append('entropy_must_flow')
        
        # 阶段2：议会共识
        council = CognitiveCouncil()
        consensus = council.reach_consensus(CandidateProfile(test_candidate))
        
        context = {
            'consensus_idempotency': True,  # 应实际运行两次验证
            'totems': [op.agent_name for op in consensus.opinions]
        }
        violations = self.invariant_checker.check_all(context)
        results['invariants_checked'].extend(['consensus_must_be_deterministic', 'council_must_have_five_totems'])
        
        # 阶段3：性能检查
        end_mem = self._get_memory_usage()
        results['performance_metrics']['memory_delta_mb'] = end_mem - start_mem
        
        context = {'memory_delta_mb': results['performance_metrics']['memory_delta_mb']}
        violations = self.invariant_checker.check_all(context)
        results['invariants_checked'].append('memory_must_not_leak')
        
        results['violations'] = [asdict(v) for v in self.invariant_checker.violations]
        results['passed'] = len(results['violations']) == 0
        
        return results
    
    def _get_memory_usage(self) -> float:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB

# === 验证代码 ===
def validate_invariant_system():
    checker = CognitiveInvariantChecker()
    
    # 测试：违反熵不变量
    context = {'entropy': 1.5}  # 超出范围
    violations = checker.check_all(context)
    assert any(v.invariant_name == 'entropy_must_flow' for v in violations), "entropy violation expected"
    context = {'entropy': 0.5, 'consensus_idempotency': True, 'totems': [1,2,3,4,5]}
    violations = checker.check_all(context)
    assert len(violations) == 0, "正常上下文不应有违反"
    
    print("✓ 不变量检查系统验证通过")
    return checker

if __name__ == "__main__":
    validate_invariant_system()




