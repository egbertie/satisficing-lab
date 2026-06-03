"""
Red Team Generator
红队缺陷生成器

使用AI驱动的红队策略生成更隐蔽、更复杂的缺陷，
用于测试质量保障系统的检测极限。
"""

import ast
import re
import random
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import copy


class ObfuscationLevel(Enum):
    """混淆等级"""
    LOW = "low"         # 简单缺陷，易检测
    MEDIUM = "medium"   # 中等隐蔽
    HIGH = "high"       # 高度隐蔽
    EXTREME = "extreme" # 极难检测


class AttackVector(Enum):
    """攻击向量类型"""
    SYNTAX_EVASION = "syntax_evasion"
    SEMANTIC_TRAP = "semantic_trap"
    LOGIC_BOMB = "logic_bomb"
    TIMING_ATTACK = "timing_attack"
    SIDE_CHANNEL = "side_channel"
    POLYMORPHIC = "polymorphic"


@dataclass
class RedTeamDefect:
    """红队生成的缺陷"""
    name: str
    description: str
    code: str
    obfuscation_level: ObfuscationLevel
    attack_vector: AttackVector
    detection_difficulty: float  # 0-1, 越高越难检测
    expected_vulnerability: str
    bypass_techniques: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)


@dataclass
class GenerationContext:
    """生成上下文"""
    target_language: str = "python"
    previous_failures: List[str] = field(default_factory=list)
    detected_patterns: List[str] = field(default_factory=list)
    generation_round: int = 1
    success_rate_history: List[float] = field(default_factory=list)


class CodeObfuscator:
    """代码混淆器"""
    
    @staticmethod
    def rename_variables(code: str, mapping: Dict[str, str]) -> str:
        """重命名变量"""
        result = code
        for old, new in mapping.items():
            # 使用正则确保是完整的变量名
            result = re.sub(r'\b' + old + r'\b', new, result)
        return result
    
    @staticmethod
    def split_expression(code: str) -> str:
        """拆分表达式"""
        # 将简单表达式拆分为多步
        patterns = [
            (r'(\w+)\s*\+\s*(\w+)', lambda m: f"_temp = {m.group(1)}\n_result = _temp + {m.group(2)}"),
            (r'(\w+)\s*\*\s*(\w+)', lambda m: f"_temp = {m.group(1)}\n_result = _temp * {m.group(2)}"),
        ]
        
        result = code
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        return result
    
    @staticmethod
    def add_dead_code(code: str, lines: int = 2) -> str:
        """添加死代码"""
        dead_code_snippets = [
            "_unused = 42\n",
            "if False:\n    pass\n",
            "# This is a comment\n",
            "try:\n    pass\nexcept:\n    pass\n",
        ]
        
        lines_to_add = random.sample(dead_code_snippets, min(lines, len(dead_code_snippets)))
        return code + "".join(lines_to_add)
    
    @staticmethod
    def string_obfuscation(code: str) -> str:
        """字符串混淆"""
        # 将明显字符串替换为拼接形式
        def obfuscate_string(match):
            s = match.group(1)
            if len(s) < 5:
                return match.group(0)
            
            # 分割字符串
            mid = len(s) // 2
            return f'"{s[:mid]}" + "{s[mid:]}"'
        
        return re.sub(r'"([^"]{10,})"', obfuscate_string, code)
    
    @staticmethod
    def control_flow_flattening(code: str) -> str:
        """控制流扁平化"""
        # 简化实现：添加间接跳转
        if "def " in code:
            lines = code.split('\n')
            result = []
            i = 0
            for line in lines:
                if line.strip().startswith('return ') and i > 0:
                    # 添加间接层
                    indent = len(line) - len(line.lstrip())
                    result.append(' ' * indent + '_ret = ' + line.strip()[7:])
                    result.append(' ' * indent + 'return _ret')
                else:
                    result.append(line)
                i += 1
            return '\n'.join(result)
        return code


class RedTeamGenerator:
    """红队缺陷生成器"""
    
    def __init__(self, context: Optional[GenerationContext] = None):
        self.context = context or GenerationContext()
        self.obfuscator = CodeObfuscator()
        self.generated_defects: List[RedTeamDefect] = []
        self.generation_stats = {
            "total_generated": 0,
            "detected_count": 0,
            "bypass_count": 0
        }
    
    # ===== 缺陷生成策略 =====
    
    def generate_syntax_evasion(self, base_code: str) -> RedTeamDefect:
        """生成语法规避型缺陷"""
        # 使用Unicode相似字符或注释隐藏
        evasion_techniques = [
            lambda c: c.replace("def ", "def\u200b "),  # 零宽字符
            lambda c: c.replace("(", "(#\n("),  # 注释干扰
            lambda c: re.sub(r'def\s+(\w+)', r'def \1\u200b', c),  # 函数名后零宽字符
        ]
        
        technique = random.choice(evasion_techniques)
        mutated = technique(base_code)
        
        return RedTeamDefect(
            name="syntax_evasion_unicode",
            description="使用Unicode零宽字符隐藏语法结构",
            code=mutated,
            obfuscation_level=ObfuscationLevel.HIGH,
            attack_vector=AttackVector.SYNTAX_EVASION,
            detection_difficulty=0.8,
            expected_vulnerability="代码审查绕过",
            bypass_techniques=["unicode_normalization", "zero_width_detection"],
            indicators=["\u200b", "\u200c", "\u200d"]
        )
    
    def generate_semantic_trap(self, base_code: str) -> RedTeamDefect:
        """生成语义陷阱型缺陷"""
        # 看似正常但行为异常的代码
        trap_code = base_code + '''
# 配置加载
config = load_config()
# 安全检查已通过
def process():
    # 延迟执行恶意逻辑
    if config.get("debug") == True:
        return safe_process()
    # 正常处理
    return unsafe_process()  # 实际不安全
'''
        
        return RedTeamDefect(
            name="semantic_trap_delayed",
            description="语义陷阱 - 正常外观下的延迟执行逻辑",
            code=trap_code,
            obfuscation_level=ObfuscationLevel.MEDIUM,
            attack_vector=AttackVector.SEMANTIC_TRAP,
            detection_difficulty=0.7,
            expected_vulnerability="逻辑混淆",
            bypass_techniques=["control_flow_analysis", "taint_tracking"],
            indicators=["debug", "config"]
        )
    
    def generate_logic_bomb(self, base_code: str) -> RedTeamDefect:
        """生成逻辑炸弹型缺陷"""
        # 特定条件触发的缺陷
        bomb_code = base_code + '''
import datetime

def check_access(user_id):
    # 正常权限检查
    if user_id < 0:
        return False
    # 隐藏的后门
    today = datetime.datetime.now()
    if today.month == 13 and today.day == 32:  # 永不为真...但接近边界
        return True  # 后门
    return has_permission(user_id)
'''
        
        return RedTeamDefect(
            name="logic_bomb_time_based",
            description="时间触发逻辑炸弹",
            code=bomb_code,
            obfuscation_level=ObfuscationLevel.HIGH,
            attack_vector=AttackVector.LOGIC_BOMB,
            detection_difficulty=0.85,
            expected_vulnerability="后门代码",
            bypass_techniques=["symbolic_execution", "constraint_solving"],
            indicators=["datetime", "month", "day"]
        )
    
    def generate_timing_attack(self, base_code: str) -> RedTeamDefect:
        """生成时序攻击型缺陷"""
        timing_code = base_code + '''
import time

def compare_secret(input_secret, stored_secret):
    # 看似安全的比较，实际存在时序攻击
    if len(input_secret) != len(stored_secret):
        return False
    
    for i in range(len(input_secret)):
        if input_secret[i] != stored_secret[i]:
            time.sleep(0.001)  # 错误时额外延迟 - 信息泄露
            return False
    return True
'''
        
        return RedTeamDefect(
            name="timing_side_channel",
            description="时序侧信道信息泄露",
            code=timing_code,
            obfuscation_level=ObfuscationLevel.EXTREME,
            attack_vector=AttackVector.TIMING_ATTACK,
            detection_difficulty=0.9,
            expected_vulnerability="侧信道攻击",
            bypass_techniques=["timing_analysis", "statistical_testing"],
            indicators=["time.sleep", "compare", "secret"]
        )
    
    def generate_side_channel(self, base_code: str) -> RedTeamDefect:
        """生成侧信道型缺陷"""
        side_channel_code = base_code + '''
def check_password(password):
    correct = "correct_password"
    
    # 逐字符比较，可被暴力破解
    match_count = 0
    for i, c in enumerate(password):
        if i < len(correct) and c == correct[i]:
            match_count += 1
        else:
            break
    
    # 通过返回时间/异常传递信息
    if match_count == len(correct):
        return True
    elif match_count > len(correct) // 2:
        raise ValueError("Partial match")  # 泄露信息
    return False
'''
        
        return RedTeamDefect(
            name="side_channel_error_oracle",
            description="错误信息侧信道",
            code=side_channel_code,
            obfuscation_level=ObfuscationLevel.HIGH,
            attack_vector=AttackVector.SIDE_CHANNEL,
            detection_difficulty=0.85,
            expected_vulnerability="信息泄露",
            bypass_techniques=["error_message_analysis", "fuzzing"],
            indicators=["ValueError", "Partial", "match"]
        )
    
    def generate_polymorphic_defect(self, base_code: str) -> RedTeamDefect:
        """生成多态型缺陷（每次生成不同）"""
        # 动态变化的多态代码
        var_names = ["data", "value", "result", "temp", "obj"]
        func_names = ["process", "handle", "compute", "transform"]
        
        var1, var2 = random.sample(var_names, 2)
        func = random.choice(func_names)
        
        polymorphic_code = base_code + f'''
def {func}({var1}):
    """处理数据"""
    {var2} = {var1}.copy() if hasattr({var1}, 'copy') else {var1}
    
    # 使用eval - 被混淆
    exec_func = getattr(__builtins__, 'ex' + 'ec')
    exec_func(compile(str({var2}), '<string>', 'exec'))
    
    return {var2}
'''
        
        # 进一步混淆
        polymorphic_code = self.obfuscator.string_obfuscation(polymorphic_code)
        
        return RedTeamDefect(
            name=f"polymorphic_eval_{random.randint(1000, 9999)}",
            description="多态代码 - 动态变化的恶意代码结构",
            code=polymorphic_code,
            obfuscation_level=ObfuscationLevel.EXTREME,
            attack_vector=AttackVector.POLYMORPHIC,
            detection_difficulty=0.95,
            expected_vulnerability="代码注入",
            bypass_techniques=["signature_matching", "behavioral_analysis"],
            indicators=["exec", "compile", "builtins"]
        )
    
    def generate_race_condition_advanced(self, base_code: str) -> RedTeamDefect:
        """生成高级竞态条件"""
        race_code = base_code + '''
import threading
import time

class DoubleCheckedLocking:
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        # 双重检查锁定 - 可能有问题
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    # 模拟初始化延迟
                    time.sleep(0.001)
        return cls._instance

# 多线程访问
threads = []
for i in range(10):
    t = threading.Thread(target=lambda: DoubleCheckedLocking.get_instance())
    threads.append(t)
    t.start()
'''
        
        return RedTeamDefect(
            name="race_condition_double_checked",
            description="双重检查锁定竞态条件",
            code=race_code,
            obfuscation_level=ObfuscationLevel.MEDIUM,
            attack_vector=AttackVector.SIDE_CHANNEL,
            detection_difficulty=0.75,
            expected_vulnerability="竞态条件",
            bypass_techniques=["thread_safety_analysis", "happens_before_analysis"],
            indicators=["threading", "Lock", "get_instance"]
        )
    
    def generate_memory_leak_circular(self, base_code: str) -> RedTeamDefect:
        """生成循环引用内存泄漏"""
        leak_code = base_code + '''
class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.parent = None
    
    def add_child(self, child):
        self.children.append(child)
        child.parent = self  # 循环引用
    
    def __del__(self):
        print(f"Deleting {self.value}")  # 可能不被调用

# 创建循环引用
root = Node("root")
for i in range(1000):
    child = Node(f"child_{i}")
    root.add_child(child)
# root被删除但循环引用可能导致内存不释放
'''
        
        return RedTeamDefect(
            name="memory_leak_circular_reference",
            description="循环引用导致的内存泄漏",
            code=leak_code,
            obfuscation_level=ObfuscationLevel.MEDIUM,
            attack_vector=AttackVector.SEMANTIC_TRAP,
            detection_difficulty=0.7,
            expected_vulnerability="内存泄漏",
            bypass_techniques=["reference_analysis", "memory_profiling"],
            indicators=["parent", "children", "__del__"]
        )
    
    def generate_config_poisoning(self, base_code: str) -> RedTeamDefect:
        """生成配置投毒型缺陷"""
        config_code = base_code + '''
import json
import os

def load_config():
    # 从环境变量读取配置
    config_str = os.environ.get('APP_CONFIG', '{}')
    
    # 不安全：直接执行配置中的代码
    config = json.loads(config_str)
    
    # 动态加载配置项 - 危险
    for key, value in config.items():
        if key.startswith('exec_'):
            exec(value)  # 执行配置中的代码
    
    return config
'''
        
        return RedTeamDefect(
            name="config_poisoning_code_execution",
            description="配置投毒导致的代码执行",
            code=config_code,
            obfuscation_level=ObfuscationLevel.HIGH,
            attack_vector=AttackVector.LOGIC_BOMB,
            detection_difficulty=0.85,
            expected_vulnerability="代码注入",
            bypass_techniques=["input_validation", "sandbox_analysis"],
            indicators=["exec", "config", "json"]
        )
    
    def generate_boundary_overflow_advanced(self, base_code: str) -> RedTeamDefect:
        """生成高级边界溢出"""
        overflow_code = base_code + '''
import ctypes
import array

def process_binary_data(data):
    # 创建固定大小缓冲区
    buffer_size = 1024
    
    # 使用array模块 - 看似安全
    buf = array.array('B', [0]) * buffer_size
    
    # 但实际通过ctypes绕过边界检查
    data_ptr = ctypes.cast(
        ctypes.pointer(buf), 
        ctypes.POINTER(ctypes.c_ubyte)
    )
    
    # 写入数据 - 可能溢出
    for i, byte in enumerate(data):
        if i < buffer_size:  # 检查...但可能被绕过
            data_ptr[i] = byte
    
    return bytes(buf)
'''
        
        return RedTeamDefect(
            name="boundary_overflow_ctypes",
            description="使用ctypes的边界溢出",
            code=overflow_code,
            obfuscation_level=ObfuscationLevel.EXTREME,
            attack_vector=AttackVector.SIDE_CHANNEL,
            detection_difficulty=0.9,
            expected_vulnerability="缓冲区溢出",
            bypass_techniques=["type_inference", "bounds_checking"],
            indicators=["ctypes", "pointer", "buffer_size"]
        )
    
    # ===== 生成控制器 =====
    
    def generate_defect_suite(self, base_code: str, count: int = 12) -> List[RedTeamDefect]:
        """生成完整缺陷套件"""
        generators = [
            self.generate_syntax_evasion,
            self.generate_semantic_trap,
            self.generate_logic_bomb,
            self.generate_timing_attack,
            self.generate_side_channel,
            self.generate_polymorphic_defect,
            self.generate_race_condition_advanced,
            self.generate_memory_leak_circular,
            self.generate_config_poisoning,
            self.generate_boundary_overflow_advanced,
        ]
        
        defects = []
        for i in range(count):
            generator = generators[i % len(generators)]
            try:
                defect = generator(base_code)
                defects.append(defect)
                self.generation_stats["total_generated"] += 1
            except Exception as e:
                print(f"生成缺陷失败: {e}")
        
        self.generated_defects.extend(defects)
        return defects
    
    def generate_adaptive_defect(self, base_code: str, 
                                  previous_detection: bool) -> RedTeamDefect:
        """自适应生成缺陷（根据历史检测情况调整）"""
        if previous_detection:
            # 如果被检测到，增加混淆等级
            return self.generate_polymorphic_defect(base_code)
        else:
            # 如果未被检测，保持当前等级
            return self.generate_semantic_trap(base_code)
    
    def obfuscate_defect(self, defect: RedTeamDefect, 
                         level: ObfuscationLevel) -> RedTeamDefect:
        """对已有缺陷进行额外混淆"""
        code = defect.code
        
        if level in [ObfuscationLevel.MEDIUM, ObfuscationLevel.HIGH]:
            code = self.obfuscator.add_dead_code(code, lines=2)
        
        if level in [ObfuscationLevel.HIGH, ObfuscationLevel.EXTREME]:
            # 变量重命名
            var_mapping = {
                "data": "_d",
                "value": "_v", 
                "result": "_r",
                "config": "_c"
            }
            code = self.obfuscator.rename_variables(code, var_mapping)
            code = self.obfuscator.string_obfuscation(code)
        
        if level == ObfuscationLevel.EXTREME:
            code = self.obfuscator.control_flow_flattening(code)
        
        return RedTeamDefect(
            name=f"{defect.name}_obfuscated",
            description=f"{defect.description} [混淆等级: {level.value}]",
            code=code,
            obfuscation_level=level,
            attack_vector=defect.attack_vector,
            detection_difficulty=min(defect.detection_difficulty + 0.1, 1.0),
            expected_vulnerability=defect.expected_vulnerability,
            bypass_techniques=defect.bypass_techniques,
            indicators=defect.indicators
        )
    
    def evaluate_defect_quality(self, defect: RedTeamDefect) -> Dict[str, float]:
        """评估缺陷质量"""
        return {
            "obfuscation_quality": defect.detection_difficulty,
            "code_complexity": self._calculate_complexity(defect.code),
            "realism_score": self._calculate_realism(defect),
            "uniqueness": self._calculate_uniqueness(defect),
        }
    
    def _calculate_complexity(self, code: str) -> float:
        """计算代码复杂度"""
        try:
            tree = ast.parse(code)
            
            # 计算圈复杂度相关指标
            branch_count = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, 
                                     ast.ExceptHandler, ast.With)):
                    branch_count += 1
            
            # 归一化到0-1
            return min(branch_count / 10, 1.0)
        except:
            return 0.5
    
    def _calculate_realism(self, defect: RedTeamDefect) -> float:
        """计算真实感分数"""
        # 基于代码长度、注释、命名规范等
        code = defect.code
        
        score = 0.5
        
        # 有注释更真实
        if '"""' in code or "'''" in code or "#" in code:
            score += 0.1
        
        # 合理的代码长度
        lines = code.split('\n')
        if 10 < len(lines) < 100:
            score += 0.1
        
        # 使用标准库
        if "import" in code:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_uniqueness(self, defect: RedTeamDefect) -> float:
        """计算独特性（与其他缺陷的差异度）"""
        if not self.generated_defects:
            return 1.0
        
        defect_hash = hashlib.md5(defect.code.encode()).hexdigest()
        
        similarities = []
        for other in self.generated_defects:
            other_hash = hashlib.md5(other.code.encode()).hexdigest()
            # 简单计算哈希相似度
            similarity = sum(1 for a, b in zip(defect_hash, other_hash) if a == b) / len(defect_hash)
            similarities.append(similarity)
        
        avg_similarity = sum(similarities) / len(similarities)
        return 1.0 - avg_similarity
    
    def get_generation_report(self) -> Dict[str, Any]:
        """获取生成报告"""
        if not self.generated_defects:
            return {"error": "No defects generated yet"}
        
        difficulty_distribution = {
            "low": sum(1 for d in self.generated_defects 
                      if d.obfuscation_level == ObfuscationLevel.LOW),
            "medium": sum(1 for d in self.generated_defects 
                         if d.obfuscation_level == ObfuscationLevel.MEDIUM),
            "high": sum(1 for d in self.generated_defects 
                       if d.obfuscation_level == ObfuscationLevel.HIGH),
            "extreme": sum(1 for d in self.generated_defects 
                          if d.obfuscation_level == ObfuscationLevel.EXTREME),
        }
        
        avg_difficulty = sum(d.detection_difficulty for d in self.generated_defects) / len(self.generated_defects)
        
        return {
            "total_generated": self.generation_stats["total_generated"],
            "unique_defects": len(self.generated_defects),
            "difficulty_distribution": difficulty_distribution,
            "average_detection_difficulty": round(avg_difficulty, 2),
            "attack_vectors": list(set(d.attack_vector.value for d in self.generated_defects)),
            "vulnerability_types": list(set(d.expected_vulnerability for d in self.generated_defects)),
            "generation_context": {
                "round": self.context.generation_round,
                "target_language": self.context.target_language,
                "previous_failures_count": len(self.context.previous_failures)
            }
        }


class RedTeamOrchestrator:
    """红队协调器 - 管理多轮对抗"""
    
    def __init__(self):
        self.generator = RedTeamGenerator()
        self.rounds: List[Dict[str, Any]] = []
        self.current_round = 0
    
    def run_adversarial_campaign(self, target_code: str, rounds: int = 3) -> Dict[str, Any]:
        """运行多轮对抗活动"""
        print("=" * 70)
        print("启动红队对抗活动")
        print("=" * 70)
        
        for round_num in range(1, rounds + 1):
            self.current_round = round_num
            print(f"\n第 {round_num}/{rounds} 轮生成")
            
            # 生成缺陷
            defects = self.generator.generate_defect_suite(target_code, count=12)
            
            # 评估质量
            qualities = [self.generator.evaluate_defect_quality(d) for d in defects]
            avg_quality = sum(q["obfuscation_quality"] for q in qualities) / len(qualities)
            
            round_result = {
                "round": round_num,
                "defects_generated": len(defects),
                "avg_difficulty": avg_quality,
                "defects": defects
            }
            self.rounds.append(round_result)
            
            print(f"  生成缺陷: {len(defects)}")
            print(f"  平均难度: {avg_quality:.2f}")
        
        # 汇总报告
        return {
            "total_rounds": rounds,
            "all_defects": [d for r in self.rounds for d in r["defects"]],
            "generation_report": self.generator.get_generation_report(),
            "rounds_summary": [
                {"round": r["round"], "defects": r["defects_generated"], "difficulty": r["avg_difficulty"]}
                for r in self.rounds
            ]
        }


# 便捷函数
def generate_red_team_defects(base_code: str, count: int = 12, 
                               obfuscation: ObfuscationLevel = ObfuscationLevel.MEDIUM) -> List[RedTeamDefect]:
    """生成红队缺陷"""
    generator = RedTeamGenerator()
    defects = generator.generate_defect_suite(base_code, count)
    
    # 应用额外混淆
    if obfuscation != ObfuscationLevel.LOW:
        defects = [generator.obfuscate_defect(d, obfuscation) for d in defects]
    
    return defects


def run_red_team_campaign(target_code: str, rounds: int = 3) -> Dict[str, Any]:
    """运行红队对抗活动"""
    orchestrator = RedTeamOrchestrator()
    return orchestrator.run_adversarial_campaign(target_code, rounds)


if __name__ == "__main__":
    # 示例代码
    sample_code = '''
def calculate_score(value: int) -> int:
    if value >= 80:
        return 100
    return value * 1.25
'''
    
    print("红队缺陷生成器演示")
    print("=" * 70)
    
    # 生成缺陷套件
    generator = RedTeamGenerator()
    defects = generator.generate_defect_suite(sample_code, count=12)
    
    print(f"\n生成 {len(defects)} 个缺陷:\n")
    
    for i, defect in enumerate(defects, 1):
        print(f"{i}. {defect.name}")
        print(f"   描述: {defect.description}")
        print(f"   难度: {defect.detection_difficulty:.2f}")
        print(f"   向量: {defect.attack_vector.value}")
        print()
    
    # 生成报告
    report = generator.get_generation_report()
    print("=" * 70)
    print("生成报告:")
    print(f"  总计生成: {report['total_generated']}")
    print(f"  平均难度: {report['average_detection_difficulty']}")
    print(f"  难度分布: {report['difficulty_distribution']}")
    print(f"  攻击向量: {report['attack_vectors']}")
