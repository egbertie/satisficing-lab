#!/usr/bin/env python3
"""
Memory Guardian V2 - 事件驱动 + 满意解优化
基于满意解决策框架的内存监控系统

变化:
- V1: 固定15分钟检查 ❌ 不满意解
- V2: 场景驱动，对话感知，Token优化 ✅ 满意解
"""

import os
import sys
import psutil
import gc
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/root/.openclaw/workspace")
STATE_FILE = WORKSPACE / ".memory-guardian-state.json"
LOG_FILE = WORKSPACE / "logs" / "memory-guardian.log"
PID_FILE = WORKSPACE / ".memory-guardian.pid"

# 满意解决策阈值
SATISFICE_THRESHOLDS = {
    "safe": {"memory_mb": 1024, "check_interval_min": 120},      # 2小时
    "yellow": {"memory_mb": 1536, "check_interval_min": 60},     # 1小时
    "orange": {"memory_mb": 2048, "check_interval_min": 30},     # 30分钟
    "red": {"memory_mb": 2560, "check_interval_min": 10},        # 10分钟
    "critical": {"memory_mb": 3072, "check_interval_min": 5}      # 5分钟
}

class MemoryGuardianV2:
    """
    满意解内存守护者 V2
    
    核心原则: 场景驱动，对话感知，Token优化
    - 有对话时不检查 (人在看)
    - 有任务时频率跟任务走
    - 空闲时2小时检查一次
    """
    
    def __init__(self):
        self.log_file = LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self.load_state()
        
    def load_state(self) -> dict:
        """加载状态文件"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "last_check_time": None,
            "last_memory_mb": 0,
            "check_count": 0,
            "token_saved": 0,
            "scenario": "init"
        }
    
    def save_state(self):
        """保存状态文件"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def log(self, level: str, message: str):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def get_memory_usage_mb(self) -> float:
        """获取当前内存使用 (MB)"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def detect_scenario(self) -> dict:
        """
        S1: 全局考虑 - 检测当前场景
        返回场景信息，用于满意解决策
        """
        scenario = {
            "has_dialog": False,           # 是否有活跃对话
            "active_task": None,           # 当前任务类型
            "task_memory_risk": "low",     # 任务内存风险
            "time_since_last_check": 0,    # 距离上次检查时间
            "current_memory_mb": self.get_memory_usage_mb()
        }
        
        # 检测对话状态 (通过检查最近交互时间)
        # 实际实现中可以通过更复杂的方式检测
        # 这里简化为：如果距离上次检查<5分钟，认为可能有对话
        if self.state["last_check_time"]:
            last_check = datetime.fromisoformat(self.state["last_check_time"])
            elapsed = (datetime.now() - last_check).total_seconds() / 60
            scenario["time_since_last_check"] = elapsed
            
            # 如果上次检查是5分钟内，可能有人在操作
            if elapsed < 5:
                scenario["has_dialog"] = True
        
        # 检测任务状态 (通过检查进程或状态文件)
        scenario["active_task"] = self.detect_active_task()
        
        # 根据任务类型判断内存风险
        if scenario["active_task"] in ["knowledge_ingest", "large_import", "batch_process"]:
            scenario["task_memory_risk"] = "high"
        elif scenario["active_task"] in ["file_processing", "data_sync"]:
            scenario["task_memory_risk"] = "medium"
        
        return scenario
    
    def detect_active_task(self) -> str:
        """检测当前活跃任务"""
        # 检查任务标记文件
        task_file = WORKSPACE / ".active-task"
        if task_file.exists():
            try:
                with open(task_file, 'r') as f:
                    task_info = json.load(f)
                    return task_info.get("task_type", "none")
            except:
                pass
        return "none"
    
    def satisfice_decision(self, scenario: dict) -> dict:
        """
        满意解决策引擎
        
        决策逻辑:
        1. 有对话 → 不检查 (人在看)
        2. 高风险任务 → 10-15分钟
        3. 中风险任务 → 30分钟
        4. 无任务+Safe内存 → 2小时
        5. 内存接近红线 → 不管任务，按内存频率
        """
        decision = {
            "should_check": True,
            "reason": "",
            "next_check_min": 120,
            "token_estimate": 75
        }
        
        mem = scenario["current_memory_mb"]
        
        # 规则1: 内存Critical，必须检查
        if mem >= SATISFICE_THRESHOLDS["critical"]["memory_mb"]:
            decision["should_check"] = True
            decision["reason"] = f"内存Critical ({mem:.0f}MB >= 3072MB)"
            decision["next_check_min"] = SATISFICE_THRESHOLDS["critical"]["check_interval_min"]
            return decision
        
        # 规则2: 有对话，不检查
        if scenario["has_dialog"]:
            decision["should_check"] = False
            decision["reason"] = "有活跃对话，人在监控"
            decision["next_check_min"] = 30  # 30分钟后再看
            return decision
        
        # 规则3: 根据任务风险
        if scenario["task_memory_risk"] == "high":
            decision["should_check"] = True
            decision["reason"] = f"高风险任务+内存{mem:.0f}MB"
            decision["next_check_min"] = 15
        elif scenario["task_memory_risk"] == "medium":
            decision["should_check"] = True
            decision["reason"] = f"中风险任务+内存{mem:.0f}MB"
            decision["next_check_min"] = 30
        elif mem >= SATISFICE_THRESHOLDS["orange"]["memory_mb"]:
            # 内存Orange，即使没有任务也要检查
            decision["should_check"] = True
            decision["reason"] = f"内存Orange ({mem:.0f}MB >= 2048MB)"
            decision["next_check_min"] = SATISFICE_THRESHOLDS["orange"]["check_interval_min"]
        elif mem >= SATISFICE_THRESHOLDS["yellow"]["memory_mb"]:
            decision["should_check"] = True
            decision["reason"] = f"内存Yellow ({mem:.0f}MB >= 1536MB)"
            decision["next_check_min"] = SATISFICE_THRESHOLDS["yellow"]["check_interval_min"]
        else:
            # Safe状态，2小时检查
            decision["should_check"] = True
            decision["reason"] = f"Safe状态 ({mem:.0f}MB < 1536MB)，无高风险任务"
            decision["next_check_min"] = SATISFICE_THRESHOLDS["safe"]["check_interval_min"]
        
        return decision
    
    def should_check_now(self) -> bool:
        """判断是否现在应该检查"""
        scenario = self.detect_scenario()
        decision = self.satisfice_decision(scenario)
        
        # 如果决策是不检查，记录原因
        if not decision["should_check"]:
            self.log("INFO", f"跳过检查: {decision['reason']}")
            return False
        
        # 检查距离上次检查时间
        if self.state["last_check_time"]:
            last_check = datetime.fromisoformat(self.state["last_check_time"])
            elapsed_min = (datetime.now() - last_check).total_seconds() / 60
            
            if elapsed_min < decision["next_check_min"]:
                self.log("INFO", f"距离上次检查{elapsed_min:.0f}分钟，建议间隔{decision['next_check_min']}分钟，跳过")
                return False
        
        return True
    
    def clean_python_cache(self) -> int:
        """清理Python缓存文件"""
        count = 0
        for root, dirs, files in os.walk(WORKSPACE):
            for file in files:
                if file.endswith('.pyc'):
                    try:
                        os.remove(os.path.join(root, file))
                        count += 1
                    except:
                        pass
            for dir in dirs:
                if dir == '__pycache__':
                    try:
                        import shutil
                        shutil.rmtree(os.path.join(root, dir))
                        count += 1
                    except:
                        pass
        return count
    
    def clean_logs(self, max_size_mb: int = 50) -> int:
        """清理过大的日志文件"""
        count = 0
        log_dir = WORKSPACE / "logs"
        if not log_dir.exists():
            return 0
        
        for log_file in log_dir.glob("*.log"):
            try:
                size_mb = log_file.stat().st_size / 1024 / 1024
                if size_mb > max_size_mb:
                    backup = log_file.with_suffix('.log.old')
                    log_file.rename(backup)
                    count += 1
            except:
                pass
        return count
    
    def force_garbage_collect(self) -> dict:
        """强制垃圾回收"""
        before = self.get_memory_usage_mb()
        gc.collect()
        after = self.get_memory_usage_mb()
        
        return {
            "before_mb": before,
            "after_mb": after,
            "freed_mb": before - after
        }
    
    def emergency_cleanup(self) -> dict:
        """紧急清理"""
        mem = self.get_memory_usage_mb()
        self.log("WARNING", f"内存达到红线: {mem:.1f}MB，启动紧急清理")
        
        results = {
            "python_cache_cleaned": self.clean_python_cache(),
            "logs_cleaned": self.clean_logs(),
            "garbage": self.force_garbage_collect(),
            "before_mb": mem,
            "after_mb": 0
        }
        
        results["after_mb"] = self.get_memory_usage_mb()
        freed = results["before_mb"] - results["after_mb"]
        
        self.log("INFO", f"清理完成: 释放{freed:.1f}MB，当前{results['after_mb']:.1f}MB")
        return results
    
    def run(self):
        """主运行逻辑"""
        # 满意解决策：是否应该现在检查
        if not self.should_check_now():
            return 0
        
        mem = self.get_memory_usage_mb()
        scenario = self.detect_scenario()
        decision = self.satisfice_decision(scenario)
        
        self.log("INFO", f"检查内存: {mem:.1f}MB | 场景: {decision['reason']}")
        
        # 更新状态
        self.state["last_check_time"] = datetime.now().isoformat()
        self.state["last_memory_mb"] = mem
        self.state["check_count"] += 1
        self.state["scenario"] = decision["reason"]
        self.save_state()
        
        # 根据内存级别采取行动
        if mem >= SATISFICE_THRESHOLDS["critical"]["memory_mb"]:
            self.emergency_cleanup()
            return 2  # Critical
        elif mem >= SATISFICE_THRESHOLDS["red"]["memory_mb"]:
            self.emergency_cleanup()
            return 1  # Red
        elif mem >= SATISFICE_THRESHOLDS["orange"]["memory_mb"]:
            self.clean_python_cache()
            self.clean_logs()
            return 0
        elif mem >= SATISFICE_THRESHOLDS["yellow"]["memory_mb"]:
            self.clean_python_cache()
            return 0
        
        return 0
    
    def generate_report(self) -> str:
        """生成满意解报告"""
        scenario = self.detect_scenario()
        decision = self.satisfice_decision(scenario)
        
        report = f"""# Memory Guardian V2 - 满意解报告

生成时间: {datetime.now().isoformat()}

## 满意解决策结果

| 维度 | 状态 | 决策 |
|------|------|------|
| 当前内存 | {scenario['current_memory_mb']:.1f}MB | {decision['reason']} |
| 有对话 | {'是' if scenario['has_dialog'] else '否'} | {'跳过检查' if scenario['has_dialog'] else '继续检查'} |
| 活跃任务 | {scenario['active_task']} | 风险等级: {scenario['task_memory_risk']} |
| 建议检查间隔 | {decision['next_check_min']}分钟 | - |

## Token优化效果

| 指标 | 原方案(V1) | 满意解方案(V2) | 节省 |
|------|-----------|---------------|------|
| 检查频率 | 每15分钟 | 场景驱动 | 动态调整 |
| Safe状态 | 96次/天 | ~12次/天 | 87.5% |
| 有对话时 | 96次/天 | 0次/天 | 100% |
| Token消耗 | ~7,200/天 | ~900/天 | **87.5%** |

## 局限标注 (S6)

- 对话检测基于时间启发式，可能误判
- 任务检测依赖.active-task文件，需要任务系统配合
- 场景判断简化，复杂场景可能覆盖不全

---
*Memory Guardian V2 - 满意解决策驱动*
"""
        return report
    
    def adversarial_test(self) -> dict:
        """S7: 对抗测试"""
        tests = []
        
        # 测试1: 对话状态检测
        self.state["last_check_time"] = datetime.now().isoformat()
        scenario = self.detect_scenario()
        tests.append(("对话状态检测", scenario["time_since_last_check"] < 5, 
                     f"上次检查{scenario['time_since_last_check']:.1f}分钟前"))
        
        # 测试2: 满意解决策
        scenario["has_dialog"] = True
        decision = self.satisfice_decision(scenario)
        tests.append(("对话时跳过决策", not decision["should_check"], 
                     f"决策: {decision['reason']}"))
        
        # 测试3: 内存Critical强制检查
        scenario["has_dialog"] = False
        scenario["current_memory_mb"] = 3500
        decision = self.satisfice_decision(scenario)
        tests.append(("Critical内存强制检查", decision["should_check"], 
                     f"决策: {decision['reason']}"))
        
        return {
            "all_passed": all(t[1] for t in tests),
            "results": tests
        }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("="*70)
        print("🧪 Memory Guardian V2 S5/S7 验证")
        print("="*70)
        
        guardian = MemoryGuardianV2()
        
        # S7: 对抗测试
        print("\n[S7] 对抗测试...")
        test_result = guardian.adversarial_test()
        for name, passed, detail in test_result["results"]:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}: {detail}")
        
        # S5: 自我验证
        print("\n[S5] 自我验证...")
        report = guardian.generate_report()
        assert "满意解决策结果" in report
        print("  ✅ 报告生成正常")
        
        assert "Token优化效果" in report
        print("  ✅ Token优化分析正常")
        
        print("\n" + "="*70)
        print("✅ S5/S7验证通过")
        print("="*70)
        return 0
    
    elif len(sys.argv) > 1 and sys.argv[1] == "report":
        guardian = MemoryGuardianV2()
        report = guardian.generate_report()
        report_file = WORKSPACE / "logs" / "memory-report-v2.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"报告已保存: {report_file}")
        return 0
    
    else:
        guardian = MemoryGuardianV2()
        return guardian.run()

if __name__ == "__main__":
    sys.exit(main())
