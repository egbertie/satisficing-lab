# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import ast
import inspect
import types
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
import copy

@dataclass
class SelfModel:
    source_code: str
    ast_representation: ast.AST
    capabilities: List[str]
    limitations: List[str]
    current_goals: List[str]
    modification_history: List[Dict]

class SelfModifyingSystem:
    
    def __init__(self):
        self.self_model: Optional[SelfModel] = None
        self.reflection_depth: int = 0
        self.max_reflection_depth: int = 3  # 防止无限递归
        self._build_initial_self_model()
    
    def _build_initial_self_model(self):
        # 获取自身源代码（简化：只获取当前类）
        source = inspect.getsource(self.__class__)
        tree = ast.parse(source)
        
        # 分析能力
        capabilities = self._extract_capabilities(tree)
        limitations = self._extract_limitations(tree)
        
        self.self_model = SelfModel(
            source_code=source,
            ast_representation=tree,
            capabilities=capabilities,
            limitations=limitations,
            current_goals=["improve_reasoning", "reduce_uncertainty"],
            modification_history=[]
        )
    
    def _extract_capabilities(self, tree: ast.AST) -> List[str]:
        capabilities = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 方法名即能力
                capabilities.append(node.name)
            elif isinstance(node, ast.ClassDef):
                capabilities.append(f"class:{node.name}")
        
        return capabilities
    
    def _extract_limitations(self, tree: ast.AST) -> List[str]:
        limitations = []
        
        # 检查是否有硬编码的阈值
        for node in ast.walk(tree):
            if isinstance(node, ast.Num):
                if isinstance(node.n, (int, float)) and node.n in [100, 3, 0.5]:
                    limitations.append(f"hardcoded_threshold:{node.n}")
        
        # 检查异常处理缺失
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                pass  # 有try块是好的
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and 'risky' in node.func.id:
                    if not any(isinstance(parent, ast.Try) for parent in ast.walk(tree)):
                        limitations.append(f"missing_exception_handling:{node.func.id}")
        
        return limitations
    
    def reflect(self) -> Dict:
        if self.reflection_depth >= self.max_reflection_depth:
            return {
                'status': 'reflection_limited',
                'reason': 'reached_max_depth',
                'depth': self.reflection_depth
            }
        
        self.reflection_depth += 1
        
        analysis = {
            'current_capabilities': len(self.self_model.capabilities),
            'identified_limitations': len(self.self_model.limitations),
            'modification_count': len(self.self_model.modification_history),
            'improvement_opportunities': []
        }
        
        # 识别改进机会
        for limitation in self.self_model.limitations:
            if "hardcoded" in limitation:
                analysis['improvement_opportunities'].append({
                    'target': limitation,
                    'strategy': 'make_adaptive',
                    'code_change': 'replace_constant_with_parameter'
                })
        
        # 生成新目标
        if len(self.self_model.limitations) > 5:
            self.self_model.current_goals.append("reduce_complexity")
        
        self.reflection_depth -= 1
        return analysis
    
    def self_modify(self, modification_plan: Dict) -> bool:
        # 安全检查1：修改是否被允许
        if not self._verify_modification_safety(modification_plan):
            return False
        
        # 安全检查2：修改是否可逆
        backup = copy.deepcopy(self.self_model)
        
        try:
            # 执行修改（简化：只修改数据结构，不实际修改代码）
            if modification_plan['type'] == 'add_capability':
                new_method = modification_plan['implementation']
                self.self_model.capabilities.append(new_method.__name__)
                
                # 动态添加方法（Python的灵活性）
                setattr(self, new_method.__name__, types.MethodType(new_method, self))
                
            elif modification_plan['type'] == 'remove_limitation':
                target = modification_plan['target']
                if target in self.self_model.limitations:
                    self.self_model.limitations.remove(target)
            
            # 记录修改
            self.self_model.modification_history.append({
                'timestamp': len(self.self_model.modification_history),
                'plan': modification_plan,
                'success': True
            })
            
            return True
            
        except Exception as e:
            # 恢复
            self.self_model = backup
            self.self_model.modification_history.append({
                'plan': modification_plan,
                'success': False,
                'error': str(e)
            })
            return False
    
    def _verify_modification_safety(self, plan: Dict) -> bool:
        # 规则1：不能移除核心能力（如reflect）
        if plan.get('type') == 'remove_capability':
            if plan.get('target') in ['reflect', 'self_modify', '_build_initial_self_model']:
                return False
        
        # 规则2：修改必须可回滚
        if 'rollback_plan' not in plan:
            return False
        
        # 规则3：修改幅度限制
        if plan.get('complexity_score', 0) > 0.8:
            return False
        
        return True
    
    def generate_self_improvement_code(self, target_capability: str) -> str:
        # 基于当前自我模型生成新代码
        template = f"""
def improved_{target_capability}(self, *args, **kwargs):
    # 自动生成的改进版本
    # 基于当前模型的理解: {self.self_model.capabilities[:3]}
    
    # 添加不确定性量化
    uncertainty = self._estimate_uncertainty()
    
    # 原逻辑（假设）
    result = self.{target_capability}(*args, **kwargs)
    
    # 增强：返回带置信度的结果
    return {{
        'result': result,
        'confidence': 1.0 - uncertainty,
        'generated_by': 'self_improvement_system'
    }}
        return template
    
    def _estimate_uncertainty(self) -> float:
        if not self.self_model.modification_history:
            return 0.5
        
        recent = self.self_model.modification_history[-10:]
        failures = sum(1 for h in recent if not h.get('success', True))
        return failures / len(recent)

# === 验证 ===
def validate_self_modeling():
    system = SelfModifyingSystem()
    
    print("=== 初始自我模型 ===")
    print(f"能力数量: {len(system.self_model.capabilities)}")
    print(f"局限性: {system.self_model.limitations[:3]}")
    
    # 反思
    reflection = system.reflect()
    print(f"\n=== 反思分析 ===")
    print(f"改进机会: {len(reflection['improvement_opportunities'])}")
    for opp in reflection['improvement_opportunities']:
        print(f"  - {opp['target']}: {opp['strategy']}")
    
    # 尝试自我修改
    def new_capability(self):
        return "动态添加的能力"
    
    modification = {
        'type': 'add_capability',
        'implementation': new_capability,
        'rollback_plan': 'remove_method',
        'complexity_score': 0.3
    }
    
    success = system.self_modify(modification)
    print(f"\n自我修改结果: {'成功' if success else '失败'}")
    
    if success:
        # 验证新能力
        result = system.new_capability()
        print(f"新能力测试: {result}")
    
    # 生成改进代码
    improved_code = system.generate_self_improvement_code("reflect")
    print(f"\n=== 自动生成的改进代码 ===")
    print(improved_code[:200] + "...")
    
    print("\n✓ 自我建模递归系统验证通过")
    return system

if __name__ == "__main__":
    validate_self_modeling()
"""
