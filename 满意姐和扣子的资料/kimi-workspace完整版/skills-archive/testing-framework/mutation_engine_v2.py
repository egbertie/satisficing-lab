"""
Mutation Engine V2 - 真实的AST语义突变测试引擎
支持 boundary_break / operator_flip / return_corrupt
"""

import ast
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class MutationType(Enum):
    BOUNDARY_BREAK = "boundary_break"
    OPERATOR_FLIP = "operator_flip"
    RETURN_CORRUPT = "return_corrupt"


@dataclass
class Mutation:
    mutation_id: str
    mutation_type: MutationType
    target_file: str
    line_number: int
    original_code: str
    mutated_code: str
    detected: bool = False
    detection_output: str = ""


class MutationEngineV2:
    """AST级突变引擎"""

    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.mutations: List[Mutation] = []

    def _load_ast(self, file_path: Path) -> ast.AST:
        return ast.parse(file_path.read_text(encoding="utf-8"))

    def _save_ast(self, tree: ast.AST, file_path: Path):
        file_path.write_text(ast.unparse(tree), encoding="utf-8")

    def generate_mutations(self, target_file: Path) -> List[Mutation]:
        """为单个文件生成突变点"""
        generated = []
        source = target_file.read_text(encoding="utf-8")
        tree = self._load_ast(target_file)

        class Mutator(ast.NodeTransformer):
            def __init__(self, engine, source_lines, generated_list):
                self.engine = engine
                self.source_lines = source_lines
                self.generated = generated_list
                self.counter = 0

            def visit_Compare(self, node):
                self.generic_visit(node)
                for i, op in enumerate(node.ops):
                    if isinstance(op, ast.Gt):
                        new_op = ast.GtE()
                        typ = MutationType.BOUNDARY_BREAK
                    elif isinstance(op, ast.Lt):
                        new_op = ast.LtE()
                        typ = MutationType.BOUNDARY_BREAK
                    elif isinstance(op, ast.Eq):
                        new_op = ast.NotEq()
                        typ = MutationType.OPERATOR_FLIP
                    elif isinstance(op, ast.NotEq):
                        new_op = ast.Eq()
                        typ = MutationType.OPERATOR_FLIP
                    else:
                        continue

                    mutated = ast.Compare(left=node.left, ops=[new_op], comparators=node.comparators)
                    m = Mutation(
                        mutation_id=f"{typ.value}_{target_file.stem}_{self.counter}",
                        mutation_type=typ,
                        target_file=str(target_file),
                        line_number=getattr(node, 'lineno', 0),
                        original_code=self.source_lines[getattr(node, 'lineno', 1) - 1].strip(),
                        mutated_code=ast.unparse(mutated)
                    )
                    self.generated.append((m, mutated, node))
                    self.counter += 1
                return node

            def visit_BinOp(self, node):
                self.generic_visit(node)
                if isinstance(node.op, ast.Add):
                    mutated = ast.BinOp(left=node.left, op=ast.Sub(), right=node.right)
                    typ = MutationType.OPERATOR_FLIP
                elif isinstance(node.op, ast.Sub):
                    mutated = ast.BinOp(left=node.left, op=ast.Add(), right=node.right)
                    typ = MutationType.OPERATOR_FLIP
                else:
                    return node

                m = Mutation(
                    mutation_id=f"{typ.value}_{target_file.stem}_{self.counter}",
                    mutation_type=typ,
                    target_file=str(target_file),
                    line_number=getattr(node, 'lineno', 0),
                    original_code=self.source_lines[getattr(node, 'lineno', 1) - 1].strip(),
                    mutated_code=ast.unparse(mutated)
                )
                self.generated.append((m, mutated, node))
                self.counter += 1
                return node

            def visit_Return(self, node):
                self.generic_visit(node)
                if node.value:
                    # 简单篡改：数值/字符串取反，None保持不变
                    if isinstance(node.value, ast.Constant):
                        val = node.value.value
                        if isinstance(val, bool):
                            new_val = ast.Constant(value=not val)
                        elif isinstance(val, (int, float)) and val != 0:
                            new_val = ast.Constant(value=-val)
                        elif isinstance(val, str):
                            new_val = ast.Constant(value=val + "_CORRUPTED")
                        else:
                            return node
                    elif isinstance(node.value, ast.NameConstant):  # Py<3.8 compat
                        new_val = ast.NameConstant(value=not node.value.value)
                    else:
                        return node

                    m = Mutation(
                        mutation_id=f"{MutationType.RETURN_CORRUPT.value}_{target_file.stem}_{self.counter}",
                        mutation_type=MutationType.RETURN_CORRUPT,
                        target_file=str(target_file),
                        line_number=getattr(node, 'lineno', 0),
                        original_code=self.source_lines[getattr(node, 'lineno', 1) - 1].strip(),
                        mutated_code=ast.unparse(ast.Return(value=new_val))
                    )
                    self.generated.append((m, ast.Return(value=new_val), node))
                    self.counter += 1
                return node

        source_lines = source.splitlines()
        temp_generated = []
        Mutator(self, source_lines, temp_generated).visit(tree)

        # 为每个突变点保存独立的突变文件
        for m, mutated_node, original_node in temp_generated:
            # 深拷贝AST并应用单点突变
            fresh_tree = self._load_ast(target_file)

            class SingleApplier(ast.NodeTransformer):
                def __init__(self, target_lineno, replacement):
                    self.target_lineno = target_lineno
                    self.replacement = replacement
                    self.applied = False

                def visit(self, node):
                    if hasattr(node, 'lineno') and node.lineno == self.target_lineno and not self.applied:
                        if type(node) == type(self.replacement):
                            self.applied = True
                            return self.replacement
                    return self.generic_visit(node)

            # 这里简化处理：按行号匹配可能有歧义，但大多数情况下够用
            SingleApplier(getattr(original_node, 'lineno', 0), mutated_node).visit(fresh_tree)
            ast.fix_missing_locations(fresh_tree)

            mutated_path = self.workspace / ".staging" / "mutations" / f"{m.mutation_id}.py"
            mutated_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_ast(fresh_tree, mutated_path)
            m.mutated_code = str(mutated_path)
            generated.append(m)

        return generated

    def run_tests(self, mutation: Mutation, test_command: str, working_dir: Optional[Path] = None) -> bool:
        """运行测试，返回是否杀死突变（测试失败=杀死）"""
        # 备份原文件
        original_file = Path(mutation.target_file)
        backup = original_file.with_suffix(original_file.suffix + ".bak")
        shutil = __import__("shutil")
        shutil.copy2(original_file, backup)

        # 替换为突变文件
        mutated_ast = self._load_ast(Path(mutation.mutated_code))
        self._save_ast(mutated_ast, original_file)

        try:
            result = subprocess.run(
                test_command, shell=True, cwd=str(working_dir or self.workspace),
                capture_output=True, text=True, timeout=60
            )
            detected = result.returncode != 0
            mutation.detected = detected
            mutation.detection_output = result.stdout + result.stderr
        except Exception as e:
            mutation.detected = True  # 超时/异常视为杀死
            mutation.detection_output = str(e)
        finally:
            # 恢复原文件
            shutil.copy2(backup, original_file)
            backup.unlink()

        return mutation.detected

    def run_mutation_suite(self, target_files: List[Path], test_command: str) -> Dict:
        """对多个文件批量运行突变测试"""
        all_mutations = []
        for tf in target_files:
            all_mutations.extend(self.generate_mutations(tf))

        killed = 0
        for m in all_mutations:
            if self.run_tests(m, test_command):
                killed += 1

        kill_rate = (killed / len(all_mutations) * 100) if all_mutations else 0.0

        return {
            "total_mutations": len(all_mutations),
            "killed": killed,
            "survived": len(all_mutations) - killed,
            "kill_rate": round(kill_rate, 2),
            "mutations": [
                {
                    "id": m.mutation_id,
                    "type": m.mutation_type.value,
                    "file": m.target_file,
                    "line": m.line_number,
                    "detected": m.detected,
                    "output_snippet": m.detection_output[:200]
                }
                for m in all_mutations
            ],
            "recommendations": [
                "Kill rate >= 50%：测试覆盖良好" if kill_rate >= 50 else f"Kill rate {kill_rate:.1f}% 偏低，需要增加断言覆盖边界条件和返回值"
            ]
        }
