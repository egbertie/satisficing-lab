#!/usr/bin/env python3
"""
Digital-Avatar-Swarm 快速演示
运行: python3 demo.py
"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from avatar_swarm import SwarmOrchestrator, Task, SwarmTester


async def main():
    print("=" * 70)
    print("  Digital-Avatar-Swarm (数字人蜂群) - 快速演示")
    print("=" * 70)
    print()
    
    # 初始化蜂群
    print("🚀 初始化蜂群 (5个数字人代理)...")
    swarm = SwarmOrchestrator(
        max_avatars=5,
        token_budget=50000,
        timeout=300
    )
    print("   ✓ 蜂群初始化完成\n")
    
    # 显示初始状态
    print("📊 初始状态:")
    status = swarm.get_status()
    ss = status['swarm_status']
    print(f"   总代理数: {ss['total_avatars']}")
    print(f"   空闲代理: {ss['idle_avatars']}")
    print(f"   Token预算: {status['metrics']['token_budget_remaining']:,}")
    print()
    
    # 执行复杂任务
    print("📝 执行复杂分析任务...")
    print("   任务: 分析AI Agent市场竞争格局")
    print()
    
    task = Task(
        description="""分析当前AI Agent市场的竞争格局，评估主要玩家如AutoGPT、MetaGPT、LangChain等
        的技术特点、商业模式和市场定位，对比它们的优势和劣势，并给出投资建议""",
        context={
            'market': 'AI Agent',
            'focus': 'competitive_analysis',
            'players': ['AutoGPT', 'MetaGPT', 'LangChain']
        },
        priority=8
    )
    
    result = await swarm.execute(task)
    
    print(f"   ✓ 任务完成!")
    print(f"   状态: {result.status.name}")
    print(f"   执行时间: {result.execution_time:.2f}秒")
    print(f"   置信度: {result.confidence:.1%}")
    print(f"   Token消耗: {result.token_used:,}")
    print()
    
    # 显示结果预览
    print("📄 结果预览:")
    print("-" * 70)
    preview = result.content[:800] + "..." if len(result.content) > 800 else result.content
    print(preview)
    print("-" * 70)
    print()
    
    # 显示执行后状态
    print("📊 执行后状态:")
    status = swarm.get_status()
    m = status['metrics']
    print(f"   总任务数: {m['total_tasks']}")
    print(f"   成功任务: {m['completed_tasks']}")
    print(f"   成功率: {m['success_rate']}")
    print(f"   平均执行时间: {m['avg_execution_time']}")
    print(f"   Token已消耗: {m['token_consumed']:,}")
    print()
    
    # 代理详情
    print("🤖 代理详情:")
    for avatar in status['avatars'][:3]:  # 只显示前3个
        print(f"   {avatar['name']} ({avatar['id']}):")
        print(f"      状态: {avatar['status']}")
        print(f"      成功率: {avatar['success_rate']}")
        print(f"      平均响应: {avatar['avg_response_time']}")
        print(f"      健康: {avatar['health']}")
    print()
    
    # 运行对抗测试
    print("🧪 运行对抗测试...")
    tester = SwarmTester(swarm)
    
    await tester.test_high_load()
    
    report = tester.get_test_report()
    summary = report['summary']
    print(f"   测试总数: {summary['total_tests']}")
    print(f"   通过: {summary['passed']}")
    print(f"   失败: {summary['failed']}")
    print(f"   通过率: {summary['pass_rate']}")
    print()
    
    print("=" * 70)
    print("  演示完成! 🎉")
    print("=" * 70)
    print()
    print("更多信息请查看:")
    print("  - SKILL.md: 完整文档")
    print("  - 5standard-completion-report.md: 5标准化完成报告")
    print("  - tests/test_swarm.py: 测试用例")


if __name__ == "__main__":
    asyncio.run(main())
