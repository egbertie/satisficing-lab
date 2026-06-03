"""
---
KIA-CODE: 知识入库代码级闭环
Asset: case_repository_system.py
Status: ✅ 代码级KIA完成
Date: 2026-04-15
Batch: OM-03 Python资产25份代码级KIA-批次三

KIA-Loop:
  - 接收清点: 2026-04-15
  - 轻量提取: 2026-04-15 (代码结构识别)
  - 查重去冗: 2026-04-15 (无重复代码)
  - Tier分级: T1 (核心项目资产)
  - 深度洞察: 2026-04-15 (案例库与决策系统)
  - 血液化: ✅ 完成 (五路图腾映射确认)
  - 归档锁定: 2026-04-15

功能定位:
  - 用途: 案例库系统
  - 关联: 12类型案例库
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 案例管理
  - 产品映射: 司马贺-方法论
  - 运营映射: 案例库与决策支持

---
"""

#!/usr/bin/env python3
# case_repository_system.py - 案例库管理系统
# 来源: 文件2 - 案例库深度方案.docx
# 功能: 基于SECI模型的智能化案例库系统
# 创建时间: 2026-04-04
# 版本: 1.0

import json
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

@dataclass
class Case:
    """案例数据结构"""
    id: str
    title: str
    industry: str
    stage: str  # 天使轮/A轮/B轮等
    founder_profile: Dict
    partner_profile: Dict
    matching_factors: List[str]  # 匹配成功因素
    decision_logic: str  # 决策逻辑
    outcome: str  # 结果
    lessons: str  # 经验教训
    tags: List[str] = field(default_factory=list)
    created_at: str = ""

class CaseRepositorySystem(BaseComponent):
    """
    案例库管理系统
    基于SECI知识转化模型的智能化案例库
    
    SECI模型:
    - S (Socialization): 社会化 - 隐性→隐性
    - E (Externalization): 外显化 - 隐性→显性
    - C (Combination): 组合化 - 显性→显性
    - I (Internalization): 内隐化 - 显性→隐性
    """
    
    def __init__(self):
        super().__init__('case_repository')
        self.metrics = MetricsCollector('case_repo')
        self.data_path = f"{self.workspace}/case_repository"
        Path(self.data_path).mkdir(parents=True, exist_ok=True)
        
        self.cases: Dict[str, Case] = {}
        self.tags_index: Dict[str, List[str]] = {}
        
        self.metrics.record(action='system_init')
    
    def create_case(self, case_data: Dict) -> Case:
        """
        E - 外显化(Externalization)
        将隐性决策经验转化为结构化案例
        """
        case_id = f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        case = Case(
            id=case_id,
            title=case_data.get('title', ''),
            industry=case_data.get('industry', ''),
            stage=case_data.get('stage', ''),
            founder_profile=case_data.get('founder_profile', {}),
            partner_profile=case_data.get('partner_profile', {}),
            matching_factors=case_data.get('matching_factors', []),
            decision_logic=case_data.get('decision_logic', ''),
            outcome=case_data.get('outcome', ''),
            lessons=case_data.get('lessons', ''),
            tags=case_data.get('tags', []),
            created_at=datetime.now().isoformat()
        )
        
        self.cases[case_id] = case
        self._update_tags_index(case)
        
        self.metrics.record(action='case_created', case_id=case_id)
        print(f"✅ 案例创建: {case.title}")
        
        return case
    
    def _update_tags_index(self, case: Case):
        """更新标签索引"""
        for tag in case.tags:
            if tag not in self.tags_index:
                self.tags_index[tag] = []
            self.tags_index[tag].append(case.id)
    
    def search_similar_cases(self, query: Dict, top_k: int = 5) -> List[Case]:
        """
        C - 组合化(Combination)
        基于案例特征进行相似度匹配
        """
        results = []
        
        for case in self.cases.values():
            score = self._calculate_similarity(query, case)
            results.append((case, score))
        
        # 排序返回Top-K
        results.sort(key=lambda x: x[1], reverse=True)
        
        self.metrics.record(action='case_searched', query=str(query)[:50])
        
        return [case for case, score in results[:top_k]]
    
    def _calculate_similarity(self, query: Dict, case: Case) -> float:
        """计算案例相似度"""
        score = 0.0
        
        # 行业匹配
        if query.get('industry') == case.industry:
            score += 0.3
        
        # 阶段匹配
        if query.get('stage') == case.stage:
            score += 0.2
        
        # 标签匹配
        query_tags = set(query.get('tags', []))
        case_tags = set(case.tags)
        if query_tags and case_tags:
            tag_overlap = len(query_tags & case_tags) / len(query_tags | case_tags)
            score += 0.3 * tag_overlap
        
        # 创始人画像匹配
        founder_sim = self._profile_similarity(
            query.get('founder_profile', {}),
            case.founder_profile
        )
        score += 0.2 * founder_sim
        
        return score
    
    def _profile_similarity(self, profile1: Dict, profile2: Dict) -> float:
        """计算画像相似度"""
        if not profile1 or not profile2:
            return 0.0
        
        # 简化计算
        common_keys = set(profile1.keys()) & set(profile2.keys())
        if not common_keys:
            return 0.0
        
        matches = sum(1 for k in common_keys if profile1.get(k) == profile2.get(k))
        return matches / len(common_keys)
    
    def generate_lessons(self, case_ids: List[str]) -> str:
        """
        I - 内隐化(Internalization)
        从案例中提炼经验教训，形成决策直觉
        """
        cases = [self.cases[cid] for cid in case_ids if cid in self.cases]
        
        if not cases:
            return "无有效案例"
        
        # 提取共同成功因素
        all_factors = []
        for case in cases:
            all_factors.extend(case.matching_factors)
        
        # 统计频次
        factor_counts = {}
        for factor in all_factors:
            factor_counts[factor] = factor_counts.get(factor, 0) + 1
        
        # 生成经验总结
        top_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        lessons = f"""基于{len(cases)}个案例的经验总结：

关键成功因素（按重要性排序）：
"""
        for i, (factor, count) in enumerate(top_factors, 1):
            lessons += f"{i}. {factor}（出现{count}次）\n"
        
        lessons += f"\n决策建议：\n"
        lessons += f"- 优先考虑具备'{top_factors[0][0]}'特质的合伙人\n"
        lessons += f"- 参考行业：{cases[0].industry}\n"
        
        return lessons
    
    def analyze_patterns(self) -> Dict:
        """
        跨案例分析，发现匹配模式
        """
        industries = {}
        stages = {}
        factors = {}
        
        for case in self.cases.values():
            industries[case.industry] = industries.get(case.industry, 0) + 1
            stages[case.stage] = stages.get(case.stage, 0) + 1
            
            for factor in case.matching_factors:
                factors[factor] = factors.get(factor, 0) + 1
        
        return {
            'total_cases': len(self.cases),
            'industry_distribution': industries,
            'stage_distribution': stages,
            'top_factors': sorted(factors.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def save(self):
        """保存案例库到文件"""
        data = {
            'cases': [
                {
                    'id': c.id,
                    'title': c.title,
                    'industry': c.industry,
                    'stage': c.stage,
                    'matching_factors': c.matching_factors,
                    'decision_logic': c.decision_logic,
                    'tags': c.tags,
                    'created_at': c.created_at
                }
                for c in self.cases.values()
            ],
            'tags_index': self.tags_index
        }
        
        filename = f"{self.data_path}/case_repository_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 案例库已保存: {filename}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_cases': len(self.cases),
            'total_tags': len(self.tags_index),
            'industries': len(set(c.industry for c in self.cases.values()))
        }

# 便捷函数
def create_case_repository():
    """快速创建案例库"""
    return CaseRepositorySystem()

if __name__ == '__main__':
    repo = create_case_repository()
    
    # 创建示例案例
    case_data = {
        'title': '芯片公司A合伙人匹配案例',
        'industry': '半导体',
        'stage': 'Pre-A轮',
        'matching_factors': ['技术背景', '产业资源', '管理经验'],
        'decision_logic': '优先选择有晶圆厂背景的合伙人',
        'tags': ['芯片', '硬科技', '合伙人匹配']
    }
    
    repo.create_case(case_data)
    print(repo.get_stats())
