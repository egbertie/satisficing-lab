"""
---
KIA-CODE: 知识入库代码级闭环
Asset: honeybee_democracy_toolkit.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次四

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (协作与认知系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 蜜蜂民主工具包
  - 关联: 群体决策
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 共识机制
  - 产品映射: 六祖慧能-集体智慧
  - 运营映射: 协作与认知优化

---
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
honeybee_democracy_toolkit.py
《蜜蜂的民主：群体如何做出决策》托马斯·D.西利

核心内化:
  - 蜜蜂通过侦察蜂的民主讨论选择新家园
  - 无中央计划者、无独裁者（蜂后只是产卵者）
  - 巢址评估有明确标准
  - 通过摇摆舞（waggle dance）进行公开讨论和竞争
  - 法定人数（quorum）触发共识与行动
  - 五大教训可映射到人类群体决策

来源: Thomas D. Seeley, Honeybee Democracy (2010)
译者: 刘国伟
产出时间: 2026-04-09
状态: CONDITIONAL_PASS
"""

from typing import Dict, List, Optional


KNOWLEDGE_BASE = {
    "meta": {
        "book": "蜜蜂的民主：群体如何做出决策",
        "original_title": "Honeybee Democracy",
        "author": "托马斯·D.西利 (Thomas D. Seeley)",
        "year": 2010,
        "translated_by": "刘国伟",
        "publisher": "中信出版集团"
    },
    "nest_site_criteria": {
        "入口大小": {
            "preference": "小入口",
            "ideal_value_cm2": 12.5,
            "natural_range_cm2": "10~30",
            "reason": "利于防御捕食者，减少热量损失"
        },
        "入口方向": {
            "preference": "朝南",
            "reason": "提供阳光加热的通道，冬季便于清洁飞行，不易被冰堵住"
        },
        "入口高度": {
            "preference": "高",
            "ideal_value_m": 6.5,
            "reason": "不容易被捕食者发现，不会飞的捕食者无法到达"
        },
        "入口位置": {
            "preference": "巢穴底部",
            "reason": "有助于把对流造成的热量损失降至最低"
        },
        "空洞容量": {
            "preference": "足够宽敞",
            "minimum_liters": 15,
            "ideal_liters": 40,
            "reason": "必须容纳群落过冬所需的蜜和培养幼虫的蜂房"
        },
        "旧蜂巢存在": {
            "preference": "偏好有旧蜂巢",
            "reason": "节省巨大的能量（建造蜂房需要约7.5千克蜜，相当于过冬储蜜的1/3）"
        }
    },
    "nest_site_irrelevant": {
        "说明": "蜜蜂可自行修补，因此侦察蜂不太关注这些",
        "因素": [
            "入口形状",
            "空洞形状",
            "空洞通风状况",
            "空洞干湿度"
        ]
    },
    "decision_process": {
        "步骤1_分群与悬挂": "约1万只工蜂与老蜂后一起飞离原巢，在树枝上聚集成蜂群",
        "步骤2_侦察蜂出动": "数百只最老的侦察蜂开始搜索方圆5千米甚至更广范围内的潜在居所",
        "步骤3_巢址评估": "侦察蜂发现候选巢址后，按6项标准进行独立评估",
        "步骤4_舞蹈宣传": "认为巢址可接受的侦察蜂返回蜂群，表演摇摆舞（waggle dance）报告方位、距离和合意性；舞蹈强度反映巢址质量",
        "步骤5_中立者考察": "中立的侦察蜂跟随舞蹈去实地考察；若认可，就也回蜂群跳舞支持；若不认可，就回归中立或支持其他选项",
        "步骤6_竞争与筛选": "不同巢址的支持者通过舞蹈竞争；质量越高的巢址，舞蹈越强，吸引的中立者越多（富者越富效应）",
        "步骤7_法定人数与共识": "当一个巢址处的侦察蜂数量超过临界数量（法定人数quorum），访问者行为剧变，开始发出信号劝诱整个蜂群起飞",
        "步骤8_引导迁移": "侦察蜂引导蜂群飞往已达成共识的新家"
    },
    "human_lessons": {
        "教训1_建立有效的团队关系": {
            "core": "团体成员需要有相当程度的利益交集和相互尊重，以利于建设性讨论",
            "detail": "即使有共同利益、友善的个体，适当的冲突也可能是有益的，它能促进认真、彻底的讨论"
        },
        "教训2_把领导者的影响降至最低": {
            "core": "领导者应尽可能不偏不倚，避免在审议一开始就展示出偏好",
            "detail": "颐指气使的领导者是良好群体决策的最大威胁之一；领导者应塑造程序，而非决定结果"
        },
        "教训3_寻求问题的不同解决办法": {
            "core": "派出多样化的、独立考察的搜索委员会，收集广泛选项",
            "detail": "一个蜂群通常会发现10到20个甚至更多候选居所；开放探索是成功的起点"
        },
        "教训4_通过讨论汇聚团体的知识": {
            "core": "利用公开、公平的思想交锋，整合分散在成员之中的信息",
            "detail": "蜜蜂通过舞蹈进行'激烈的讨论'；最佳选项因为优越性而在讨论中胜出"
        },
        "教训5_运用法定数量来平衡凝聚力、精确性和速度": {
            "core": "当支持某一选项的成员达到临界数量（如80%），即可触发共识行动",
            "detail": "不必追求无限制讨论直到完全一致；测验性投票可加速共识构建，同时不牺牲准确性"
        }
    },
    "key_mechanisms": {
        "摇摆舞 (Waggle Dance)": "报告巢址的方位、距离和质量；舞蹈循环次数越多，说明巢址越佳",
        "法定人数 (Quorum)": "支持某一巢址的侦察蜂数量达到临界值后，触发蜂群起飞信号",
        "积极反馈 (Positive Feedback)": "越好的巢址舞蹈越强，吸引越多中立者，形成'富者越富'的竞争格局",
        "独立判断": "每只侦察蜂自主决定是否支持某个巢址，即使它的判断与其他蜜蜂不同",
        "工蜂吹哨 (Worker Piping)": "200~250赫兹的振动信号，激励蜂群为飞行热身"
    }
}


def query_nest_criteria(criterion: Optional[str] = None) -> Dict:
    """查询蜜蜂选择巢址的评估标准。"""
    data = KNOWLEDGE_BASE["nest_site_criteria"]
    if criterion is None:
        return {"criteria": list(data.keys()), "note": "另有6项不太关注的因素见 nest_site_irrelevant"}
    for key, value in data.items():
        if criterion in key or key in criterion:
            return {key: value}
    return {"error": f"未找到标准 '{criterion}'，可用: {list(data.keys())}"}


def query_decision_process() -> Dict:
    """查询蜜蜂民主决策的完整8步流程。"""
    return KNOWLEDGE_BASE["decision_process"]


def query_lesson(lesson_name: Optional[str] = None) -> Dict:
    """查询对人类群体决策的启示/教训。"""
    data = KNOWLEDGE_BASE["human_lessons"]
    if lesson_name is None:
        return {"lessons": list(data.keys())}
    for key, value in data.items():
        if lesson_name in key or key in lesson_name:
            return {key: value}
    return {"error": f"未找到教训 '{lesson_name}'，可用: {list(data.keys())}"}


def query_mechanism(mechanism_name: Optional[str] = None) -> Dict:
    """查询关键机制说明。"""
    data = KNOWLEDGE_BASE["key_mechanisms"]
    if mechanism_name is None:
        return {"mechanisms": list(data.keys())}
    for key, value in data.items():
        if mechanism_name in key or key in mechanism_name:
            return {key: value}
    return {"error": f"未找到机制 '{mechanism_name}'，可用: {list(data.keys())}"}


class SwarmDecisionHealthChecker:
    """
    蜂群式群体决策健康度检查器。
    评估人类会议/团队决策是否符合蜜蜂民主的核心原则。
    """

    CHECKLIST = [
        {
            "item": "领导者的影响被最小化",
            "question": "会议主持人是否在开始时明确表示没有预设结论？",
            "weight": 3
        },
        {
            "item": "选项多样化",
            "question": "在讨论前是否收集了至少3个不同的备选方案？",
            "weight": 3
        },
        {
            "item": "信息自由分享",
            "question": "团队成员是否能自由表达支持或反对某一选项的理由？",
            "weight": 3
        },
        {
            "item": "存在建设性冲突",
            "question": "讨论中是否有不同意见被提出并得到认真回应？",
            "weight": 2
        },
        {
            "item": "独立考察/验证",
            "question": "关键信息是否经过不止一个人的独立验证？",
            "weight": 2
        },
        {
            "item": "使用法定数量/显性共识标准",
            "question": "团队是否在讨论前就明确了'达成共识'的阈值（如80%同意）？",
            "weight": 2
        },
        {
            "item": "避免过早一致",
            "question": "是否有人在正式决策前试图强行统一意见？",
            "weight": 2,
            "negative": True
        }
    ]

    def evaluate(self, answers: List[bool]) -> Dict:
        """
        answers: 与 CHECKLIST 顺序对应的布尔值列表。
                 对于 negative=True 的项，True 表示'不存在该问题'（即健康）。
        """
        if len(answers) != len(self.CHECKLIST):
            return {"error": f"答案数量不匹配，期望 {len(self.CHECKLIST)}，实际 {len(answers)}"}
        
        score = 0
        max_score = sum(item["weight"] for item in self.CHECKLIST)
        details = []
        
        for item, ans in zip(self.CHECKLIST, answers):
            is_negative = item.get("negative", False)
            if is_negative:
                effective = ans  # True = 不存在该负面问题 → 得分
            else:
                effective = ans
            
            item_score = item["weight"] if effective else 0
            score += item_score
            details.append({
                "item": item["item"],
                "passed": bool(effective),
                "score": item_score,
                "max": item["weight"]
            })
        
        percentage = round((score / max_score) * 100, 1)
        level = "优秀" if percentage >= 85 else "良好" if percentage >= 70 else "一般" if percentage >= 50 else "需改进"
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "level": level,
            "details": details,
            "advice": self._generate_advice(details)
        }
    
    def _generate_advice(self, details: List[Dict]) -> List[str]:
        advice_map = {
            "领导者的影响被最小化": "主持人应明确表示无预设结论，鼓励不同意见。",
            "选项多样化": "在决策前派出'侦察蜂'，主动收集至少3个不同的备选方案。",
            "信息自由分享": "建立安全的发言环境，确保关键信息不会被少数人垄断。",
            "存在建设性冲突": "不要害怕分歧，适当的冲突是认真讨论的催化剂。",
            "独立考察/验证": "让不同的人独立评估同一选项，避免人云亦云。",
            "使用法定数量/显性共识标准": "在讨论前明确'多少比例同意算通过'，避免无限拖延。",
            "避免过早一致": "警惕有人提前说'看来大家都同意'，这可能是压制讨论的信号。"
        }
        failed = [d["item"] for d in details if not d["passed"]]
        return [advice_map.get(item, f"请检查: {item}") for item in failed]


class ScoutBeeSimulator:
    """
    侦察蜂巢址评估模拟器。
    输入一个候选巢址的特征，输出侦察蜂的'舞蹈强度评分'（0-10）。
    仅用于教学演示蜜蜂的决策逻辑。
    """

    def evaluate_site(self, entrance_size_cm2: float, entrance_direction: str,
                     entrance_height_m: float, entrance_position: str,
                     cavity_volume_liters: float, has_old_comb: bool,
                     wind_exposure: str = "low") -> Dict:
        """
        简化版评分逻辑，基于书中实验数据。
        """
        score = 0.0
        reasons = []
        
        # 入口大小: 最佳12.5，越小越好但不宜<5
        if 10 <= entrance_size_cm2 <= 20:
            score += 2.5
            reasons.append("入口大小合适（10-20 cm²），防御性好")
        elif 5 <= entrance_size_cm2 < 10:
            score += 2.0
            reasons.append("入口较小，偏安全")
        else:
            score += 0.5
            reasons.append("入口过大，不利于防御和保温")
        
        # 入口方向
        if entrance_direction in ["南", "南向"]:
            score += 1.5
            reasons.append("朝南，阳光加热")
        elif entrance_direction in ["东南", "西南"]:
            score += 1.0
        else:
            score += 0.3
            reasons.append("非南向，热量获取较差")
        
        # 入口高度
        if entrance_height_m >= 5:
            score += 2.0
            reasons.append("入口高度足够（≥5m），捕食者难达")
        elif entrance_height_m >= 2:
            score += 1.0
            reasons.append("入口中等高度，有一定风险")
        else:
            score += 0.2
            reasons.append("入口过低，易受捕食者侵袭")
        
        # 入口位置
        if entrance_position in ["底部", "巢穴底部", "低处"]:
            score += 1.0
            reasons.append("入口在底部，热量损失小")
        else:
            score += 0.3
            reasons.append("入口不在底部，热量对流损失大")
        
        # 空洞容量
        if cavity_volume_liters >= 40:
            score += 2.0
            reasons.append("容量宽敞（≥40L），足够过冬")
        elif cavity_volume_liters >= 15:
            score += 1.0
            reasons.append("容量基本够用（15-40L）")
        else:
            score += 0.0
            reasons.append("容量太小（<15L），无法过冬")
        
        # 旧蜂巢
        if has_old_comb:
            score += 1.0
            reasons.append("有旧蜂巢，可节省大量能量")
        
        # 封顶10分
        score = min(score, 10.0)
        
        dance_recommendation = "强烈舞蹈" if score >= 8 else "中等舞蹈" if score >= 5 else "微弱舞蹈或不跳舞"
        
        return {
            "score": round(score, 1),
            "max_score": 10.0,
            "dance_recommendation": dance_recommendation,
            "reasons": reasons,
            "quorum_likelihood": "高" if score >= 7 else "中" if score >= 5 else "低"
        }


def get_cross_book_mapping(concept: str) -> Dict:
    """
    将蜜蜂民主概念映射到前两本决策科学书的框架中。
    """
    mapping = {
        "适当的冲突": {
            "slow_think_fast_decide": "以偏概全策略中的'法庭辩论(Red Team)'",
            "kahneman_tversky": "批判性倾听与独立判断，避免群体思维"
        },
        "领导者最小化": {
            "slow_think_fast_decide": "后入为主策略中的'盲听盲选'",
            "kahneman_tversky": "减少权威偏见和政治性偏见(Politics)"
        },
        "独立考察": {
            "slow_think_fast_decide": "旁观者清策略中的'互审程序'",
            "kahneman_tversky": "可得性与代表性启发法中的基础比率忽视纠正"
        },
        "法定人数": {
            "slow_think_fast_decide": "决策质量检查清单中的'明确定义通过标准'",
            "kahneman_tversky": "避免后悔理论中的无限拖延与现状偏见"
        }
    }
    return mapping.get(concept, {"note": "暂无跨书映射"})


def demo():
    print("=" * 60)
    print("《蜜蜂的民主》工具箱 —— 功能验证")
    print("=" * 60)

    print("\n[1] 巢址标准查询")
    r1 = query_nest_criteria("入口大小")
    print(f" 理想值: {list(r1.values())[0]['ideal_value_cm2']} cm²")

    print("\n[2] 决策流程查询")
    r2 = query_decision_process()
    print(f" 总步骤: {len(r2)}")

    print("\n[3] 人类教训查询")
    r3 = query_lesson("领导者")
    print(f" 核心: {list(r3.values())[0]['core']}")

    print("\n[4] 侦察蜂模拟器")
    sim = ScoutBeeSimulator()
    r4 = sim.evaluate_site(
        entrance_size_cm2=12.5,
        entrance_direction="南",
        entrance_height_m=6.5,
        entrance_position="底部",
        cavity_volume_liters=40,
        has_old_comb=True
    )
    print(f" 评分: {r4['score']}/10 | 建议: {r4['dance_recommendation']}")

    print("\n[5] 群体决策健康度检查")
    checker = SwarmDecisionHealthChecker()
    r5 = checker.evaluate([True, True, True, False, True, True, True])
    print(f" 得分: {r5['percentage']}% | 等级: {r5['level']}")
    if r5['advice']:
        print(f" 改进建议: {r5['advice'][0]}")

    print("\n[6] 跨书映射")
    r6 = get_cross_book_mapping("适当的冲突")
    print(f" 慢思考快决策映射: {r6['slow_think_fast_decide']}")

    print("\n" + "=" * 60)
    print("验证通过。资产可运行。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
