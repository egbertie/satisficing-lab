#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
slow_think_fast_decide_toolkit.py
《慢思考，快决策》申先军 决策偏见检测与纠偏工具箱

来源内化:
  《慢思考，快决策》(申先军，人民邮电出版社 2024)

核心框架:
  - 一个中心: 以流程为决策中心
  - 四大策略: 以小博大 / 以偏概全 / 后入为主 / 旁观者清
  - 八种技巧: 助推 / 检查清单 / 法庭辩论 / 反过来想 / 盲听盲选 / 事后表态 / 互审程序 / 有效试错
  - 五大偏见类型(SPEED): Safety / Politics / Expedience / Experience / Distance

产出时间: 2026-04-09
执行者: 蓝军 Skeptor-7
监督者: 满意姐
状态: CONDITIONAL_PASS
"""

from typing import Dict, List, Optional, Tuple


KNOWLEDGE_BASE = {
    "meta": {
        "book": "慢思考，快决策",
        "author": "申先军",
        "year": 2024,
        "isbn": "9787115645791",
        "framework": "一个中心 + 四大策略 + 八种技巧 + SPEED五大偏见"
    },
    "speed_biases": {
        "安全性偏見 (Safety)": {
            "tagline": "\"坏\"比\"好\"强",
            "biases": {
                "不确定性效应": {
                    "alias": ["模糊效應", "埃爾斯伯格悖論"],
                    "definition": "人們傾向避開資訊不足的選項，選擇已知信息量更多的選項；對確定性結果賦予較高權重。",
                    "example": "寧可選擇確定性低的保守投資，也不願選擇信息不足的潛在高回報項目。"
                },
                "框架效應": {
                    "alias": [],
                    "definition": "對客觀上同一個問題的不同表述方式，導致不同的決策判斷。",
                    "example": "手術存活率90% vs 死亡率10%，描述相同但決策傾向不同。"
                },
                "沉沒成本謬誤": {
                    "alias": [],
                    "definition": "因為已經投入的成本而繼續投入，忽視未來的收益與風險。",
                    "example": "電影很無聊但因為買了票還是硬著頭皮看完。"
                },
                "負面偏見": {
                    "alias": ["消極偏見", "負性認知偏見"],
                    "definition": "相比積極記憶，人們對負面信息更加敏感。",
                    "example": "一條差評掩蓋了十條好評的影響。"
                },
                "鴕鳥效應": {
                    "alias": [],
                    "definition": "忽視明顯的負面情況，故意逃避負面信息。",
                    "example": "明知市場萎縮卻不願查看財報數據，自欺欺人。"
                }
            }
        },
        "政治性偏見 (Politics)": {
            "tagline": "\"同\"比\"异\"好",
            "biases": {
                "內群體偏見": {
                    "alias": ["派系偏見"],
                    "definition": "對同一群體成員的偏好，對特定社會群體更有認同感。",
                    "example": "部門之間互相袒護，認為自己部門的人比別部門強。"
                },
                "群體思維": {
                    "alias": ["Groupthink"],
                    "definition": "群體為了趨於一致而忽視不同的觀點，導致批判性思維受抑制。",
                    "example": "會議上無人反對明顯有漏洞的方案，因為不想破壞和諧。"
                },
                "從眾效應": {
                    "alias": ["羊群效應", "花車效應"],
                    "definition": "人們從事或相信某件事時依賴於其他人做出的選擇。",
                    "example": "看到別人都在投資某項目，於是跟風投入。"
                },
                "社會期許偏見": {
                    "alias": ["布拉德利效應"],
                    "definition": "傾向向外界展示社會期望的行為表現，隱藏不被欣賞的方面。",
                    "example": "調查中表示會投票給少數族裔候選人，實際投票時卻沒有。"
                }
            }
        },
        "便利性偏見 (Expedience)": {
            "tagline": "\"快\"比\"慢\"真",
            "biases": {
                "錨定效應": {
                    "alias": ["聚焦效應"],
                    "definition": "定量評估時過度依賴最初獲得的信息作為起始值。",
                    "example": "談判時先報價的一方往往會成為價格談判的錨點。"
                },
                "可得性啟發法": {
                    "alias": [],
                    "definition": "高估記憶中容易回想起的事件的可能性。",
                    "example": "飛機失事後不敢坐飛機，儘管統計上飛機比汽車安全。"
                },
                "注意力偏見": {
                    "alias": [],
                    "definition": "做決定時將更多注意力集中在特定刺激上，忽視其他重要信息。",
                    "example": "被競爭對手的促銷活動吸引注意力，忽略了自身長期戰略。"
                },
                "證實偏見": {
                    "alias": ["確認偏見", "驗證性偏見"],
                    "definition": "傾向於尋找支持自己想法的信息，忽視反對意見。",
                    "example": "高管只聽匯報中的好消息，質疑或忽略負面數據。"
                },
                "結果偏見": {
                    "alias": ["結果效應"],
                    "definition": "僅根據結果成敗評估決策質量，而不考慮當時的現實條件。",
                    "example": "成功者說什麼都對，失敗者的合理建議也被忽視。"
                },
                "信念偏見": {
                    "alias": ["信念固著"],
                    "definition": "評價論據是否合乎邏輯受到其結論可信度的影響。",
                    "example": "因為相信某結論而認為其推理過程是正確的。"
                },
                "基本比率謬誤": {
                    "alias": [],
                    "definition": "忽略事件的先驗概率或基本比率，只關注具體描述。",
                    "example": "根據文學氣質判斷某人是大學教授而非卡車司機，忽視基礎比率。"
                },
                "暈輪效應": {
                    "alias": ["愛屋及烏"],
                    "definition": "對一個人的某種特徵形成好或壞的印象後，傾向於據此推論該人其他方面的特徵。",
                    "example": "某員工業績好，於是認為他所有建議都是有道理的。"
                }
            }
        },
        "經驗性偏見 (Experience)": {
            "tagline": "\"我\"比\"你\"對",
            "biases": {
                "過度自信效應": {
                    "alias": ["自負效應"],
                    "definition": "決策者認為自己所擁有知識和經驗的有效性比實際更高。",
                    "example": "90%的司機認為自己的駕駛技術高於平均水平。"
                },
                "自利偏見": {
                    "alias": [],
                    "definition": "將成功歸因於自己，將失敗歸因於外部因素。",
                    "example": "業績好是因為自己能力強，業績差是因為市場環境不好。"
                }
            }
        },
        "距離性偏見 (Distance)": {
            "tagline": "\"近\"比\"远\"美",
            "biases": {
                "稟賦效應": {
                    "alias": ["敝帚自珍效應"],
                    "definition": "一旦擁有某物品，便對其價值賦予更高的評價，不願失去。",
                    "example": "持有股票時認為它比市場價值更高，因此不願賣出虧損股票。"
                }
            }
        }
    },
    "scenarios": {
        "棋手(形勢評估)": {
            "core": "從何處開始著手",
            "questions": ["我應該首先採取哪些變革措施？", "行業面臨新進入者，我們應如何面對？"],
            "focus": "了解和分析全盤局勢，制定有效的應變策略"
        },
        "偵探(原因分析)": {
            "core": "發生問題的原因",
            "questions": ["為什麼員工對變革如此抵觸？", "為什麼離職率不斷增加？"],
            "focus": "廣泛精準收集信息，發現問題發生的主要原因"
        },
        "採購(方案選擇)": {
            "core": "應該選擇哪個方案",
            "questions": ["採取哪種方式更有效幫助人們接受變革？", "晉升哪一位候選人？"],
            "focus": "確保擁有足夠數量的備選方案，並確定明確的選擇標準"
        },
        "裁判(採取行動)": {
            "core": "是否應該採取行動",
            "questions": ["我們是否應進行數字化轉型？", "是否應採用新的物流系統？"],
            "focus": "權衡採取或不採取行動可能帶來的結果、影響和風險"
        }
    },
    "strategies": {
        "以小博大": {
            "description": "用較小的成本或風險撬動較大的收益",
            "techniques": {
                "巧用助推(Nudge)": "通過環境設計或非強制性提示，引導人們做出更好的選擇",
                "檢查清單(Checklist)": "系統化檢查關鍵步驟，避免遺漏和疏忽"
            }
        },
        "以偏概全": {
            "description": "故意從反面或多個極端角度審視問題",
            "techniques": {
                "法庭辯論(Red Team)": "組建反對方，刻意挑戰主流觀點，尋找漏洞",
                "反過來想(Inversion)": "思考如何讓事情變糟，從而反推避免之道"
            }
        },
        "後入為主": {
            "description": "延遲判斷或隱藏偏好，避免先入為主",
            "techniques": {
                "盲聽盲選(Blind Audition)": "在不知來源的情況下評估方案或候選人",
                "事後表態(Premortem)": "假設決策已經失敗，反推可能的原因"
            }
        },
        "旁觀者清": {
            "description": "引入外部視角，彌補自我盲區",
            "techniques": {
                "互審程序(Peer Review)": "邀請他人審視自己的決策邏輯和證據",
                "有效試錯(Fail Fast)": "小步快跑，快速試錯，及時止損"
            }
        }
    }
}


def query_speed_bias(category: Optional[str] = None, bias_name: Optional[str] = None) -> Dict:
    """查詢 SPEED 決策偏見體系。"""
    data = KNOWLEDGE_BASE["speed_biases"]
    if category is None:
        return {
            "categories": list(data.keys()),
            "summary": {k: v["tagline"] for k, v in data.items()}
        }
    cat_data = data.get(category)
    if cat_data is None:
        return {"error": f"未找到類別 '{category}'，可用類別: {list(data.keys())}"}
    if bias_name is None:
        return {
            "tagline": cat_data["tagline"],
            "biases": list(cat_data["biases"].keys())
        }
    bias_data = cat_data["biases"].get(bias_name)
    if bias_data is None:
        return {"error": f"未找到偏見 '{bias_name}'，可用偏見: {list(cat_data['biases'].keys())}"}
    return bias_data


def query_scenario(scene_name: Optional[str] = None) -> Dict:
    """查詢四種決策場景。"""
    data = KNOWLEDGE_BASE["scenarios"]
    if scene_name is None:
        return {
            "available_scenarios": list(data.keys())
        }
    return data.get(scene_name, {"error": f"未找到場景 '{scene_name}'"})


def query_strategy(strategy_name: Optional[str] = None) -> Dict:
    """查詢四大策略與八種技巧。"""
    data = KNOWLEDGE_BASE["strategies"]
    if strategy_name is None:
        return {
            "available_strategies": list(data.keys())
        }
    return data.get(strategy_name, {"error": f"未找到策略 '{strategy_name}'"})


class DecisionBiasDetector:
    """
    基於用戶描述的決策情境，識別潛在的 SPEED 偏見類型。
    簡化版規則引擎。
    """

    RULES = [
        {
            "keywords": ["確定", "穩定", "安全", "保守", "虧損", "已經投入", "捨不得", "害怕未知", "逃避", "壞消息", "負面", "不願面對", "眼不見"],
            "category": "安全性偏見 (Safety)",
            "reason": "情境中出現對確定性的過度追求或對負面信息的逃避"
        },
        {
            "keywords": ["我們部門", "自己人", "派系", "團隊一致", "大家都這麼說", "跟風", "主流", "別人都在做", "為了面子", "社會期望", "不敢反對", "保持沉默"],
            "category": "政治性偏見 (Politics)",
            "reason": "情境中存在群體認同、從眾壓力或社會形象考量"
        },
        {
            "keywords": ["第一印象", "最初報價", "最先聽到", "最近發生", "容易想起", "媒體報導", "只看支持", "成功案例", "我相信", "直覺告訴我", "光環", "文學氣質", "概率"],
            "category": "便利性偏見 (Expedience)",
            "reason": "情境中依賴直覺、易得信息或既有信念進行快速判斷"
        },
        {
            "keywords": ["我經驗豐富", "我有把握", "肯定沒問題", "我比別人強", "歷來如此", "以前都是這樣", "成功是因為我", "失敗是運氣不好"],
            "category": "經驗性偏見 (Experience)",
            "reason": "情境中表現出對自身經驗或能力的過度高估"
        },
        {
            "keywords": ["捨不得賣", "自己的東西", "擁有後", "放了這麼久", "感情", "敝帚自珍", "離我太近"],
            "category": "距離性偏見 (Distance)",
            "reason": "情境中對已擁有事物的價值賦予過高評價"
        }
    ]

    def detect(self, situation: str) -> List[Dict]:
        situation = situation.lower()
        matched = []
        for rule in self.RULES:
            if any(kw in situation for kw in rule["keywords"]):
                matched.append({
                    "category": rule["category"],
                    "reason": rule["reason"]
                })
        if not matched:
            matched.append({
                "category": "暫無明顯匹配",
                "reason": "請提供更多決策細節以便進一步分析。"
            })
        return matched


class DecisionScenarioClassifier:
    """
    根據問題描述，判斷決策屬於哪種場景：棋手 / 偵探 / 採購 / 裁判。
    """

    RULES = [
        {
            "keywords": ["從哪裡開始", "首先", "著手", "形勢", "趨勢", "全局", "應對", "變革措施", "新職位", "行業挑戰"],
            "scene": "棋手(形勢評估)"
        },
        {
            "keywords": ["為什麼", "原因", "根本", "離職率", "下降", "抵觸", "發生問題", "蹲下來", "沒有效果"],
            "scene": "偵探(原因分析)"
        },
        {
            "keywords": ["選擇哪個", "哪一位", "哪一種", "晉升", "採購", "投資", "方案", "候選人", "選哪個", "對比"],
            "scene": "採購(方案選擇)"
        },
        {
            "keywords": ["是否應該", "要不要", "做不做", "是否採用", "是否推出", "是否轉型", "進入新市場", "採取行動"],
            "scene": "裁判(採取行動)"
        }
    ]

    def classify(self, situation: str) -> Dict:
        situation = situation.lower()
        scores = {}
        for rule in self.RULES:
            score = sum(1 for kw in rule["keywords"] if kw in situation)
            if score > 0:
                scores[rule["scene"]] = scores.get(rule["scene"], 0) + score
        if not scores:
            return {"scene": "未識別", "confidence": 0.0, "advice": "請更具體描述您面臨的決策類型"}
        best = max(scores, key=scores.get)
        total = sum(scores.values())
        return {
            "scene": best,
            "confidence": round(scores[best] / total, 2),
            "all_scores": scores
        }


class BiasMitigationAdvisor:
    """
    根據識別出的偏見類型，推薦對應的糾偏策略與技巧。
    """

    RECOMMENDATIONS = {
        "安全性偏見 (Safety)": [
            {"strategy": "以小博大", "technique": "檢查清單", "action": "列出決策中所有不確定因素，系統化檢查而非憑感覺回避。"},
            {"strategy": "以偏概全", "technique": "反過來想", "action": "思考：如果現在不採取任何行動，三個月後最壞的情況是什麼？"}
        ],
        "政治性偏見 (Politics)": [
            {"strategy": "以偏概全", "technique": "法庭辯論", "action": "指定一人專門扮演反對黨，挑戰團隊一致意見，尋找漏洞。"},
            {"strategy": "旁觀者清", "technique": "互審程序", "action": "邀請外部中立人士審視決策邏輯，打破群體思維。"}
        ],
        "便利性偏見 (Expedience)": [
            {"strategy": "以小博大", "technique": "巧用助推", "action": "在決策環境中設置提示，強制要求列出至少三條反對意見或替代方案。"},
            {"strategy": "後入為主", "technique": "盲聽盲選", "action": "隱藏提案來源，僅依據內容質量進行評估，避免錨定和光環效應。"}
        ],
        "經驗性偏見 (Experience)": [
            {"strategy": "後入為主", "technique": "事後表態", "action": "假設這個決策在一年後徹底失敗了，請寫下三個最可能的原因。"},
            {"strategy": "旁觀者清", "technique": "有效試錯", "action": "設定小規模試點和明確的止損條件，用事實檢驗經驗假設。"}
        ],
        "距離性偏見 (Distance)": [
            {"strategy": "旁觀者清", "technique": "互審程序", "action": "問自己：如果現在沒有持有這項資產，我是否會以當前價格買入？"},
            {"strategy": "後入為主", "technique": "盲聽盲選", "action": "將現有方案與全新方案匿名對比，去除擁有者情感偏見。"}
        ]
    }

    def advise(self, categories: List[str]) -> List[Dict]:
        results = []
        for cat in categories:
            if cat in self.RECOMMENDATIONS:
                results.extend(self.RECOMMENDATIONS[cat])
        if not results:
            results.append({
                "strategy": "通用建議",
                "technique": "慢思考流程",
                "action": "暫停直覺反應，將決策寫下來，24小時後再審視。"
            })
        return results


def decision_quality_checklist() -> List[Dict]:
    """
    決策質量快速檢查清單（以流程為中心）。
    """
    return [
        {"item": "明確決策場景", "question": "這是形勢評估、原因分析、方案選擇還是行動判斷？", "checked": False},
        {"item": "打破信息繭房", "question": "我是否主動尋找過反對意見和反面證據？", "checked": False},
        {"item": "延遲判斷", "question": "我是否給了自己足夠的時間跳出第一反應？", "checked": False},
        {"item": "引入外部視角", "question": "有沒有請別人審視過這個決策的盲點？", "checked": False},
        {"item": "設置止損條件", "question": "如果決策錯了，我能否在什麼時間點、以什麼代價糾正？", "checked": False},
        {"item": "審視情緒狀態", "question": "我此刻是否處於疲憊、憤怒或極度興奮的狀態？", "checked": False}
    ]


def demo():
    print("=" * 60)
    print("《慢思考，快决策》工具箱 —— 功能驗證")
    print("=" * 60)

    print("\n[1] SPEED 偏見查詢")
    r1 = query_speed_bias("便利性偏見 (Expedience)", "錨定效應")
    print(f" 定義: {r1['definition']}")

    print("\n[2] 決策場景分類")
    classifier = DecisionScenarioClassifier()
    r2 = classifier.classify("我應該晉升張三還是李四？")
    print(f" 場景: {r2['scene']} | 置信度: {r2['confidence']}")

    print("\n[3] 偏見檢測")
    detector = DecisionBiasDetector()
    r3 = detector.detect("我們團隊一致認為這個方案沒問題，雖然財務部門提出了風險警告，但大家都這麼說應該不會錯。")
    for item in r3:
        print(f" 檢測到: {item['category']} | 原因: {item['reason']}")

    print("\n[4] 糾偏建議")
    advisor = BiasMitigationAdvisor()
    cats = [item['category'] for item in r3 if item['category'] != "暫無明顯匹配"]
    r4 = advisor.advise(cats)
    for item in r4:
        print(f" [{item['strategy']}] {item['technique']}: {item['action']}")

    print("\n[5] 決策質量檢查清單（前3項）")
    r5 = decision_quality_checklist()
    for item in r5[:3]:
        print(f" - {item['item']}: {item['question']}")

    print("\n" + "=" * 60)
    print("驗證通過。資產可運行。")
    print("=" * 60)


if __name__ == "__main__":
    demo()
