"""
Blackboard V2 测试套件
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 直接从模块导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blackboard_manager import BlackboardManager, get_blackboard
from shared_memory import SharedMemory
from event_system import EventSystem
from audit_logger import AuditLogger


class TestRunner:
    """简易测试运行器"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str, func):
        """运行单个测试"""
        try:
            func()
            print(f"  ✓ {name}")
            self.passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
            self.failed += 1
        except Exception as e:
            print(f"  ✗ {name}: Exception - {e}")
            self.failed += 1
    
    def summary(self):
        """输出测试摘要"""
        print(f"\n{'='*40}")
        print(f"测试结果: {self.passed} 通过, {self.failed} 失败")
        print(f"{'='*40}")
        return self.failed == 0


def test_shared_memory():
    """测试共享内存"""
    # 清理
    SharedMemory.reset_all()
    
    mem = SharedMemory("test_ns")
    
    # 基础操作
    mem.set("key1", "value1")
    assert mem.get("key1") == "value1"
    assert mem.get("key2", "default") == "default"
    assert mem.exists("key1") is True
    assert mem.exists("key2") is False
    
    # keys
    assert "key1" in mem.keys()
    
    # delete
    assert mem.delete("key1") is True
    assert mem.delete("key1") is False
    
    # 复杂数据类型
    mem.set("dict", {"a": 1, "b": 2})
    mem.set("list", [1, 2, 3])
    assert mem.get("dict") == {"a": 1, "b": 2}
    assert mem.get("list") == [1, 2, 3]
    
    # 命名空间隔离
    mem2 = SharedMemory("test_ns2")
    mem2.set("key", "value2")
    assert mem.get("key") is None
    assert mem2.get("key") == "value2"
    
    SharedMemory.reset_all()


def test_event_system():
    """测试事件系统"""
    events = EventSystem()
    received = []
    
    def handler(event_type, data):
        received.append((event_type, data))
    
    # 精确匹配
    events.subscribe("test:event", handler)
    events.publish("test:event", {"data": 1})
    assert len(received) == 1
    
    # 不匹配
    events.publish("other:event", {"data": 2})
    assert len(received) == 1
    
    # 通配符匹配
    received.clear()
    events.subscribe("test:*", handler)
    events.publish("test:foo", {"data": 3})
    events.publish("test:bar", {"data": 4})
    assert len(received) == 2
    
    # 取消订阅
    events.unsubscribe("test:event", handler)
    received.clear()
    events.publish("test:event", {"data": 5})
    assert len(received) == 1  # 只剩 test:* 的订阅
    
    events.clear()


def test_audit_logger():
    """测试审计日志"""
    logger = AuditLogger()
    
    # 基础日志
    logger.log("TEST", "test message")
    assert len(logger) == 1
    
    # 多条日志
    logger.log("GET", "get key1")
    logger.log("SET", "set key2")
    assert len(logger) == 3
    
    # 获取最近
    recent = logger.get_recent(2)
    assert len(recent) == 2
    assert recent[0]["action"] == "GET"
    assert recent[1]["action"] == "SET"
    
    # 搜索
    results = logger.search(action="SET")
    assert len(results) == 1
    assert results[0]["action"] == "SET"
    
    # 清空
    logger.clear()
    assert len(logger) == 0


def test_blackboard_manager():
    """测试黑板管理器"""
    import tempfile
    import shutil
    
    # 使用临时目录
    tmpdir = tempfile.mkdtemp()
    
    try:
        board = BlackboardManager("test_board", persist_dir=tmpdir)
        
        # 基础操作
        board.set("key1", "value1")
        assert board.get("key1") == "value1"
        
        # exists
        assert board.exists("key1") is True
        assert board.exists("key2") is False
        
        # delete
        assert board.delete("key1") is True
        assert board.delete("key1") is False
        
        # 生命周期
        assert board.is_running() is False
        board.start()
        assert board.is_running() is True
        board.stop()
        assert board.is_running() is False
        
        # 持久化
        board.set("persist_key", "persist_value")
        filepath = board.save()
        assert os.path.exists(filepath)
        
        # 加载
        board2 = BlackboardManager("test_board2", persist_dir=tmpdir)
        board2.load(filepath)
        assert board2.get("persist_key") == "persist_value"
        
        # 统计
        stats = board.stats()
        assert "reads" in stats
        assert "writes" in stats
        
        # 审计日志
        logs = board.get_audit_log(10)
        assert len(logs) > 0
        
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_event_integration():
    """测试事件集成"""
    import tempfile
    import shutil
    
    tmpdir = tempfile.mkdtemp()
    
    try:
        board = BlackboardManager("test_events", persist_dir=tmpdir)
        received = []
        
        def handler(event_type, data):
            received.append((event_type, data))
        
        # 订阅数据变更事件
        board.subscribe("data:*", handler)
        
        # 设置数据会触发事件
        board.set("key1", "value1")
        assert len(received) == 1
        assert received[0][0] == "data:key1"
        
        # 再设置一个，再触发
        board.set("key2", "value2")
        assert len(received) == 2
        assert received[1][0] == "data:key2"
        
        # 订阅自定义事件
        custom_received = []
        def custom_handler(event_type, data):
            custom_received.append((event_type, data))
        board.subscribe("custom:*", custom_handler)
        
        board.publish("custom:event", {"msg": "hello"})
        assert len(custom_received) == 1
        assert custom_received[0][0] == "custom:event"
        
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_singleton():
    """测试单例模式"""
    # 清理全局实例
    import blackboard_manager as bm
    bm._global_blackboard = None
    
    board1 = get_blackboard("singleton_test")
    board2 = get_blackboard("singleton_test")
    board3 = get_blackboard("other_ns")
    
    assert board1 is board2
    assert board1 is not board3


def run_all_tests():
    """运行所有测试"""
    runner = TestRunner()
    
    print("\n测试共享内存...")
    runner.test("SharedMemory 基础操作", test_shared_memory)
    
    print("\n测试事件系统...")
    runner.test("EventSystem 发布订阅", test_event_system)
    
    print("\n测试审计日志...")
    runner.test("AuditLogger 日志记录", test_audit_logger)
    
    print("\n测试黑板管理器...")
    runner.test("BlackboardManager 核心功能", test_blackboard_manager)
    
    print("\n测试事件集成...")
    runner.test("事件系统集成", test_event_integration)
    
    print("\n测试单例模式...")
    runner.test("全局单例", test_singleton)
    
    return runner.summary()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
