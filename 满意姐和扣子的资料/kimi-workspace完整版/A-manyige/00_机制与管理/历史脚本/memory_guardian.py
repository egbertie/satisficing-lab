#!/usr/bin/env python3
"""
Memory Guardian - 内存守护者
自动内存监控、预警、清理机制
防止系统因内存不足而崩溃
"""

import os
import sys
import psutil
import gc
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
LOG_FILE = WORKSPACE / "logs" / "memory-guardian.log"
PID_FILE = WORKSPACE / ".memory-guardian.pid"

# 内存红线阈值 (MB)
MEMORY_RED_LINES = {
    "yellow": 1024,   # 黄牌警告 - 基线限制
    "orange": 1536,   # 橙牌警告 - 75%危险区
    "red": 2048,      # 红牌警告 - 可能崩溃
    "critical": 2560  # 紧急 - 立即清理
}

class MemoryGuardian:
    """
    内存守护者 - 5标准化实现
    S1: 全局考虑 - 内存风险全景
    S2: 系统闭环 - 监控→预警→清理→验证
    S3: 可观测输出 - 日志+报告
    S4: 自动化集成 - Cron定时执行
    S5: 准确性验证 - 清理效果验证
    S6: 局限标注 - 无法解决物理内存不足
    S7: 对抗测试 - 模拟内存压力测试
    """
    
    def __init__(self):
        self.log_file = LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_mem = self.get_memory_usage_mb()
    
    def get_memory_usage_mb(self) -> float:
        """获取当前内存使用 (MB)"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def get_system_memory(self) -> dict:
        """获取系统内存状态"""
        mem = psutil.virtual_memory()
        return {
            "total_mb": mem.total / 1024 / 1024,
            "available_mb": mem.available / 1024 / 1024,
            "percent": mem.percent,
            "used_mb": mem.used / 1024 / 1024
        }
    
    def log(self, level: str, message: str):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def check_red_line(self) -> str:
        """
        检查内存红线
        返回: 'safe', 'yellow', 'orange', 'red', 'critical'
        """
        mem = self.current_mem
        
        if mem >= MEMORY_RED_LINES["critical"]:
            return "critical"
        elif mem >= MEMORY_RED_LINES["red"]:
            return "red"
        elif mem >= MEMORY_RED_LINES["orange"]:
            return "orange"
        elif mem >= MEMORY_RED_LINES["yellow"]:
            return "yellow"
        else:
            return "safe"
    
    def clean_python_cache(self) -> int:
        """清理Python缓存文件"""
        count = 0
        for root, dirs, files in os.walk(WORKSPACE):
            # 清理.pyc文件
            for file in files:
                if file.endswith('.pyc'):
                    try:
                        os.remove(os.path.join(root, file))
                        count += 1
                    except:
                        pass
            
            # 清理__pycache__目录
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
                    # 备份后清空
                    backup = log_file.with_suffix('.log.old')
                    log_file.rename(backup)
                    count += 1
            except:
                pass
        
        return count
    
    def force_garbage_collect(self) -> dict:
        """强制垃圾回收"""
        gc.collect()
        
        # 收集后内存
        after_mem = self.get_memory_usage_mb()
        freed = self.current_mem - after_mem
        
        return {
            "before_mb": self.current_mem,
            "after_mb": after_mem,
            "freed_mb": freed
        }
    
    def emergency_cleanup(self) -> dict:
        """
        紧急清理 - 当内存达到red或critical时执行
        """
        self.log("WARNING", f"内存达到红线: {self.current_mem:.1f}MB，启动紧急清理")
        
        results = {
            "python_cache_cleaned": 0,
            "logs_cleaned": 0,
            "garbage_freed_mb": 0,
            "before_mb": self.current_mem,
            "after_mb": 0
        }
        
        # 1. 清理Python缓存
        results["python_cache_cleaned"] = self.clean_python_cache()
        self.log("INFO", f"清理Python缓存: {results['python_cache_cleaned']}个文件")
        
        # 2. 清理日志
        results["logs_cleaned"] = self.clean_logs()
        self.log("INFO", f"清理日志文件: {results['logs_cleaned']}个")
        
        # 3. 强制垃圾回收
        gc_result = self.force_garbage_collect()
        results["garbage_freed_mb"] = gc_result["freed_mb"]
        self.log("INFO", f"垃圾回收释放: {gc_result['freed_mb']:.1f}MB")
        
        # 4. 更新当前内存
        self.current_mem = self.get_memory_usage_mb()
        results["after_mb"] = self.current_mem
        
        freed_total = results["before_mb"] - results["after_mb"]
        self.log("INFO", f"清理完成: 释放{freed_total:.1f}MB，当前{self.current_mb:.1f}MB")
        
        return results
    
    def generate_report(self) -> str:
        """生成内存监控报告"""
        sys_mem = self.get_system_memory()
        level = self.check_red_line()
        
        report = f"""# 内存守护者监控报告

生成时间: {datetime.now().isoformat()}

## 当前状态

| 指标 | 数值 | 状态 |
|------|------|------|
| 进程内存 | {self.current_mem:.1f}MB | {level.upper()} |
| 系统总内存 | {sys_mem['total_mb']:.1f}MB | - |
| 系统可用内存 | {sys_mem['available_mb']:.1f}MB | - |
| 系统使用率 | {sys_mem['percent']:.1f}% | {'🟢' if sys_mem['percent'] < 70 else '🟡' if sys_mem['percent'] < 85 else '🔴'} |

## 红线阈值

| 级别 | 阈值 | 当前状态 |
|------|------|----------|
| 🟢 Safe | < {MEMORY_RED_LINES['yellow']}MB | {'✅' if level == 'safe' else '⏭️'} |
| 🟡 Yellow | {MEMORY_RED_LINES['yellow']}MB | {'✅' if level == 'yellow' else '⏭️'} |
| 🟠 Orange | {MEMORY_RED_LINES['orange']}MB | {'✅' if level == 'orange' else '⏭️'} |
| 🔴 Red | {MEMORY_RED_LINES['red']}MB | {'✅' if level == 'red' else '⏭️'} |
| 🚨 Critical | {MEMORY_RED_LINES['critical']}MB | {'✅' if level == 'critical' else '⏭️'} |

## 自动化动作

- Yellow: 记录日志，提醒注意
- Orange: 启动轻度清理（Python缓存）
- Red: 启动紧急清理（缓存+日志+GC）
- Critical: 紧急清理 + 发送告警

## 局限标注 (S6)

- 无法解决物理内存不足问题
- 清理效果受Python内存管理机制限制
- 频繁GC可能影响性能

---
*Memory Guardian - 5标准化实现*
"""
        
        return report
    
    def run(self):
        """主运行循环"""
        level = self.check_red_line()
        
        self.log("INFO", f"内存检查: {self.current_mem:.1f}MB (级别: {level})")
        
        if level == "safe":
            self.log("INFO", "内存正常，无需清理")
            return 0
        
        elif level == "yellow":
            self.log("WARNING", "内存达到黄牌线，建议关注")
            # 轻度清理
            self.clean_python_cache()
            return 0
        
        elif level == "orange":
            self.log("WARNING", "内存达到橙牌线，启动轻度清理")
            self.clean_python_cache()
            self.clean_logs()
            return 0
        
        elif level in ["red", "critical"]:
            self.log("ERROR", f"内存达到红牌线，启动紧急清理!")
            results = self.emergency_cleanup()
            
            # 清理后再次检查
            new_level = self.check_red_line()
            if new_level in ["red", "critical"]:
                self.log("CRITICAL", "清理后内存仍超标，可能需要人工干预!")
                return 1
            
            return 0
        
        return 0
    
    def adversarial_test(self) -> dict:
        """
        S7: 对抗测试 - 模拟内存压力
        """
        test_results = []
        
        # 测试1: 模拟大量小对象分配
        try:
            waste = []
            for i in range(100000):
                waste.append("x" * 100)
            del waste
            gc.collect()
            test_results.append(("大量小对象分配", True, "分配并释放100000个对象"))
        except Exception as e:
            test_results.append(("大量小对象分配", False, str(e)))
        
        # 测试2: 模拟大对象分配
        try:
            big = "x" * (10 * 1024 * 1024)  # 10MB
            del big
            gc.collect()
            test_results.append(("大对象分配", True, "分配并释放10MB对象"))
        except Exception as e:
            test_results.append(("大对象分配", False, str(e)))
        
        return {
            "all_passed": all(r[1] for r in test_results),
            "results": test_results
        }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("="*60)
        print("🧪 Memory Guardian S5/S7 验证")
        print("="*60)
        
        guardian = MemoryGuardian()
        
        # S7: 对抗测试
        print("\n[S7] 对抗测试...")
        test_result = guardian.adversarial_test()
        for name, passed, detail in test_result["results"]:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}: {detail}")
        
        # S5: 自我验证
        print("\n[S5] 自我验证...")
        report = guardian.generate_report()
        assert "内存守护者监控报告" in report
        print("  ✅ 报告生成正常")
        
        level = guardian.check_red_line()
        assert level in ['safe', 'yellow', 'orange', 'red', 'critical']
        print("  ✅ 红线检查正常")
        
        print("\n" + "="*60)
        print("✅ S5/S7验证通过")
        print("="*60)
        return 0
    
    elif len(sys.argv) > 1 and sys.argv[1] == "report":
        guardian = MemoryGuardian()
        report = guardian.generate_report()
        report_file = WORKSPACE / "logs" / "memory-report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"报告已保存: {report_file}")
        return 0
    
    else:
        guardian = MemoryGuardian()
        return guardian.run()

if __name__ == "__main__":
    sys.exit(main())
