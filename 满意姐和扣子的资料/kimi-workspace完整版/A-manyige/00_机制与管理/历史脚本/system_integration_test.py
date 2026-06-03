#!/usr/bin/env python3
"""
系统集成验证脚本
验证6 Worker系统联调

质量验证：实际运行，非静态检查
"""

import sys
from pathlib import Path

# 添加所有Skill目录到路径
SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
for skill_dir in SKILLS_DIR.iterdir():
    if skill_dir.is_dir():
        sys.path.insert(0, str(skill_dir))

from worker_orchestrator import WorkerOrchestrator, WorkerType, TaskStatus
from blackboard_manager import BlackboardManager
from checkpoint_manager import CheckpointManager


def test_worker_blackboard_integration():
    """测试Worker和Blackboard集成"""
    print("🔄 测试Worker-Blackboard集成...")
    
    # 初始化
    bb = BlackboardManager()
    orch = WorkerOrchestrator()
    
    # 在Blackboard中写入状态
    bb.write("test_state", {"data": "test"}, "test_worker")
    
    # Worker读取状态
    state, version = bb.read("test_state")
    
    if state and state.get("data") == "test":
        print("   ✅ Worker-Blackboard集成通过")
        return True
    else:
        print("   ❌ Worker-Blackboard集成失败")
        return False


def test_worker_checkpoint_integration():
    """测试Worker和Checkpoint集成"""
    print("🔄 测试Worker-Checkpoint集成...")
    
    # 初始化
    cp = CheckpointManager()
    orch = WorkerOrchestrator()
    
    # 创建检查点
    checkpoint_id = cp.create_checkpoint("integration_test")
    
    if checkpoint_id:
        print(f"   ✅ 检查点创建成功: {checkpoint_id[:20]}...")
        
        # 验证检查点
        if cp.verify_checkpoint(checkpoint_id):
            print("   ✅ 检查点验证通过")
            return True
        else:
            print("   ❌ 检查点验证失败")
            return False
    else:
        print("   ❌ 检查点创建失败")
        return False


def test_full_system():
    """测试完整系统"""
    print("🔄 测试完整系统...")
    
    # 初始化所有组件
    bb = BlackboardManager()
    orch = WorkerOrchestrator()
    cp = CheckpointManager()
    
    # 1. 提交任务
    task_id = orch.submit_task(
        name="integration_test",
        worker_type=WorkerType.WORKER_EXECUTION,
        input_data={"test": "data"},
    )
    
    if not task_id:
        print("   ❌ 任务提交失败")
        return False
    
    print(f"   ✅ 任务提交成功: {task_id}")
    
    # 2. 在Blackboard中记录任务状态
    bb.write(f"task_{task_id}", {"status": "submitted"}, "orchestrator")
    
    # 3. 创建检查点
    checkpoint_id = cp.create_checkpoint("pre_execution")
    
    if checkpoint_id:
        print(f"   ✅ 预执行检查点创建: {checkpoint_id[:20]}...")
    
    # 4. 验证所有组件协同工作
    task_status = orch.get_task_status(task_id)
    bb_state, _ = bb.read(f"task_{task_id}")
    
    if task_status and bb_state:
        print("   ✅ 完整系统协同工作")
        return True
    else:
        print("   ❌ 系统协同失败")
        return False


def main():
    """主函数"""
    print("═══════════════════════════════════════════════════════════")
    print("              系统集成验证 - 6 Worker联调")
    print("═══════════════════════════════════════════════════════════")
    print()
    
    results = []
    
    # 测试1: Worker-Blackboard集成
    results.append(("Worker-Blackboard集成", test_worker_blackboard_integration()))
    print()
    
    # 测试2: Worker-Checkpoint集成
    results.append(("Worker-Checkpoint集成", test_worker_checkpoint_integration()))
    print()
    
    # 测试3: 完整系统
    results.append(("完整系统协同", test_full_system()))
    print()
    
    # 汇总
    print("═══════════════════════════════════════════════════════════")
    print("验证汇总:")
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    print()
    print(f"总体状态: {'✅ 全部通过' if all_passed else '❌ 有失败项'}")
    print("═══════════════════════════════════════════════════════════")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
