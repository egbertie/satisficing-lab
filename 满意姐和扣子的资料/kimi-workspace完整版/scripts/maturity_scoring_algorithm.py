#!/usr/bin/env python3
"""
合伙人决策成熟度评分算法 V1.0
基于满意解研究所 12 类型冲突案例库
"""

# 评分维度权重
SCORING_DIMENSIONS = {
    "决策经验": {
        "weight": 0.25,
        "factors": [
            {"name": "创业次数", "field": "startup_count", "max_score": 25},
            {"name": "合伙人决策次数", "field": "partner_decision_count", "max_score": 25},
            {"name": "退出经验", "field": "exit_experience", "max_score": 25},
            {"name": "失败经历", "field": "failure_experience", "max_score": 25},
        ]
    },
    "风险认知": {
        "weight": 0.20,
        "factors": [
            {"name": "风险意识", "field": "risk_awareness", "max_score": 30},
            {"name": "退出机制认知", "field": "exit_mechanism", "max_score": 35},
            {"name": "责任边界认知", "field": "responsibility_boundary", "max_score": 35},
        ]
    },
    "沟通能力": {
        "weight": 0.20,
        "factors": [
            {"name": "沟通频率", "field": "communication_frequency", "max_score": 25},
            {"name": "冲突处理", "field": "conflict_handling", "max_score": 35},
            {"name": "信任表达", "field": "trust_expression", "max_score": 40},
        ]
    },
    "价值观对齐": {
        "weight": 0.15,
        "factors": [
            {"name": "愿景一致性", "field": "vision_alignment", "max_score": 40},
            {"name": "价值观匹配", "field": "values_match", "max_score": 35},
            {"name": "目标协同", "field": "goal_synergy", "max_score": 25},
        ]
    },
    "制度意识": {
        "weight": 0.20,
        "factors": [
            {"name": "协议意识", "field": "agreement_awareness", "max_score": 30},
            {"name": "股权认知", "field": "equity_cognition", "max_score": 35},
            {"name": "决策流程", "field": "decision_process", "max_score": 35},
        ]
    }
}

# 成熟度等级定义
MATURITY_LEVELS = {
    (90, 100): {"level": "A+", "title": "卓越决策者", "color": "#2E7D32", "risk": "极低"},
    (80, 89): {"level": "A", "title": "成熟决策者", "color": "#388E3C", "risk": "低"},
    (70, 79): {"level": "B+", "title": "良好决策者", "color": "#FBC02D", "risk": "可控"},
    (60, 69): {"level": "B", "title": "发展中决策者", "color": "#F57C00", "risk": "中等"},
    (50, 59): {"level": "C", "title": "新手决策者", "color": "#E64A19", "risk": "较高"},
    (0, 49): {"level": "D", "title": "高风险决策者", "color": "#D32F2F", "risk": "高"},
}

# 12类型案例库映射（用于生成建议）
CASE_TYPE_MAPPING = {
    "Type01": {"name": "股权分配冲突", "keywords": ["股权", "分配", "出资", "比例"]},
    "Type02": {"name": "决策权争夺", "keywords": ["决策", "投票", "控制权", "一言堂"]},
    "Type03": {"name": "价值观冲突", "keywords": ["价值观", "愿景", "理念", "分歧"]},
    "Type04": {"name": "责任推诿", "keywords": ["责任", "推诿", "担当", "逃避"]},
    "Type05": {"name": "利益冲突", "keywords": ["利益", "关联交易", "私心", "侵占"]},
    "Type06": {"name": "信任崩塌", "keywords": ["信任", "隐瞒", "欺骗", "背叛"]},
    "Type07": {"name": "沟通障碍", "keywords": ["沟通", "沉默", "冷战", "误解"]},
    "Type08": {"name": "退出机制缺失", "keywords": ["退出", "散伙", "分手", "机制"]},
    "Type09": {"name": "能力不匹配", "keywords": ["能力", "贡献", "付出", "不对等"]},
    "Type10": {"name": "资源争夺", "keywords": ["资源", "争夺", "客户", "渠道"]},
    "Type11": {"name": "外部干预", "keywords": ["家人", "朋友", "外部", "干预"]},
    "Type12": {"name": "声誉危机", "keywords": ["声誉", "品牌", "危机", "公关"]},
}


def calculate_maturity_score(assessment_data: dict) -> dict:
    """
    计算合伙人决策成熟度总分
    
    Args:
        assessment_data: 测评问卷原始数据
        
    Returns:
        包含总分、各维度得分、等级、建议的字典
    """
    dimension_scores = {}
    total_weighted_score = 0
    
    # 计算各维度得分
    for dimension, config in SCORING_DIMENSIONS.items():
        dimension_total = 0
        factor_details = []
        
        for factor in config["factors"]:
            field_value = assessment_data.get(factor["field"], 0)
            # 标准化到0-100
            normalized_score = min(100, max(0, field_value))
            factor_details.append({
                "name": factor["name"],
                "raw": field_value,
                "normalized": normalized_score,
                "max": factor["max_score"]
            })
            dimension_total += normalized_score * (factor["max_score"] / 100)
        
        # 维度加权平均分
        max_possible = sum(f["max_score"] for f in config["factors"])
        dimension_score = (dimension_total / max_possible) * 100 if max_possible > 0 else 0
        dimension_scores[dimension] = {
            "score": round(dimension_score, 1),
            "weight": config["weight"],
            "factors": factor_details
        }
        total_weighted_score += dimension_score * config["weight"]
    
    # 确定成熟度等级
    final_score = round(total_weighted_score, 1)
    maturity_level = None
    for score_range, level_info in MATURITY_LEVELS.items():
        if score_range[0] <= final_score <= score_range[1]:
            maturity_level = level_info
            break
    
    if not maturity_level:
        maturity_level = MATURITY_LEVELS[(0, 49)]
    
    return {
        "total_score": final_score,
        "maturity_level": maturity_level,
        "dimension_scores": dimension_scores,
        "assessment_date": assessment_data.get("submission_time", ""),
        "respondent_id": assessment_data.get("respondent_id", "")
    }


def match_case_types(assessment_data: dict, top_n: int = 3) -> list:
    """
    根据测评数据匹配最相关的案例类型
    
    Args:
        assessment_data: 测评数据
        top_n: 返回前N个最相关的类型
        
    Returns:
        匹配的案例类型列表，带相关性分数
    """
    matches = []
    
    for type_id, type_info in CASE_TYPE_MAPPING.items():
        relevance_score = 0
        matched_keywords = []
        
        # 检查关键词匹配
        for keyword in type_info["keywords"]:
            if keyword in str(assessment_data.values()):
                relevance_score += 10
                matched_keywords.append(keyword)
        
        # 根据具体字段加权
        if type_id == "Type01" and assessment_data.get("equity_cognition", 0) < 50:
            relevance_score += 20
        elif type_id == "Type02" and assessment_data.get("decision_process", 0) < 50:
            relevance_score += 20
        elif type_id == "Type07" and assessment_data.get("communication_frequency", 0) < 50:
            relevance_score += 20
        elif type_id == "Type08" and assessment_data.get("exit_mechanism", 0) < 30:
            relevance_score += 25
        
        if relevance_score > 0:
            matches.append({
                "type_id": type_id,
                "name": type_info["name"],
                "relevance": relevance_score,
                "keywords": matched_keywords
            })
    
    # 按相关性排序
    matches.sort(key=lambda x: x["relevance"], reverse=True)
    return matches[:top_n]


def generate_recommendations(score_result: dict, matched_cases: list) -> list:
    """
    基于评分结果和匹配案例生成建议
    
    Args:
        score_result: 评分结果
        matched_cases: 匹配的案例类型
        
    Returns:
        建议列表
    """
    recommendations = []
    
    # 基于总分生成整体建议
    total_score = score_result["total_score"]
    if total_score >= 80:
        recommendations.append({
            "priority": "P3",
            "category": "整体",
            "suggestion": "决策成熟度良好，建议关注细节优化和持续学习"
        })
    elif total_score >= 60:
        recommendations.append({
            "priority": "P2",
            "category": "整体",
            "suggestion": "决策基础尚可，建议系统学习合伙人治理框架"
        })
    else:
        recommendations.append({
            "priority": "P1",
            "category": "整体",
            "suggestion": "决策风险较高，强烈建议暂缓重大决策，先进行专业咨询"
        })
    
    # 基于弱项维度生成具体建议
    weak_dimensions = [
        (name, data) for name, data in score_result["dimension_scores"].items()
        if data["score"] < 60
    ]
    
    for dim_name, dim_data in sorted(weak_dimensions, key=lambda x: x[1]["score"]):
        recommendations.append({
            "priority": "P2",
            "category": dim_name,
            "suggestion": f"{dim_name}得分{dim_data['score']}，建议针对性强化训练"
        })
    
    # 基于匹配案例生成预防建议
    for case in matched_cases[:2]:  # 只取前2个
        recommendations.append({
            "priority": "P1",
            "category": "风险预防",
            "suggestion": f"警惕【{case['name']}】风险，建议提前建立防范机制"
        })
    
    return recommendations


if __name__ == "__main__":
    # 测试用例
    test_data = {
        "respondent_id": "TEST001",
        "submission_time": "2026-04-18T12:00:00+08:00",
        "startup_count": 80,
        "partner_decision_count": 60,
        "exit_experience": 40,
        "failure_experience": 70,
        "risk_awareness": 65,
        "exit_mechanism": 30,  # 弱项
        "responsibility_boundary": 55,
        "communication_frequency": 45,  # 弱项
        "conflict_handling": 50,
        "trust_expression": 60,
        "vision_alignment": 70,
        "values_match": 65,
        "goal_synergy": 60,
        "agreement_awareness": 40,
        "equity_cognition": 35,  # 弱项
        "decision_process": 45,
    }
    
    result = calculate_maturity_score(test_data)
    matched = match_case_types(test_data)
    recs = generate_recommendations(result, matched)
    
    print("=" * 50)
    print("合伙人决策成熟度测评结果")
    print("=" * 50)
    print(f"总分: {result['total_score']}")
    print(f"等级: {result['maturity_level']['level']} - {result['maturity_level']['title']}")
    print(f"风险等级: {result['maturity_level']['risk']}")
    print("\n各维度得分:")
    for dim, data in result['dimension_scores'].items():
        print(f"  {dim}: {data['score']} (权重{data['weight']*100}%)")
    print("\n匹配案例类型:")
    for case in matched:
        print(f"  {case['type_id']}: {case['name']} (相关度{case['relevance']})")
    print("\n建议:")
    for rec in recs:
        print(f"  [{rec['priority']}] {rec['category']}: {rec['suggestion']}")
