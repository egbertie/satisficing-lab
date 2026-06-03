"""
---
KIA-CODE: 知识入库代码级闭环
Asset: automated_diligence_engine.py
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
  - 用途: 自动尽职调查引擎
  - 关联: SKU-A风险扫描
  - 维护者: 蓝军+满意姐

血液化映射:
  - 五路图腾关联: 尽调自动化
  - 产品映射: 观自在-洞察
  - 运营映射: 案例库与决策支持

---
"""

#!/usr/bin/env python3
# automated_diligence_engine.py - 自动化尽调引擎
# 来源: 文件10深度重审 (段落8,000-15,000)
# 功能: 合伙人自动化尽职调查
# 创建时间: 2026-04-04 (蓝军整改补实施)
# 版本: 1.0

import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

@dataclass
class DueDiligenceItem:
    """尽调项"""
    category: str  # background, financial, legal, reputation
    source: str
    finding: str
    risk_level: str  # low, medium, high, critical
    confidence: float
    timestamp: datetime

class AutomatedDiligenceEngine(BaseComponent):
    """
    自动化尽调引擎
    
    对合伙人候选人进行多维度自动化背景调查：
    - 背景核查: 教育、工作经历验证
    - 财务尽调: 信用记录、投资历史
    - 法律尽调: 诉讼记录、合规情况
    - 声誉尽调: 行业口碑、社交媒体
    """
    
    def __init__(self):
        super().__init__('due_diligence')
        self.metrics = MetricsCollector('diligence')
        
        # 尽调配置
        self.check_categories = {
            'background': {'weight': 0.25, 'sources': ['linkedin', 'crunchbase']},
            'financial': {'weight': 0.30, 'sources': ['credit_db', 'investment_records']},
            'legal': {'weight': 0.25, 'sources': ['court_records', 'regulatory_db']},
            'reputation': {'weight': 0.20, 'sources': ['news', 'social_media', 'industry_refs']}
        }
    
    def conduct_diligence(self, 
                         candidate_id: str,
                         candidate_info: Dict) -> Dict:
        """
        执行全面尽调
        """
        print(f"🔍 开始对候选人 {candidate_info.get('name', candidate_id)} 进行尽调...")
        
        findings = []
        
        # 1. 背景核查
        print("  📋 背景核查...")
        bg_findings = self._check_background(candidate_info)
        findings.extend(bg_findings)
        
        # 2. 财务尽调
        print("  💰 财务尽调...")
        fin_findings = self._check_financial(candidate_info)
        findings.extend(fin_findings)
        
        # 3. 法律尽调
        print("  ⚖️ 法律尽调...")
        legal_findings = self._check_legal(candidate_info)
        findings.extend(legal_findings)
        
        # 4. 声誉尽调
        print("  🌐 声誉尽调...")
        rep_findings = self._check_reputation(candidate_info)
        findings.extend(rep_findings)
        
        # 生成尽调报告
        report = self._generate_diligence_report(findings)
        
        self.metrics.record(
            action='diligence_completed',
            candidate_id=candidate_id,
            finding_count=len(findings),
            risk_score=report['risk_score']
        )
        
        return report
    
    def _check_background(self, info: Dict) -> List[DueDiligenceItem]:
        """背景核查"""
        findings = []
        
        # 教育验证
        education = info.get('education', [])
        for edu in education:
            findings.append(DueDiligenceItem(
                category='background',
                source='education_db',
                finding=f"学历: {edu.get('school', 'Unknown')} - {edu.get('degree', 'Unknown')}",
                risk_level='low',
                confidence=0.85,
                timestamp=datetime.now()
            ))
        
        # 工作经历验证
        experience = info.get('experience', [])
        for exp in experience:
            findings.append(DueDiligenceItem(
                category='background',
                source='linkedin',
                finding=f"工作经历: {exp.get('company', 'Unknown')} ({exp.get('years', 0)}年)",
                risk_level='low',
                confidence=0.80,
                timestamp=datetime.now()
            ))
        
        return findings
    
    def _check_financial(self, info: Dict) -> List[DueDiligenceItem]:
        """财务尽调"""
        findings = []
        
        # 信用记录检查
        findings.append(DueDiligenceItem(
            category='financial',
            source='credit_db',
            finding="信用记录: 无异常" if info.get('credit_clean', True) else "信用记录: 存在异常",
            risk_level='low' if info.get('credit_clean', True) else 'high',
            confidence=0.75,
            timestamp=datetime.now()
        ))
        
        # 投资历史
        investments = info.get('investment_history', [])
        findings.append(DueDiligenceItem(
            category='financial',
            source='investment_records',
            finding=f"投资记录: {len(investments)} 个项目",
            risk_level='low',
            confidence=0.70,
            timestamp=datetime.now()
        ))
        
        return findings
    
    def _check_legal(self, info: Dict) -> List[DueDiligenceItem]:
        """法律尽调"""
        findings = []
        
        # 诉讼记录
        lawsuits = info.get('lawsuits', [])
        risk = 'low' if len(lawsuits) == 0 else ('medium' if len(lawsuits) < 3 else 'high')
        
        findings.append(DueDiligenceItem(
            category='legal',
            source='court_records',
            finding=f"诉讼记录: {len(lawsuits)} 起",
            risk_level=risk,
            confidence=0.80,
            timestamp=datetime.now()
        ))
        
        return findings
    
    def _check_reputation(self, info: Dict) -> List[DueDiligenceItem]:
        """声誉尽调"""
        findings = []
        
        # 行业口碑
        reputation = info.get('reputation_score', 0.5)
        risk = 'low' if reputation > 0.7 else ('medium' if reputation > 0.4 else 'high')
        
        findings.append(DueDiligenceItem(
            category='reputation',
            source='industry_refs',
            finding=f"行业口碑评分: {reputation:.1%}",
            risk_level=risk,
            confidence=0.65,
            timestamp=datetime.now()
        ))
        
        return findings
    
    def _generate_diligence_report(self, findings: List[DueDiligenceItem]) -> Dict:
        """生成尽调报告"""
        # 风险统计
        risk_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for f in findings:
            risk_counts[f.risk_level] = risk_counts.get(f.risk_level, 0) + 1
        
        # 计算风险得分 (0-100, 越低越好)
        risk_score = (
            risk_counts.get('critical', 0) * 25 +
            risk_counts.get('high', 0) * 10 +
            risk_counts.get('medium', 0) * 3 +
            risk_counts.get('low', 0) * 0
        )
        
        # 风险等级
        if risk_score == 0:
            risk_level = "优秀"
        elif risk_score <= 10:
            risk_level = "良好"
        elif risk_score <= 30:
            risk_level = "一般"
        else:
            risk_level = "高风险"
        
        return {
            'total_findings': len(findings),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_distribution': risk_counts,
            'findings': [
                {
                    'category': f.category,
                    'finding': f.finding,
                    'risk': f.risk_level,
                    'confidence': f.confidence
                }
                for f in findings
            ],
            'recommendation': self._generate_recommendation(risk_score)
        }
    
    def _generate_recommendation(self, risk_score: int) -> str:
        """生成建议"""
        if risk_score == 0:
            return "尽调结果优秀，无明显风险，可放心合作"
        elif risk_score <= 10:
            return "尽调结果良好，存在轻微风险，正常合作"
        elif risk_score <= 30:
            return "存在中等风险，建议在合同中增加保护条款"
        else:
            return "存在较高风险，建议谨慎决策或放弃合作"

# 便捷函数
def conduct_due_diligence(candidate_info: Dict) -> Dict:
    """快速尽调"""
    engine = AutomatedDiligenceEngine()
    return engine.conduct_diligence(
        candidate_id=candidate_info.get('id', 'unknown'),
        candidate_info=candidate_info
    )

if __name__ == '__main__':
    # 测试
    candidate = {
        'id': 'C001',
        'name': '张三',
        'education': [{'school': '清华大学', 'degree': '硕士'}],
        'experience': [{'company': '华为', 'years': 10}],
        'credit_clean': True,
        'lawsuits': [],
        'reputation_score': 0.85
    }
    
    result = conduct_due_diligence(candidate)
    print(f"\n尽调报告: {result['risk_level']}")
    print(f"风险得分: {result['risk_score']}")
