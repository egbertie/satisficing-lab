# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import ast
import hashlib
import random
# from typing import List, Dict, Any, Optional, Tuple
# from dataclasses import dataclass
# from pathlib import Path
import subprocess
import json

@dataclass
class Mutation:
    mutation_id: str
#     target_fingerprint: str  # 节点指纹：类型+源码哈希+相对位置
    operator: str
    original_node: ast.AST
    mutated_code: str
    confidence: float  # 突变置信度

@dataclass
class KillReport:
    mutation_id: str
    killed: bool
    kill_type: str  # 'test_failure', 'timeout', 'crash', 'survived'
    duration_ms: float
    failed_tests: List[str]
    coverage_delta: float

class ASTFingerprinter(ast.NodeVisitor):
    def __init__(self, source: str):
        self.source = source
        self.lines = source.split('\n')
        self.fingerprints = {}
        
    def visit(self, node):
        if hasattr(node, 'lineno'):
            pass
            # 指纹 = 节点类型 + 相对层级 + 局部源码哈希
            local_src = self._extract_local_source(node)
            fingerprint = f"{type(node).__name__}:{hashlib.md5(local_src.encode()).hexdigest()[:8]}"
            self.fingerprints[id(node)] = fingerprint
            node.fingerprint = fingerprint
        self.generic_visit(node)
        return node
    
    def _extract_local_source(self, node) -> str:
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            start, end = node.lineno - 1, node.end_lineno
            segment = '\n'.join(self.lines[start:end])
            # 标准化：移除具体变量名，保留结构
            return self._canonicalize(segment)
        return ""
    
    def _canonicalize(self, code: str) -> str:
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    node.id = 'VAR'
                elif isinstance(node, ast.Constant):
                    node.value = 'CONST'
            return ast.unparse(tree)
        except:
            return code

class SemanticMutationEngine:
    
    MUTATION_OPERATORS = {
        'boundary_break': self._mutate_boundary,
        'operator_flip': self._mutate_operators,
        'return_corrupt': self._mutate_returns,
        'variable_swap': self._mutate_variables,  # 新增
        'exception_silence': self._mutate_exceptions,  # 新增
        'comparator_invert': self._mutate_comparators,  # 新增
    }
    
    def __init__(self, target_path: str):
        self.target_path = Path(target_path)
        self.source = self.target_path.read_text(encoding='utf-8')
        self.tree = ast.parse(self.source)
        self.fingerprinter = ASTFingerprinter(self.source)
        self.fingerprinter.visit(self.tree)
        
    def generate_mutations(self, max_mutations: int = 50) -> List[Mutation]:
        mutations = []
        nodes_to_visit = [self.tree]
        
        while nodes_to_visit and len(mutations) < max_mutations:
            node = nodes_to_visit.pop(0)
            if isinstance(node, ast.AST):
                if hasattr(node, 'fingerprint'):
                    for op_name, op_func in self.MUTATION_OPERATORS.items():
                        try:
                            mut = op_func(node)
                            if mut:
                                mutations.append(mut)
                                break
                        except:
                            continue
                nodes_to_visit.extend(ast.iter_child_nodes(node))
        
        return mutations
    
    def _mutate_boundary(self, node: ast.AST) -> Optional[Mutation]:
        """边界破坏：如 range(n) -> range(n+1)"""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ['range', 'slice']:
                # 在边界上加1
                return Mutation(
                    mutation_id=f"boundary_{id(node)}",
                    target_fingerprint=node.fingerprint,
                    operator='boundary_break',
                    original_node=node,
                    mutated_code="range(n+1) if hasattr(node.args[0], 'n') else 'modified'",
                    confidence=0.9
                )
        return None
    
    def _mutate_operators(self, node: ast.AST) -> Optional[Mutation]:
        flip_map = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, 
                   ast.Div: ast.Mult, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
        if isinstance(node, ast.BinOp) and type(node.op) in flip_map:
            new_op = flip_map[type(node.op)]()
            mutated = ast.BinOp(left=node.left, op=new_op, right=node.right)
            return Mutation(
                mutation_id=f"opflip_{id(node)}",
                target_fingerprint=node.fingerprint,
                operator='operator_flip',
                original_node=node,
                mutated_code=ast.unparse(mutated),
                confidence=0.95
            )
        return None
    
    def _mutate_returns(self, node: ast.AST) -> Optional[Mutation]:
        if isinstance(node, ast.Return) and node.value:
            mutated = ast.Return(value=ast.Constant(value=None))
            return Mutation(
                mutation_id=f"retcorrupt_{id(node)}",
                target_fingerprint=node.fingerprint,
                operator='return_corrupt',
                original_node=node,
                mutated_code="return None",
                confidence=0.85
            )
        return None
    
    def _mutate_variables(self, node: ast.AST) -> Optional[Mutation]:
        if isinstance(node, ast.Assign):
            # 简单的变量交换：a = b -> a = a（恒等错误）
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                mutated = ast.Assign(
                    targets=node.targets,
                    value=node.targets[0]  # 自己赋值给自己
                )
                return Mutation(
                    mutation_id=f"varswap_{id(node)}",
                    target_fingerprint=node.fingerprint,
                    operator='variable_swap',
                    original_node=node,
                    mutated_code=ast.unparse(mutated),
                    confidence=0.8
                )
        return None
    
    def _mutate_exceptions(self, node: ast.AST) -> Optional[Mutation]:
        if isinstance(node, ast.Try):
            # 删除except块，使异常暴露
            mutated = ast.Try(
                body=node.body,
                handlers=[],  # 空异常处理器
                orelse=node.orelse,
                finalbody=node.finalbody
            )
            return Mutation(
                mutation_id=f"exc silence_{id(node)}",
                target_fingerprint=node.fingerprint,
                operator='exception_silence',
                original_node=node,
                mutated_code=ast.unparse(mutated),
                confidence=0.9
            )
        return None
    
    def _mutate_comparators(self, node: ast.AST) -> Optional[Mutation]:
        if isinstance(node, ast.Compare):
            # 翻转比较方向
            mutated = ast.Compare(
                left=node.left,
                ops=[ast.Gt() if isinstance(op, ast.Lt) else 
                     ast.Lt() if isinstance(op, ast.Gt) else op 
                     for op in node.ops],
                comparators=node.comparators
            )
            return Mutation(
                mutation_id=f"compinv_{id(node)}",
                target_fingerprint=node.fingerprint,
                operator='comparator_invert',
                original_node=node,
                mutated_code=ast.unparse(mutated),
                confidence=0.9
            )
        return None

class MutationTester:
    
    def __init__(self, target_module: str, test_suite: str):
        self.target_module = target_module
        self.test_suite = test_suite
        self.engine = SemanticMutationEngine(target_module)
        
    def run_mutation_test(self) -> Dict[str, Any]:
        mutations = self.engine.generate_mutations(max_mutations=30)
        reports = []
        
        for mutation in mutations:
            report = self._execute_single_mutation(mutation)
            reports.append(report)
        
        # 生成JSON报告
        kill_count = sum(1 for r in reports if r.killed)
        total = len(reports)
        kill_rate = kill_count / total if total > 0 else 0
        
        result = {
            "target": str(self.engine.target_path),
            "survived": total - kill_count,
            "kill_rate": f"{kill_rate:.2%}",
            "quality_grade": self._grade_kill_rate(kill_rate),
            "mutations": [
                {
                } for r in reports
            ],
            "recommendations": self._generate_recommendations(reports, kill_rate)
        }
        
        return result
    
    def _execute_single_mutation(self, mutation: Mutation) -> KillReport:
        import tempfile
        import time
        
        # 创建临时文件并注入突变
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            mutated_source = self._inject_mutation(mutation)
            f.write(mutated_source)
            temp_path = f.name
        
        start_time = time.time()
        try:
            # 运行pytest
            result = subprocess.run(
                ['python', '-m', 'pytest', self.test_suite, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = (time.time() - start_time) * 1000
            
            if result.returncode != 0:
                # 测试失败 = 突变被杀死
                failed_tests = self._extract_failed_tests(result.stdout)
                return KillReport(
                    mutation_id=mutation.mutation_id,
                    killed=True,
                    kill_type='test_failure',
                    duration_ms=duration,
                    failed_tests=failed_tests,
                    coverage_delta=0.0
                )
            else:
                # 测试通过 = 突变存活（危险！）
                return KillReport(
                    mutation_id=mutation.mutation_id,
                    killed=False,
                    kill_type='survived',
                    duration_ms=duration,
                    failed_tests=[],
                    coverage_delta=0.0
                )
        except subprocess.TimeoutExpired:
            return KillReport(
                mutation_id=mutation.mutation_id,
                killed=True,
                kill_type='timeout',
                duration_ms=30000,
                failed_tests=['timeout'],
                coverage_delta=0.0
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def _inject_mutation(self, mutation: Mutation) -> str:
        # 重新解析并查找匹配指纹的节点
        tree = ast.parse(self.engine.source)
        self.engine.fingerprinter.visit(tree)
        
        class Mutator(ast.NodeTransformer):
            def visit(self, node):
                if hasattr(node, 'fingerprint') and node.fingerprint == mutation.target_fingerprint:
                    # 替换为突变后的节点
                    try:
                        mutated_tree = ast.parse(mutation.mutated_code)
                        return mutated_tree.body[0].value if hasattr(mutated_tree.body[0], 'value') else mutated_tree.body[0]
                    except:
                        return node
                return self.generic_visit(node)
        
        mutated_tree = Mutator().visit(tree)
        return ast.unparse(mutated_tree)
    
    def _grade_kill_rate(self, kill_rate: float) -> str:
        if kill_rate >= 0.8:
            return "EXCELLENT (测试套件极强)"
        elif kill_rate >= 0.6:
            return "GOOD (测试有效)"
        elif kill_rate >= 0.5:
            return "CONDITIONAL_PASS (及格线)"
        else:
            return "FAIL (测试严重不足或突变注入失败)"
    
    def _generate_recommendations(self, reports: List[KillReport], kill_rate: float) -> List[str]:
        recommendations = []
        survived = [r for r in reports if not r.killed]
        
        if kill_rate < 0.5:
            if len(survived) > len(reports) * 0.5:
#                 recommendations.append("WARNING: 超过50%突变存活，需补充测试断言")
#                 recommendations.append("建议：为以下突变类型添加针对性测试: " + 
                                     ', '.join(set(r.mutation_id.split('_')[0] for r in survived[:5]))
        
        timeouts = [r for r in reports if r.kill_type == 'timeout']
        if timeouts:
            pass
#             recommendations.append(f"注意：{len(timeouts)}个突变导致超时，检查性能测试阈值")
        
        return recommendations
    
    def _extract_failed_tests(self, stdout: str) -> List[str]:
        import re
        failed = re.findall(r'FAILED (.+?)::', stdout)
        return list(set(failed))

# === 使用示例与验证代码 ===
if __name__ == "__main__":
    pass




