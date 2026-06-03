"""
认知生态系统 v1.0 端到端验证脚本
使用真实DOCX文件，跑通全部 Pipeline
"""

import sys
import os
import asyncio
from pathlib import Path

# 确保 workspace 在路径中
sys.path.insert(0, str(Path(__file__).parent))

from interface.user_api import SatisfyingAI


async def main():
    print("=" * 60)
    print("🔧 认知生态系统 v1.0 - 端到端验证")
    print("=" * 60)

    # 使用真实的 docx 文件
    test_docx = Path(
        "/root/.openclaw/workspace/OLD-ARCHIVE-2026/archived_folders/.kimi/downloads/"
        "19d4cd4c-fe42-8b31-8000-000095b952b1_222天1夜_睡个好觉_体验营_活动方案.docx"
    )

    if not test_docx.exists():
        print(f"❌ 测试文件不存在: {test_docx}")
        sys.exit(1)

    print(f"\n[1] 初始化 SatisfyingAI...")
    ai = SatisfyingAI(data_dir="./cognitive_ecosystem/data")
    print(f"     状态: {ai.get_status()['system_health']}")

    print(f"\n[2] 知识摄入: {test_docx.name}")
    try:
        ingest_result = await ai.ingest(str(test_docx), priority=2)
        print(f"     Crystal ID: {ingest_result['crystal_id']}")
        print(f"     压缩比: {ingest_result['compression_ratio']:.3f}")
        print(f"     审计状态: {ingest_result['audit_status']}")
        if ingest_result['contradictions']:
            print(f"     ⚠️ 矛盾标记: {ingest_result['contradictions']}")
    except Exception as e:
        print(f"     ❌ 摄入失败: {e}")

    print("\n[3] 路由查询测试")
    queries = [
        "如何优化睡眠质量？",  # routine
        "这是一个高风险方案，可能失败",  # crisis
        "我们想要突破性的新方案",  # exploration
    ]
    for q in queries:
        result = ai.chat(q)
        route = result["route"]
        print(f"     Q: {q}")
        print(f"     -> 状态: {route['cognitive_state']} | 管道: {route['pipeline']} | {route['routing_reason']}")

    print("\n[4] 议会主动审计测试")
    proposal = {
        "id": "TEST-001",
        "title": "引入外部图数据库 Neo4j",
        "description": "将所有认知晶体迁移到Neo4j",
        "action": "infrastructure_change",
        "risk_level": "medium"
    }
    verdict = ai.audit_proposal(proposal)
    print(f"     审计结果: {verdict['status']}")
    for arg in verdict.get("arguments", [])[:2]:
        print(f"     - [{arg['totem']}] {arg['severity']}: {arg['attack_vector']}")

    print("\n[5] 语义事件检索")
    for q in ["文档入库", "睡眠"]:
        events = ai.store.semantic_query(q, top_k=3)
        print(f"     查询 '{q}' 检索到 {len(events)} 个相关事件")
        for e in events:
            print(f"     - [{e.semantic_time}] {e.content[:60]}...")

    print("\n" + "=" * 60)
    print("✅ 端到端验证完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
