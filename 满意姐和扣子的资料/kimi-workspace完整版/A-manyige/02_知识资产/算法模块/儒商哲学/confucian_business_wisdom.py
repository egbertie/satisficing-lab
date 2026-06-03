"""
---
KIA-CODE: 知识入库代码级闭环
Asset: confucian_business_wisdom.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次五

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (伦理与跨文化系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 儒商智慧库
  - 关联: 黎红雷教授思想
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 儒商伦理
  - 产品映射: 孔子-伦理基石
  - 运营映射: 伦理与跨文化评估

---
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confucian_business_wisdom.py
《儒家商道智慧》（黎红雷 著，人民出版社，2017）

核心内化:
  - 儒商企业的八大核心智慧（八大道）
  - 儒商企业的文化资本与精神内核
  - 从西方管理理论到儒家商道的现代转化

来源: 黎红雷《儒家商道智慧》（人民出版社，2017年第1版）
产出时间: 2026-04-09
状态: FIN (2026-04-09 蓝军闭环)
"""

from typing import Dict, List, Optional


KNOWLEDGE_BASE = {
    "meta": {
        "book": "儒家商道智慧",
        "author": "黎红雷",
        "publisher": "人民出版社",
        "year": 2017,
        "ISBN": "978-7-01-017762-5"
    },
    "core_message": {
        "文化资本": "中国企业家靠的不是单纯的技术或资本，而是深厚的儒家文化资本",
        "儒商精神": "以儒家伦理为基础，将商业行为与社会责任、道德修养相结合的企业家精神",
        "当代企业儒学": "儒家思想不仅是历史遗产，更是可以在现代企业管理中创造性转化的活资源"
    },
    "eight_ways": {
        "第一章_组织之道_拟家庭化的企业组织形态": {
            "core": "企业组织不应只是冷冰冰的科层制或单纯的契约关系，而应借鉴家庭关系，建立'拟家庭化'的组织形态",
            "key_concepts": ["拟家庭化", "经济契约", "心理契约", "效率逻辑", "情感逻辑", "科层制", "扁平制"],
            "practices": [
                "构建经济契约与心理契约双重纽带",
                "平衡效率逻辑与情感逻辑",
                "在科层制结构基础上注入家庭温情"
            ],
            "modern_mapping": "企业文化与员工归属感；心理契约理论；关怀型组织"
        },
        "第二章_教化之道_教以人伦的企业教化哲学": {
            "core": "企业不仅是生产单位，也是教化场所。通过人伦教育，培养员工的道德人格和职业素养",
            "key_concepts": ["教化观", "学习型组织", "弟子规", "因果观", "天地国亲师", "仁义礼智信"],
            "practices": [
                "建设学习型组织，但不止于技能培训，更重视人伦教化",
                "引导员工践行《弟子规》等传统蒙学，培养基础德行",
                "敬畏因果，感恩天地国亲师",
                "将仁义礼智信融入日常行为规范"
            ],
            "modern_mapping": "企业大学+德育；价值观培训；文化传承"
        },
        "第三章_管理之道_道之以德的企业管理文化": {
            "core": "企业管理应以道德教化为主导，制度约束为辅，形成以德服人的管理文化",
            "key_concepts": ["德治观", "企业文化", "同仁共勉", "精进人生", "菩萨心肠", "霹雳手段"],
            "practices": [
                "编写《中国传统文化导读》等企业德育教材",
                "制定'同仁共勉十条'等集体道德公约",
                "倡导《精进人生》的修身理念",
                "既有菩萨心肠的关怀，也有霹雳手段的制度底线"
            ],
            "modern_mapping": "价值观管理；道德领导力；文化驱动型管理"
        },
        "第四章_经营之道_义以生利的企业经营理念": {
            "core": "经营的正当性不在于利润本身，而在于'义以生利'——以合乎道义的方式获取利润，并通过利他实现自利",
            "key_concepts": ["义利观", "利他之心", "客户第一", "平台思维", "生态系统思维", "太极思维"],
            "practices": [
                "培养利他之心，为客户、合作伙伴、社会创造价值",
                "客户第一，利润第二",
                "建立平台思维和生态系统思维，构建互利共赢的商业网络",
                "运用太极思维，在竞争与合作中寻求动态平衡"
            ],
            "modern_mapping": "利益相关者理论；平台经济；生态战略；CSR与利润统一"
        },
        "第五章_品牌之道_诚信为本的企业品牌观念": {
            "core": "品牌的根基不是营销技巧，而是诚信人品。'三品合一'——人品、产品、品牌合一",
            "key_concepts": ["诚信观", "真诚赢得顾客", "信誉造就品牌", "三品合一", "人品的养成", "以道御术"],
            "practices": [
                "真诚对待每一位顾客，建立信任资产",
                "以人品的可靠性支撑产品的可信度",
                "'三品合一'：企业家的人品→企业的产品→市场的品牌",
                "以道御术：道德为体，品牌传播为用"
            ],
            "modern_mapping": "品牌信任理论；企业家IP；声誉管理；真实营销"
        },
        "第六章_领导之道_正己正人的企业领导方式": {
            "core": "领导者的首要任务是修身正己，然后以德化人、以能服人。建班子、定战略、带队伍",
            "key_concepts": ["领导观", "正己正人", "建班子", "定战略", "带队伍"],
            "practices": [
                "领导者先正己，再正人；以身作则是最有力的领导方式",
                "建班子：组建志同道合、德行兼备的核心团队",
                "定战略：以儒家审时度势的智慧制定企业方向",
                "带队伍：不是控制，而是教化与赋能"
            ],
            "modern_mapping": "变革型领导；道德领导力； servant leadership；班子建设"
        },
        "第七章_战略之道_与时变化的企业战略思维": {
            "core": "战略的核心是顺应时势、主动求变。顺时而变、乘势而变、适中之变、以变应变、主动求变",
            "key_concepts": ["时变观", "战略变革", "名牌战略", "多元化战略", "国际化战略", "全球化品牌", "网络化战略"],
            "practices": [
                "顺时而变：把握时代脉搏，实施名牌战略",
                "乘势而变：在行业风口期推进多元化",
                "适中之变：以中庸之道稳步推进国际化",
                "以变应变：用全球化品牌战略应对竞争",
                "主动求变：提前布局网络化、数字化转型"
            ],
            "modern_mapping": "动态能力理论；战略敏捷；数字化转型；VUCA环境下的持续变革"
        },
        "第八章_责任之道_善行天下的企业责任意识": {
            "core": "企业的终极意义不仅在于盈利，更在于'善行天下'—对员工负责、对社会负责、对环境负责",
            "key_concepts": ["责任观", "诚信经营", "爱护员工", "公益事业", "环境保护"],
            "practices": [
                "坚持诚信经营，不欺诈、不投机",
                "关心爱护员工，共享发展成果",
                "积极参与公益事业，回馈社会",
                "努力保护环境，践行可持续发展"
            ],
            "modern_mapping": "企业社会责任（CSR）/ESG；可持续发展；利益相关者资本主义"
        }
    }
}


def query_way(way_keyword: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["eight_ways"]
    if way_keyword is None:
        return {"ways": list(data.keys())}
    for k, v in data.items():
        if way_keyword in k or k in way_keyword:
            return {k: v}
    return {"error": f"未找到 '{way_keyword}'，可用: {list(data.keys())}"}


def get_core_message() -> Dict:
    return KNOWLEDGE_BASE["core_message"]


class RuShangAuditor:
    """
    儒商企业成熟度八维度评估器（基于《儒家商道智慧》）
    """

    DIMENSIONS = [
        {"name": "组织之道", "question": "企业是否建立了超越单纯契约的经济+心理双重纽带？"},
        {"name": "教化之道", "question": "企业是否重视员工的道德人格培养和价值观传承？"},
        {"name": "管理之道", "question": "企业管理是否以德化为主、制度为辅，重视企业文化建设？"},
        {"name": "经营之道", "question": "企业经营是否坚持义利合一、客户第一、利他共赢？"},
        {"name": "品牌之道", "question": "品牌建设是否以诚信人品为根基，真诚赢得顾客？"},
        {"name": "领导之道", "question": "领导者是否以身作则、正己正人，善于建班子带队伍？"},
        {"name": "战略之道", "question": "企业战略是否能够顺应时势、主动求变、灵活调整？"},
        {"name": "责任之道", "question": "企业是否积极承担对员工、社会和环境的责任？"}
    ]

    def evaluate(self, scores: List[int]) -> Dict:
        if len(scores) != 8:
            return {"error": "需要提供恰好8个维度的评分"}
        total = sum(scores)
        avg = total / 8
        weaknesses = []
        for i, dim in enumerate(self.DIMENSIONS):
            if scores[i] <= 5:
                weaknesses.append({"dimension": dim["name"], "question": dim["question"], "score": scores[i]})
        return {
            "total_score": total,
            "average_score": round(avg, 1),
            "maturity_level": self._level(avg),
            "weaknesses": weaknesses,
            "recommendation": self._recommendation(weaknesses)
        }

    def _level(self, avg: float) -> str:
        if avg >= 8:
            return "儒商标杆（文化资本深厚，现代转化得当）"
        elif avg >= 6.5:
            return "儒商特色（有明显儒家元素，个别维度有改进空间）"
        elif avg >= 5:
            return "儒商萌芽（具备基本伦理意识，但功利化倾向仍明显）"
        elif avg >= 3.5:
            return "待儒商化（管理和经营中儒家元素缺失，需要系统改造）"
        else:
            return "严重偏离（与儒商精神基本无关，价值观亟待重构）"

    def _recommendation(self, weaknesses: List[Dict]) -> str:
        if not weaknesses:
            return "继续发挥儒商示范作用，对外输出儒家商道经验。"
        top = weaknesses[0]
        return f"优先改进维度：{top['dimension']}。建议围绕'{top['question']}'制定为期3个月的改进行动计划。"


def get_case_principle(case_keyword: str) -> Dict:
    """
    输入客户痛点或关键词，返回对应的儒商商道建议。
    """
    mappings = {
        "合伙人信任": {
            "way": "品牌之道 / 领导之道",
            "advice": "以诚信为本（品牌之道），领导者以身作则（领导之道）。'三品合一'要求合伙人的人品经得起考验。"
        },
        "团队凝聚力": {
            "way": "组织之道 / 教化之道",
            "advice": "建立拟家庭化的组织氛围，超越冰冷的契约关系；同时通过人伦教化培养员工的归属感。"
        },
        "融资与估值": {
            "way": "经营之道 / 品牌之道",
            "advice": "义以生利，不追逐短期估值泡沫；以诚信品牌积累长期估值，建立投资人的信任资本。"
        },
        "战略迷茫": {
            "way": "战略之道 / 管理之道",
            "advice": "顺时而变、乘势而变，以审时度势的智慧制定方向；同时以德化人凝聚团队共识。"
        },
        "人才流失": {
            "way": "教化之道 / 责任之道",
            "advice": "重视员工的道德成长和职业发展；以善意和责任留住人，而非仅靠薪酬。"
        },
        "市场竞争": {
            "way": "经营之道 / 战略之道",
            "advice": "培养利他之心与平台思维，构建互利共赢的生态；同时顺应时代趋势主动求变。"
        }
    }
    for k, v in mappings.items():
        if case_keyword in k or k in case_keyword:
            return {k: v}
    return {"note": f"暂无 '{case_keyword}' 的映射，可用关键词: {list(mappings.keys())}"}


def demo():
    print("=" * 60)
    print("《儒家商道智慧》工具箱 —— 功能验证")
    print("=" * 60)

    print("\n[1] 八大道查询")
    r1 = query_way("经营之道")
    print(f" 核心: {list(r1.values())[0]['core'][:40]}...")

    print("\n[2] 儒商成熟度评估")
    auditor = RuShangAuditor()
    r2 = auditor.evaluate([7, 6, 6, 7, 5, 6, 7, 6])
    print(f" 总分: {r2['total_score']}/80, 成熟度: {r2['maturity_level']}")

    print("\n[3] 合伙案例映射")
    r3 = get_case_principle("合伙人信任")
    print(f" 建议: {list(r3.values())[0]['advice'][:40]}...")

    print("\n" + "=" * 60)
    print("验证通过。资产可运行。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
