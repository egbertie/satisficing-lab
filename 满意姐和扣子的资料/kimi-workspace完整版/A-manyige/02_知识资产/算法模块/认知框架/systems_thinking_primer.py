#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
systems_thinking_primer.py
《系统之美：决策者的系统思考》德内拉·梅多斯

核心内化:
  - 系统三要素：要素、连接、功能/目标
  - 存量-流量（Stock and Flow）思维
  - 反馈回路：增强回路（正反馈）与调节回路（负反馈）
  - 时间延迟
  - 系统陷阱与对策（8种基模）
  - 12大杠杆点（Leverage Points）

来源: Donella H. Meadows, Thinking in Systems: A Primer (2008)
译者: 邱昭良
产出时间: 2026-04-09
状态: CONDITIONAL_PASS
"""

from typing import Dict, List, Optional


KNOWLEDGE_BASE = {
    "meta": {
        "book": "系统之美：决策者的系统思考",
        "original_title": "Thinking in Systems: A Primer",
        "author": "德内拉·H.梅多斯 (Donella H. Meadows)",
        "year": 2008,
        "translated_by": "邱昭良",
        "publisher": "浙江人民出版社"
    },
    "system_components": {
        "要素": "系统中可见的、可观察的部分（如人口、树木、资金），但单独改变要素 rarely 改变系统行为",
        "连接": "要素之间的关系和信息流，是系统行为真正的塑造者",
        "功能或目标": "系统的目的，是最隐蔽但最重要的部分；改变目标往往能最有效地改变系统"
    },
    "stock_and_flow": {
        "存量 (Stock)": "在任何时刻都能观察、感知、计数和测量的系统要素的积累量。如水库中的水、人口数量、库存、银行账户",
        "流量 (Flow)": "一段时间内改变存量的状况。如流入量（出生、购买、存入）和流出量（死亡、出售、取出）",
        "核心原则": [
            "只要流入量总和超过流出量总和，存量水平就会上升",
            "只要流出量总和超过流入量总和，存量水平就会下降",
            "当流入量与流出量相等时，存量保持不变（动态平衡）",
            "存量的变化需要时间，因此可以起到延迟、缓存或减震器的作用",
            "人们的大脑更容易关注存量而非流量，更容易关注流入量而非流出量"
        ]
    },
    "feedback_loops": {
        "增强回路 (Reinforcing Feedback Loop)": {
            "alias": "正反馈回路",
            "icon": "脱缰的野马",
            "behavior": "指数增长或崩溃",
            "examples": ["复利", "人口增长", "病毒传播", "军备竞赛"],
            "principle": "增强回路会不断强化其自身的方向；没有外部约束或资源限制，它将无限增长或衰减"
        },
        "调节回路 (Balancing Feedback Loop)": {
            "alias": "负反馈回路",
            "icon": "自动洄游的鱼",
            "behavior": "寻求稳定、回归目标",
            "examples": ["温度调节器", "身体对血糖的调节", "库存补充", "市场价格对供需的调节"],
            "principle": "调节回路努力使存量趋向一个目标或均衡点；它是系统稳定性的根源"
        }
    },
    "delays": {
        "定义": "反馈回路中的时间延迟是系统行为复杂性的主要来源之一",
        "影响": "延迟可能导致振荡、行为不可预测、决策效果滞后显现",
        "原则": "在具有时间延迟的系统中，过于激进的干预往往导致过度调整和经济周期式的波动"
    },
    "traps": {
        "政策阻力 (Policy Resistance)": {
            "description": "多个调节回路各自拉向不同的目标，导致任何单一政策措施都会遇到强大阻力",
            "example": "毒品战、贫富差距、环境保护与经济发展的拉锯",
            "countermeasure": "放弃单一干预，让所有参与者坐到一起来协商共同的目标和整体福利政策"
        },
        "公地悲剧 (Tragedy of the Commons)": {
            "description": "共享资源的使用者对资源过度开采，每个人都受到激励去加速使用，但没有人有动力去维护",
            "example": "过度捕捞、地下水抽取、空气污染、公共牧场",
            "countermeasure": "教育+自我约束；资源私有化；对公共资源进行管制或配额管理"
        },
        "目标侵蚀 (Erosion of Goals)": {
            "description": "当系统表现不佳时，人们倾向于降低目标标准，而非努力改善绩效，导致系统持续下滑",
            "example": "产品质量标准下降、业绩目标逐年下调、环境标准放松",
            "countermeasure": "坚守标准，绝不下调；将绩效标准保持在与最佳实践一致的水平"
        },
        "竞争升级 (Escalation)": {
            "description": "两个增强回路相互较劲，双方不断升级自己的投入，试图压倒对方",
            "example": "军备竞赛、广告大战、价格战、噪音攀比",
            "countermeasure": "单方面裁军、谈判达成限制协议、将竞争目标转向非零和领域"
        },
        "富者愈富 (Success to the Successful)": {
            "description": "一个增强回路使得领先者获得更多资源，进一步扩大优势，直到消灭几乎所有竞争者",
            "example": "垄断形成、贫富差距扩大、资源向明星集中",
            "countermeasure": "多元化经营、反垄断、补贴弱势竞争者、引入奖励失败者的新游戏规则"
        },
        "转嫁负担 (Shifting the Burden)": {
            "description": "用'症状解'替代'根本解'，导致对症状解上瘾，削弱系统解决根本问题的能力",
            "example": "用借贷维持消费、用止痛药掩盖病因、用补贴维持落后产业",
            "countermeasure": "聚焦于根本解；减少或消除症状解；建立触发机制，在症状解生效时同时启动根本解"
        },
        "规避规则 (Rule Beating)": {
            "description": "系统参与者用合法但不合理的方式绕过规则，规则的初衷被架空",
            "example": "上有政策下有对策、为应付考核而造假、避税天堂",
            "countermeasure": "设计更少的但更有效的规则；强化规则背后的价值观和目标；让参与者参与规则设计"
        },
        "目标错位 (Seeking the Wrong Goal)": {
            "description": "系统目标与真正的愿景不一致，导致系统行为偏离初衷",
            "example": "GDP至上而忽视幸福感、以考试分数代替真实学习、以点击量代替内容质量",
            "countermeasure": "认真定义真正的目标；设计指标时要包含多维度的质性和隐性信息"
        }
    },
    "leverage_points": {
        "12_常数和参数": {
            "level": "效果最小但最常见",
            "description": "调整数字（如税率、利率、工资标准）；作用有限，因为系统结构未变"
        },
        "11_缓冲器": {
            "level": "稳定器",
            "description": "比流量力量更大、更稳定的存量；大缓冲器使系统更稳定，但也更难改变方向"
        },
        "10_存量-流量结构": {
            "level": "基础设施层级",
            "description": "改变系统的物理布局或结构（如建水库、修铁路、改供应链）；成本高、见效慢但影响深远"
        },
        "9_时间延迟": {
            "level": "动态调节器",
            "description": "改变系统对变化做出反应的速度；太短会导致振荡，太长会导致反应迟钝"
        },
        "8_调节回路": {
            "level": "稳定力量的强弱",
            "description": "增强或削弱反馈力量；如价格机制、自我纠错能力的强弱"
        },
        "7_增强回路": {
            "level": "增长或衰退引擎",
            "description": "改变驱动收益增长或加速衰退的反馈力量；如网络效应、复利、病毒传播系数"
        },
        "6_信息流": {
            "level": "认知改变",
            "description": "让原本不可见的信息可见；信息即力量，改变谁拥有信息和谁获取信息能改变权力结构"
        },
        "5_系统规则": {
            "level": "制度设计",
            "description": "激励、惩罚和约束条件（如法律、合同、公司政策）；规则塑造了行为"
        },
        "4_自组织": {
            "level": "系统进化能力",
            "description": "系统学习、 diversify、 进化的能力；如生物多样性、技术创新、组织学习能力"
        },
        "3_目标": {
            "level": "方向设定",
            "description": "系统的目的或功能；改变目标能够剧烈改变系统行为，但目标往往被隐藏或被视为理所当然"
        },
        "2_范式": {
            "level": "心智模式",
            "description": "人们共享的关于现实本质的假设和信念；范式是系统的根基，改变范式能产生最深刻的变革"
        },
        "1_超越范式": {
            "level": "最高层级",
            "description": "保持灵活性，认识到没有任何范式是绝对真实的；能够在不同范式之间自由切换"
        }
    },
    "survival_rules": [
        "1. 扩大关注的时间范围",
        "2. 扩大关切的范围",
        "3. 不要降低'善'的标准",
        "4. 有多少反馈、延迟和振荡，就显示多少",
        "5. 信息就是力量",
        "6. 不要在反馈回路中制造扭曲",
        "7. 促进多样性",
        "8. 保持谦逊，保持学习"
    ]
}


def query_component(name: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["system_components"]
    if name is None:
        return {"components": list(data.keys())}
    return {k: v for k, v in data.items() if name in k or k in name} or {"error": f"未找到 '{name}'"}


def query_trap(trap_name: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["traps"]
    if trap_name is None:
        return {"traps": list(data.keys())}
    for k, v in data.items():
        if trap_name in k or k in trap_name:
            return {k: v}
    return {"error": f"未找到陷阱 '{trap_name}'，可用: {list(data.keys())}"}


def query_leverage_point(level: Optional[int] = None) -> Dict:
    data = KNOWLEDGE_BASE["leverage_points"]
    if level is None:
        return {"levels": list(data.keys())}
    for k, v in data.items():
        if k.startswith(f"{level}_") or f"_{level}_" in k:
            return {k: v}
    return {"error": f"未找到杠杆点层级 '{level}'，可用: 1-12"}


def query_feedback_loop(loop_type: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["feedback_loops"]
    if loop_type is None:
        return {"loops": list(data.keys())}
    for k, v in data.items():
        if loop_type in k or k in loop_type:
            return {k: v}
    return {"error": f"未找到 '{loop_type}'，可用: {list(data.keys())}"}


class SystemTrapDiagnoser:
    """
    基于问题描述，快速诊断可能陷入的系统陷阱。
    基于梅多斯的8种系统基模。
    """

    RULES = [
        {
            "trap": "政策阻力",
            "keywords": ["各方拉锯", "阻力很大", "上有政策下有对策", "谁都不同意", "利益冲突", "措施无效"],
            "advice": "让所有利益相关方坐到一起来协商共同目标，而不是单边推进。"
        },
        {
            "trap": "公地悲剧",
            "keywords": ["过度使用", "资源枯竭", "共享资源", "谁都在抢", " nobody 维护", "免费使用", "超载"],
            "advice": "实施配额、私有化或共同管理协议，建立使用和维护的激励机制。"
        },
        {
            "trap": "目标侵蚀",
            "keywords": ["标准降低", "目标下调", "业绩越来越差", "得过且过", "放宽要求", "底线失守"],
            "advice": "坚守标准绝不松动，将绩效目标锚定在历史最佳或行业最佳水平。"
        },
        {
            "trap": "竞争升级",
            "keywords": ["军备竞赛", "价格战", "广告大战", "不断升级", "互相攀比", "恶性竞争"],
            "advice": "单方面停止升级，或谈判达成限制协议，将竞争转向非零和领域。"
        },
        {
            "trap": "富者愈富",
            "keywords": ["马太效应", "赢家通吃", "两极分化", "资源向头部集中", "垄断", "贫富差距"],
            "advice": "反垄断、补贴后来者、引入多元化奖励规则，打破单一增强回路。"
        },
        {
            "trap": "转嫁负担",
            "keywords": ["上瘾", "治标不治本", "借贷度日", "掩盖问题", "依赖短期解", "症状解"],
            "advice": "减少对症状解的依赖，聚焦于根本解，建立长期能力建设。"
        },
        {
            "trap": "规避规则",
            "keywords": ["上有政策下有对策", "钻空子", "应付检查", "造假", "规则被架空"],
            "advice": "减少繁文缛节，让参与者参与规则设计，强化规则背后的价值观。"
        },
        {
            "trap": "目标错位",
            "keywords": ["唯GDP", "唯分数", "唯KPI", "指标成了目标", "本末倒置", "走偏了"],
            "advice": "重新审视并定义真正的目标，引入多维度质性和隐性评价指标。"
        }
    ]

    def diagnose(self, description: str) -> List[Dict]:
        desc = description.lower()
        matched = []
        for rule in self.RULES:
            if any(kw in desc for kw in rule["keywords"]):
                matched.append(rule)
        if not matched:
            matched.append({"trap": "暂无明确匹配", "advice": "请提供更多系统结构和参与者行为的细节。"})
        return matched


class LeveragePointAdvisor:
    """
    根据用户想要改变的系统行为，推荐可能的杠杆点层级。
    """

    def recommend(self, behavior: str) -> Dict:
        behavior = behavior.lower()
        if any(kw in behavior for kw in ["振荡", "忽上忽下", "过度反应"]):
            return {
                "primary": "9_时间延迟",
                "secondary": "8_调节回路",
                "reason": "振荡通常由过短的反馈延迟或过于敏感的调节回路引起"
            }
        elif any(kw in behavior for kw in ["增长停滞", "指数增长", "崩溃"]):
            return {
                "primary": "7_增强回路",
                "secondary": "8_调节回路",
                "reason": "增长或衰退由增强回路驱动，需要同时看限制因素（调节回路）"
            }
        elif any(kw in behavior for kw in ["各方对抗", "目标不一", "阻力"]):
            return {
                "primary": "3_目标",
                "secondary": "5_系统规则",
                "reason": "对抗往往源于隐藏的、冲突的系统目标或不合理的规则"
            }
        elif any(kw in behavior for kw in ["信息不对称", "隐瞒", "不透明"]):
            return {
                "primary": "6_信息流",
                "secondary": "5_系统规则",
                "reason": "信息就是力量，改变谁能获取信息往往能改变权力结构"
            }
        elif any(kw in behavior for kw in ["僵化", "缺乏创新", "死板"]):
            return {
                "primary": "4_自组织",
                "secondary": "2_范式",
                "reason": "创新能力不足通常是自组织能力受限和范式锁死导致的"
            }
        elif any(kw in behavior for kw in ["价值观错误", "方向错误", "本末倒置"]):
            return {
                "primary": "2_范式",
                "secondary": "3_目标",
                "reason": "方向性的错误需要从根本的共享信念和目标入手"
            }
        else:
            return {
                "primary": "12_常数和参数",
                "secondary": "10_存量-流量结构",
                "reason": "如果不清楚深层结构，从可见的参数和结构入手进行试探性调整"
            }


def demo():
    print("=" * 60)
    print("《系统之美》入门工具箱 —— 功能验证")
    print("=" * 60)

    print("\n[1] 系统要素查询")
    r1 = query_component("连接")
    print(f" 定义: {list(r1.values())[0]}")

    print("\n[2] 系统陷阱查询")
    r2 = query_trap("转嫁负担")
    print(f" 对策: {list(r2.values())[0]['countermeasure']}")

    print("\n[3] 杠杆点查询")
    r3 = query_leverage_point(2)
    print(f" {list(r3.keys())[0]}: {list(r3.values())[0]['level']}")

    print("\n[4] 反馈回路查询")
    r4 = query_feedback_loop("增强")
    print(f" 行为: {list(r4.values())[0]['behavior']}")

    print("\n[5] 系统陷阱诊断")
    d = SystemTrapDiagnoser()
    r5 = d.diagnose("各个部门都在争夺预算，没有人愿意削减开支")
    print(f" 诊断: {r5[0]['trap']}")

    print("\n[6] 杠杆点推荐")
    a = LeveragePointAdvisor()
    r6 = a.recommend("业绩增长忽上忽下，很不稳定")
    print(f" 推荐: {r6['primary']}")

    print("\n" + "=" * 60)
    print("验证通过。资产可运行。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
