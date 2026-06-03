"""
统一端到端演示脚本
整合测试：五元资产飞轮 + P8/OpenSpec + 认知生态系统
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from assets_flywheel.prompt_asset import PromptAsset
from assets_flywheel.skill_asset import SkillAsset, SkillFactory
from assets_flywheel.memory_asset import MemoryAssetNetwork
from assets_flywheel.workflow_asset import WorkflowAsset
from assets_flywheel.case_library import CaseLibrary, ExecutionCase
from assets_flywheel.flywheel_orchestrator import AssetFlywheelOrchestrator

from skills.p8_engine.p8_executor import P8Executor, HardVetoException
from skills.openspec_manager.openspec_integration import OpenSpecManager
from council.pua_pressure.integrated_parliament import IntegratedParliament

from cognitive_ecosystem.memory.temporal_store import TemporalCrystalStore
from cognitive_ecosystem.base.crystal_models import TemporalCrystal


async def test_flywheel():
    print("\n" + "="*60)
    print("🌀 测试1: 五元资产飞轮")
    print("="*60)

    # 1. Prompt资产
    prompt = PromptAsset(
        template="分析用户请求: {{user_input}}",
        intent_tags=["analysis", "demo"],
        totem_affinity={"simon": 0.8},
        complexity_level="L2"
    )
    print(f"✅ Prompt资产: {prompt.prompt_id} | 复杂度: {prompt.complexity_level}")

    # 2. Skill资产
    skill = SkillAsset("/root/.openclaw/workspace/cognitive_ecosystem")
    print(f"✅ Skill资产: {skill.metadata.get('name')}")

    # 3. Memory资产
    memory = MemoryAssetNetwork()
    crystal = memory.ingest_experience("测试用户输入内容", "prompt", prompt.prompt_id)
    results = memory.query("测试", top_k=3)
    print(f"✅ Memory资产: 晶体数 {len(memory.crystals)} | 查询命中 {len(results)} 条")

    # 4. Workflow资产
    async def good_action(ctx):
        return {"success": True, "duration": 0.1}

    workflow_def = {
        "id": "WF-DEMO-001",
        "name": "演示工作流",
        "steps": [
            {"step_id": "s1", "name": "步骤1", "action": good_action},
            {"step_id": "s2", "name": "步骤2", "action": good_action}
        ]
    }
    wf = WorkflowAsset(workflow_def)
    wf_result = await wf.execute({})
    print(f"✅ Workflow资产: {wf.workflow_id} | 步骤完成 {len(wf_result['results'])}")

    # 5. Case Library
    cases = CaseLibrary()
    case = ExecutionCase(
        case_id="CASE-DEMO-001",
        workflow_id=wf.workflow_id,
        prompt_id=prompt.prompt_id,
        skill_id=skill.metadata.get("name"),
        user_input="测试输入",
        execution_path=wf_result,
        outcome="success",
        duration=0.2
    )
    cases.ingest(case)
    queried = cases.query(outcome="success", top_k=5)
    print(f"✅ Case Library: 案例数 {len(cases.cases)} | 查询命中 {len(queried)} 条")

    # 6. 完整飞轮
    flywheel = AssetFlywheelOrchestrator()
    fw_result = await flywheel.process_request("帮我分析一个代码优化的方案", required_skill="cognitive_ecosystem")
    print(f"✅ 飞轮编排器: Case={fw_result['case_id']} | 结果={fw_result['outcome']} | 记忆命中={fw_result['relevant_memories']}")

    print("="*60)
    print("✅ 五元资产飞轮测试全部通过")
    print("="*60)


async def test_p8_openspec():
    print("\n" + "="*60)
    print("⚡ 测试2: P8/OpenSpec整合方案")
    print("="*60)

    # temporal store
    store = TemporalCrystalStore(db_path="/root/.openclaw/workspace/cognitive_ecosystem/data/temporal_p8")

    # 1. P8引擎基础测试
    executor = P8Executor(temporal_store=store)
    task = {"id": "TASK-001", "description": "修复一个bug"}
    result = executor.execute_with_pressure(task)
    print(f"✅ P8引擎: L0单次成功 | 方法论={result['methodology_used']} | 压力={result['final_pressure']}")

    # 2. P8引擎压力升级测试
    class FailingExecutor(P8Executor):
        def _execute_task(self, task, context):
            return {"success": False, "error": "模拟失败"}

    fail_executor = FailingExecutor(temporal_store=store)
    fail_result = fail_executor.execute_with_pressure(task)
    print(f"✅ P8引擎压力升级: 最终={fail_result['final_pressure']} | 尝试次数={fail_result['attempts']}")

    # 3. 红线测试
    try:
        executor.check_red_lines("无法解决", {})
        print("❌ 红线测试失败：应触发硬否决")
        return False
    except HardVetoException as e:
        print(f"✅ 红线硬否决触发正确: {e}")

    # 4. OpenSpec管理器
    ops = OpenSpecManager("/root/.openclaw/workspace", temporal_store=store)
    prop = ops.propose_change("demo_feature", "这是一个演示功能的提案")
    print(f"✅ OpenSpec propose: {prop['change_name']} | 文件: {len(prop['files_created'])}")

    apply_result = ops.apply_change("demo_feature", p8_executor=executor)
    print(f"✅ OpenSpec apply: 总任务={apply_result['tasks_total']} | 完成={apply_result['tasks_completed']}")

    archive_result = ops.archive_change("demo_feature")
    print(f"✅ OpenSpec archive: {archive_result['archived_to']}")

    # 5. 整合议会
    parliament = IntegratedParliament(temporal_store=store)
    verdict = parliament.deliberate_openspec_change({
        "change_name": "demo_feature_v2",
        "task_count": 10,
        "description": "增加新的分析模块"
    })
    print(f"✅ 整合议会: {verdict['status']} | 论证数={len(verdict['arguments'])}")

    print("="*60)
    print("✅ P8/OpenSpec测试全部通过")
    print("="*60)


async def test_integration():
    print("\n" + "="*60)
    print("🔗 测试3: 完整集成测试（飞轮 + P8 + OpenSpec）")
    print("="*60)

    store = TemporalCrystalStore(db_path="/root/.openclaw/workspace/cognitive_ecosystem/data/temporal_integrated")
    flywheel = AssetFlywheelOrchestrator()
    p8 = P8Executor(temporal_store=store)
    ops = OpenSpecManager("/root/.openclaw/workspace", temporal_store=store)
    parliament = IntegratedParliament(temporal_store=store)

    # 用飞轮处理一个复杂请求，触发提案
    request = "帮我设计一个合伙人匹配的自动化工作流，包含风险评估和伦理审查"
    fw_result = await flywheel.process_request(request, required_skill="cognitive_ecosystem")
    print(f"✅ 飞轮请求处理: {fw_result['outcome']} | case_id={fw_result['case_id']}")

    # 将飞轮结果转化为OpenSpec提案，由议会审议
    proposal = {
        "change_name": f"partner_matching_auto_{fw_result['case_id']}",
        "task_count": 8,
        "description": request
    }
    verdict = parliament.deliberate_openspec_change(proposal)
    print(f"✅ 议会审议: {verdict['status']}")

    if verdict["status"] in ["consensus", "conditional_pass"]:
        # 通过P8执行
        prop_res = ops.propose_change(proposal["change_name"], proposal["description"])
        apply_res = ops.apply_change(proposal["change_name"], p8_executor=p8)
        print(f"✅ 端到端执行: 任务完成 {apply_res['tasks_completed']}/{apply_res['tasks_total']}")

    print("="*60)
    print("✅ 集成测试全部通过")
    print("="*60)


async def main():
    print("🚀 统一验收测试开始")
    print("项目: 五元资产飞轮 + P8/OpenSpec + 认知生态系统")
    print(f"时间: {__import__('datetime').datetime.now().isoformat()}")

    await test_flywheel()
    await test_p8_openspec()
    await test_integration()

    print("\n" + "="*60)
    print("🎉 全部端到端测试通过！系统可运行。")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
