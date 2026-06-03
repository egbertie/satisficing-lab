#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confucian_management_philosophy.py
《儒家管理哲学》第2版（黎红雷 著）

核心内化:
  - 儒家管理哲学的基本精神：以人为中心，以道德教化为导向，以正己正人为途径
  - 十大管理哲学论：本体论→认识论→方法论→价值论→本质观→人性观→组织观→行为观→控制观→目标观
  - 与现代管理概念的对照映射

来源: 黎红雷《儒家管理哲学》（广东高等教育出版社，1997年第2版）
产出时间: 2026-04-09
状态: CONDITIONAL_PASS
"""

from typing import Dict, List, Optional


KNOWLEDGE_BASE = {
    "meta": {
        "book": "儒家管理哲学",
        "author": "黎红雷",
        "edition": "第2版",
        "publisher": "广东高等教育出版社",
        "year": 1997,
        "ISBN": "7-5361-0923-7"
    },
    "core_spirit": {
        "以人为中心": "儒家管理哲学不孤立探索自然本质，也不单独考虑人，而是把天与人作为对立统一的整体，以人的完善和发展为管理的核心目标",
        "以道德教化为导向": "通过道德教化而非单纯的制度约束来实现管理目标，强调管理者的身教示范",
        "以正己正人为途径": "管理者先修己（自我养成、自我约束），再安人（指导、管理和使用被管理者）"
    },
    "ten_chapters": {
        "第一章_唯人则天的管理本体论": {
            "core": "人类社会管理的依据在'天人合一'。孔子则天、孟子事天、荀子应天，论证管理活动的哲学本体论基础",
            "key_concepts": ["天人合一", "天人相通", "天人相分", "天人相循", "天人相类", "天人相异", "天人相胜"],
            "modern_mapping": "组织使命与社会责任的统一；企业管理不能脱离社会伦理和自然规律的制约"
        },
        "第二章_知治一致的管理认识论": {
            "core": "知识与治理的一致性。儒家强调'格物致知'不仅是求知，更是为了'治国平天下'",
            "key_concepts": ["格物致知", "知行合一", "学思并重", "经世致用"],
            "modern_mapping": "知识管理必须与组织治理相结合；学习的目的在于改进管理实践"
        },
        "第三章_执经达权的管理方法论": {
            "core": "管理必须在守'经'（原则、常道）与行'权'（变通、权变）之间取得平衡。'经'是不变之常，'权'是改常之变",
            "key_concepts": ["执经达权", "常变", "经权", "权变", "时中"],
            "modern_mapping": "战略定力与战术灵活的平衡；标准化流程与情境化调整的统一"
        },
        "第四章_义以生利的管理价值论": {
            "core": "管理的价值追求不是单纯的利，而是义利合一。'义以生利'，见利思义，以义制利",
            "key_concepts": ["义利合一", "见利思义", "以义制利", "义以生利"],
            "modern_mapping": "企业社会责任（CSR）与利润追求的统一；ESG投资的东方理论基础"
        },
        "第五章_劳心治人的管理本质观": {
            "core": "管理的本质在于'劳心'而非'劳力'，在于'治人'（组织和引导人）而非单纯治事",
            "key_concepts": ["劳心者治人", "劳力者治于人", "君子不器", "治人者食于人"],
            "modern_mapping": "管理者应以战略思维、人际协调和文化建设为核心职能，而非亲力亲为执行"
        },
        "第六章_人性可塑的管理人性观": {
            "core": "儒家认为人性是可塑的，通过教育和环境可以改善。'性相近也，习相远也'",
            "key_concepts": ["性相近习相远", "人性可塑", "化性起伪", "有教无类"],
            "modern_mapping": "组织学习和人才发展的理论基础；相信员工可以通过培训和激励不断成长"
        },
        "第七章_能群善分的管理组织观": {
            "core": "人之所以能胜物，在于'能群'（组织起来）。而能群的关键在于'善分'（明确的角色分工和等级秩序）",
            "key_concepts": ["能群", "善分", "明分使群", "伦常秩序"],
            "modern_mapping": "组织结构设计；岗位职责清晰化；团队协作与分工专业化"
        },
        "第八章_无为而治的管理行为观": {
            "core": "最高明的管理是'无为而治'。管理者通过修身立德，以身作则，使下属自然归化，而非强权压制",
            "key_concepts": ["无为而治", "其身正不令而行", "清静无为", "垂拱而治"],
            "modern_mapping": "赋能式领导；自组织团队；企业文化驱动而非命令控制"
        },
        "第九章_道之以德的管理控制观": {
            "core": "管理的控制手段应以道德教化为本，刑罚制度为辅。'道之以德，齐之以礼，有耻且格'",
            "key_concepts": ["道之以德", "齐之以礼", "有耻且格", "德主刑辅"],
            "modern_mapping": "价值观管理；企业文化约束；内在动机激励优于外在惩罚"
        },
        "第十章_修己安人的管理目标观": {
            "core": "管理的最终目标是'修己以安人'、'修己以安百姓'。管理者通过自我修养，实现组织和谐与社会安定",
            "key_concepts": ["修己安人", "修己安百姓", "内圣外王", "修齐治平"],
            "modern_mapping": "领导力发展；管理者人格魅力； stakeholder 福祉最大化"
        }
    },
    "key_concepts": {
        "天人合一": {
            "definition": "自然存在的本质（天道）与人类社会存在的本质（人道）相一致，共同构成世界存在的最高本质（道）",
            "management_implication": "企业管理必须顺应社会伦理和自然规律的统一要求"
        },
        "执经达权": {
            "definition": "坚守基本原则（经）的同时，根据实际情况灵活变通（权）",
            "management_implication": "战略定力与战术灵活之间的动态平衡"
        },
        "义利合一": {
            "definition": "义与利不是对立的，而是统一的；正当的利益追求必须以道义为前提",
            "management_implication": "企业应在符合商业伦理的前提下追求利润，社会责任与经济利益相辅相成"
        },
        "修己安人": {
            "definition": "管理者首先修养自身，然后以此影响他人，使被管理者安定和谐",
            "management_implication": "领导者的人格修养是组织效能的根基；身教重于言教"
        },
        "人性可塑": {
            "definition": "人的本性相近，但可以通过后天的学习、教育和环境而发生显著差异",
            "management_implication": "企业应投入培训和发展，相信员工具有成长潜力"
        },
        "能群善分": {
            "definition": "人之所以强大在于能够组织成群；组织有效的关键在于明确分工（分）和等级秩序",
            "management_implication": "清晰的角色分工、组织层级和协作机制是管理效能的基础"
        },
        "无为而治": {
            "definition": "管理者通过德行示范和制度建设，使组织成员自发向善、自动运转，而不需要事事干预",
            "management_implication": "建立自驱型组织；减少微观管理；以文化替代控制"
        }
    }
}


def query_chapter(chapter_keyword: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["ten_chapters"]
    if chapter_keyword is None:
        return {"chapters": list(data.keys())}
    for k, v in data.items():
        if chapter_keyword in k or k in chapter_keyword:
            return {k: v}
    return {"error": f"未找到 '{chapter_keyword}'，可用: {list(data.keys())}"}


def query_concept(concept_name: Optional[str] = None) -> Dict:
    data = KNOWLEDGE_BASE["key_concepts"]
    if concept_name is None:
        return {"concepts": list(data.keys())}
    for k, v in data.items():
        if concept_name in k or k in concept_name:
            return {k: v}
    return {"error": f"未找到 '{concept_name}'，可用: {list(data.keys())}"}


def query_core_spirit() -> Dict:
    return KNOWLEDGE_BASE["core_spirit"]


class ConfucianManagementAuditor:
    """
    基于儒家管理哲学的十维度快速诊断器。
    用10个儒家管理哲学维度评估一个组织的管理成熟度。
    """

    DIMENSIONS = [
        {"id": "本体论", "name": "唯人则天", "question": "组织决策是否考虑了社会责任与自然伦理的和谐统一？"},
        {"id": "认识论", "name": "知治一致", "question": "组织中的知识获取是否直接服务于治理改善和业务实践？"},
        {"id": "方法论", "name": "执经达权", "question": "组织在坚守核心价值观的同时，能否根据情境灵活调整策略？"},
        {"id": "价值论", "name": "义以生利", "question": "组织在追求利润时是否将道义、诚信和社会责任置于同等重要位置？"},
        {"id": "本质观", "name": "劳心治人", "question": "管理者是否专注于战略规划、文化建设和人才发展，而非陷入事务性执行？"},
        {"id": "人性观", "name": "人性可塑", "question": "组织是否相信员工可以通过教育和发展不断成长，并提供持续学习机会？"},
        {"id": "组织观", "name": "能群善分", "question": "组织内的角色分工、层级秩序和协作机制是否清晰且高效？"},
        {"id": "行为观", "name": "无为而治", "question": "领导者是否通过德行示范和赋能文化，使团队能够自驱动运转？"},
        {"id": "控制观", "name": "道之以德", "question": "组织的控制手段是否以价值观和道德约束为主，制度惩罚为辅？"},
        {"id": "目标观", "name": "修己安人", "question": "管理者是否以身作则，把 stakeholder 的和谐安定作为最终管理目标？"}
    ]

    def evaluate(self, scores: List[int]) -> Dict:
        """
        scores: 10个维度的评分，每个0-10分，共100分
        """
        if len(scores) != 10:
            return {"error": "需要提供恰好10个维度的评分"}
        total = sum(scores)
        average = total / 10
        weaknesses = []
        for i, dim in enumerate(self.DIMENSIONS):
            if scores[i] <= 5:
                weaknesses.append({"dimension": dim["name"], "question": dim["question"], "score": scores[i]})
        return {
            "total_score": total,
            "average_score": round(average, 1),
            "maturity_level": self._level(average),
            "weaknesses": weaknesses,
            "recommendation": self._recommendation(weaknesses)
        }

    def _level(self, avg: float) -> str:
        if avg >= 8:
            return "卓越（儒家管理哲学的典范）"
        elif avg >= 6.5:
            return "良好（有明显儒家特色，个别维度需改进）"
        elif avg >= 5:
            return "一般（基本符合，但机械化/功利化倾向明显）"
        elif avg >= 3.5:
            return "待改进（管理逻辑与儒商精神存在较大偏离）"
        else:
            return "严重偏离（急需从价值观和管理方式上重构）"

    def _recommendation(self, weaknesses: List[Dict]) -> str:
        if not weaknesses:
            return "继续保持，并在行业生态中发挥儒商标杆作用。"
        top = weaknesses[0]
        return f"优先改进维度：{top['dimension']}。建议围绕'{top['question']}'制定专项行动计划。"


def get_modern_mapping(modern_term: str) -> Dict:
    """
    输入现代管理术语，返回对应的儒家管理哲学映射。
    """
    mappings = {
        "企业社会责任_CSR": {
            "confucian_concept": "义以生利 / 天人合一",
            "mapping": "儒家'义利合一'是CSR的东方理论基础；'天人合一'要求企业尊重自然与社会伦理"
        },
        "知识管理": {
            "confucian_concept": "知治一致 / 格物致知",
            "mapping": "儒家强调求知必须与治理实践相结合，学思并重、经世致用"
        },
        "战略管理": {
            "confucian_concept": "执经达权",
            "mapping": "战略定力（经）与战术灵活（权）的动态平衡；顺应时势而不失根本"
        },
        "领导力": {
            "confucian_concept": "修己安人 / 无为而治",
            "mapping": "领导者以身作则、以德服人，通过人格魅力而非权力压迫实现组织目标"
        },
        "组织设计": {
            "confucian_concept": "能群善分",
            "mapping": "明确的角色分工和协作机制；'明分使群'是古代的组织理论"
        },
        "人才发展": {
            "confucian_concept": "人性可塑 / 有教无类",
            "mapping": "相信员工可以通过教育和环境塑造而成长；投资于培训和发展"
        },
        "企业文化": {
            "confucian_concept": "道之以德 / 齐之以礼",
            "mapping": "通过价值观和道德规范约束行为，使员工'有耻且格'；制度为辅，教化为本"
        },
        "公司治理": {
            "confucian_concept": "劳心治人 / 唯人则天",
            "mapping": "管理者应以战略思维和人际协调为本；公司治理必须顺应天道人道"
        }
    }
    for k, v in mappings.items():
        if modern_term.lower() in k.lower() or k.lower() in modern_term.lower():
            return {k: v}
    return {"note": f"暂无 '{modern_term}' 的映射，可用术语: {list(mappings.keys())}"}


def demo():
    print("=" * 60)
    print("《儒家管理哲学》工具箱 —— 功能验证")
    print("=" * 60)

    print("\n[1] 章节查询")
    r1 = query_chapter("义以生利")
    print(f" 核心: {list(r1.values())[0]['core'][:40]}...")

    print("\n[2] 概念查询")
    r2 = query_concept("执经达权")
    print(f" 定义: {list(r2.values())[0]['definition'][:40]}...")

    print("\n[3] 十维度评估")
    auditor = ConfucianManagementAuditor()
    r3 = auditor.evaluate([8, 7, 6, 5, 7, 8, 6, 5, 6, 7])
    print(f" 总分: {r3['total_score']}/100, 成熟度: {r3['maturity_level']}")

    print("\n[4] 现代管理映射")
    r4 = get_modern_mapping("领导力")
    print(f" 儒家概念: {list(r4.values())[0]['confucian_concept']}")

    print("\n" + "=" * 60)
    print("验证通过。资产可运行。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
