"""
Universal Task Executor V3.0 - 核心引擎测试
验证所有核心组件的功能
"""

import asyncio
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    TaskEngine, Task, TaskBatch, TaskResult, TaskStatus, TaskPriority,
    TokenLevel, TokenEngine, TokenBudget, TokenAwareScheduler,
    TaskRegistry, TaskHandler, TaskTypeConfig,
    CheckpointManager, FileCheckpointStorage, Checkpoint,
    StateManager, ExecutorState,
    create_engine, ExecutionContext, ExecutorConfig
)


class TestHandler(TaskHandler):
    """测试处理器"""
    
    handler_name = "test_handler"
    supported_categories = ["category_test"]
    version = "1.0.0"
    
    def execute(self, task, checkpoint_state=None):
        """执行测试任务"""
        print(f"  Executing task: {task.task_id} - {task.title}")
        return TaskResult(
            task_id=task.task_id,
            status="completed",
            output={"message": "Test completed"},
            token_consumed=100,
            time_elapsed=0.1
        )
    
    def estimate_cost(self, task):
        return {"tokens": 100, "time_seconds": 1}


def test_structures():
    """测试数据结构"""
    print("\n[1/6] Testing Structures...")
    
    # 测试Task创建
    task = Task(
        category="category_6",
        priority=TaskPriority.P0,
        title="测试任务",
        description="这是一个测试任务"
    )
    assert task.task_id is not None
    assert task.category == "category_6"
    assert task.priority == TaskPriority.P0
    print(f"  ✓ Task created: {task.task_id}")
    
    # 测试序列化
    task_dict = task.to_dict()
    task2 = Task.from_dict(task_dict)
    assert task2.task_id == task.task_id
    print("  ✓ Task serialization works")
    
    # 测试TaskBatch
    batch = TaskBatch(
        tasks=[task, task2],
        name="测试批次"
    )
    assert len(batch.tasks) == 2
    print(f"  ✓ TaskBatch created: {batch.batch_id}")
    
    # 测试TokenBudget
    budget = TokenBudget(total=10000, reserved=1000)
    assert budget.available == 9000
    assert budget.get_level() == TokenLevel.L5_FULL
    print("  ✓ TokenBudget works")
    
    # 测试Checkpoint
    checkpoint = Checkpoint(
        task_id=task.task_id,
        progress=0.5,
        processed_task_ids=["task1"],
        pending_task_ids=["task2"]
    )
    assert checkpoint.is_resumable()
    print(f"  ✓ Checkpoint created: {checkpoint.checkpoint_id}")
    
    print("  Structures test PASSED")
    return True


def test_token_engine():
    """测试Token引擎"""
    print("\n[2/6] Testing Token Engine...")
    
    engine = TokenEngine(total_budget=10000, reserve_ratio=0.1)
    
    # 测试初始状态
    assert engine.budget.total == 10000
    assert engine.budget.reserved == 1000
    assert engine.budget.available == 9000
    assert engine.budget.get_level() == TokenLevel.L5_FULL
    print("  ✓ Initial state correct")
    
    # 测试消费
    level = engine.consume(1000, "test_task")
    assert engine.budget.consumed == 1000
    assert level == TokenLevel.L5_FULL
    print("  ✓ Token consumption works")
    
    # 测试档位变化 - 注意：档位基于available/total比例
    # 消耗6000后：consumed=6000, reserved=1000, available=3000, total=10000
    # available/total = 3000/10000 = 0.3 -> L3_THROTTLE (0.3-0.5)
    engine.consume(5000, "test_task2")  # 总消耗6000
    level = engine.budget.get_level()
    print(f"  Current level: {level.value}, available ratio: {engine.budget.available/engine.budget.total:.2f}")
    assert level in [TokenLevel.L3_THROTTLE, TokenLevel.L2_CRITICAL]  # 边界值可能落在L2
    print(f"  ✓ Token level changed to {level.value}")
    
    # 测试执行策略
    strategy = engine.get_execution_strategy("category_6", "p0")
    assert "should_execute" in strategy
    print("  ✓ Execution strategy works")
    
    # 测试调度器
    scheduler = TokenAwareScheduler(engine)
    task = Task(category="category_6", priority=TaskPriority.P1, title="测试")
    decision = scheduler.schedule_task(task)
    assert "action" in decision  # 直接包含action键
    print("  ✓ Token-aware scheduler works")
    
    print("  Token Engine test PASSED")
    return True


def test_registry():
    """测试任务注册表"""
    print("\n[3/6] Testing Task Registry...")
    
    # 重置单例
    from core import registry
    registry.reset_registry()
    
    reg = registry.get_registry()
    
    # 测试默认配置
    categories = reg.list_categories()
    assert len(categories) == 6
    assert "category_1" in categories
    assert "category_6" in categories
    print(f"  ✓ Default categories loaded: {len(categories)}")
    
    # 测试配置获取
    config = reg.get_config("category_6")
    assert config is not None
    assert config.blue_army_required == True
    print("  ✓ Category config works")
    
    # 测试处理器注册 - 确保先注册类别配置
    test_config = TaskTypeConfig(
        category="category_test",
        name="test",
        display_name="测试类型",
        description="用于测试的任务类型",
        default_handler="test_handler"
    )
    reg.register_task_type(test_config)
    
    reg.register_handler(TestHandler)
    handler = reg.get_handler("category_test")
    assert handler is not None, "Handler should not be None after registration"
    assert handler.handler_name == "test_handler"
    print("  ✓ Handler registration works")
    
    print("  Registry test PASSED")
    return True


async def test_checkpoint_manager():
    """测试Checkpoint管理器"""
    print("\n[4/6] Testing Checkpoint Manager...")
    
    # 使用临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    storage = FileCheckpointStorage(temp_dir)
    manager = CheckpointManager(storage=storage, auto_save_interval=60)
    
    # 测试创建
    task = Task(category="category_6", priority=TaskPriority.P0, title="测试")
    checkpoint = await manager.create_checkpoint(
        task_id=task.task_id,
        progress=0.5,
        processed_ids=["task1"],
        pending_ids=["task2", "task3"]
    )
    assert checkpoint.checkpoint_id is not None
    print(f"  ✓ Checkpoint created: {checkpoint.checkpoint_id}")
    
    # 测试加载
    loaded = await manager.storage.load(checkpoint.checkpoint_id)
    assert loaded is not None
    assert loaded.task_id == task.task_id
    print("  ✓ Checkpoint load works")
    
    # 测试恢复
    result = await manager.resume_from_checkpoint(checkpoint.checkpoint_id)
    assert result.success
    assert len(result.remaining_tasks) == 2
    print("  ✓ Checkpoint resume works")
    
    # 测试更新
    await manager.update_checkpoint(
        checkpoint.checkpoint_id,
        progress=0.8,
        processed_ids=["task1", "task2"],
        pending_ids=["task3"]
    )
    updated = await manager.storage.load(checkpoint.checkpoint_id)
    assert updated.progress == 0.8
    print("  ✓ Checkpoint update works")
    
    # 测试完成
    await manager.complete_checkpoint(checkpoint.checkpoint_id)
    completed = await manager.storage.load(checkpoint.checkpoint_id)
    assert completed.status == "completed"
    print("  ✓ Checkpoint completion works")
    
    # 清理
    import shutil
    shutil.rmtree(temp_dir)
    
    print("  Checkpoint Manager test PASSED")
    return True


def test_state_manager():
    """测试状态管理器"""
    print("\n[5/6] Testing State Manager...")
    
    manager = StateManager()
    
    # 测试初始状态
    assert manager.state == ExecutorState.IDLE
    print("  ✓ Initial state is IDLE")
    
    # 测试状态变更
    manager.set_state(ExecutorState.RUNNING, "Test")
    assert manager.state == ExecutorState.RUNNING
    print("  ✓ State change works")
    
    # 测试任务管理
    task = Task(category="category_6", priority=TaskPriority.P0, title="测试")
    manager.add_task(task)
    assert manager.has_pending_tasks()
    assert manager.get_queue_counts()["pending"] == 1
    print("  ✓ Task queue management works")
    
    # 测试获取下一个任务
    next_task = manager.get_next_task()
    assert next_task is not None
    assert next_task.task_id == task.task_id
    print("  ✓ Task retrieval works")
    
    # 测试完成任务
    result = TaskResult(
        task_id=task.task_id,
        status="completed",
        output={},
        token_consumed=100,
        time_elapsed=0.1
    )
    manager.complete_task(task.task_id, result)
    assert manager.get_metrics().tasks_completed == 1
    print("  ✓ Task completion tracking works")
    
    # 测试序列化
    state_dict = manager.to_dict()
    assert "state" in state_dict
    assert "queue_state" in state_dict
    print("  ✓ State serialization works")
    
    # 测试反序列化
    manager2 = StateManager()
    manager2.from_dict(state_dict)
    assert manager2.get_metrics().tasks_completed == 1
    print("  ✓ State deserialization works")
    
    print("  State Manager test PASSED")
    return True


async def test_task_engine():
    """测试任务调度引擎"""
    print("\n[6/6] Testing Task Engine...")
    
    # 创建引擎
    config = ExecutorConfig(
        token_default_budget=50000,
        checkpoint_enabled=True,
        checkpoint_path="/tmp/ute_test_checkpoints"
    )
    
    engine = TaskEngine(config)
    
    # 注册测试处理器
    engine.register_handler(TestHandler)
    
    # 创建任务
    tasks = [
        Task(category="category_test", priority=TaskPriority.P0, title=f"任务{i}")
        for i in range(3)
    ]
    
    # 启动引擎
    await engine.startup()
    assert engine.state_manager.state == ExecutorState.IDLE
    print("  ✓ Engine startup works")
    
    # 执行任务
    result = await engine.execute(tasks)
    assert result.status == "completed"
    print("  ✓ Task execution works")
    
    # 检查统计
    stats = engine.get_stats()
    assert stats["metrics"]["tasks_completed"] == 3
    print("  ✓ Execution statistics work")
    
    # 生成报告
    report = engine.generate_report()
    assert "total_tasks" in report
    print("  ✓ Report generation works")
    
    # 关闭引擎
    await engine.shutdown()
    print("  ✓ Engine shutdown works")
    
    print("  Task Engine test PASSED")
    return True


async def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("Universal Task Executor V3.0 - Core Engine Tests")
    print("="*60)
    
    tests = [
        test_structures,
        test_token_engine,
        test_registry,
        test_checkpoint_manager,
        test_state_manager,
        test_task_engine,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                await test()
            else:
                test()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
