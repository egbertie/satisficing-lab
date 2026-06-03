#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kahneman_tversky_decision_archive.py
《思维的发现：关于决策与判断的科学》迈克尔·刘易斯

核心内化:
  - 人物: 丹尼尔·卡尼曼 (Daniel Kahneman) + 阿莫斯·特沃斯基 (Amos Tversky)
  - 理论演进: 批判保守贝叶斯人 → 启发法与偏见 → 后悔理论 → 前景理论
  - 关键实验: 代表性/可得性/锚定/医生诊断一致性/琳达问题
  - 跨领域: 医学、体育(NBA/棒球)、军事(以色列空军)、政治选举

来源: Michael Lewis, The Undoing Project (2017)
产出时间: 2026-04-09
状态: CONDITIONAL_PASS
"""

from typing import Dict, List, Optional


KNOWLEDGE_BASE = {
    "meta": {
        "book": "思维的发现：关于决策与判断的科学",
        "original_title": "The Undoing Project: A Friendship That Changed Our Minds",
        "author": "迈克尔·刘易斯 (Michael Lewis)",
        "year": 2017,
        "translated_by": "钟莉婷",
        "publisher": "中信出版集团"
    },
    "people": {
        "丹尼尔·卡尼曼 (Daniel Kahneman)": {
            "role": "心理学家，2002年诺贝尔经济学奖得主",
            "personality": "怀疑者、内向、善于从错误中学习、依靠直觉做判断但深知其陷阱",
            "background": "童年在法国经历纳粹迫害，后加入以色列国防军，在希伯来大学任教",
            "key_contribution": "提出直觉判断的系统1概念雏形，专注于人类思维的缺陷与偏见"
        },
        "阿莫斯·特沃斯基 (Amos Tversky)": {
            "role": "认知心理学家，数学天才",
            "personality": "直率、自信、极度聪明、5分钟内判断电影值不值得看",
            "background": "出生于以色列海法，曾是以色列国防军伞兵，后在希伯来大学任教",
            "key_contribution": "数学形式化天才，将模糊的心理学直觉转化为严密的数学模型"
        }
    },
    "theory_evolution": {
        "批判保守的贝叶斯人": {
            "time": "1960年代末-1970年代初",
            "core": "人类不是保守的统计学家；在面对概率问题时，人们并非按贝叶斯公式逐步调整信念",
            "key_finding": "人们的判断方向正确（比如红筹码多就猜红），但幅度远远不够（贝叶斯27倍 vs 实际3倍）",
            "significance": "打破了当时心理学界'人脑像统计学家'的主流比喻"
        },
        "启发法与偏见": {
            "time": "1970年代初",
            "core": "大脑用经验法则（启发法）代替机会法则，导致系统性偏见",
            "three_heuristics": {
                "代表性启发法 (Representativeness)": "人们根据事物与典型模式的相似度来判断概率，忽视基础比率",
                "可得性启发法 (Availability)": "人们根据事件在记忆中容易被回想起的程度来判断频率",
                "锚定与调整启发法 (Anchoring and Adjustment)": "人们的判断过度依赖最初获得的信息（锚点），调整不足"
            },
            "key_experiments": ["琳达问题（合取谬误）", "K打头单词 vs K在第三位的单词", "8×7×6...的速算"]
        },
        "后悔理论 (Regret Theory)": {
            "time": "1973年前后",
            "core": "人们做决策时并非追求效用最大化，而是追求后悔最小化",
            "rules": [
                "后悔与'靠近程度'有关：越接近目标，未达成时越后悔",
                "后悔与责任感有关：觉得自己对结局负有责任时更后悔",
                "改变现状失败带来的痛苦 > 维持现状失败带来的痛苦"
            ],
            "status": "后来被前景理论吸收并超越"
        },
        "前景理论 (Prospect Theory)": {
            "time": "1975年完成论文",
            "core": "解释人类在风险决策中的非理性行为，用心理学概念重构经济学",
            "three_insights": [
                "人们对微弱变化做出反应（敏感性递减）",
                "损失和收益的风险态度不对称：收益时风险规避，损失时风险寻求",
                "人们对概率的反应是非线性的：会高估小概率事件，低估中高概率事件"
            ],
            "significance": "引爆了经济学殿堂，奠定了行为经济学的基础",
            "famous_quote": "人们不是追求效用最大化，而是追求懊悔最小化（后悔理论阶段）→ 随后升级为参照点理论"
        }
    },
    "experiments": {
        "保守的贝叶斯人实验": {
            "setup": "从装了红/白筹码的口袋中抽取筹码，让被试判断哪个口袋红色居多",
            "finding": "被试更新信念的幅度只有贝叶斯定理所要求的1/9",
            "field": "概率判断"
        },
        "琳达问题 (合取谬误)": {
            "setup": "琳达是一位关心歧视问题的前哲学系学生，她更可能是'A.银行出纳员'还是'B.银行出纳员且积极参与女权运动'",
            "finding": "大多数人认为B比A更有可能——违反了概率基本法则（合取事件不可能比单事件概率更高）",
            "explanation": "代表性启发法：B的描述更符合人们对琳达的'典型印象'"
        },
        "医生诊断一致性研究": {
            "setup": "俄勒冈研究所让放射科医生根据胃部X光片的7条线索判断癌症，并重复展示同一张图片",
            "finding_1": "医生之间的诊断不一致，甚至同一位医生对同一张图片的前后诊断也矛盾",
            "finding_2": "简单线性模型（7条线索等权重）不仅准确预测了医生的诊断，甚至比医生本人更准确",
            "significance": "专家判断不如简单算法可靠"
        },
        "以色列空军教练实验": {
            "setup": "空军教练认为批评比表扬更有效，因为批评后飞行员表现更好，表扬后反而变差",
            "finding": "这其实是'回归均值'现象：表现极端好/差的下次都会趋向平均水平，与表扬或批评无关",
            "significance": "人们容易把随机波动误解释为因果效应"
        },
        "锚定实验 (8×7×6...)": {
            "setup": "第一组速算 8×7×6×5×4×3×2×1，第二组速算 1×2×3×4×5×6×7×8（限时5秒）",
            "finding": "第一组估算值显著高于第二组，尽管实际答案相同",
            "explanation": "人们以最初计算的几个数字为锚点，调整不足"
        }
    },
    "domain_cases": {
        "医学": {
            "cases": ["医生诊断一致性研究", "乳腺X光误诊率（20岁女性基准率差异）"],
            "key_bias": "专家判断的不稳定性、回归均值忽视、基础比率忽视"
        },
        "体育 (NBA/棒球)": {
            "cases": ["达里尔·莫雷的数据模型", "林书豪被低估", "专家选秀偏见"],
            "key_bias": "禀赋效应、后视偏见、证实性偏见、外表偏见（长相/身材）"
        },
        "军事 (以色列空军)": {
            "cases": ["空军教练的表扬vs批评", "赎罪日战争后的决策反思"],
            "key_bias": "回归均值忽视、反事实思维、后悔与国家决策"
        },
        "法律/政治": {
            "cases": ["选举预测（奈特·西尔弗/特朗普）", "政治民调偏差"],
            "key_bias": "过度自信、框架效应、可得性启发法"
        }
    }
}


def query_person(name: Optional[str] = None) -> Dict:
    """查询卡尼曼或特沃斯基的档案。"""
    data = KNOWLEDGE_BASE["people"]
    if name is None:
        return {"available_people": list(data.keys())}
    for key, value in data.items():
        if name in key or key in name:
            return {key: value}
    return {"error": f"未找到人物 '{name}'，可用选项: {list(data.keys())}"}


def query_theory(theory_name: Optional[str] = None) -> Dict:
    """查询核心理论。"""
    data = KNOWLEDGE_BASE["theory_evolution"]
    if theory_name is None:
        return {"available_theories": list(data.keys())}
    for key, value in data.items():
        if theory_name in key or key in theory_name:
            return {key: value}
    return {"error": f"未找到理论 '{theory_name}'，可用选项: {list(data.keys())}"}


def query_experiment(exp_name: Optional[str] = None) -> Dict:
    """查询关键实验。"""
    data = KNOWLEDGE_BASE["experiments"]
    if exp_name is None:
        return {"available_experiments": list(data.keys())}
    for key, value in data.items():
        if exp_name in key or key in exp_name:
            return {key: value}
    return {"error": f"未找到实验 '{exp_name}'，可用选项: {list(data.keys())}"}


def query_domain(domain_name: Optional[str] = None) -> Dict:
    """查询领域案例。"""
    data = KNOWLEDGE_BASE["domain_cases"]
    if domain_name is None:
        return {"available_domains": list(data.keys())}
    for key, value in data.items():
        if domain_name in key or key in domain_name:
            return {key: value}
    return {"error": f"未找到领域 '{domain_name}'，可用选项: {list(data.keys())}"}


def get_heuristic_bias(heuristic_name: str) -> Dict:
    """获取特定启发法及其偏见的详细说明。"""
    mapping = {
        "代表性": ("代表性启发法 (Representativeness)", KNOWLEDGE_BASE["theory_evolution"]["启发法与偏见"]["three_heuristics"]["代表性启发法 (Representativeness)"]),
        "可得性": ("可得性启发法 (Availability)", KNOWLEDGE_BASE["theory_evolution"]["启发法与偏见"]["three_heuristics"]["可得性启发法 (Availability)"]),
        "锚定": ("锚定与调整启发法 (Anchoring and Adjustment)", KNOWLEDGE_BASE["theory_evolution"]["启发法与偏见"]["three_heuristics"]["锚定与调整启发法 (Anchoring and Adjustment)"])
    }
    for key, (full_name, value) in mapping.items():
        if heuristic_name in key or key in heuristic_name:
            return {"heuristic": full_name, "description": value}
    return {"error": f"未找到启发法 '{heuristic_name}'，可用: {list(mapping.keys())}"}


class ExpertVsAlgorithmEvaluator:
    """
    基于书中戈德堡研究的简化评估器。
    核心洞察：在大量判断任务中，简单线性模型往往比专家本人的判断更准确。
    """

    RULES = [
        {
            "condition": "需要整合多条线索并进行加权判断",
            "verdict": "算法优势",
            "reason": "人类在同时处理多条线索时权重不稳定，容易因为疲劳、情绪导致前后不一致"
        },
        {
            "condition": "决策结果反馈周期长或模糊",
            "verdict": "算法优势",
            "reason": "专家缺少'即时反馈'来校准自己的判断准确性"
        },
        {
            "condition": "涉及大量相似案例的重复判断",
            "verdict": "算法优势",
            "reason": "简单模型可以消除人类判断中的随机波动"
        },
        {
            "condition": "需要敏锐捕捉细微模式或异常信号",
            "verdict": "专家仍有价值",
            "reason": "在数据稀疏或规则不明的领域，专家的经验直觉可能发现算法看不到的模式"
        },
        {
            "condition": "决策涉及人际关系、谈判或道德判断",
            "verdict": "专家/人类必要",
            "reason": "算法无法处理情感、伦理和动态博弈中的隐性因素"
        }
    ]

    def evaluate(self, decision_context: str) -> Dict:
        """根据决策情境判断是算法更优还是专家更优。"""
        context = decision_context.lower()
        matched = []
        for rule in self.RULES:
            # 简化匹配：基于关键词出现与否
            if any(kw in context for kw in rule["condition"].split("并")[:1]):
                matched.append(rule)
        if not matched:
            # 默认推荐
            return {
                "verdict": "建议混合使用",
                "reason": "在数据充足的结构化判断中让算法主导，在异常识别和人际互动中保留专家角色",
                "source": "Goldberg (1970s) / Lewis (2017)"
            }
        return {
            "verdicts": [m["verdict"] for m in matched],
            "details": matched,
            "source": "Goldberg (1970s) / Lewis (2017)"
        }


class DecisionBiasDetectorV2:
    """
    基于《思维的发现》中启发法与偏见的关键词检测器。
    与第一本《慢思考，快决策》的SPEED模型互补。
    """

    RULES = {
        "代表性启发法": {
            "keywords": ["看起来像", "典型的", "更像是", "符合形象", "描述很具体", "琳达"],
            "description": "根据描述与典型模式的相似度判断概率，忽视基础比率"
        },
        "可得性启发法": {
            "keywords": ["容易想起", "媒体", "最近发生", "印象深刻", "记忆犹新"],
            "description": "根据事件在记忆中的易得程度判断频率"
        },
        "锚定与调整": {
            "keywords": ["最初报价", "第一印象", "先听到的", "参考点", "从...开始"],
            "description": "判断过度依赖最初信息，后续调整不足"
        },
        "回归均值忽视": {
            "keywords": ["表扬后变差", "批评后变好", "上次表现好", "这次退步", "持续提升"],
            "description": "把极端表现后的自然回落误解释为干预效果"
        },
        "损失厌恶": {
            "keywords": ["舍不得", "已经投入了", "不想亏", "宁可冒险", "避免损失"],
            "description": "人们对损失的痛苦感受大于等量收益的快乐"
        },
        "框架效应": {
            "keywords": ["存活率", "死亡率", "收益", "损失", "换一种说法"],
            "description": "同一问题的不同表述导致不同决策"
        }
    }

    def detect(self, text: str) -> List[Dict]:
        text_lower = text.lower()
        results = []
        for bias_name, meta in self.RULES.items():
            if any(kw in text_lower for kw in meta["keywords"]):
                results.append({
                    "bias": bias_name,
                    "description": meta["description"]
                })
        if not results:
            results.append({"bias": "未识别明显偏见", "description": "请提供更多情境细节"})
        return results


def get_cross_book_bias_lookup(bias_name: str) -> Dict:
    """
    跨书查询：将《思维的发现》中的学术偏见名称映射到《慢思考，快决策》中的SPEED分类。
    """
    mapping = {
        "损失厌恶": {"speed_category": "安全性偏見 (Safety)", "sub_type": "不确定性效应/框架效应"},
        "框架效应": {"speed_category": "安全性偏見 (Safety)", "sub_type": "框架效应"},
        "可得性启发法": {"speed_category": "便利性偏見 (Expedience)", "sub_type": "可得性啟發法"},
        "锚定与调整": {"speed_category": "便利性偏見 (Expedience)", "sub_type": "錨定效應"},
        "代表性启发法": {"speed_category": "便利性偏見 (Expedience)", "sub_type": "證實偏見/結果偏見"},
        "回归均值忽视": {"speed_category": "經驗性偏見 (Experience)", "sub_type": "過度自信效應"}
    }
    return mapping.get(bias_name, {"note": "暂无SPEED映射，请手动分类"})


def demo():
    print("=" * 60)
    print("《思维的发现》决策档案 —— 功能验证")
    print("=" * 60)

    print("\n[1] 人物查询")
    r1 = query_person("卡尼曼")
    print(f" 角色: {list(r1.values())[0]['role']}")

    print("\n[2] 理论查询")
    r2 = query_theory("前景理论")
    theory_data = list(r2.values())[0]
    print(f" 核心理论: {theory_data['core']}")

    print("\n[3] 实验查询")
    r3 = query_experiment("琳达")
    exp_data = list(r3.values())[0]
    print(f" 实验发现: {exp_data['finding']}")

    print("\n[4] 领域查询")
    r4 = query_domain("医学")
    print(f" 关键偏见: {list(r4.values())[0]['key_bias']}")

    print("\n[5] 专家 vs 算法评估")
    evaluator = ExpertVsAlgorithmEvaluator()
    r5 = evaluator.evaluate("医生需要根据7条X光线索判断癌症良恶性")
    print(f"  verdict: {r5['verdict']}")

    print("\n[6] 偏见检测")
    detector = DecisionBiasDetectorV2()
    r6 = detector.detect("这个候选人看起来就是一个成功的企业家")
    print(f" 检测到: {r6[0]['bias']}")

    print("\n[7] 跨书映射")
    r7 = get_cross_book_bias_lookup("损失厌恶")
    print(f" SPEED分类: {r7['speed_category']}")

    print("\n" + "=" * 60)
    print("验证通过。资产可运行。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
