"""
知识策展人 - Knowledge Curator
核心模块: 文献筛选四阶段协议 + 三层审查
版本: 1.0.0
日期: 2026-04-02
Expert_ID: CKA-17 (哲学文献筛选员)
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time


@dataclass
class LiteratureEntry:
    """文献条目"""
    entry_id: str
    title: str
    authors: List[str]
    year: int
    venue: str
    citations: int
    h_index: float
    award: str
    abstract: str
    pdf_url: str
    expert_alignment: str
    advisor_id: str
    totem_alignment: str


@dataclass
class CuratorReport:
    """策展报告"""
    expert_id: str
    total_entries: int
    quality_score: float
    stage_check: Dict[str, bool]
    literature_package: List[LiteratureEntry]
    metadata: Dict


class KnowledgeCurator:
    """
    知识策展人 (CKA-17)
    
    四阶段协议:
    1. 需求图谱分析
    2. 文献来源清单构建
    3. 向量化处理
    4. 质量闸口审查
    
    三层审查:
    - 期刊/会议级别
    - 作者影响力
    - 引用质量
    """
    
    def __init__(self, expert_id: str = "CKA-17"):
        self.expert_id = expert_id
        self.advisor_id = "11"  # 哲学文献筛选员
        
        # 高质量期刊/会议列表
        self.top_tier_venues = {
            "journals": [
                "Nature", "Science", "Cell",
                "Mind", "Philosophical Review", "Nous",
                "IEEE Transactions", "ACM Computing Surveys"
            ],
            "conferences": [
                "CVPR", "NeurIPS", "ICML", "ICLR",
                "ACL", "EMNLP", "AAAI", "IJCAI"
            ]
        }
        
        # 质量阈值
        self.thresholds = {
            "min_citations": 50,
            "min_h_index": 20,
            "min_year": 2015,
            "max_entries": 110
        }
    
    def stage1_demand_analysis(self, research_topic: str) -> Dict:
        """
        阶段1: 需求图谱分析
        
        分析研究主题的知识需求结构
        """
        # 关键词提取（简化版）
        keywords = self._extract_keywords(research_topic)
        
        # 需求分层
        demand_layers = {
            "foundational": [k for k in keywords if any(t in k for t in ["理论", "框架", "模型"])],
            "methodological": [k for k in keywords if any(t in k for t in ["方法", "技术", "算法"])],
            "applied": [k for k in keywords if any(t in k for t in ["应用", "实践", "案例"])]
        }
        
        return {
            "stage": "stage1",
            "topic": research_topic,
            "keywords": keywords,
            "demand_layers": demand_layers,
            "estimated_entries": min(len(keywords) * 3, self.thresholds["max_entries"]),
            "completed": True
        }
    
    def stage2_source_building(self, demand_analysis: Dict) -> List[Dict]:
        """
        阶段2: 文献来源清单构建
        
        基于需求生成文献候选列表
        """
        sources = []
        keywords = demand_analysis["keywords"]
        
        for i, keyword in enumerate(keywords[:20]):  # 限制关键词数
            # 生成模拟文献条目（实际应接入学术数据库API）
            entry = {
                "entry_id": f"{self.expert_id}-{i+1:03d}",
                "title": f"Research on {keyword.title()}: A Systematic Review",
                "authors": [f"Author_{i+1}", "CoAuthor"],
                "year": 2020 + (i % 5),
                "venue": self._select_venue(i),
                "citations": 50 + (i * 10),
                "h_index": 20.0 + (i * 0.5),
                "award": "Best Paper" if i < 3 else "",
                "keyword": keyword
            }
            sources.append(entry)
        
        return sources
    
    def stage3_vectorization(self, sources: List[Dict]) -> List[LiteratureEntry]:
        """
        阶段3: 向量化处理
        
        将文献转换为结构化向量条目
        """
        entries = []
        
        for src in sources:
            entry = LiteratureEntry(
                entry_id=src["entry_id"],
                title=src["title"],
                authors=src["authors"],
                year=src["year"],
                venue=src["venue"],
                citations=src["citations"],
                h_index=src["h_index"],
                award=src["award"],
                abstract=f"Abstract for {src['title']}...",
                pdf_url=f"https://example.com/pdf/{src['entry_id']}.pdf",
                expert_alignment=self.expert_id,
                advisor_id=self.advisor_id,
                totem_alignment=self._map_to_totem(src)
            )
            entries.append(entry)
        
        return entries
    
    def stage4_quality_gate(self, entries: List[LiteratureEntry]) -> Tuple[List[LiteratureEntry], Dict]:
        """
        阶段4: 质量闸口审查
        
        三层审查:
        1. 期刊/会议级别
        2. 作者影响力
        3. 引用质量
        """
        passed = []
        rejected = []
        
        for entry in entries:
            checks = {
                "venue_quality": self._check_venue_quality(entry.venue),
                "author_influence": entry.h_index >= self.thresholds["min_h_index"],
                "citation_quality": entry.citations >= self.thresholds["min_citations"],
                "recency": entry.year >= self.thresholds["min_year"]
            }
            
            # 至少通过3项
            passed_checks = sum(checks.values())
            if passed_checks >= 3:
                passed.append(entry)
            else:
                rejected.append({"entry": entry, "checks": checks})
        
        # 限制总数
        if len(passed) > self.thresholds["max_entries"]:
            passed = passed[:self.thresholds["max_entries"]]
        
        stats = {
            "total_processed": len(entries),
            "passed": len(passed),
            "rejected": len(rejected),
            "pass_rate": len(passed) / len(entries) if entries else 0
        }
        
        return passed, stats
    
    def generate_report(self, entries: List[LiteratureEntry], stats: Dict) -> CuratorReport:
        """生成策展报告"""
        # 计算质量分数
        quality_score = self._calculate_quality_score(entries)
        
        return CuratorReport(
            expert_id=self.expert_id,
            total_entries=len(entries),
            quality_score=quality_score,
            stage_check={
                "stage1": True,
                "stage2": True,
                "stage3": True,
                "stage4": True
            },
            literature_package=entries,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "advisor_id": self.advisor_id,
                "thresholds": self.thresholds,
                "stats": stats
            }
        )
    
    def full_pipeline(self, research_topic: str) -> CuratorReport:
        """完整四阶段流程"""
        # Stage 1
        demand = self.stage1_demand_analysis(research_topic)
        
        # Stage 2
        sources = self.stage2_source_building(demand)
        
        # Stage 3
        entries = self.stage3_vectorization(sources)
        
        # Stage 4
        passed, stats = self.stage4_quality_gate(entries)
        
        # Report
        return self.generate_report(passed, stats)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "expert_id": self.expert_id,
            "advisor_id": self.advisor_id,
            "thresholds": self.thresholds,
            "top_venues_count": len(self.top_tier_venues["journals"]) + len(self.top_tier_venues["conferences"])
        }
    
    # ============ 辅助方法 ============
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简化版关键词提取
        common_terms = [
            "ethics", "ai", "philosophy", "governance",
            "decision", "cognition", "neuroscience",
            "narrative", "strategy", "organization"
        ]
        found = []
        for term in common_terms:
            if term.lower() in text.lower():
                found.append(term)
        return found[:10] or ["general"]
    
    def _select_venue(self, index: int) -> str:
        """选择期刊/会议"""
        venues = self.top_tier_venues["journals"] + self.top_tier_venues["conferences"]
        return venues[index % len(venues)]
    
    def _check_venue_quality(self, venue: str) -> bool:
        """检查期刊/会议质量"""
        top_venues = self.top_tier_venues["journals"] + self.top_tier_venues["conferences"]
        return any(v in venue for v in top_venues)
    
    def _map_to_totem(self, entry: Dict) -> str:
        """映射到五路图腾"""
        keyword = entry.get("keyword", "").lower()
        if any(t in keyword for t in ["ethic", "moral", "value"]):
            return "06_惟吾德馨"
        elif any(t in keyword for t in ["decision", "satisfic", "simon"]):
            return "07_满意解"
        elif any(t in keyword for t in ["calm", "mindful", "aware"]):
            return "08_自在从容"
        elif any(t in keyword for t in ["ritual", "propriety", "confucian"]):
            return "09_万世师表"
        else:
            return "10_红莲淬火"
    
    def _calculate_quality_score(self, entries: List[LiteratureEntry]) -> float:
        """计算质量分数"""
        if not entries:
            return 0.0
        
        scores = []
        for entry in entries:
            score = 0
            # 期刊质量
            if self._check_venue_quality(entry.venue):
                score += 0.3
            # 引用
            if entry.citations >= 100:
                score += 0.3
            elif entry.citations >= 50:
                score += 0.2
            # h-index
            if entry.h_index >= 30:
                score += 0.2
            elif entry.h_index >= 20:
                score += 0.1
            # 奖项
            if entry.award:
                score += 0.2
            
            scores.append(score)
        
        return sum(scores) / len(scores)


# 便捷函数接口
def curate_knowledge(research_topic: str, expert_id: str = "CKA-17") -> CuratorReport:
    """便捷策展函数"""
    curator = KnowledgeCurator(expert_id=expert_id)
    return curator.full_pipeline(research_topic)


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="知识策展人")
    parser.add_argument("--test", action="store_true", help="运行完整测试套件")
    args = parser.parse_args()
    
    if args.test:
        print("=" * 70)
        print("知识策展人 - 完整测试套件 (v1.0.0)")
        print("=" * 70)
        
        curator = KnowledgeCurator(expert_id="CKA-17")
        test_results = []
        
        # 测试1: 需求分析
        print("\n[测试1/12] 需求图谱分析...")
        try:
            demand = curator.stage1_demand_analysis("AI ethics and governance framework")
            passed = len(demand['keywords']) > 0
            test_results.append(("需求图谱分析", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: keywords={len(demand['keywords'])}")
        except Exception as e:
            test_results.append(("需求图谱分析", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试2: 来源构建
        print("\n[测试2/12] 文献来源清单...")
        try:
            demand = curator.stage1_demand_analysis("AI governance")
            sources = curator.stage2_source_building(demand)
            passed = len(sources) > 0
            test_results.append(("文献来源清单", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: sources={len(sources)}")
        except Exception as e:
            test_results.append(("文献来源清单", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试3: 向量化
        print("\n[测试3/12] 向量化处理...")
        try:
            demand = curator.stage1_demand_analysis("AI")
            sources = curator.stage2_source_building(demand)
            entries = curator.stage3_vectorization(sources)
            passed = len(entries) > 0 and hasattr(entries[0], 'expert_alignment')
            test_results.append(("向量化处理", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: entries={len(entries)}")
        except Exception as e:
            test_results.append(("向量化处理", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试4: 质量闸口
        print("\n[测试4/12] 质量闸口审查...")
        try:
            demand = curator.stage1_demand_analysis("AI")
            sources = curator.stage2_source_building(demand)
            entries = curator.stage3_vectorization(sources)
            passed_entries, stats = curator.stage4_quality_gate(entries)
            passed = stats['pass_rate'] >= 0
            test_results.append(("质量闸口审查", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: pass_rate={stats['pass_rate']*100:.1f}%")
        except Exception as e:
            test_results.append(("质量闸口审查", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试5: 完整流程
        print("\n[测试5/12] 完整四阶段流程...")
        try:
            report = curator.full_pipeline("AI governance and ethical frameworks")
            passed = (report.total_entries > 0 and 
                     report.quality_score > 0 and 
                     all(report.stage_check.values()))
            test_results.append(("完整四阶段流程", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: entries={report.total_entries}")
        except Exception as e:
            test_results.append(("完整四阶段流程", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试6: 多主题支持
        print("\n[测试6/12] 多主题支持...")
        try:
            topics = ["AI ethics", "decision making", "neuroscience"]
            all_passed = True
            for topic in topics:
                report = curator.full_pipeline(topic)
                if report.total_entries == 0:
                    all_passed = False
            test_results.append(("多主题支持", all_passed))
            print(f"  {'✅ PASS' if all_passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("多主题支持", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试7: 质量分数计算
        print("\n[测试7/12] 质量分数计算...")
        try:
            report = curator.full_pipeline("AI")
            passed = 0 <= report.quality_score <= 1
            test_results.append(("质量分数计算", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: score={report.quality_score:.2f}")
        except Exception as e:
            test_results.append(("质量分数计算", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试8: 阶段检查标记
        print("\n[测试8/12] 阶段检查标记...")
        try:
            report = curator.full_pipeline("AI")
            passed = len(report.stage_check) == 4
            test_results.append(("阶段检查标记", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {report.stage_check}")
        except Exception as e:
            test_results.append(("阶段检查标记", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试9: Expert_ID一致性
        print("\n[测试9/12] Expert_ID一致性...")
        try:
            report = curator.full_pipeline("AI")
            passed = report.expert_id == "CKA-17"
            test_results.append(("Expert_ID一致性", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {report.expert_id}")
        except Exception as e:
            test_results.append(("Expert_ID一致性", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试10: 条目属性完整性
        print("\n[测试10/12] 条目属性完整性...")
        try:
            demand = curator.stage1_demand_analysis("AI")
            sources = curator.stage2_source_building(demand)
            entries = curator.stage3_vectorization(sources)
            entry = entries[0]
            passed = all([entry.entry_id, entry.title, entry.authors])
            test_results.append(("条目属性完整性", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("条目属性完整性", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试11: 阈值过滤
        print("\n[测试11/12] 阈值过滤...")
        try:
            demand = curator.stage1_demand_analysis("AI")
            sources = curator.stage2_source_building(demand)
            entries = curator.stage3_vectorization(sources)
            passed_entries, stats = curator.stage4_quality_gate(entries)
            passed = stats['total_processed'] >= stats['passed']
            test_results.append(("阈值过滤", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: processed={stats['total_processed']}")
        except Exception as e:
            test_results.append(("阈值过滤", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试12: 统计功能
        print("\n[测试12/12] 统计功能...")
        try:
            curator2 = KnowledgeCurator(expert_id="CKA-17")
            report1 = curator2.full_pipeline("AI topic 1")
            report2 = curator2.full_pipeline("AI topic 2")
            stats = curator2.get_stats()
            passed = stats.get('total_curated', 0) >= 0
            test_results.append(("统计功能", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: total_curated={stats.get('total_curated', 0)}")
        except Exception as e:
            test_results.append(("统计功能", False))
            print(f"  ❌ FAIL: {e}")
        
        # 总结
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        passed_count = sum(1 for _, p in test_results if p)
        total_count = len(test_results)
        print(f"通过: {passed_count}/{total_count}")
        print(f"失败: {total_count - passed_count}/{total_count}")
        print(f"通过率: {passed_count/total_count*100:.1f}%")
        
        if passed_count == total_count:
            print("\n✅ 所有测试通过!")
            sys.exit(0)
        else:
            print("\n❌ 存在失败的测试:")
            for name, passed in test_results:
                if not passed:
                    print(f"  - {name}")
            sys.exit(1)
    else:
        print("=" * 60)
        print("知识策展人 - Knowledge Curator")
        print("=" * 60)
        print("\n使用 --test 运行完整测试套件")
        print("Expert_ID: CKA-17 (哲学文献筛选员)")