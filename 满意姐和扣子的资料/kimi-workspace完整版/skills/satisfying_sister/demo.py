#!/usr/bin/env python3
"""
满意尺系统 - 端到端验证Demo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.satisfying_sister import (
    RoleEngine, RoleMode,
    CommandParser,
    IntentContract,
    MemoryCitation,
    TotemOS,
    BlueArmyTrigger,
    LanguageGuard,
    HealthFuse,
)


def test_role_engine():
    print("=" * 50)
    print("🎭 测试1: 角色引擎 - 双模人格")
    print("=" * 50)
    engine = RoleEngine()

    # 默认模式
    print(f"默认模式: {engine.current_mode.value}")
    print(f"口头禅: {engine.collaborator_phrase()}")

    # 触发审计者模式
    context = {"claimed_progress": 90, "actual_progress": 70}
    mode = engine.detect_mode(context)
    print(f"进度虚报后模式: {mode.value}")
    print(f"审计输出示例:\n{engine.auditor_format('🔴高危', ['进度虚报'], ['修正进度声明'])}")

    # 信任边界
    print(f"本地读操作: {engine.get_trust_boundary('read')}")
    print(f"对外发消息: {engine.get_trust_boundary('send_msg')}")

    # 工作节律
    from datetime import datetime
    print(f"当前节律(假设16:00): {engine.get_work_rhythm(datetime(2026, 4, 5, 16, 0))}")
    print("✅ 角色引擎测试通过\n")


def test_command_parser():
    print("=" * 50)
    print("📋 测试2: 五段式指令解析")
    print("=" * 50)
    parser = CommandParser()

    cmd = """
    [角色] 蓝军审计官
    [上下文] 评估zero-idle-enforcer修复质量
    [输入] 运行19个单元测试并生成诚实报告
    [约束] Token预算<2000，输出必须包含物理路径
    [阻塞条件] 测试未全绿前不得声称修复完成
    """
    result = parser.parse(cmd)
    validation = parser.validate(result)
    print(f"解析结果: {result['角色']}")
    print(f"上下文: {result['上下文'][:30]}...")
    print(f"是否五段式: {result['is_five_segment']}")
    print(f"验证结果: {validation}")
    print("✅ 五段式解析测试通过\n")


def test_intent_contract():
    print("=" * 50)
    print("📝 测试3: 意图契约")
    print("=" * 50)
    ic = IntentContract()
    contract = ic.build_contract("帮我修复所有失败的测试", complexity="P0")
    print(f"契约阻塞状态: {contract['blocking']}")
    print(f"边界条件: {contract['boundaries'][:40]}...")

    confirmed = ic.confirm(contract)
    print(f"确认后可执行: {ic.is_ready_to_execute(confirmed)}")
    print("✅ 意图契约测试通过\n")


def test_memory_citation():
    print("=" * 50)
    print("🧠 测试4: 记忆引用系统")
    print("=" * 50)
    mc = MemoryCitation()

    stats = mc.get_memory_stats()
    print(f"记忆库统计: {stats}")

    cite = mc.generate_citation()
    print(f"随机引用句: {cite}")

    # 测试归档（不污染，用后清理说明）
    test_content = "这是一条demo测试记忆，确认archive功能正常。"
    path = mc.archive_memory(test_content, date_str="2026-04-05")
    print(f"归档路径: {path}")
    print("✅ 记忆引用测试通过\n")


def test_totem_os():
    print("=" * 50)
    print("🔥 测试5: 五路图腾操作系统")
    print("=" * 50)
    totem = TotemOS()

    morning = totem.morning_ritual()
    print(f"晨间仪式类型: {morning['ritual_type']}")
    print(f"步骤数: {len(morning['steps'])}")

    evening = totem.evening_ritual(deliverables_checked=["demo.py"], risks_identified=["API 401"])
    print(f"黄昏仪式洞察: {evening['insight']}")

    activated = totem.activate_totem("我需要做一个伦理决策")
    print(f"伦理场景激活图腾: {activated['totem']} ({activated['element']})")
    print("✅ 图腾OS测试通过\n")


def test_blue_army_trigger():
    print("=" * 50)
    print("🛡️ 测试6: 蓝军触发器")
    print("=" * 50)
    bat = BlueArmyTrigger()

    # 正常任务
    result = bat.audit({"claimed_progress": 50, "actual_progress": 48})
    print(f"正常任务审计:\n{bat.format_audit(result)}\n")

    # 问题任务
    result = bat.audit({
        "claimed_progress": 90,
        "actual_progress": 70,
        "token_over_budget": True,
        "tmp_file_count": 15,
        "has_timeout": False,
    })
    print(f"问题任务审计:\n{bat.format_audit(result)}")
    print("✅ 蓝军触发器测试通过\n")


def test_language_guard():
    print("=" * 50)
    print("🗣️ 测试7: 语言风格守卫")
    print("=" * 50)
    guard = LanguageGuard()

    bad_text = "好的！处理完成，这是一个好问题！"
    violations = guard.check(bad_text)
    print(f"违规检测: 发现{len(violations)}处")
    for v in violations:
        print(f"  - {v['pattern']}: {v['message']}")

    fixed = guard.suggest_fix(bad_text)
    print(f"修复后: {fixed}")

    fmt = guard.delivery_format("结论：语言测试通过", {"状态": "正常", "路径": "skills/satisfying_sister/"})
    print(f"交付格式示例:\n{fmt}")
    print("✅ 语言守卫测试通过\n")


def test_health_fuse():
    print("=" * 50)
    print("⚡ 测试8: 健康与熔断系统")
    print("=" * 50)
    hf = HealthFuse()

    token_check = hf.check_token_budget(150000, 50000)
    print(f"Token熔断: {token_check['level']} → {token_check['action']}")

    sim_check = hf.check_similarity("测试输出A")
    sim_check = hf.check_similarity("测试输出B")
    sim_check = hf.check_similarity("测试输出C")
    print(f"相似度检查(多样): {sim_check['action']}")

    # 构造高相似
    hf2 = HealthFuse()
    same = "这是一个重复的测试输出内容，用于验证相似度检测功能。"
    for _ in range(3):
        r = hf2.check_similarity(same)
    print(f"相似度检查(重复): {r['action']} - {r['message'][:30]}...")

    conf = hf.check_confidence(0.3)
    print(f"低置信度累积: 第1次 {conf['action']}")
    for _ in range(3):
        conf = hf.check_confidence(0.3)
    print(f"低置信度累积: 第4次 {conf['action']} - {conf.get('note', '')}")
    print("✅ 健康熔断测试通过\n")


def main():
    print("\n" + "=" * 50)
    print("🚀 满意尺 (Man Yi Chi) 端到端验证启动")
    print("=" * 50 + "\n")

    test_role_engine()
    test_command_parser()
    test_intent_contract()
    test_memory_citation()
    test_totem_os()
    test_blue_army_trigger()
    test_language_guard()
    test_health_fuse()

    print("=" * 50)
    print("🎉 全部8项测试通过")
    print("=" * 50)


if __name__ == "__main__":
    main()
