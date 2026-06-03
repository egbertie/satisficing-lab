#!/usr/bin/env python3
"""
Digital-Avatar-Swarm 测试套件

测试范围:
- S1: 全局考虑 (资源边界、协作模型)
- S2: 系统闭环 (任务流程、反馈循环)
- S3: 可观测输出 (状态监控、指标收集)
- S4: 自动化集成 (分解、负载均衡、故障转移)
- S5: 自我验证 (健康检查、一致性校验)
- S6: 认知谦逊 (局限标注、WIP标识)
- S7: 对抗测试 (故障模拟、压力测试)

运行: pytest tests/test_swarm.py -v
"""

import asyncio
import pytest
import time
from datetime import datetime

# 确保可以导入主模块
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from avatar_swarm import (


def get_skill_main_file(skill_path: Path):
    """获取Skill的主代码文件"""
    skill_name = skill_path.name.replace('-', '_')
    candidates = [
        skill_path / f"{skill_name}.py",
        skill_path / "__init__.py",
        skill_path / "main.py",
        skill_path / "runner.py",
        skill_path / "skill.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    py_files = list(skill_path.glob("*.py"))
    if py_files:
        return py_files[0]
    return None

    SwarmOrchestrator,
    Task,
    SubTask,
    Result,
    Avatar,
    TaskDecomposer,
    LoadBalancer,
    ResultAggregator,
    HealthChecker,
    SwarmTester,
    AvatarStatus,
    TaskStatus,
    ResultStatus
)


# ═══════════════════════════════════════════════════════════════════════════
# S1: 全局考虑测试
# ═══════════════════════════════════════════════════════════════════════════

class TestS1_GlobalConsideration:
    """S1: 全局考虑测试"""
    
    def test_resource_boundaries(self):
        """测试资源边界限制"""
        # 测试最大代理数限制
        with pytest.raises(ValueError):
            SwarmOrchestrator(max_avatars=100)  # 超过限制
        
        swarm = SwarmOrchestrator(max_avatars=5)
        assert len(swarm.avatars) == 5
        
        # 测试Token预算
        assert swarm.token_budget == 100000
        
        # 测试超时设置
        assert swarm.timeout == 300
    
    def test_avatar_initialization(self):
        """测试代理初始化"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        assert len(swarm.avatars) == 3
        
        for i, avatar in enumerate(swarm.avatars):
            assert avatar.avatar_id == f"avatar-{i+1:02d}"
            assert avatar.status == AvatarStatus.IDLE
            assert len(avatar.capabilities) > 0
            assert avatar.success_rate == 1.0
    
    def test_collaboration_model(self):
        """测试协作模型"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        # 验证主控AI存在
        assert swarm.decomposer is not None
        assert swarm.aggregator is not None
        assert swarm.load_balancer is not None
        
        # 验证代理列表
        assert isinstance(swarm.avatars, list)
        assert all(isinstance(a, Avatar) for a in swarm.avatars)


# ═══════════════════════════════════════════════════════════════════════════
# S2: 系统闭环测试
# ═══════════════════════════════════════════════════════════════════════════

class TestS2_SystemClosedLoop:
    """S2: 系统闭环测试"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """测试完整工作流程"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        task = Task(
            description="测试完整工作流",
            context={'test': True}
        )
        
        result = await swarm.execute(task)
        
        # 验证结果
        assert result is not None
        assert result.task_id is not None
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.PARTIAL]
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_feedback_loop(self):
        """测试反馈循环"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        initial_success_rate = swarm.metrics.success_rate
        
        # 执行多个任务
        for i in range(5):
            task = Task(description=f"反馈测试任务-{i}")
            await swarm.execute(task)
        
        # 验证指标更新
        assert swarm.metrics.total_tasks > 0
        assert swarm.metrics.completed_tasks >= 0
        assert swarm.metrics.avg_execution_time >= 0
    
    @pytest.mark.asyncio
    async def test_task_decomposition_integration(self):
        """测试任务分解集成"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        # 高复杂度任务应该被分解
        complex_task = Task(
            description="分析并评估系统架构设计方案，对比多个技术选型，给出详细分析报告和优化建议",
            context={'detailed': True, 'multi_dimension': True}
        )
        
        subtasks = swarm.decomposer.decompose(complex_task)
        
        # 高复杂度任务应该分解为多个子任务
        assert len(subtasks) > 1
        
        result = await swarm.execute(complex_task)
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.PARTIAL, ResultStatus.CONFLICT]


# ═══════════════════════════════════════════════════════════════════════════
# S3: 可观测输出测试
# ═══════════════════════════════════════════════════════════════════════════

class TestS3_ObservableOutput:
    """S3: 可观测输出测试"""
    
    def test_status_monitoring(self):
        """测试状态监控面板"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        status = swarm.get_status()
        
        # 验证状态结构
        assert 'swarm_status' in status
        assert 'metrics' in status
        assert 'avatars' in status
        
        # 验证蜂群状态
        swarm_status = status['swarm_status']
        assert 'total_avatars' in swarm_status
        assert 'active_avatars' in swarm_status
        assert 'idle_avatars' in swarm_status
        
        # 验证指标
        metrics = status['metrics']
        assert 'total_tasks' in metrics
        assert 'success_rate' in metrics
        assert 'token_consumed' in metrics
    
    @pytest.mark.asyncio
    async def test_timeline_tracking(self):
        """测试时间线追踪"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        # 创建任务
        task = Task(description="时间线测试任务")
        swarm.active_tasks[task.task_id] = task
        
        timeline = swarm.get_timeline()
        
        # 验证时间线结构
        assert isinstance(timeline, list)
        assert len(timeline) > 0
        
        event = timeline[0]
        assert 'timestamp' in event
        assert 'event' in event
        assert 'task_id' in event
    
    def test_resource_metrics(self):
        """测试资源指标"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        # 验证初始指标
        assert swarm.metrics.total_tasks == 0
        assert swarm.metrics.completed_tasks == 0
        assert swarm.metrics.success_rate == 1.0
        
        # 模拟Token消耗
        swarm.token_consumed = 5000
        status = swarm.get_status()
        assert status['metrics']['token_consumed'] == 5000


# ═══════════════════════════════════════════════════════════════════════════
# S4: 自动化集成测试
# ═══════════════════════════════════════════════════════════════════════════

class TestS4_AutomationIntegration:
    """S4: 自动化集成测试"""
    
    def test_auto_decomposition(self):
        """测试自动任务分解"""
        decomposer = TaskDecomposer()
        
        # 低复杂度任务
        simple_task = Task(description="简单任务")
        subtasks = decomposer.decompose(simple_task)
        assert len(subtasks) == 1
        
        # 高复杂度任务
        complex_task = Task(
            description="分析和设计一个分布式系统架构，考虑性能、可扩展性、安全性，对比多种技术方案",
            context={'context1': 1, 'context2': 2, 'context3': 3}
        )
        subtasks = decomposer.decompose(complex_task)
        assert len(subtasks) > 1
    
    def test_complexity_analysis(self):
        """测试复杂度分析"""
        decomposer = TaskDecomposer()
        
        # 测试简单任务
        simple = Task(description="简单任务")
        simple_score = decomposer.analyze_complexity(simple)
        assert 0 <= simple_score < 0.5
        
        # 测试复杂任务
        complex_task = Task(
            description="""分析并评估系统架构设计方案，对比多个技术选型，包括数据库选择、缓存策略、
            消息队列设计、微服务划分、API网关配置等，给出详细分析报告和优化建议，
            并考虑未来3年的扩展需求""",
            context={'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
        )
        complex_score = decomposer.analyze_complexity(complex_task)
        assert complex_score > 0.5
    
    def test_load_balancing(self):
        """测试负载均衡"""
        avatars = [
            Avatar(avatar_id="a1", name="Avatar1", status=AvatarStatus.IDLE, success_rate=0.9, avg_response_time=1.0),
            Avatar(avatar_id="a2", name="Avatar2", status=AvatarStatus.IDLE, success_rate=0.7, avg_response_time=3.0),
            Avatar(avatar_id="a3", name="Avatar3", status=AvatarStatus.BUSY, success_rate=0.95, avg_response_time=0.5),
        ]
        
        balancer = LoadBalancer(avatars)
        subtask = SubTask(parent_id="test", description="测试")
        
        # 应该分配到空闲且评分高的代理
        assigned = balancer.assign(subtask)
        assert assigned is not None
        assert assigned.status == AvatarStatus.IDLE
        assert assigned.avatar_id in ["a1", "a2"]  # a3是BUSY
    
    def test_fault_tolerance_config(self):
        """测试容错配置"""
        from avatar_swarm import FaultTolerantExecutor
        
        executor = FaultTolerantExecutor(max_retries=3)
        assert executor.max_retries == 3
        assert len(executor.retry_delays) == 3


# ═══════════════════════════════════════════════════════════════════════════
# S5: 自我验证测试
# ═══════════════════════════════════════════════════════════════════════════

class TestS5_SelfValidation:
    """S5: 自我验证测试"""
    
    def test_health_check(self):
        """测试健康检查"""
        checker = HealthChecker()
        
        # 健康代理
        healthy = Avatar(
            avatar_id="h1",
            name="Healthy",
            status=AvatarStatus.IDLE,
            avg_response_time=1.0,
            success_rate=0.95
        )
        
        health = checker.check(healthy)
        assert health['overall'] == 'healthy'
        assert 'checks' in health
        assert health['checks']['latency']['passed'] is True
        assert health['checks']['success_rate']['passed'] is True
        
        # 不健康代理
        unhealthy = Avatar(
            avatar_id="u1",
            name="Unhealthy",
            status=AvatarStatus.ERROR,
            avg_response_time=15.0,
            success_rate=0.5
        )
        
        health = checker.check(unhealthy)
        assert health['overall'] == 'degraded'
    
    def test_consistency_check(self):
        """测试一致性校验"""
        aggregator = ResultAggregator()
        
        # 高度一致的结果
        similar_results = [
            Result(task_id="t1", content="结果A很好", status=ResultStatus.SUCCESS, confidence=0.9),
            Result(task_id="t2", content="结果A优秀", status=ResultStatus.SUCCESS, confidence=0.85),
            Result(task_id="t3", content="结果A良好", status=ResultStatus.SUCCESS, confidence=0.88),
        ]
        
        consistency = aggregator._calculate_consistency(similar_results)
        assert consistency > 0.7  # 应该高度一致
        
        # 不一致的结果
        divergent_results = [
            Result(task_id="t1", content="选择方案A", status=ResultStatus.SUCCESS),
            Result(task_id="t2", content="选择方案B", status=ResultStatus.SUCCESS),
            Result(task_id="t3", content="选择方案C完全不同", status=ResultStatus.SUCCESS),
        ]
        
        consistency = aggregator._calculate_consistency(divergent_results)
        assert consistency < 0.5  # 应该不一致


# ═══════════════════════════════════════════════════════════════════════════
# S6: 认知谦逊测试 (文档/代码标注)
# ═══════════════════════════════════════════════════════════════════════════

class TestS6_EpistemicHumility:
    """S6: 认知谦逊测试"""
    
    def test_confidence_scoring(self):
        """测试置信度评分"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        # 结果应该包含置信度信息
        result = Result(
            task_id="test",
            content="测试",
            status=ResultStatus.SUCCESS,
            confidence=0.85
        )
        
        assert result.confidence == 0.85
        assert 0 <= result.confidence <= 1.0
    
    def test_result_metadata(self):
        """测试结果元数据"""
        result = Result(
            task_id="test",
            content="测试",
            status=ResultStatus.SUCCESS,
            metadata={
                'consistency_score': 0.87,
                'sub_results_count': 4,
                'uncertainty_factors': ['task_complexity', 'data_quality']
            }
        )
        
        assert 'consistency_score' in result.metadata
        assert 'uncertainty_factors' in result.metadata


# ═══════════════════════════════════════════════════════════════════════════
# S7: 对抗测试
# ═══════════════════════════════════════════════════════════════════════════

class TestS7_AdversarialTesting:
    """S7: 对抗测试"""
    
    @pytest.mark.asyncio
    async def test_high_load(self):
        """测试高负载场景"""
        swarm = SwarmOrchestrator(max_avatars=5)
        
        # 同时提交多个任务
        tasks = [
            Task(description=f"高负载测试任务-{i}")
            for i in range(15)
        ]
        
        results = await asyncio.gather(*[
            swarm.execute(task)
            for task in tasks
        ])
        
        # 验证成功率
        success_count = sum(1 for r in results if r.status == ResultStatus.SUCCESS)
        success_rate = success_count / len(results)
        
        assert success_rate >= 0.8  # 至少80%成功
    
    @pytest.mark.asyncio
    async def test_swarm_tester_integration(self):
        """测试SwarmTester集成"""
        swarm = SwarmOrchestrator(max_avatars=3)
        tester = SwarmTester(swarm)
        
        # 运行测试
        await tester.test_high_load()
        
        report = tester.get_test_report()
        assert 'summary' in report
        assert 'details' in report
        assert 'timestamp' in report
    
    def test_error_handling(self):
        """测试错误处理"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        # 验证错误处理机制存在
        assert swarm.fault_executor is not None
        assert swarm.fault_executor.max_retries == 3
    
    @pytest.mark.asyncio
    async def test_pause_resume(self):
        """测试暂停/恢复功能"""
        swarm = SwarmOrchestrator(max_avatars=3)
        
        # 暂停
        assert swarm.pause() is True
        assert swarm._paused is True
        
        # 恢复
        assert swarm.resume() is True
        assert swarm._paused is False


# ═══════════════════════════════════════════════════════════════════════════
# 集成测试
# ═══════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """测试完整流水线"""
        swarm = SwarmOrchestrator(max_avatars=5)
        
        # 复杂任务
        task = Task(
            description="""分析当前AI Agent市场的竞争格局，评估主要玩家如AutoGPT、MetaGPT、LangChain等的技术特点、
            商业模式和市场定位，对比它们的优势和劣势，并给出投资建议""",
            context={'market': 'AI Agent', 'players': ['AutoGPT', 'MetaGPT', 'LangChain']},
            priority=8
        )
        
        # 执行
        result = await swarm.execute(task)
        
        # 验证
        assert result is not None
        assert result.content is not None
        assert result.execution_time > 0
        assert result.status in [ResultStatus.SUCCESS, ResultStatus.PARTIAL]
        
        # 验证状态更新
        status = swarm.get_status()
        assert status['metrics']['total_tasks'] >= 1
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self):
        """测试并发执行"""
        swarm = SwarmOrchestrator(max_avatars=5)
        
        start_time = time.time()
        
        # 并发执行任务
        tasks = [
            Task(description=f"并发任务-{i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*[
            swarm.execute(task)
            for task in tasks
        ])
        
        total_time = time.time() - start_time
        
        # 并发应该比串行快
        assert len(results) == 5
        assert total_time < 30  # 应该在30秒内完成
        
        # 所有任务都应有结果
        for r in results:
            assert r is not None
            assert r.status in [ResultStatus.SUCCESS, ResultStatus.PARTIAL]


# ═══════════════════════════════════════════════════════════════════════════
# 性能测试
# ═══════════════════════════════════════════════════════════════════════════

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """测试响应时间"""
        swarm = SwarmOrchestrator(max_avatars=5)
        
        task = Task(description="响应时间测试任务")
        
        start = time.time()
        result = await swarm.execute(task)
        elapsed = time.time() - start
        
        # 应该快速响应
        assert elapsed < 10  # 10秒内完成
        assert result.execution_time < 10
    
    @pytest.mark.asyncio
    async def test_throughput(self):
        """测试吞吐量"""
        swarm = SwarmOrchestrator(max_avatars=10)
        
        start = time.time()
        
        # 执行10个任务
        tasks = [Task(description=f"吞吐量测试-{i}") for i in range(10)]
        results = await asyncio.gather(*[swarm.execute(t) for t in tasks])
        
        elapsed = time.time() - start
        throughput = len(results) / elapsed
        
        # 吞吐量应该合理
        assert throughput > 0.5  # 至少每秒0.5个任务


# ═══════════════════════════════════════════════════════════════════════════
# 主函数 (直接运行测试)
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 运行pytest
    import subprocess
    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        capture_output=False
    )
    sys.exit(result.returncode)