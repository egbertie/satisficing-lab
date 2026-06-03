#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
integrative_decision_toolkit.py
《整合决策》詹妮弗·里尔 & 罗杰·L.马丁

核心内化:
  - 整合思维：不在次优选项中取舍，而是利用对立观点创造更好的第三方案
  - 思维模型的5个特点与3个优秀决策原则
  - 整合决策的4个阶段
  - 创造性整合的3条路径（隐藏的宝石/双倍下注/解构）

来源: Jennifer Riel & Roger L. Martin, Creating Great Choices (2017)
译者: (湛庐文化)
产出时间: 2026-04-09
状态: CONDITIONAL_PASS
"""

from typing import Dict, List, Optional


KNOWLEDGE_BASE = {
    "meta": {
        "book": "整合决策",
        "original_title": "Creating Great Choices: A Leader's Guide to Integrative Thinking",
        "authors": "詹妮弗·里尔 (Jennifer Riel) & 罗杰·L.马丁 (Roger L. Martin)",
        "year": 2017,
        "publisher": "浙江人民出版社 / 湛庐文化"
    },
    "mind_model_characteristics": {
        "特点1_思维模型是内隐的": "我们常常意识不到自己正在使用某个思维模型",
        "特点2_思维模型容易被操控": "情绪、环境、框架会轻易改变我们的判断",
        "特点3_思维模型非常顽固": "一旦形成，很难被反证改变",
        "特点4_思维模型过于简单": "现实复杂，但我们的心智模式倾向于过度简化",
        "特点5_思维模型过于单一": "我们往往只依赖一个模型，而忽视了其他可能的视角"
    },
    "decision_principles": {
        "原则1_元认知": "更清晰地理解自己的思维过程；知道自己如何思考",
        "原则2_同理心": "有目的地理解他人的想法和观念；不急于否定对立观点",
        "原则3_创造力": "寻找新方案，拥抱独特性；拒绝被迫接受单选题"
    },
    "four_stages": {
        "阶段1_呈现对立模式": {
            "goal": "让问题变成真正的两难困境，而非伪装成选择题",
            "steps": [
                "步骤1：界定问题——我们要解决什么？",
                "步骤2：明确两种极端而对立的模式——代表两种完全不同的解决思路",
                "步骤3：阐明对立模式——清楚地说明它们各自的假设、逻辑和价值",
                "步骤4：指出每种模式的运作方式——它们在现实中如何产生结果"
            ]
        },
        "阶段2_审视对立模式": {
            "goal": "发掘每种模式的优点，而非急于找出它们的缺点",
            "steps": [
                "步骤1：理解对立模式之间的冲突——为什么它们不能简单地并存？",
                "步骤2：考察两种对立模式中最重要的价值——每种模式真正保护的是什么？",
                "步骤3：回顾——暂停判断，真正地理解两种模式的内在逻辑"
            ]
        },
        "阶段3_探究各种可能性": {
            "goal": "解决现有模式之间的冲突，创造超越对立的第三方案",
            "creative_paths": {
                "路径1_隐藏的宝石": {
                    "description": "从两种对立模式中分别提取最好、最有价值的部分，然后进行组合",
                    "example": "四季酒店：既提供高端奢华体验（A模式），又保持较低的资本投入（B模式）"
                },
                "路径2_双倍下注": {
                    "description": "不把两种模式看作非此即彼，而是找到一种方式让两种优势都发挥到极致",
                    "example": "红帽软件：既保持开源软件的免费共享（A模式），又通过企业版服务获得收入（B模式）"
                },
                "路径3_解构": {
                    "description": "打破两种模式各自的关键假设，从根本上重新建构问题，创造全新的解决框架",
                    "example": "伊萨多·夏普重新定义'酒店'：不是提供住宿，而是提供独特的生活体验"
                }
            }
        },
        "阶段4_评估初始方案": {
            "goal": "找出更好的解决方案，而不是完美的方案",
            "steps": [
                "步骤1：定义每一种方案——清晰地描述整合后的第三方案是什么",
                "步骤2：理解每种方案的逻辑——它为什么能够整合两种对立模式的优势？",
                "步骤3：设计和执行方案测试——通过低成本实验验证整合方案的可行性"
            ]
        }
    }
}


def query_mind_model_characteristic(name: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["mind_model_characteristics"]
    if name is None:
        return {"characteristics": list(data.keys())}
    for k, v in data.items():
        if name in k or k in name:
            return {k: v}
    return {"error": f"未找到 '{name}'，可用: {list(data.keys())}"}


def query_principle(name: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["decision_principles"]
    if name is None:
        return {"principles": list(data.keys())}
    for k, v in data.items():
        if name in k or k in name:
            return {k: v}
    return {"error": f"未找到 '{name}'，可用: {list(data.keys())}"}


def query_stage(stage_name: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["four_stages"]
    if stage_name is None:
        return {"stages": list(data.keys())}
    for k, v in data.items():
        if stage_name in k or k in stage_name:
            return {k: v}
    return {"error": f"未找到 '{stage_name}'，可用: {list(data.keys())}"}


def query_creative_path(path_name: Optional[str] = None) -> Dict:
    stage3 = KNOWLEDGE_BASE["four_stages"]["阶段3_探究各种可能性"]["creative_paths"]
    if path_name is None:
        return {"paths": list(stage3.keys())}
    for k, v in stage3.items():
        if path_name in k or k in path_name:
            return {k: v}
    return {"error": f"未找到 '{path_name}'，可用: {list(stage3.keys())}"}


class OpposingModelsAnalyzer:
    """
    对立模式分析器。
    输入两种对立的解决模式，输出整合思维的4阶段分析框架。
    """

    def analyze(self, model_a_name: str, model_a_logic: str,
                model_b_name: str, model_b_logic: str) -> Dict:
        return {
            "stage1_呈现对立模式": {
                "model_a": {"name": model_a_name, "logic": model_a_logic},
                "model_b": {"name": model_b_name, "logic": model_b_logic},
                "core_tension": f"{model_a_name} 与 {model_b_name} 代表了两种根本不同的价值和假设"
            },
            "stage2_审视对立模式": {
                "task": "分别列出每种模式试图保护的核心价值和优点",
                "questions": [
                    f"{model_a_name} 在什么情况下确实是最佳方案？",
                    f"{model_b_name} 在什么情况下确实是最佳方案？",
                    "两种模式各自的'不可让步'是什么？"
                ]
            },
            "stage3_探究可能性": {
                "prompts": [
                    f"隐藏的宝石：能否提取 {model_a_name} 和 {model_b_name} 的最佳部分进行组合？",
                    f"双倍下注：能否设计一种方案，让 {model_a_name} 和 {model_b_name} 的优势同时最大化？",
                    f"解构：两种模式各自依赖了什么关键假设？打破这些假设能否创造全新框架？"
                ]
            },
            "stage4_评估方案": {
                "task": "选择最有潜力的整合方案，设计低成本实验进行验证"
            }
        }


class IntegrativeSolutionAdvisor:
    """
    基于对立模式的特征，推荐最可能成功的创造性整合路径。
    """

    def recommend_path(self, model_a_name: str, model_a_strength: str,
                       model_b_name: str, model_b_strength: str,
                       conflict_type: str) -> Dict:
        """
        conflict_type: "资源竞争" / "目标冲突" / "假设对立" / "时间尺度差异"
        """
        if conflict_type == "资源竞争":
            return {
                "recommended_path": "路径1_隐藏的宝石",
                "reason": f"{model_a_name} 和 {model_b_name} 各自在资源使用上有优势，组合可以优化配置",
                "action": "明确两种资源分配方式的最佳实践，设计一种分段或分区组合方案"
            }
        elif conflict_type == "目标冲突":
            return {
                "recommended_path": "路径2_双倍下注",
                "reason": f"{model_a_name} 追求 {model_a_strength}，{model_b_name} 追求 {model_b_strength}，两者并非零和",
                "action": "设计一种可以同时追求两个目标的全新商业模式或流程"
            }
        elif conflict_type == "假设对立":
            return {
                "recommended_path": "路径3_解构",
                "reason": "冲突根植于深层次假设，打破假设才能打开新空间",
                "action": "列出两种模式的隐藏假设，逐一挑战并重构问题定义"
            }
        elif conflict_type == "时间尺度差异":
            return {
                "recommended_path": "路径1_隐藏的宝石",
                "reason": "短期与长期往往可以分阶段整合",
                "action": "设计分阶段方案，在不同时间窗口应用不同模式的优势"
            }
        else:
            return {
                "recommended_path": "建议依次尝试3条路径",
                "reason": "冲突类型不明确，系统性地从隐藏宝石→双倍下注→解构进行探索",
                "action": "召开创意工作坊，分别用3种路径对同一问题进行头脑风暴"
            }


def integrative_thinking_checklist() -> List[Dict]:
    """
    整合思维决策前自检清单。
    """
    return [
        {"item": "问题已被界定为两难困境", "question": "我们是否被迫在两个不尽如人意的选项间做选择？", "checked": False},
        {"item": "两种对立模式已清晰呈现", "question": "我们能否清楚地说出两种极端方案的逻辑和假设？", "checked": False},
        {"item": "已发掘每种模式的优点", "question": "我们是否真诚地理解了每种模式的内在价值？", "checked": False},
        {"item": "已尝试3条创造性路径", "question": "我们是否尝试过隐藏宝石、双倍下注、解构这3种整合方式？", "checked": False},
        {"item": "整合方案经过低成本验证", "question": "我们是否设计了小规模实验来测试这个第三方案？", "checked": False}
    ]


def get_cross_book_mapping(concept: str) -> Dict:
    mapping = {
        "元认知": {
            "slow_think_fast_decide": "以流程为决策中心，使用检查清单反思维过程",
            "kahneman_tversky": "意识到启发法与偏见对判断的影响",
            "honeybee_democracy": "侦察蜂独立判断后再进行公开的舞蹈讨论",
            "systems_thinking": "元认知即对自身心智模式的觉察，是范式层变革的前提"
        },
        "同理心": {
            "slow_think_fast_decide": "后入为主/盲听盲选，避免先入为主的偏见",
            "kahneman_tversky": "克服证实偏见，主动寻找支持对立观点的证据",
            "honeybee_democracy": "领导者影响最小化，允许所有观点被表达",
            "systems_thinking": "理解不同利益相关方的目标与调节回路"
        },
        "创造力": {
            "slow_think_fast_decide": "四大策略与八种技巧中的'以偏概全'和'反过来想'",
            "kahneman_tversky": "突破简单启发法的限制，寻找非直觉的解决方案",
            "honeybee_democracy": "数百只侦察蜂探索多样化的候选巢址",
            "systems_thinking": "自组织与范式转换，打破现有连接结构"
        }
    }
    return mapping.get(concept, {"note": "暂无跨书映射"})


def demo():
    print("=" * 60)
    print("《整合决策》工具箱 —— 功能验证")
    print("=" * 60)

    print("\n[1] 思维模型特点查询")
    r1 = query_mind_model_characteristic("顽固")
    print(f" {list(r1.keys())[0]}: {list(r1.values())[0]}")

    print("\n[2] 创造性路径查询")
    r2 = query_creative_path("双倍下注")
    print(f" {list(r2.keys())[0]}: {list(r2.values())[0]['description']}")

    print("\n[3] 对立模式分析")
    analyzer = OpposingModelsAnalyzer()
    r3 = analyzer.analyze(
        "高端定制", "提供独特个性化服务，成本高",
        "规模量产", "通过标准化降低成本，牺牲个性化"
    )
    print(f" 核心张力: {r3['stage1_呈现对立模式']['core_tension']}")

    print("\n[4] 整合路径推荐")
    advisor = IntegrativeSolutionAdvisor()
    r4 = advisor.recommend_path(
        "高端定制", "独特性",
        "规模量产", "低成本",
        "目标冲突"
    )
    print(f" 推荐路径: {r4['recommended_path']}")

    print("\n[5] 自检清单")
    r5 = integrative_thinking_checklist()
    print(f" 检查项数: {len(r5)}")

    print("\n[6] 跨书映射")
    r6 = get_cross_book_mapping("创造力")
    print(f" 系统之美映射: {r6['systems_thinking']}")

    print("\n" + "=" * 60)
    print("验证通过。资产可运行。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
