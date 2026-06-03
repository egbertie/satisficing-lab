#!/usr/bin/env python3
"""
Entanglement Partner Matching System - 演示脚本
量子纠缠合伙人匹配系统演示
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.entanglement_system import (
    EntanglementMatchingSystem,
    PartnerProfile,
    BiomarkerData,
    QuantumEngine,
    CognitiveAgent,
    EmergentMatcher,
    EmbodiedAnalyzer,
    NarrativeAnalyzer,
    DiversityOptimizer,
    EthicalAligner,
    CognitiveStyle
)
import random
import json
from datetime import datetime

# ANSI颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.HEADER}{'='*60}{Colors.END}\n")

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}▶ {title}{Colors.END}")
    print(f"{Colors.YELLOW}{'─'*50}{Colors.END}")

def print_result(label, value, color=Colors.GREEN):
    print(f"  {Colors.BOLD}{label}:{Colors.END} {color}{value}{Colors.END}")

def demo_quantum_engine():
    """演示量子感知引擎"""
    print_section("Layer 1: 量子化感知引擎演示")
    
    engine = QuantumEngine()
    
    # 创建示例问题
    from core.entanglement_system import QuantumQuestion, WaveFunction
    
    q1 = QuantumQuestion(
        id='risk_attitude',
        text='面对重大决策时，你的风险态度是？',
        dimension='risk'
    )
    
    # 设置叠加态
    q1.wave_function.amplitudes = {
        'conservative': 0.6 + 0.1j,
        'balanced': 0.5 + 0.2j,
        'aggressive': 0.3 - 0.1j
    }
    q1.wave_function.normalize()
    
    engine.register_question(q1)
    
    print("  量子问题: 面对重大决策时，你的风险态度是？")
    print("  初始波函数（叠加态）:")
    for state, amp in q1.wave_function.amplitudes.items():
        prob = abs(amp)**2
        print(f"    |{state}⟩: 概率幅 = {amp:.3f}, 概率 = {prob:.1%}")
    
    # 模拟多次测量
    print("\n  多次测量（坍缩）结果:")
    results = {'conservative': 0, 'balanced': 0, 'aggressive': 0}
    for i in range(10):
        collapsed, certainty = engine.answer_question('risk_attitude')
        results[collapsed] += 1
        indicator = "★" if certainty > 0.7 else "○"
        print(f"    测量 {i+1}: 坍缩为 |{collapsed}⟩ (确定性: {certainty:.1%}) {indicator}")
    
    print("\n  统计分布:")
    for state, count in results.items():
        bar = "█" * count
        print(f"    {state:12} {bar} {count}")

def demo_emergent_matching():
    """演示涌现式匹配"""
    print_section("Layer 2: 涌现式匹配算法演示")
    
    # 创建两个认知风格不同的代理人
    agent_analytical = CognitiveAgent(
        name="分析型创始人",
        cognitive_profile={
            'analytical': 0.8,
            'intuitive': 0.2,
            'risk_tolerance': 0.4,
            'detail_focus': 0.9,
            'decision_speed': 0.4
        }
    )
    
    agent_intuitive = CognitiveAgent(
        name="直觉型创始人",
        cognitive_profile={
            'analytical': 0.3,
            'intuitive': 0.8,
            'risk_tolerance': 0.7,
            'detail_focus': 0.4,
            'decision_speed': 0.8
        }
    )
    
    print(f"  代理人A: {agent_analytical.name}")
    print(f"    - 分析倾向: {agent_analytical.analytical:.0%}")
    print(f"    - 风险容忍: {agent_analytical.risk_tolerance:.0%}")
    
    print(f"\n  代理人B: {agent_intuitive.name}")
    print(f"    - 分析倾向: {agent_intuitive.analytical:.0%}")
    print(f"    - 风险容忍: {agent_intuitive.risk_tolerance:.0%}")
    
    # 模拟合作
    matcher = EmergentMatcher()
    result = matcher.simulate_partnership(agent_analytical, agent_intuitive, n_scenarios=50)
    
    print(f"\n  {Colors.BOLD}模拟结果 (50个场景):{Colors.END}")
    print_result("主导协作模式", result['dominant_mode'], Colors.CYAN)
    print_result("创造性能量", f"{result['creativity_index']:.1%}", Colors.GREEN)
    print_result("系统稳定性", f"{result['stability_score']:.1%}", Colors.GREEN)
    print_result("涌现性指数", f"{result['emergence_score']:.1%}", Colors.YELLOW)
    
    print(f"\n  协作模式分布:")
    for mode, count in result['collaboration_pattern'].items():
        bar = "█" * int(count / 2)
        print(f"    {mode:15} {bar} {count}")
    
    print(f"\n  识别到的吸引子:")
    for i, attractor in enumerate(result['attractors'][:3], 1):
        print(f"    {i}. {attractor['mode']} (强度: {attractor['strength']:.1%})")

def demo_cognitive_diversity():
    """演示认知多样性优化"""
    print_section("Layer 5: 认知多样性优化演示")
    
    optimizer = DiversityOptimizer()
    
    # 定义三种不同风格的认知档案
    profiles = [
        ("技术型创始人", CognitiveStyle(
            analytical=0.8, detail_oriented=0.9,
            risk_tolerance=0.3, independent=0.7
        )),
        ("市场型创始人", CognitiveStyle(
            analytical=0.4, detail_oriented=0.3,
            risk_tolerance=0.8, independent=0.6
        )),
        ("运营型创始人", CognitiveStyle(
            analytical=0.6, detail_oriented=0.7,
            risk_tolerance=0.5, independent=0.5
        ))
    ]
    
    print("  三种认知风格档案:")
    for name, style in profiles:
        print(f"\n  {Colors.BOLD}{name}:{Colors.END}")
        print(f"    分析型: {style.analytical:.0%} | 细节导向: {style.detail_oriented:.0%}")
        print(f"    风险容忍: {style.risk_tolerance:.0%} | 独立性: {style.independent:.0%}")
    
    # 计算配对多样性
    print(f"\n  {Colors.BOLD}配对多样性分析:{Colors.END}")
    
    pairs = [
        ("技术 + 市场", profiles[0][1], profiles[1][1]),
        ("技术 + 运营", profiles[0][1], profiles[2][1]),
        ("市场 + 运营", profiles[1][1], profiles[2][1])
    ]
    
    for name, style_a, style_b in pairs:
        result = optimizer.evaluate_diversity_sweet_spot(style_a, style_b)
        
        status = "✓ 最优区" if not result['in_danger_zone'] else "✗ 危险区"
        color = Colors.GREEN if not result['in_danger_zone'] else Colors.RED
        
        print(f"\n  {Colors.BOLD}{name}:{Colors.END} {color}{status}{Colors.END}")
        print(f"    认知距离: {result['cognitive_distance']:.2f}")
        print(f"    多样性收益: {result['diversity_benefit']:.1%}")
        print(f"    冲突风险: {result['conflict_risk']:.1%}")

def demo_ethical_alignment():
    """演示伦理价值对齐"""
    print_section("Layer 6: 伦理-价值对齐演示")
    
    aligner = EthicalAligner()
    
    # 模拟义利情境测试回答
    choices = [
        {'decision_type': 'yi_first_count'},
        {'decision_type': 'yi_li_balance_count'},
        {'decision_type': 'yi_guides_li_count'},
        {'decision_type': 'yi_first_count'},
        {'decision_type': 'yi_li_balance_count'}
    ]
    
    result = aligner.conduct_yili_scenario_test(choices)
    
    print("  义利情境测试 (5个场景):")
    print(f"\n  {Colors.BOLD}决策模式分布:{Colors.END}")
    for mode, ratio in result['decision_pattern'].items():
        bar = "█" * int(ratio * 20)
        print(f"    {mode:20} {bar} {ratio:.1%}")
    
    print(f"\n  {Colors.BOLD}分析结果:{Colors.END}")
    print_result("主导伦理取向", result['dominant_ethic'], Colors.CYAN)
    print_result("儒商伦理契合度", f"{result['ru_shang_alignment']:.1%}", Colors.GREEN)
    print_result("伦理灵活性", f"{result['ethical_flexibility']:.1%}", Colors.YELLOW)

def demo_full_matching():
    """演示完整匹配流程"""
    print_header("🎯 完整匹配评估演示")
    
    system = EntanglementMatchingSystem()
    
    # 创建两个典型的硬件初创企业家档案
    partner_tech = PartnerProfile(
        name="张伟（技术创始人）",
        id="tech_001",
        cognitive_profile={
            'analytical': 0.85,
            'detail_oriented': 0.9,
            'risk_tolerance': 0.4,
            'independent': 0.7
        },
        narrative_profile={
            'interview': '从小对技术充满热情...',
            'sense_test': '倾向于系统化解决问题'
        },
        ethical_profile={
            'responses': [{'continuity_rating': 0.75}],
            'scenarios': [
                {'decision_type': 'yi_first_count'},
                {'decision_type': 'yi_guides_li_count'}
            ]
        }
    )
    
    partner_biz = PartnerProfile(
        name="李娜（商业创始人）",
        id="biz_001",
        cognitive_profile={
            'analytical': 0.45,
            'detail_oriented': 0.4,
            'risk_tolerance': 0.75,
            'independent': 0.6
        },
        narrative_profile={
            'interview': '在市场一线打拼多年...',
            'sense_test': '倾向于快速抓住机遇'
        },
        ethical_profile={
            'responses': [{'continuity_rating': 0.8}],
            'scenarios': [
                {'decision_type': 'yi_li_balance_count'},
                {'decision_type': 'yi_guides_li_count'}
            ]
        }
    )
    
    print(f"\n  {Colors.BOLD}评估对象:{Colors.END}")
    print(f"    Partner A: {partner_tech.name}")
    print(f"    Partner B: {partner_biz.name}")
    
    print(f"\n  {Colors.YELLOW}正在执行六层深度评估...{Colors.END}")
    
    # 执行匹配
    result = system.comprehensive_match(partner_tech, partner_biz)
    
    # 展示结果
    print(f"\n  {Colors.BOLD}{Colors.GREEN}✓ 评估完成{Colors.END}")
    
    print_header("📊 匹配评估报告")
    
    print_section("综合兼容度")
    score = result['overall_compatibility']
    color = Colors.GREEN if score > 0.7 else (Colors.YELLOW if score > 0.5 else Colors.RED)
    print(f"\n  {Colors.BOLD}综合评分: {color}{score:.1%}{Colors.END}")
    
    # 各层评分
    print_section("六维评估详情")
    layers = result['layer_results']
    
    quantum_score = layers['quantum_perception'].get('entanglement_strength', 0.5)
    print_result("量子纠缠度", f"{quantum_score:.1%}")
    
    emergent_score = layers['emergent_matching'].get('stability_score', 0.5)
    print_result("涌现稳定性", f"{emergent_score:.1%}")
    
    embodied_score = layers['embodied_cognition'].get('embodied_resonance_score', 0.5)
    print_result("身体共鸣", f"{embodied_score:.1%}")
    
    diversity_score = layers['cognitive_diversity'].get('sweet_spot_score', 0.5)
    print_result("多样性匹配", f"{diversity_score:.1%}")
    
    print_section("未来演化预测")
    for timeframe, pred in result['predictions'].items():
        prob = pred['success_probability']
        color = Colors.GREEN if prob > 0.7 else (Colors.YELLOW if prob > 0.5 else Colors.RED)
        print(f"  {Colors.BOLD}{timeframe}:{Colors.END}")
        print(f"    成功率: {color}{prob:.1%}{Colors.END}")
        print(f"    关键挑战: {pred['key_challenge']}")
    
    print_section("优化建议")
    for i, rec in enumerate(result['recommendations'], 1):
        priority_color = Colors.RED if rec['priority'] == 'high' else Colors.YELLOW
        print(f"  {i}. [{priority_color}{rec['priority'].upper()}{Colors.END}] {rec['category']}")
        print(f"     {rec['suggestion']}")

def main():
    """主演示程序"""
    print_header("🔮 Entanglement Partner Matching System V1.1")
    print("  量子纠缠合伙人匹配决策系统 - 演示")
    print(f"  {Colors.GRAY}全球首创 · 神经科学 · 复杂系统 · 量子认知{Colors.END}")
    
    # 运行各层演示
    demo_quantum_engine()
    demo_emergent_matching()
    demo_cognitive_diversity()
    demo_ethical_alignment()
    demo_full_matching()
    
    print_header("演示完成")
    print(f"\n  {Colors.CYAN}了解更多:{Colors.END}")
    print("  - 文档: docs/")
    print("  - UI演示: ui/index.html")
    print("  - API文档: docs/api.md")
    print(f"\n  {Colors.GREEN}追求极致，全球首创，让科学遇见美学。{Colors.END}\n")

if __name__ == '__main__':
    # 添加GRAY颜色
    Colors.GRAY = '\033[90m'
    main()
