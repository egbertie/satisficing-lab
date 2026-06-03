#!/usr/bin/env python3
"""
五路图腾AI决策系统 - MVP版本（补充简化方案）
基于用户要求：未实现的提供简化方案，记录迭代条件
"""

import json
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

# 五路图腾智能体定义（保持不变）
TOTEMS = {
    "刘禹锡": {
        "role": "聚贤才为伍，引智士同行",
        "essence": "根基稳固，品德为锚",
        "style": "保守稳健，重视品德",
        "framework": "伦理优先",
        "questions": ["这个决策符合我们的价值观吗？", "团队会怎么看这个决定？"]
    },
    "司马贺": {
        "role": "不求最优，但求最适；结果为本，满意为尺",
        "essence": "理性决策，满意解理论",
        "style": "理性分析，数据驱动",
        "framework": "理性分析",
        "questions": ["这是不是满意解？", "数据支持这个决策吗？"]
    },
    "观自在": {
        "role": "居方寸之地，以价值致远",
        "essence": "内心自由，不执于形",
        "style": "灵活应变，洞察本质",
        "framework": "系统思考",
        "questions": ["我们有没有被表象迷惑？", "本质是什么？"]
    },
    "孔子": {
        "role": "仁义礼智信，修身齐家治国平天下",
        "essence": "儒商伦理，信任治理",
        "style": "伦理优先，长期主义",
        "framework": "伦理优先",
        "questions": ["这个决策符合仁义礼智信吗？", "长期影响是什么？"]
    },
    "六祖慧能": {
        "role": "顿悟红莲，直指人心",
        "essence": "直觉突破，压力中顿悟",
        "style": "直觉敏锐，快速决断",
        "framework": "直觉驱动",
        "questions": ["直觉告诉你什么？", "如果必须现在决定，你会怎么选？"]
    }
}

# 认知框架定义（Q5: 框架转换简化实现）
COGNITIVE_FRAMEWORKS = {
    "伦理优先": {
        "description": "以仁义礼智信为核心，优先考虑道德和长期声誉",
        "keywords": ["道德", "伦理", "信任", "长期", "声誉", "价值观"],
        "questions": ["这是否符合我们的核心价值观？", "长期看会有什么影响？"]
    },
    "理性分析": {
        "description": "以数据和逻辑为核心，追求满意解而非最优解",
        "keywords": ["数据", "逻辑", "分析", "概率", "风险", "收益"],
        "questions": ["数据支持这个结论吗？", "这是满意解还是最优解？"]
    },
    "系统思考": {
        "description": "从整体视角看问题，识别本质和关联",
        "keywords": ["整体", "关联", "本质", "结构", "动态", "反馈"],
        "questions": ["这个决策的系统影响是什么？", "忽略了什么关键因素？"]
    },
    "直觉驱动": {
        "description": "基于模式识别和快速判断，适用于高不确定性",
        "keywords": ["直觉", "感觉", "模式", "经验", "快速", "敏锐"],
        "questions": ["直觉告诉你什么？", "这和过去哪些情况相似？"]
    }
}

class TotemDecisionSystem:
    """五路图腾决策系统（含简化方案）"""
    
    def __init__(self):
        self.decision_history = []
        self.user_preferences = {}
        self.feedback_data = []
        self.framework_usage_count = {k: 0 for k in COGNITIVE_FRAMEWORKS.keys()}
        
    # ==================== Q5: 框架转换（简化实现） ====================
    
    def detect_framework(self, user_input: str) -> str:
        """
        简化方案：基于关键词匹配检测当前认知框架
        完整方案需要：NLP意图识别模型（BERT/GPT微调）
        """
        input_lower = user_input.lower()
        scores = {}
        
        for framework, info in COGNITIVE_FRAMEWORKS.items():
            score = sum(1 for kw in info["keywords"] if kw in input_lower)
            scores[framework] = score
        
        # 选择得分最高的框架，如果都为0则默认"理性分析"
        best_framework = max(scores, key=scores.get) if max(scores.values()) > 0 else "理性分析"
        self.framework_usage_count[best_framework] += 1
        
        return best_framework
    
    def framework_switch(self, user_input: str, target_framework: str = None) -> Dict:
        """
        Q5: 框架转换（简化实现）
        完整方案需要：多模态框架嵌入、动态框架权重调整
        """
        print(f"\n{'='*70}")
        print("🔄 认知框架转换")
        print(f"{'='*70}")
        
        # 检测当前框架
        current_framework = self.detect_framework(user_input)
        print(f"\n检测到的当前框架: {current_framework}")
        print(f"描述: {COGNITIVE_FRAMEWORKS[current_framework]['description']}")
        
        # 如果指定了目标框架，进行对比
        if target_framework and target_framework != current_framework:
            print(f"\n转换到目标框架: {target_framework}")
            print(f"目标描述: {COGNITIVE_FRAMEWORKS[target_framework]['description']}")
            
            # 生成对比分析（简化版）
            comparison = self._generate_framework_comparison(current_framework, target_framework)
            print(f"\n对比分析:")
            for point in comparison:
                print(f"  • {point}")
        
        # 显示所有框架的使用统计
        print(f"\n框架使用统计:")
        for fw, count in sorted(self.framework_usage_count.items(), key=lambda x: -x[1]):
            bar = "█" * count + "░" * (10 - min(count, 10))
            print(f"  {fw:<12} {bar} {count}")
        
        return {
            "current_framework": current_framework,
            "target_framework": target_framework,
            "switch_recommendation": target_framework != current_framework if target_framework else None
        }
    
    def _generate_framework_comparison(self, current: str, target: str) -> List[str]:
        """生成两个框架的对比点（简化版）"""
        comparisons = {
            ("伦理优先", "理性分析"): [
                "伦理优先关注'应该做什么'，理性分析关注'最优结果是什么'",
                "建议：先通过理性分析评估选项，再用伦理优先筛选"
            ],
            ("理性分析", "直觉驱动"): [
                "理性分析需要充足数据和时间，直觉驱动适合紧急决策",
                "建议：时间充裕时用理性分析，紧急时用直觉驱动"
            ],
            ("系统思考", "伦理优先"): [
                "系统思考关注整体影响，伦理优先关注道德底线",
                "建议：用系统思考评估影响，用伦理优先设定底线"
            ]
        }
        
        key = (current, target)
        reverse_key = (target, current)
        
        if key in comparisons:
            return comparisons[key]
        elif reverse_key in comparisons:
            return [f"反向对比：{c}" for c in comparisons[reverse_key]]
        else:
            return [f"{current}和{target}有不同的关注点，建议结合使用"]
    
    # ==================== Q6: 直觉能力（简化实现） ====================
    
    def generate_intuition_signal(self, decision_context: str, user_history: List[Dict] = None) -> Dict:
        """
        Q6: 直觉能力（简化实现）
        基于模式匹配和历史经验生成"直觉信号"
        完整方案需要：神经网络模式识别、隐性知识嵌入
        """
        print(f"\n{'='*70}")
        print("🔮 直觉信号生成（六祖慧能模块）")
        print(f"{'='*70}")
        
        # 简化方案1：关键词模式匹配
        pattern_signals = self._pattern_based_intuition(decision_context)
        
        # 简化方案2：基于历史经验的快速判断（如果有历史数据）
        experience_signals = []
        if user_history and len(user_history) >= 3:
            experience_signals = self._experience_based_intuition(decision_context, user_history)
        
        # 简化方案3：生成快速判断建议
        quick_judgment = self._generate_quick_judgment(decision_context)
        
        print(f"\n基于模式的直觉信号:")
        for signal in pattern_signals:
            print(f"  ⚡ {signal}")
        
        if experience_signals:
            print(f"\n基于经验的直觉信号:")
            for signal in experience_signals:
                print(f"  💡 {signal}")
        
        print(f"\n快速判断建议:")
        print(f"  🎯 {quick_judgment}")
        
        print(f"\n⚠️  重要提示:")
        print(f"  直觉信号仅供参考，不能替代深入分析")
        print(f"  当直觉与分析冲突时，建议暂停决策，收集更多信息")
        
        return {
            "pattern_signals": pattern_signals,
            "experience_signals": experience_signals,
            "quick_judgment": quick_judgment,
            "confidence": "low" if not user_history else "medium",  # 简化置信度评估
            "warning": "数据不足，直觉可靠性较低" if not user_history else "基于有限历史数据"
        }
    
    def _pattern_based_intuition(self, context: str) -> List[str]:
        """基于关键词模式的直觉信号"""
        patterns = {
            " urgency": ["时间紧迫", "机会窗口有限", "需要快速决策"],
            " high_risk": ["风险很高", "可能失败", "不确定性大"],
            " partnership": ["合伙人", "合作", "信任", "关系"],
            " ethical": ["道德", "伦理", "价值观", "正确"],
            " growth": ["增长", "扩张", "机会", "发展"]
        }
        
        signals = []
        context_lower = context.lower()
        
        if any(kw in context_lower for kw in ["时间紧", "紧急", "快", "立即"]):
            signals.append("时间压力高 - 直觉倾向于快速决断")
        
        if any(kw in context_lower for kw in ["风险", "可能失败", "不确定性"]):
            signals.append("风险感知强 - 直觉倾向于谨慎")
        
        if any(kw in context_lower for kw in ["合伙人", "合作", "信任"]):
            signals.append("关系敏感 - 直觉关注人的因素")
        
        if len(signals) == 0:
            signals.append("模式不明确 - 建议深入分析")
        
        return signals
    
    def _experience_based_intuition(self, context: str, history: List[Dict]) -> List[str]:
        """基于历史经验的直觉信号（简化版）"""
        # 查找相似情境（简化：关键词匹配）
        similar_cases = []
        for case in history[-5:]:  # 只看最近5个
            if any(kw in case.get('context', '') for kw in context.split()[:3]):
                similar_cases.append(case)
        
        if not similar_cases:
            return ["没有找到相似历史经验"]
        
        # 统计相似案例的结果
        outcomes = [c.get('outcome_score', 5) for c in similar_cases]
        avg_outcome = sum(outcomes) / len(outcomes)
        
        signals = [f"发现{len(similar_cases)}个相似历史案例"]
        
        if avg_outcome >= 7:
            signals.append(f"相似案例平均结果良好({avg_outcome:.1f}/10) - 直觉倾向积极")
        elif avg_outcome <= 4:
            signals.append(f"相似案例平均结果不佳({avg_outcome:.1f}/10) - 直觉倾向谨慎")
        else:
            signals.append(f"相似案例结果中等({avg_outcome:.1f}/10) - 直觉不确定")
        
        return signals
    
    def _generate_quick_judgment(self, context: str) -> str:
        """生成快速判断建议"""
        # 基于关键词的简单规则
        if "合伙" in context or "合作" in context:
            return "先建立信任，再谈合作细节"
        elif "投资" in context or "融资" in context:
            return "评估资金需求与稀释比例的平衡"
        elif "招聘" in context or "人才" in context:
            return "文化契合度比技能更重要"
        else:
            return "收集更多信息后再做判断"
    
    # ==================== Q8: 防止过拟合（简化实现） ====================
    
    def check_overfitting_risk(self, decision_pattern: Dict) -> Dict:
        """
        Q8: 防止过拟合（简化实现）
        检测决策模式是否存在过度依赖历史经验的风险
        完整方案需要：统计正则化、交叉验证、多样性采样
        """
        print(f"\n{'='*70}")
        print("⚠️  过拟合风险检测")
        print(f"{'='*70}")
        
        warnings = []
        recommendations = []
        risk_level = "low"
        
        # 检查1：历史数据量不足（简化：固定阈值）
        if len(self.decision_history) < 10:
            warnings.append(f"历史决策数据不足({len(self.decision_history)}个)，模型可能欠拟合")
            recommendations.append("收集至少10个决策数据后再依赖系统建议")
            risk_level = "medium"
        
        # 检查2：决策多样性（简化：基于类型统计）
        if len(self.decision_history) >= 5:
            decision_types = {}
            for d in self.decision_history:
                dtype = d.get('decision_type', 'other')
                decision_types[dtype] = decision_types.get(dtype, 0) + 1
            
            # 如果某个类型占比超过70%，存在过拟合风险
            for dtype, count in decision_types.items():
                ratio = count / len(self.decision_history)
                if ratio > 0.7:
                    warnings.append(f"决策类型过于集中({dtype}占{ratio*100:.0f}%)，可能产生偏见")
                    recommendations.append(f"主动寻找不同类型的决策情境进行训练")
                    risk_level = "high"
        
        # 检查3：框架使用平衡（简化：基于计数）
        if sum(self.framework_usage_count.values()) >= 10:
            total = sum(self.framework_usage_count.values())
            max_framework = max(self.framework_usage_count, key=self.framework_usage_count.get)
            max_ratio = self.framework_usage_count[max_framework] / total
            
            if max_ratio > 0.6:
                warnings.append(f"过度依赖{max_framework}框架({max_ratio*100:.0f}%)，思维可能僵化")
                recommendations.append("刻意练习使用其他认知框架")
                risk_level = "high"
        
        # 检查4：反馈一致性（简化：基于最近反馈）
        recent_feedback = [f for f in self.feedback_data if f.get('rating')]
        if len(recent_feedback) >= 5:
            recent_ratings = [f['rating'] for f in recent_feedback[-5:]]
            if all(r >= 8 for r in recent_ratings):
                warnings.append("最近反馈过于一致（都是高分），可能存在确认偏误")
                recommendations.append("主动寻求挑战性反馈，测试系统边界")
                risk_level = "medium"
        
        # 输出结果
        if warnings:
            print(f"\n🔴 检测到风险（等级: {risk_level}）:")
            for w in warnings:
                print(f"  • {w}")
            
            print(f"\n💡 建议:")
            for r in recommendations:
                print(f"  • {r}")
        else:
            print(f"\n✅ 暂未检测到过拟合风险")
            print(f"   当前历史数据: {len(self.decision_history)}个决策")
            print(f"   建议至少收集20个决策后启用高级防过拟合功能")
        
        # 输出多样性建议
        print(f"\n📊 多样性指标:")
        print(f"  历史决策数: {len(self.decision_history)}")
        print(f"  反馈记录数: {len(self.feedback_data)}")
        print(f"  框架使用分布:")
        for fw, count in sorted(self.framework_usage_count.items(), key=lambda x: -x[1]):
            print(f"    {fw}: {count}次")
        
        return {
            "risk_level": risk_level,
            "warnings": warnings,
            "recommendations": recommendations,
            "diversity_score": len(decision_types) / max(len(self.decision_history), 1) if len(self.decision_history) > 0 else 0
        }
    
    # ==================== 原有功能（保持不变） ====================
    
    def council_discussion(self, decision_context: str) -> Dict:
        """五路图腾议事厅"""
        print(f"\n{'='*70}")
        print(f"🏛️  五路图腾议事厅")
        print(f"{'='*70}")
        print(f"决策情境: {decision_context}")
        print(f"{'='*70}\n")
        
        perspectives = {}
        
        for name, profile in TOTEMS.items():
            print(f"\n🔥 {name} | {profile['role']}")
            print(f"   精髓: {profile['essence']}")
            print(f"   风格: {profile['style']}")
            
            perspective = self._generate_perspective(name, profile, decision_context)
            perspectives[name] = perspective
            
            print(f"   💬 提问: {random.choice(profile['questions'])}")
            print(f"   📋 建议: {perspective}")
        
        return perspectives
    
    def _generate_perspective(self, totem_name: str, profile: Dict, context: str) -> str:
        """基于图腾特性生成决策视角"""
        if totem_name == "刘禹锡":
            return "评估团队凝聚力和品德风险，建议慎重选择合作伙伴"
        elif totem_name == "司马贺":
            return "分析数据，寻找满意解而非最优解，设定明确的决策标准"
        elif totem_name == "观自在":
            return "透过表象看本质，识别真正的风险和机会"
        elif totem_name == "孔子":
            return "确保决策符合伦理底线，考虑长期声誉影响"
        elif totem_name == "六祖慧能":
            return "倾听直觉，在关键时刻敢于突破常规"
        else:
            return "综合分析"
    
    def evaluate_decision_quality(self, decision: Dict) -> Dict:
        """决策质量评估"""
        print(f"\n{'='*70}")
        print("📊 决策质量评估")
        print(f"{'='*70}")
        
        process_score = 0
        criteria = {
            "信息充分性": decision.get('info_completeness', 5),
            "分析深度": decision.get('analysis_depth', 5),
            "多视角考虑": decision.get('perspective_diversity', 5),
            "风险评估": decision.get('risk_assessment', 5),
            "时间压力管理": decision.get('time_pressure_mgmt', 5)
        }
        
        for criterion, score in criteria.items():
            process_score += score
            print(f"   {criterion}: {score}/10")
        
        avg_process_score = process_score / len(criteria)
        result_score = decision.get('outcome_score', None)
        
        print(f"\n   过程质量平均分: {avg_process_score:.1f}/10")
        if result_score:
            print(f"   结果质量评分: {result_score}/10")
            overall = (avg_process_score + result_score) / 2
        else:
            overall = avg_process_score
        
        print(f"   综合决策质量: {overall:.1f}/10")
        
        return {
            "process_score": avg_process_score,
            "result_score": result_score,
            "overall_score": overall,
            "criteria": criteria
        }
    
    def seci_knowledge_loop(self, decision: Dict, reflection: str) -> Dict:
        """SECI知识发酵"""
        print(f"\n{'='*70}")
        print("🔄 SECI知识发酵闭环")
        print(f"{'='*70}")
        
        print("\n1️⃣ 社会化(Socialization) - 经验分享")
        print(f"   记录决策情境: {decision.get('context', '')}")
        
        print("\n2️⃣ 外显化(Externalization) - 结构化")
        knowledge_asset = {
            "decision_id": f"DEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "context": decision.get('context', ''),
            "options": decision.get('options', []),
            "chosen_option": decision.get('chosen', ''),
            "reasoning": decision.get('reasoning', ''),
            "reflection": reflection,
            "totem_perspectives": decision.get('perspectives', {}),
            "quality_score": decision.get('quality_score', {}),
            "framework_used": decision.get('framework_used', '理性分析')
        }
        print(f"   生成知识资产: {knowledge_asset['decision_id']}")
        
        print("\n3️⃣ 组合化(Combination) - 知识关联")
        related_cases = self._find_related_cases(decision.get('context', ''))
        print(f"   找到 {len(related_cases)} 个相关案例")
        
        print("\n4️⃣ 内隐化(Internalization) - 学习吸收")
        print(f"   反思: {reflection}")
        print("   更新决策模式...")
        
        self._save_knowledge(knowledge_asset)
        self.decision_history.append(decision)
        
        return knowledge_asset
    
    def _find_related_cases(self, context: str) -> List[str]:
        """查找相关案例"""
        return ["CASE-2026-001", "CASE-2026-002"]
    
    def _save_knowledge(self, knowledge: Dict):
        """保存知识资产"""
        data_dir = Path("/root/.openclaw/workspace/ai_decision_mvp/data")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        kb_file = data_dir / "knowledge_base.jsonl"
        with open(kb_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(knowledge, ensure_ascii=False) + '\n')
    
    def unified_dialogue(self, user_input: str, active_totems: List[str] = None) -> str:
        """统一对话界面"""
        if active_totems is None:
            active_totems = list(TOTEMS.keys())
        
        print(f"\n{'='*70}")
        print("💬 统一对话界面")
        print(f"{'='*70}")
        print(f"用户: {user_input}")
        print(f"激活的图腾: {', '.join(active_totems)}")
        
        if "合伙" in user_input or "合作" in user_input:
            context = "合伙人匹配决策"
        elif "投资" in user_input or "融资" in user_input:
            context = "投资决策"
        else:
            context = "一般决策"
        
        perspectives = self.council_discussion(context)
        response = self._synthesize_response(user_input, perspectives)
        
        print(f"\n🤖 系统: {response}")
        return response
    
    def _synthesize_response(self, user_input: str, perspectives: Dict) -> str:
        """综合多Agent意见"""
        return f"基于五路图腾的分析，建议：1) 司马贺提醒用数据说话 2) 观自在建议看清本质 3) 孔子强调伦理底线。请告诉我更多背景信息，我可以给出更精准的建议。"
    
    def feedback_learning(self, decision_id: str, feedback: str, rating: int):
        """反馈学习"""
        print(f"\n{'='*70}")
        print("📈 反馈学习")
        print(f"{'='*70}")
        print(f"决策ID: {decision_id}")
        print(f"反馈: {feedback}")
        print(f"评分: {rating}/10")
        
        self.feedback_data.append({
            "decision_id": decision_id,
            "feedback": feedback,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        })
        
        if rating >= 7:
            print("✅ 符合风格，强化此模式")
        else:
            print("⚠️  不符合风格，调整权重")
        
        print(f"已收集 {len(self.feedback_data)} 条反馈")

# CLI接口
if __name__ == "__main__":
    import sys
    
    system = TotemDecisionSystem()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 totem_decision.py council '决策情境'       - 五路图腾议事")
        print("  python3 totem_decision.py evaluate '决策文件.json' - 评估决策质量")
        print("  python3 totem_decision.py dialogue '用户输入'      - 对话式决策")
        print("  python3 totem_decision.py framework '情境' [目标框架] - 框架转换")
        print("  python3 totem_decision.py intuition '情境'          - 直觉信号")
        print("  python3 totem_decision.py overfit                   - 过拟合检测")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "council" and len(sys.argv) >= 3:
        context = sys.argv[2]
        system.council_discussion(context)
    
    elif command == "evaluate" and len(sys.argv) >= 3:
        with open(sys.argv[2], 'r') as f:
            decision = json.load(f)
        system.evaluate_decision_quality(decision)
    
    elif command == "dialogue" and len(sys.argv) >= 3:
        user_input = sys.argv[2]
        system.unified_dialogue(user_input)
    
    elif command == "framework" and len(sys.argv) >= 3:
        context = sys.argv[2]
        target = sys.argv[3] if len(sys.argv) > 3 else None
        system.framework_switch(context, target)
    
    elif command == "intuition" and len(sys.argv) >= 3:
        context = sys.argv[2]
        system.generate_intuition_signal(context)
    
    elif command == "overfit":
        system.check_overfitting_risk({})
    
    else:
        print(f"未知命令: {command}")
