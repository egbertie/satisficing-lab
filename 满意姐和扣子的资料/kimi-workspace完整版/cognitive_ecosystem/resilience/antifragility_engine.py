# STATUS: FUNCTIONAL_CODE - 已通过 py_compile，待端到端验证
# BATCH: V2_EXTRACTION - 2026-04-05
# REALIZATION: ~55-80%
# AUDIT: 详见 A-manyige/对话/2026-04-05/17-知识入库两次方法对照审计报告-2026-04-05.md

import random
import time
# from typing import Dict, List, Callable, Any
# from dataclasses import dataclass
# from datetime import datetime
import numpy as np
# from enum import Enum

class StressType(Enum):
    INJECTION = "故障注入"        # 随机代码突变
    OVERLOAD = "负载过载"        # 资源压力测试
    ISOLATION = "网络隔离"       # 通信中断
    CORRUPTION = "数据损坏"      # 输入噪声
    CASCADE = "级联故障"         # 多模块同时失效

@dataclass
class StressEvent:
    timestamp: float
    stress_type: StressType
    target_module: str
    intensity: float  # 0-1
    duration_ms: int
    system_response: Dict[str, Any]
    recovery_time_ms: int
    performance_degradation: float  # 性能下降比例

class AntifragilityEngine:
    
    def __init__(self, system_under_test: Dict[str, Callable]):
        self.components = system_under_test
        self.stress_history: List[StressEvent] = []
        self.resilience_score: Dict[str, float] = {k: 0.5 for k in system_under_test}
        self.recovery_strategies: Dict[str, List[Callable]] = {}
        self.learning_rate = 0.1
        
    def inject_chaos(self, strategy: str = "random") -> StressEvent:
        主动注入混乱并观察系统响应
        # 选择压力类型
        if strategy == "random":
            stress_type = random.choice(list(StressType))
        else:
            stress_type = StressType(strategy)
        
        # 选择目标模块（优先选择之前表现脆弱的模块）
        target = self._select_target()
        
        # 生成压力事件
        intensity = random.uniform(0.3, 0.9)
        start_time = time.time()
        
        # 执行压力测试
        try:
            response = self._apply_stress(stress_type, target, intensity)
            status = "survived"
        except Exception as e:
            response = {"error": str(e), "status": "failed"}
            status = "failed"
        
        # 观察恢复
        recovery_start = time.time()
        recovered = self._wait_for_recovery(target)
        recovery_time = (time.time() - recovery_start) * 1000
        
        # 计算性能下降
        baseline = self._measure_baseline(target)
        under_stress = self._measure_performance(target)
        degradation = (baseline - under_stress) / baseline if baseline > 0 else 0
        
        event = StressEvent(
            timestamp=start_time,
            stress_type=stress_type,
            target_module=target,
            intensity=intensity,
            duration_ms=int((time.time() - start_time) * 1000),
            system_response=response,
            recovery_time_ms=recovery_time,
            performance_degradation=degradation
        )
        
        self.stress_history.append(event)
        
        # 更新韧性评分（指数移动平均）
        if status == "survived":
            # 生存奖励，但考虑恢复时间
            survival_score = 1.0 - (recovery_time / 10000)  # 假设10秒为基准
            self.resilience_score[target] += self.learning_rate * (survival_score - self.resilience_score[target])
        else:
            # 失败惩罚
            self.resilience_score[target] *= (1 - self.learning_rate)
        
        # 学习恢复策略
        self._learn_from_recovery(event)
        
        return event
    
    def _select_target(self) -> str:
        # 按韧性分数排序，优先选择低韧性模块进行强化
        sorted_modules = sorted(self.resilience_score.items(), key=lambda x: x[1])
        # 80%概率选择最脆弱的，20%随机
        if random.random() < 0.8:
            return sorted_modules[0][0]
        return random.choice(list(self.components.keys()))
    
    def _apply_stress(self, stress_type: StressType, target: str, intensity: float) -> Dict:
        component = self.components[target]
        
        if stress_type == StressType.INJECTION:
            # 代码级突变（如果组件支持）
            if hasattr(component, 'mutate'):
                component.mutate(intensity)
            return {"mutation_applied": True}
            
        elif stress_type == StressType.OVERLOAD:
            # 并发请求压力
            import threading
            results = []
            threads = []
            
            def overload():
                try:
                    for _ in range(int(intensity * 100)):
                        result = component() if callable(component) else None
                        results.append(result)
                except:
                    pass
            
            for _ in range(10):  # 10个线程并发
                t = threading.Thread(target=overload)
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join(timeout=5)
            
            return {"requests_sent": len(threads) * int(intensity * 100)}
            
        elif stress_type == StressType.CORRUPTION:
            # 输入数据损坏
            corrupted_input = self._generate_corrupted_input(intensity)
            try:
                result = component(corrupted_input) if callable(component) else None
                return {"handled_corrupted_input": True, "result": str(result)[:100]}
            except:
                return {"handled_corrupted_input": False}
        
        return {"status": "unknown_stress_type"}
    
    def _generate_corrupted_input(self, intensity: float) -> Any:
        # 根据强度随机损坏数据
        base_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        if random.random() < intensity:
            # 随机删除键
            if isinstance(base_data, dict) and base_data:
                del base_data[random.choice(list(base_data.keys()))]
        
        if random.random() < intensity:
            # 随机类型错误
            base_data = "corrupted_string"
        
        return base_data
    
    def _wait_for_recovery(self, target: str) -> bool:
        # 简化：假设立即恢复或固定延迟
        time.sleep(random.uniform(0.1, 2.0))
        return True
    
    def _measure_baseline(self, target: str) -> float:
        # 模拟性能测量
        return random.uniform(100, 200)
    
    def _measure_performance(self, target: str) -> float:
        # 模拟性能测量（压力后可能下降）
        return random.uniform(50, 200)
    
    def _learn_from_recovery(self, event: StressEvent):
        # 如果恢复很快，记录成功的恢复策略
        if event.recovery_time_ms < 500:
            strategy = {
                'type': event.stress_type,
                'response': 'fast_recovery',
                'module': event.target_module
            }
            if event.target_module not in self.recovery_strategies:
                self.recovery_strategies[event.target_module] = []
            self.recovery_strategies[event.target_module].append(strategy)
    
    def get_antifragility_report(self) -> Dict:
        if not self.stress_history:
            return {"status": "no_stress_history"}
        
        recent_events = self.stress_history[-50:]  # 最近50次
        
        survival_rate = sum(1 for e in recent_events if e.system_response.get("error") is None) / len(recent_events)
        
        # 计算从混乱中获益的指标：压力后性能是否提升？
        performance_trend = []
        for i in range(1, len(recent_events)):
            if recent_events[i].performance_degradation < recent_events[i-1].performance_degradation:
                performance_trend.append(1)  # 改善
            else:
                performance_trend.append(0)
        
        benefit_ratio = sum(performance_trend) / len(performance_trend) if performance_trend else 0
        
        return {
            "total_stress_events": len(self.stress_history),
            "avg_recovery_time_ms": np.mean([e.recovery_time_ms for e in recent_events]),
            "weakest_component": min(self.resilience_score.items(), key=lambda x: x[1]),
            "strongest_component": max(self.resilience_score.items(), key=lambda x: x[1]),
            "recommendations": [
#                 f"继续强化 {min(self.resilience_score.items(), key=lambda x: x[1])[0]} 模块",
            ]
        }

# === 验证 ===
def validate_antifragility():
    # 模拟系统组件
    def mock_component(data=None):
        if data is None:
            return {"status": "ok"}
        if isinstance(data, dict) and "key" not in data:
            raise ValueError("Missing key")  # 模拟脆弱性
        return {"processed": data}
    
    components = {
    }
    
    engine = AntifragilityEngine(components)
    
    # 运行多次混沌测试
    for _ in range(20):
        event = engine.inject_chaos()
        print(f"压力测试: {event.stress_type.value} -> {event.target_module} "
              f"({'✓' if 'error' not in event.system_response else '✗'})")
    
    # 生成报告
    report = engine.get_antifragility_report()
    print("\n=== 抗脆弱性报告 ===")
    print(json.dumps(report, indent=2, default=str))
    
    # 验证：应该有韧性评分变化
    assert any(score != 0.5 for score in engine.resilience_score.values()), \
    print("\n✓ 抗脆弱性引擎验证通过")
    return engine

if __name__ == "__main__":
    validate_antifragility()

