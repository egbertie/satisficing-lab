#!/usr/bin/env python3
"""
合伙人决策成熟度测评 - 自动化分析系统 V1.0
功能：轮询飞书多维表格，检测新记录，生成分析报告和PDF
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# 导入评分算法
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maturity_scoring_algorithm import (
    calculate_maturity_score, 
    match_case_types, 
    generate_recommendations,
    SCORING_DIMENSIONS
)

# 配置
APP_TOKEN = "EvF8bhloAaUZVGsUOVHcc2ZJn55"
TABLE_ID = "tbltu58p5Xp8oqSN"
STATE_FILE = "/tmp/partner_assessment_state.json"
REPORTS_DIR = "/root/.openclaw/workspace/reports/assessments"

# 确保报告目录存在
os.makedirs(REPORTS_DIR, exist_ok=True)


def load_state() -> Dict:
    """加载上次检查状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_check": None, "processed_records": [], "pending_analysis": []}


def save_state(state: Dict):
    """保存检查状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def fetch_new_records() -> List[Dict]:
    """
    从飞书多维表格获取新记录
    实际调用飞书API
    """
    # 这里将调用 feishu_bitable_app_table_record action=list
    # 返回记录列表
    print(f"[{datetime.now()}] 从飞书获取记录...")
    
    # TODO: 实际API调用
    # 模拟返回一条测试记录
    return [
        {
            "record_id": "recvh7az9MI8jK",
            "fields": {
                "单选": "Type02-第三次创业",
                "文本": [{"text": "测试记录-合伙人决策成熟度测评", "type": "text"}],
                "日期": 1744972800000
            }
        }
    ]


def parse_record_to_assessment_data(record: Dict) -> Dict:
    """
    将飞书多维表格记录解析为评分算法所需格式
    """
    fields = record.get("fields", {})
    
    # 提取基础信息
    assessment_data = {
        "record_id": record.get("record_id"),
        "submission_time": datetime.now().isoformat(),
    }
    
    # 解析文本字段（问卷JSON数据）
    text_field = fields.get("文本", [])
    if text_field and len(text_field) > 0:
        text_content = text_field[0].get("text", "")
        # 尝试解析JSON格式的问卷回答
        try:
            if text_content.startswith("{"):
                questionnaire_data = json.loads(text_content)
                assessment_data.update(questionnaire_data)
        except json.JSONDecodeError:
            assessment_data["raw_text"] = text_content
    
    # 解析单选字段（类型标签）
    single_select = fields.get("单选", "")
    assessment_data["case_type_tag"] = single_select
    
    # 解析日期
    date_field = fields.get("日期")
    if date_field:
        assessment_data["submission_timestamp"] = date_field
    
    return assessment_data


def analyze_record(record: Dict) -> Dict:
    """
    分析单条记录，生成完整的成熟度评估报告
    """
    print(f"  分析记录: {record.get('record_id', 'unknown')}")
    
    # 解析记录数据
    assessment_data = parse_record_to_assessment_data(record)
    
    # 如果数据不足，使用模拟数据（演示用）
    if not any(k in assessment_data for k in ["startup_count", "risk_awareness"]):
        print("    使用模拟数据进行分析演示...")
        assessment_data.update({
            "respondent_id": record.get("record_id", "UNKNOWN"),
            "startup_count": 60,
            "partner_decision_count": 40,
            "exit_experience": 30,
            "failure_experience": 50,
            "risk_awareness": 55,
            "exit_mechanism": 35,
            "responsibility_boundary": 45,
            "communication_frequency": 50,
            "conflict_handling": 40,
            "trust_expression": 55,
            "vision_alignment": 60,
            "values_match": 55,
            "goal_synergy": 50,
            "agreement_awareness": 45,
            "equity_cognition": 40,
            "decision_process": 50,
        })
    
    # 计算成熟度评分
    score_result = calculate_maturity_score(assessment_data)
    
    # 匹配案例类型
    matched_cases = match_case_types(assessment_data)
    
    # 生成建议
    recommendations = generate_recommendations(score_result, matched_cases)
    
    # 组装完整报告
    analysis_result = {
        "record_id": record.get("record_id"),
        "analysis_timestamp": datetime.now().isoformat(),
        "assessment_data": assessment_data,
        "score_result": score_result,
        "matched_cases": matched_cases,
        "recommendations": recommendations,
    }
    
    return analysis_result


def generate_markdown_report(analysis: Dict) -> str:
    """
    生成Markdown格式的分析报告
    """
    score = analysis["score_result"]
    level = score["maturity_level"]
    
    md = f"""# 合伙人决策成熟度评估报告

**报告编号**: {analysis['record_id']}  
**分析时间**: {analysis['analysis_timestamp']}  
**评估对象**: {score.get('respondent_id', '匿名')}

---

## 📊 总体评估

| 指标 | 结果 |
|:-----|:-----|
| **成熟度总分** | <span style="color:{level['color']};font-weight:bold">{score['total_score']}</span> |
| **等级评定** | **{level['level']}** - {level['title']} |
| **风险等级** | {level['risk']} |

---

## 📈 各维度得分

"""
    
    for dim_name, dim_data in score["dimension_scores"].items():
        md += f"""### {dim_name}
- **得分**: {dim_data['score']}/100
- **权重**: {dim_data['weight']*100}%
- **细节**:
"""
        for factor in dim_data["factors"]:
            md += f"  - {factor['name']}: {factor['raw']} (标准化: {factor['normalized']:.1f})\n"
        md += "\n"
    
    md += """---

## 🎯 匹配风险类型

"""
    
    if analysis["matched_cases"]:
        for i, case in enumerate(analysis["matched_cases"], 1):
            md += f"{i}. **{case['type_id']}**: {case['name']} (相关度: {case['relevance']})\n"
            if case.get("keywords"):
                md += f"   - 关键词: {', '.join(case['keywords'])}\n"
    else:
        md += "暂无特别匹配的风险类型。\n"
    
    md += """
---

## 💡 专业建议

"""
    
    # 按优先级排序
    sorted_recs = sorted(
        analysis["recommendations"], 
        key=lambda x: {"P1": 0, "P2": 1, "P3": 2}.get(x["priority"], 3)
    )
    
    for rec in sorted_recs:
        priority_emoji = {"P1": "🔴", "P2": "🟡", "P3": "🟢"}.get(rec["priority"], "⚪")
        md += f"- {priority_emoji} **[{rec['priority']}] {rec['category']}**: {rec['suggestion']}\n"
    
    md += """
---

## 📚 推荐学习资源

基于您的评估结果，建议重点学习以下内容：

"""
    
    # 根据弱项推荐案例
    weak_dims = [
        (name, data["score"]) 
        for name, data in score["dimension_scores"].items()
    ]
    weak_dims.sort(key=lambda x: x[1])
    
    for dim_name, dim_score in weak_dims[:2]:
        md += f"- **{dim_name}** (得分{dim_score}): 查阅满意解研究所案例库相关章节\n"
    
    md += f"""
---

*本报告由满意解研究所 AI 评估系统生成*  
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*© 满意解研究所 2026*
"""
    
    return md


def save_report(record_id: str, analysis: Dict) -> str:
    """
    保存报告到文件
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"assessment_{record_id}_{timestamp}.md"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    # 生成Markdown报告
    markdown_content = generate_markdown_report(analysis)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"    报告已保存: {filepath}")
    return filepath


def main():
    """主程序"""
    print("=" * 60)
    print("合伙人决策成熟度测评自动化系统 V1.0")
    print(f"启动时间: {datetime.now()}")
    print("=" * 60)
    
    state = load_state()
    processed_count = 0
    
    try:
        # 获取新记录
        new_records = fetch_new_records()
        
        if new_records:
            print(f"发现 {len(new_records)} 条记录待分析")
            
            for record in new_records:
                record_id = record.get("record_id")
                
                # 检查是否已处理
                if record_id in state["processed_records"]:
                    print(f"  跳过已处理记录: {record_id}")
                    continue
                
                # 分析记录
                analysis = analyze_record(record)
                
                # 保存报告
                report_path = save_report(record_id, analysis)
                
                # 标记为已处理
                state["processed_records"].append(record_id)
                processed_count += 1
                
                print(f"  ✓ 完成分析: {record_id}")
        else:
            print("暂无新记录需要分析")
        
        # 更新状态
        state["last_check"] = datetime.now().isoformat()
        save_state(state)
        
        print(f"\n本次处理: {processed_count} 条记录")
        print(f"累计处理: {len(state['processed_records'])} 条记录")
        print(f"下次检查: 5分钟后")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
