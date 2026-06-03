#!/usr/bin/env python3
"""
case-repository - 案例库管理系统
真正实现版本

功能:
- 案例CRUD管理
- 多维度标签检索
- 相似案例推荐
- 复盘报告生成
- 合伙人匹配数据支持

作者: 满意妞 (蓝军监督)
版本: 1.0.0-real
日期: 2026-04-03
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import difflib


class CaseOutcome(Enum):
    """案例结果"""
    SUCCESS = "success"           # 成功
    FAILURE = "failure"           # 失败
    PARTIAL = "partial"           # 部分成功
    ONGOING = "ongoing"           # 进行中
    PENDING = "pending"           # 待定


class Industry(Enum):
    """硬科技行业"""
    AI_CHIP = "AI芯片"
    GPU_CHIP = "GPU芯片"
    SENSOR = "传感器"
    BIOTECH = "生物医药"
    NEW_ENERGY = "新能源"
    NEW_MATERIAL = "新材料"
    ROBOTICS = "机器人"
    AEROSPACE = "航空航天"
    QUANTUM = "量子计算"
    OTHER = "其他"


class Stage(Enum):
    """项目阶段"""
    IDEA = "概念期"
    SEED = "种子期"
    ANGEL = "天使轮"
    PRE_A = "Pre-A轮"
    A_ROUND = "A轮"
    B_ROUND = "B轮"
    GROWTH = "成长期"
    EXPANSION = "扩张期"


class PartnerType(Enum):
    """合伙人类型"""
    BUSINESS = "商业合伙人"
    TECH = "技术合伙人"
    OPERATION = "运营合伙人"
    FINANCE = "财务合伙人"
    STRATEGY = "战略合伙人"


@dataclass
class FounderProfile:
    """创始人画像"""
    background: str                    # 技术/商业/混合
    core_tech: str                     # 核心技术
    main_strength: str                 # 主要优势
    main_weakness: str                 # 主要短板
    team_size: int = 0                 # 团队规模
    funding_status: str = ""           # 融资状态


@dataclass
class PartnerRequirements:
    """合伙人需求"""
    role_type: str                     # 合伙人类型
    must_have: List[str] = field(default_factory=list)
    nice_to_have: List[str] = field(default_factory=list)
    deal_breakers: List[str] = field(default_factory=list)


@dataclass
class MatchingProcess:
    """匹配过程"""
    candidates_considered: int = 0
    candidates_interviewed: int = 0
    final_candidates: int = 0
    decision_method: str = ""          # 满意解/多轮面试
    time_spent_days: int = 0
    key_criteria: List[str] = field(default_factory=list)


@dataclass
class SelectedPartner:
    """选中的合伙人"""
    background: str
    key_strengths: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    match_score: float = 0.0


@dataclass
class Outcome:
    """结果"""
    result: str                        # success/failure/partial/ongoing
    funding_raised: str = ""           # 融资额
    valuation_change: str = ""         # 估值变化
    team_stability: int = 0            # 团队稳定性评分
    key_success_factors: List[str] = field(default_factory=list)
    failure_reasons: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    if_redo: str = ""                  # 如果重做会改变什么


@dataclass
class PartnerMatchingCase:
    """合伙人匹配案例"""
    case_id: str
    case_name: str
    created_date: str
    
    # 核心分类
    industry: str
    stage: str
    partner_type: str
    outcome: str
    
    # 详细数据
    founder_profile: FounderProfile
    partner_requirements: PartnerRequirements
    matching_process: MatchingProcess
    selected_partner: SelectedPartner
    outcome_details: Outcome
    
    # 标签和元数据
    tags: List[str] = field(default_factory=list)
    confidentiality: str = "internal"  # public/anonymized/internal
    created_by: str = ""
    notes: str = ""


class CaseRepository:
    """案例库管理器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """初始化"""
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.cases_file = self.data_dir / "partner_matching_cases.json"
        self.cases: List[PartnerMatchingCase] = self._load_cases()
    
    def _load_cases(self) -> List[PartnerMatchingCase]:
        """加载案例"""
        if not self.cases_file.exists():
            return []
        
        with open(self.cases_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cases = []
            for item in data:
                case = self._dict_to_case(item)
                cases.append(case)
            return cases
    
    def _save_cases(self):
        """保存案例"""
        with open(self.cases_file, 'w', encoding='utf-8') as f:
            data = [self._case_to_dict(c) for c in self.cases]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _case_to_dict(self, case: PartnerMatchingCase) -> Dict:
        """案例转字典"""
        return {
            'case_id': case.case_id,
            'case_name': case.case_name,
            'created_date': case.created_date,
            'industry': case.industry,
            'stage': case.stage,
            'partner_type': case.partner_type,
            'outcome': case.outcome,
            'founder_profile': {
                'background': case.founder_profile.background,
                'core_tech': case.founder_profile.core_tech,
                'main_strength': case.founder_profile.main_strength,
                'main_weakness': case.founder_profile.main_weakness,
                'team_size': case.founder_profile.team_size,
                'funding_status': case.founder_profile.funding_status
            },
            'partner_requirements': {
                'role_type': case.partner_requirements.role_type,
                'must_have': case.partner_requirements.must_have,
                'nice_to_have': case.partner_requirements.nice_to_have,
                'deal_breakers': case.partner_requirements.deal_breakers
            },
            'matching_process': {
                'candidates_considered': case.matching_process.candidates_considered,
                'candidates_interviewed': case.matching_process.candidates_interviewed,
                'final_candidates': case.matching_process.final_candidates,
                'decision_method': case.matching_process.decision_method,
                'time_spent_days': case.matching_process.time_spent_days,
                'key_criteria': case.matching_process.key_criteria
            },
            'selected_partner': {
                'background': case.selected_partner.background,
                'key_strengths': case.selected_partner.key_strengths,
                'risk_factors': case.selected_partner.risk_factors,
                'match_score': case.selected_partner.match_score
            },
            'outcome_details': {
                'result': case.outcome_details.result,
                'funding_raised': case.outcome_details.funding_raised,
                'valuation_change': case.outcome_details.valuation_change,
                'team_stability': case.outcome_details.team_stability,
                'key_success_factors': case.outcome_details.key_success_factors,
                'failure_reasons': case.outcome_details.failure_reasons,
                'lessons_learned': case.outcome_details.lessons_learned,
                'if_redo': case.outcome_details.if_redo
            },
            'tags': case.tags,
            'confidentiality': case.confidentiality,
            'created_by': case.created_by,
            'notes': case.notes
        }
    
    def _dict_to_case(self, data: Dict) -> PartnerMatchingCase:
        """字典转案例"""
        return PartnerMatchingCase(
            case_id=data['case_id'],
            case_name=data['case_name'],
            created_date=data['created_date'],
            industry=data['industry'],
            stage=data['stage'],
            partner_type=data['partner_type'],
            outcome=data['outcome'],
            founder_profile=FounderProfile(**data['founder_profile']),
            partner_requirements=PartnerRequirements(**data['partner_requirements']),
            matching_process=MatchingProcess(**data['matching_process']),
            selected_partner=SelectedPartner(**data['selected_partner']),
            outcome_details=Outcome(**data['outcome_details']),
            tags=data.get('tags', []),
            confidentiality=data.get('confidentiality', 'internal'),
            created_by=data.get('created_by', ''),
            notes=data.get('notes', '')
        )
    
    def create_case(self, case_name: str, industry: str, stage: str,
                   partner_type: str, founder_bg: str, core_tech: str,
                   main_strength: str, main_weakness: str,
                   created_by: str = "") -> PartnerMatchingCase:
        """创建案例"""
        case_id = f"CASE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        case = PartnerMatchingCase(
            case_id=case_id,
            case_name=case_name,
            created_date=datetime.now().strftime('%Y-%m-%d'),
            industry=industry,
            stage=stage,
            partner_type=partner_type,
            outcome=CaseOutcome.PENDING.value,
            founder_profile=FounderProfile(
                background=founder_bg,
                core_tech=core_tech,
                main_strength=main_strength,
                main_weakness=main_weakness
            ),
            partner_requirements=PartnerRequirements(
                role_type=partner_type
            ),
            matching_process=MatchingProcess(),
            selected_partner=SelectedPartner(background=""),
            outcome_details=Outcome(result=CaseOutcome.PENDING.value),
            tags=[industry, stage, partner_type],
            created_by=created_by
        )
        
        self.cases.append(case)
        self._save_cases()
        return case
    
    def get_case(self, case_id: str) -> Optional[PartnerMatchingCase]:
        """获取案例"""
        return next((c for c in self.cases if c.case_id == case_id), None)
    
    def update_case(self, case_id: str, **kwargs) -> Optional[PartnerMatchingCase]:
        """更新案例"""
        case = self.get_case(case_id)
        if not case:
            return None
        
        # 简单字段更新
        for key, value in kwargs.items():
            if hasattr(case, key):
                setattr(case, key, value)
        
        self._save_cases()
        return case
    
    def list_cases(self, industry: Optional[str] = None,
                  stage: Optional[str] = None,
                  partner_type: Optional[str] = None,
                  outcome: Optional[str] = None,
                  tag: Optional[str] = None) -> List[PartnerMatchingCase]:
        """列出案例（支持筛选）"""
        result = self.cases
        
        if industry:
            result = [c for c in result if c.industry == industry]
        if stage:
            result = [c for c in result if c.stage == stage]
        if partner_type:
            result = [c for c in result if c.partner_type == partner_type]
        if outcome:
            result = [c for c in result if c.outcome == outcome]
        if tag:
            result = [c for c in result if tag in c.tags]
        
        return result
    
    def search_cases(self, query: str) -> List[Tuple[PartnerMatchingCase, float]]:
        """搜索案例（基于名称和标签的模糊匹配）"""
        results = []
        query_lower = query.lower()
        
        for case in self.cases:
            # 计算相似度
            name_match = difflib.SequenceMatcher(None, query_lower, case.case_name.lower()).ratio()
            
            # 标签匹配
            tag_matches = [difflib.SequenceMatcher(None, query_lower, tag.lower()).ratio() 
                          for tag in case.tags]
            tag_match = max(tag_matches) if tag_matches else 0
            
            # 综合评分
            score = max(name_match, tag_match)
            
            if score > 0.3:  # 阈值
                results.append((case, score))
        
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def find_similar_cases(self, founder_bg: str, industry: str,
                          stage: str, partner_type: str,
                          top_k: int = 5) -> List[Tuple[PartnerMatchingCase, float]]:
        """查找相似案例"""
        scores = []
        
        for case in self.cases:
            score = 0.0
            
            # 行业匹配 (30%)
            if case.industry == industry:
                score += 0.3
            elif industry in case.tags:
                score += 0.15
            
            # 阶段匹配 (20%)
            if case.stage == stage:
                score += 0.2
            
            # 合伙人类型匹配 (20%)
            if case.partner_type == partner_type:
                score += 0.2
            
            # 创始人背景匹配 (15%)
            bg_similarity = difflib.SequenceMatcher(None, founder_bg.lower(), 
                                                    case.founder_profile.background.lower()).ratio()
            score += bg_similarity * 0.15
            
            # 结果参考 (15%) - 成功案例权重更高
            if case.outcome == CaseOutcome.SUCCESS.value:
                score += 0.15
            elif case.outcome == CaseOutcome.PARTIAL.value:
                score += 0.08
            
            if score > 0:
                scores.append((case, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self.cases)
        if total == 0:
            return {'total': 0}
        
        success = len([c for c in self.cases if c.outcome == CaseOutcome.SUCCESS.value])
        failure = len([c for c in self.cases if c.outcome == CaseOutcome.FAILURE.value])
        
        # 行业分布
        industries = {}
        for c in self.cases:
            industries[c.industry] = industries.get(c.industry, 0) + 1
        
        # 阶段分布
        stages = {}
        for c in self.cases:
            stages[c.stage] = stages.get(c.stage, 0) + 1
        
        return {
            'total': total,
            'success': success,
            'failure': failure,
            'success_rate': success / total if total > 0 else 0,
            'industry_distribution': industries,
            'stage_distribution': stages
        }
    
    def generate_lessons_report(self, industry: Optional[str] = None) -> str:
        """生成经验教训报告"""
        cases = self.cases
        if industry:
            cases = [c for c in cases if c.industry == industry]
        
        success_factors = []
        failure_reasons = []
        lessons = []
        
        for case in cases:
            success_factors.extend(case.outcome_details.key_success_factors)
            failure_reasons.extend(case.outcome_details.failure_reasons)
            lessons.extend(case.outcome_details.lessons_learned)
        
        lines = [
            f"# 经验教训报告",
            f"**行业**: {industry or '全部'}",
            f"**案例数**: {len(cases)}",
            "",
            "## ✅ 成功关键因素",
            ""
        ]
        
        for factor in set(success_factors):
            count = success_factors.count(factor)
            lines.append(f"- {factor} ({count}次提及)")
        
        lines.extend(["", "## ❌ 失败原因", ""])
        for reason in set(failure_reasons):
            count = failure_reasons.count(reason)
            lines.append(f"- {reason} ({count}次提及)")
        
        lines.extend(["", "## 💡 经验教训", ""])
        for lesson in set(lessons):
            lines.append(f"- {lesson}")
        
        return '\n'.join(lines)
    
    def export_for_matching_engine(self) -> List[Dict]:
        """导出给匹配引擎使用的数据"""
        return [self._case_to_dict(c) for c in self.cases if c.outcome != CaseOutcome.PENDING.value]


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Case Repository - 案例库管理系统')
    parser.add_argument('--create', nargs=4, metavar=('NAME', 'INDUSTRY', 'STAGE', 'TYPE'),
                       help='创建案例')
    parser.add_argument('--founder-bg', default='技术',
                       help='创始人背景')
    parser.add_argument('--core-tech', default='',
                       help='核心技术')
    parser.add_argument('--strength', default='',
                       help='主要优势')
    parser.add_argument('--weakness', default='',
                       help='主要短板')
    parser.add_argument('--list', action='store_true',
                       help='列出案例')
    parser.add_argument('--search', metavar='QUERY',
                       help='搜索案例')
    parser.add_argument('--similar', nargs=4, metavar=('BG', 'INDUSTRY', 'STAGE', 'TYPE'),
                       help='查找相似案例')
    parser.add_argument('--stats', action='store_true',
                       help='查看统计')
    parser.add_argument('--report', action='store_true',
                       help='生成经验教训报告')
    parser.add_argument('--industry', help='筛选行业')
    parser.add_argument('--data-dir', help='数据目录')
    
    args = parser.parse_args()
    
    try:
        repo = CaseRepository(args.data_dir)
        
        if args.create:
            name, industry, stage, ptype = args.create
            case = repo.create_case(
                case_name=name,
                industry=industry,
                stage=stage,
                partner_type=ptype,
                founder_bg=args.founder_bg,
                core_tech=args.core_tech,
                main_strength=args.strength,
                main_weakness=args.weakness
            )
            print(f"✅ 案例已创建: {case.case_id}")
            print(f"   名称: {case.case_name}")
        
        elif args.list:
            cases = repo.list_cases(industry=args.industry)
            if not cases:
                print("暂无案例")
            else:
                print(f"共 {len(cases)} 个案例:")
                print("-" * 80)
                for c in cases[:20]:
                    outcome_icon = {
                        CaseOutcome.SUCCESS.value: "✅",
                        CaseOutcome.FAILURE.value: "❌",
                        CaseOutcome.PARTIAL.value: "⚠️",
                        CaseOutcome.ONGOING.value: "⏳",
                        CaseOutcome.PENDING.value: "⏸️"
                    }.get(c.outcome, "⚪")
                    print(f"{outcome_icon} [{c.case_id}] {c.case_name}")
                    print(f"   行业: {c.industry} | 阶段: {c.stage} | 类型: {c.partner_type}")
        
        elif args.search:
            results = repo.search_cases(args.search)
            if not results:
                print(f"未找到匹配'{args.search}'的案例")
            else:
                print(f"找到 {len(results)} 个相关案例:")
                for case, score in results[:10]:
                    print(f"  [{case.case_id}] {case.case_name} (相关度: {score:.2%})")
        
        elif args.similar:
            bg, industry, stage, ptype = args.similar
            results = repo.find_similar_cases(bg, industry, stage, ptype)
            if not results:
                print("未找到相似案例")
            else:
                print(f"找到 {len(results)} 个相似案例:")
                for case, score in results:
                    print(f"  [{case.case_id}] {case.case_name} (相似度: {score:.2%})")
        
        elif args.stats:
            stats = repo.get_statistics()
            print("=" * 50)
            print("案例库统计")
            print("=" * 50)
            print(f"总案例数: {stats['total']}")
            print(f"成功案例: {stats['success']}")
            print(f"失败案例: {stats['failure']}")
            print(f"成功率: {stats.get('success_rate', 0):.1%}")
            
            if 'industry_distribution' in stats:
                print("\n行业分布:")
                for ind, count in stats['industry_distribution'].items():
                    print(f"  {ind}: {count}")
        
        elif args.report:
            report = repo.generate_lessons_report(industry=args.industry)
            print(report)
        
        else:
            stats = repo.get_statistics()
            print(f"案例库: {stats['total']} 个案例")
            if stats['total'] > 0:
                print(f"成功率: {stats['success_rate']:.1%}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
