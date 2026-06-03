#!/usr/bin/env python3
"""
测试中断恢复机制集成
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/interrupt-recovery')

from interrupt_recovery_integration import InterruptRecoveryIntegration, with_recovery

def test_basic_execution():
    """测试基本执行"""
    recovery = InterruptRecoveryIntegration()
    
    def simple_task():
        return "success"
    
    result = recovery.quick_execute(simple_task)
    assert result == "success", f"期望success，得到{result}"
    print("✅ 基本执行测试通过")

def test_decorator():
    """测试装饰器"""
    @with_recovery("test-decorator", "test", 1)
    def decorated_task():
        return "decorated_success"
    
    result = decorated_task()
    assert result == "decorated_success", f"期望decorated_success，得到{result}"
    print("✅ 装饰器测试通过")

if __name__ == "__main__":
    print("测试中断恢复机制集成...")
    print("=" * 50)
    
    try:
        test_basic_execution()
        test_decorator()
        print("=" * 50)
        print("✅ 所有测试通过")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
