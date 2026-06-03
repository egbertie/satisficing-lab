#!/usr/bin/env python3
"""
知识内容深度提取器 - 手动分配未覆盖Skill
目标: 覆盖率从79.2%提升到85%+
"""

import json

# 手动分配未覆盖的Skill
manual_assignments = {
    "行为设计": ["behavioral-design"],
    "客户价值": ["client-value-system"],
    "经济情报": ["economic-intelligence"],
    "错误防护": ["error-guard"],
    "实验进化": ["evolution-experiment-lab"],
    "视频编辑": ["ffmpeg-video-editor"],
    "搜索工具": ["firecrawl-search", "multi-search-engine", "openclaw-tavily-search", "smart-web-scraper"],
    "新闻摘要": ["news-summary"],
    "笔记工具": ["obsidian"],
    "优化管理": ["optimization-prioritizer", "optimization-rollback-guard"],
    "专利助手": ["patent-assistant"],
    "质量评估": ["quality-assessment"],
    "通讯工具": ["slack"],
    "战略分析": ["swotpal-swot-analysis"],
    "任务协调": ["task-coordinator"],
    "资源监控": ["token-weekly-monitor"]
}

def apply_manual_assignments():
    # 读取当前概念索引
    with open("/root/.openclaw/workspace/knowledge/system/concept_skill_index_v2.json", 'r') as f:
        concept_index = json.load(f)
    
    # 应用手动分配
    newly_covered = 0
    for concept, skills in manual_assignments.items():
        if concept not in concept_index:
            concept_index[concept] = []
        for skill in skills:
            if skill not in concept_index[concept]:
                concept_index[concept].append(skill)
                newly_covered += 1
    
    # 保存更新后的索引
    with open("/root/.openclaw/workspace/knowledge/system/concept_skill_index_v3.json", 'w') as f:
        json.dump(concept_index, f, indent=2, ensure_ascii=False)
    
    # 计算覆盖率
    all_skills = set()
    covered = set()
    for concept, skills in concept_index.items():
        covered.update(skills)
    
    # 总Skill数
    with open("/root/.openclaw/workspace/knowledge/system/skill_knowledge_index.json", 'r') as f:
        skill_data = json.load(f)
    total = len(skill_data['skills'])
    
    coverage = len(covered) / total * 100
    
    print(f"更新后覆盖: {len(covered)}/{total} ({coverage:.1f}%)")
    print(f"新增覆盖: {newly_covered}个Skill")
    print(f"\n概念维度: {len(concept_index)}个")
    
    # 保存报告
    report = {
        "task": "知识内容提取补全(手动分配)",
        "start_coverage": 79.2,
        "target_coverage": 85.0,
        "actual_coverage": coverage,
        "newly_covered": newly_covered,
        "total_concepts": len(concept_index),
        "status": "completed" if coverage >= 85 else "partial"
    }
    
    with open("/root/.openclaw/workspace/memory/task1_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    return coverage

if __name__ == "__main__":
    coverage = apply_manual_assignments()
    print(f"\n任务完成: 覆盖率 {coverage:.1f}%")
    if coverage >= 85:
        print("✅ 目标达成!")
    else:
        print(f"⚠️ 未达目标，还需 {(85-coverage)/100*144:.0f} 个Skill")
