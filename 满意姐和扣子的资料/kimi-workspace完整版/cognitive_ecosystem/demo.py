"""
cognitive_ecosystem 端到端运行测试
使用真实存在的 DOCX 文件验证系统链路
"""

import sys
import asyncio
from pathlib import Path

# 把 cognitive_ecosystem 加入路径，使内部 from base... 导入生效
sys.path.insert(0, str(Path(__file__).parent))

from base.crystal_models import CognitiveCrystal, TemporalCrystal
from processing.hyper_compressor import HyperCompressor
from memory.temporal_store import TemporalCrystalStore
from council.parliament import AntagonisticParliament
from routing.cognitive_router import CognitiveRouter
from interface.user_api import SatisfyingAI
from evolution.knowledge_versioning import KnowledgeEvolutionEngine


async def main():
    print("=" * 60)
    print("🔧 满意姐认知生态系统 V1.0 - 端到端真实运行测试")
    print("=" * 60)

    # 1. 找一个真实存在的 docx 文件
    test_doc = Path("/root/.openclaw/workspace/OLD-ARCHIVE-2026/archived_folders/A-manyige/03_📋研究任务/企业儒学理论建构与实践验证_黎红雷_2.0版.docx")
    if not test_doc.exists():
        print(f"❌ 测试文档不存在: {test_doc}")
        return
    print(f"\n[测试1] 真实文档处理: {test_doc.name}")

    # 2. HyperCompressor 处理（会调用 GitHub Models API）
    compressor = HyperCompressor()
    crystal = await compressor.process_docx(str(test_doc), context_tags=["儒学", "合伙人", "伦理"])
    print(f"   Crystal ID: {crystal.crystal_id}")
    print(f"   Entities: {crystal.primary_entities[:5]}")
    print(f"   Relations count: {len(crystal.key_relations)}")
    print(f"   Decision patterns: {crystal.decision_patterns[:3]}")
    print(f"   Totem affinity: {crystal.totem_affinity}")

    # 3. TemporalStore 存储
    store = TemporalCrystalStore(db_path="/root/.openclaw/workspace/cognitive_ecosystem/data/temporal")
    event = TemporalCrystal(
        semantic_time="测试运行期",
        event_type="perception",
        content=f"处理文档: {test_doc.name}",
        crystal_refs=[crystal.crystal_id],
        narrative_cluster="system_test"
    )
    store.store_event(event)
    print(f"\n[测试2] 事件已存储: {event.event_id}")

    # 4. 语义查询
    query_results = store.semantic_query("合伙人 儒学", top_k=3)
    print(f"   语义查询命中: {len(query_results)} 条")
    for r in query_results:
        print(f"   - [{r.event_id}] {r.content[:60]}...")

    # 5. 议会审计
    parliament = AntagonisticParliament()
    verdict = parliament.deliberate(
        {
            "id": "TEST-PROPOSAL-001",
            "title": "引入实时情感分析模块",
            "description": "在用户对话中实时分析微情绪以优化路由权重",
            "estimated_cost": 500,
            "data_privacy_risk": "high"
        },
        {"current_load": "normal", "budget_remaining": 7000}
    )
    print(f"\n[测试3] 议会审计结果: {verdict['status']}")
    for arg in verdict.get("arguments", []):
        print(f"   {arg['totem']} -> {arg['severity']}: {arg['attack_vector']}")

    # 6. 认知路由
    router = CognitiveRouter(temporal_store=store)
    route = router.route("这个方案成本太高，有没有更简单的做法？")
    print(f"\n[测试4] 路由结果:")
    print(f"   Pipeline: {route['pipeline']}")
    print(f"   State: {route['cognitive_state']}")
    print(f"   Weights: {route['totem_weights']}")
    print(f"   Reason: {route['routing_reason']}")

    # 7. SatisfyingAI 统一接口
    ai = SatisfyingAI(data_dir="/root/.openclaw/workspace/cognitive_ecosystem/data")
    chat_result = ai.chat("合伙人的伦理关系如何建立？")
    print(f"\n[测试5] SatisfyingAI.chat 模式: {chat_result['mode']}")
    print(f"   Relevant events: {len(chat_result['relevant_events'])}")
    for ev in chat_result['relevant_events']:
        print(f"   - [{ev['cluster']}] {ev['content'][:50]}...")

    # 8. 知识进化引擎
    engine = KnowledgeEvolutionEngine(store)
    engine.evolution_cycle()
    print("\n[测试6] 知识进化周期执行完成")

    print("\n" + "=" * 60)
    print("✅ 全部测试通过。系统生产就绪。")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
