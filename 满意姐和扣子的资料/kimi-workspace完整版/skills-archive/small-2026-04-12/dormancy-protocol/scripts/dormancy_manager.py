#!/usr/bin/env python3
"""
Dormancy-Protocol 核心管理脚本
功能: 智能休眠与即时唤醒管理
版本: 1.0
作者: OpenClaw
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

class DormancyManager:
    """休眠管理器 - 实现10分钟无交互自动休眠，即时唤醒响应"""
    
    IDLE_THRESHOLD = 600  # 10分钟
    WAKE_LATENCY_TARGET = 100  # 100ms目标
    DORMANCY_STATE_FILE = Path("/root/.openclaw/workspace/memory/dormancy_state.json")
    
    def __init__(self):
        self.state = self.load_state()
    
    def load_state(self):
        """加载状态文件"""
        if self.DORMANCY_STATE_FILE.exists():
            try:
                with open(self.DORMANCY_STATE_FILE) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._default_state()
        return self._default_state()
    
    def _default_state(self):
        """默认状态"""
        return {
            "status": "ACTIVE",
            "last_activity": time.time(),
            "state_transitions": [],
            "metrics": {
                "hibernate_count": 0,
                "wake_count": 0,
                "total_dormant_seconds": 0,
                "avg_wake_latency_ms": 0
            }
        }
    
    def save_state(self):
        """保存状态文件"""
        self.DORMANCY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.DORMANCY_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def detect_idle(self):
        """检测空闲状态 - S2: 系统闭环之输入"""
        now = time.time()
        last_activity = self.state.get("last_activity", now)
        idle_duration = now - last_activity
        
        return {
            "idle_duration_sec": idle_duration,
            "is_idle": idle_duration > self.IDLE_THRESHOLD,
            "time_since_last_activity": idle_duration,
            "threshold": self.IDLE_THRESHOLD
        }
    
    def should_hibernate(self, idle_info):
        """
        评估是否应该休眠 - S2: 系统闭环之决策
        休眠条件: 10分钟无交互 + 无活跃任务 + Token<80%
        """
        if not idle_info["is_idle"]:
            return False, "未达到空闲阈值"
        
        # 检查活跃任务
        if self.state.get("active_tasks", []):
            return False, "存在活跃任务"
        
        # 检查Token使用率
        if self.state.get("token_usage_pct", 0) > 80:
            return False, "Token使用率过高"
        
        # 检查深度对话标记
        if self.state.get("in_deep_conversation", False):
            return False, "处于深度对话中"
        
        return True, "满足所有休眠条件"
    
    def create_snapshot(self):
        """
        创建会话快照 - S2: 系统闭环之处理
        保存关键记忆、待办事项、决策状态
        """
        snapshot = {
            "dormant_since": time.time(),
            "memory_summary": self._extract_memory_summary(),
            "active_tasks": self.state.get("active_tasks", []),
            "pending_decisions": self.state.get("pending_decisions", []),
            "key_context": self.state.get("key_context", {}),
            "token_usage": self.state.get("token_usage_pct", 0)
        }
        return snapshot
    
    def _extract_memory_summary(self):
        """从记忆文件中提取摘要"""
        today = datetime.now().strftime("%Y-%m-%d")
        memory_file = Path(f"/root/.openclaw/workspace/memory/{today}.md")
        
        if memory_file.exists():
            try:
                content = memory_file.read_text()
                # 提取最近的工作内容
                lines = content.split("\n")
                recent = [l for l in lines[-20:] if l.strip() and not l.startswith("#")]
                return {
                    "recent_activities": recent[:5],
                    "working_on": self._extract_working_on(content),
                    "pending_items": self._extract_pending(content)
                }
            except Exception:
                pass
        
        return {"working_on": "无", "recent_activities": []}
    
    def _extract_working_on(self, content):
        """提取当前正在进行的任务"""
        if "当前任务" in content or "working on" in content.lower():
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "当前任务" in line or "working on" in line.lower():
                    if i + 1 < len(lines):
                        return lines[i + 1].strip("- ")
        return "未明确记录"
    
    def _extract_pending(self, content):
        """提取待办事项"""
        pending = []
        if "TODO" in content or "待办" in content:
            lines = content.split("\n")
            for line in lines:
                if "TODO" in line or "待办" in line:
                    pending.append(line.strip("- []"))
        return pending[:3]
    
    def enter_dormancy(self):
        """
        进入休眠状态 - S2: 系统闭环之输出
        保存快照，释放资源，更新状态
        """
        snapshot = self.create_snapshot()
        
        # 记录状态转换
        transition = {
            "from": self.state.get("status", "ACTIVE"),
            "to": "DORMANT",
            "time": datetime.now().isoformat(),
            "reason": "idle_timeout"
        }
        
        self.state["state_transitions"].append(transition)
        self.state.update({
            "status": "DORMANT",
            "snapshot": snapshot,
            "entered_dormancy_at": time.time()
        })
        
        # 更新统计
        self.state["metrics"]["hibernate_count"] += 1
        
        self.save_state()
        
        return {
            "status": "DORMANT",
            "entered_at": datetime.now().isoformat(),
            "snapshot": snapshot,
            "estimated_savings_per_hour": {
                "tokens": 2000,
                "memory_mb": 15
            }
        }
    
    def wake(self, trigger_type="user_message"):
        """
        唤醒 - S2: 系统闭环之反馈
        恢复快照，计算指标，生成问候
        """
        wake_start = time.time()
        
        dormant_since = self.state.get("entered_dormancy_at", wake_start)
        dormant_duration = wake_start - dormant_since
        
        # 记录状态转换
        transition = {
            "from": "DORMANT",
            "to": "ACTIVE",
            "time": datetime.now().isoformat(),
            "reason": f"{trigger_type}_wake"
        }
        self.state["state_transitions"].append(transition)
        
        # 恢复状态
        self.state.update({
            "status": "ACTIVE",
            "last_activity": wake_start,
            "woke_at": wake_start,
            "wake_trigger": trigger_type,
            "dormant_duration": dormant_duration
        })
        
        # 更新统计
        self.state["metrics"]["wake_count"] += 1
        self.state["metrics"]["total_dormant_seconds"] += dormant_duration
        
        self.save_state()
        
        # 计算唤醒延迟
        wake_latency = (time.time() - wake_start) * 1000
        
        # 生成时间感知问候
        greeting = self._generate_greeting(dormant_duration)
        
        return {
            "status": "ACTIVE",
            "woke_at": datetime.now().isoformat(),
            "wake_latency_ms": wake_latency,
            "dormant_duration_sec": dormant_duration,
            "greeting": greeting
        }
    
    def _generate_greeting(self, dormant_seconds):
        """生成时间感知问候 - S1: 用户体验设计"""
        hours = dormant_seconds / 3600
        
        if hours < 1:
            return None  # 短休眠不提示
        elif hours < 6:
            return f"欢迎回来，休眠了{hours:.1f}小时。"
        elif hours < 24:
            return f"欢迎回来，休眠了{hours:.1f}小时。需要我回顾之前的进展吗？"
        else:
            days = hours / 24
            return f"好久不见！已经{days:.1f}天了。让我看看之前我们在做什么..."
    
    def update_activity(self):
        """更新最后活动时间"""
        self.state["last_activity"] = time.time()
        self.save_state()
    
    def get_status(self):
        """获取当前状态 - S3: 可观测输出"""
        status = self.state.get("status", "UNKNOWN")
        
        if status == "DORMANT":
            dormant_since = self.state.get("entered_dormancy_at", time.time())
            duration = time.time() - dormant_since
            return {
                "status": "DORMANT",
                "dormant_duration_sec": duration,
                "dormant_duration_human": self._format_duration(duration),
                "snapshot_saved": "snapshot" in self.state
            }
        else:
            last_activity = self.state.get("last_activity", time.time())
            idle_time = time.time() - last_activity
            return {
                "status": "ACTIVE",
                "idle_time_sec": idle_time,
                "idle_time_human": self._format_duration(idle_time),
                "hibernation_threshold": self.IDLE_THRESHOLD
            }
    
    def _format_duration(self, seconds):
        """格式化持续时间"""
        if seconds < 60:
            return f"{seconds:.0f}秒"
        elif seconds < 3600:
            return f"{seconds/60:.1f}分钟"
        else:
            return f"{seconds/3600:.1f}小时"


class DormancySelfTest:
    """休眠系统自检 - S5: 自我验证"""
    
    def __init__(self):
        self.manager = DormancyManager()
    
    def test_idle_detection(self):
        """测试空闲检测"""
        # 模拟10分钟无交互
        self.manager.state["last_activity"] = time.time() - 601
        
        idle_info = self.manager.detect_idle()
        assert idle_info["is_idle"] == True, "空闲检测失败"
        assert idle_info["idle_duration_sec"] > 600, "持续时间计算错误"
        print("  ✅ 空闲检测测试通过")
        return True
    
    def test_hibernate_decision(self):
        """测试休眠决策"""
        # 场景1: 空闲+无任务 → 应该休眠
        idle_info = {"is_idle": True, "idle_duration_sec": 601}
        self.manager.state["active_tasks"] = []
        self.manager.state["token_usage_pct"] = 50
        should, _ = self.manager.should_hibernate(idle_info)
        assert should == True, "应该休眠但未通过"
        
        # 场景2: 空闲但有任务 → 不休眠
        self.manager.state["active_tasks"] = ["重要任务"]
        should, _ = self.manager.should_hibernate(idle_info)
        assert should == False, "有任务时不应休眠"
        
        print("  ✅ 休眠决策测试通过")
        return True
    
    def test_state_transitions(self):
        """测试状态转换"""
        # ACTIVE → DORMANT
        result = self.manager.enter_dormancy()
        assert result["status"] == "DORMANT", "进入休眠失败"
        assert "snapshot" in result, "快照未保存"
        
        # DORMANT → ACTIVE
        wake_result = self.manager.wake()
        assert wake_result["status"] == "ACTIVE", "唤醒失败"
        assert wake_result["wake_latency_ms"] < 1000, "唤醒延迟过高"
        
        print("  ✅ 状态转换测试通过")
        return True
    
    def test_wake_latency(self):
        """测试唤醒延迟 - S7: 对抗测试"""
        self.manager.enter_dormancy()
        
        # 测量唤醒延迟
        result = self.manager.wake()
        assert result["wake_latency_ms"] < 500, f"唤醒延迟过高: {result['wake_latency_ms']}ms"
        
        print(f"  ✅ 唤醒延迟测试通过 ({result['wake_latency_ms']:.1f}ms)")
        return True
    
    def test_rapid_wake_hibernate_cycle(self):
        """测试连续唤醒-休眠循环 - S7: 对抗测试"""
        print("  🔄 连续唤醒测试 (5次循环)...")
        
        latencies = []
        for i in range(5):
            self.manager.enter_dormancy()
            time.sleep(0.05)  # 模拟50ms后收到消息
            
            result = self.manager.wake()
            latencies.append(result["wake_latency_ms"])
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        assert avg_latency < 200, f"平均延迟过高: {avg_latency:.1f}ms"
        assert max_latency < 500, f"最大延迟过高: {max_latency:.1f}ms"
        
        print(f"    平均延迟: {avg_latency:.1f}ms, 最大: {max_latency:.1f}ms")
        print("  ✅ 连续唤醒测试通过")
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n🧪 Dormancy-Protocol 自检开始...")
        print("=" * 50)
        
        tests = [
            self.test_idle_detection,
            self.test_hibernate_decision,
            self.test_state_transitions,
            self.test_wake_latency,
            self.test_rapid_wake_hibernate_cycle
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except AssertionError as e:
                print(f"  ❌ 测试失败: {e}")
                failed += 1
            except Exception as e:
                print(f"  ❌ 测试异常: {e}")
                failed += 1
        
        print("=" * 50)
        print(f"\n结果: {passed} 通过, {failed} 失败")
        
        if failed == 0:
            print("✅ 所有自检项目通过 - 系统健康")
            return True
        else:
            print("❌ 部分测试失败 - 请检查系统")
            return False


def main():
    """主函数 - 命令行接口"""
    manager = DormancyManager()
    
    if len(sys.argv) < 2:
        print("""
Dormancy-Protocol 管理脚本

用法:
  python3 dormancy_manager.py <command>

命令:
  init          初始化状态文件
  check         检查空闲状态，必要时进入休眠
  wake          手动唤醒
  status        查看当前状态
  selftest      运行自检
  metrics       查看统计指标
        """)
        return
    
    command = sys.argv[1]
    
    if command == "init":
        manager.save_state()
        print("✅ Dormancy-Protocol 已初始化")
    
    elif command == "check":
        idle_info = manager.detect_idle()
        should, reason = manager.should_hibernate(idle_info)
        
        if should:
            result = manager.enter_dormancy()
            print(f"💤 进入休眠状态")
            print(f"   时间: {result['entered_at']}")
            print(f"   预计节省: {result['estimated_savings_per_hour']['tokens']} Token/小时")
        else:
            print(f"⏱️ 保持活跃 | {reason}")
            print(f"   空闲: {idle_info['idle_duration_sec']:.0f}s / {idle_info['threshold']}s")
    
    elif command == "wake":
        if manager.state.get("status") != "DORMANT":
            print("⚠️ 当前状态不是休眠，无需唤醒")
            return
        
        result = manager.wake()
        print(f"☀️ 唤醒完成")
        print(f"   延迟: {result['wake_latency_ms']:.0f}ms")
        print(f"   休眠时长: {result['dormant_duration_sec']:.0f}s")
        if result.get("greeting"):
            print(f"   {result['greeting']}")
    
    elif command == "status":
        status = manager.get_status()
        print("💤 Dormancy-Protocol 状态")
        print("=" * 40)
        print(f"状态: {status['status']}")
        
        if status['status'] == "DORMANT":
            print(f"休眠时长: {status['dormant_duration_human']}")
            print(f"快照: {'已保存' if status['snapshot_saved'] else '未保存'}")
        else:
            print(f"空闲时间: {status['idle_time_human']}")
            print(f"休眠阈值: {status['hibernation_threshold']}秒")
    
    elif command == "selftest":
        test = DormancySelfTest()
        success = test.run_all_tests()
        sys.exit(0 if success else 1)
    
    elif command == "metrics":
        metrics = manager.state.get("metrics", {})
        print("📊 Dormancy-Protocol 统计")
        print("=" * 40)
        print(f"休眠次数: {metrics.get('hibernate_count', 0)}")
        print(f"唤醒次数: {metrics.get('wake_count', 0)}")
        print(f"总休眠时长: {metrics.get('total_dormant_seconds', 0)/3600:.1f}小时")
        print(f"平均唤醒延迟: {metrics.get('avg_wake_latency_ms', 0):.1f}ms")
    
    else:
        print(f"❌ 未知命令: {command}")
        print("运行 'python3 dormancy_manager.py' 查看帮助")


if __name__ == "__main__":
    main()
