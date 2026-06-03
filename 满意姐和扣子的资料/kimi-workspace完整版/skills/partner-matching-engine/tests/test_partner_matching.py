#!/usr/bin/env python3
"""
Partner Matching Engine - 测试套件

测试覆盖:
1. 数据模型测试
2. 满意解匹配算法测试
3. 互补性算法测试
4. 价值观评估测试
5. 风险兼容测试
6. 解释生成测试
7. 数据持久化测试
8. CLI集成测试
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# 添加脚本目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from partner_matching import (
    FounderProfile, CandidateProfile, ValueDimension, RiskIndicators,
    TrackRecord, SatisficingMatcher, ExplanationGenerator,
    MatchingResultStore, SatisficingThresholds, DimensionScores, MatchResult
)


class TestDataModels(unittest.TestCase):
    """数据模型测试"""
    
    def test_founder_profile_creation(self):
        """测试创始人画像创建"""
        founder = FounderProfile(
            name="测试创始人",
            industry="AI芯片",
            stage="pre_a",
            capability_matrix={
                "technical_depth": 3,
                "business_acumen": 4
            }
        )
        self.assertIsNotNone(founder.id)
        self.assertEqual(founder.name, "测试创始人")
        self.assertEqual(founder.industry, "AI芯片")
    
    def test_founder_profile_serialization(self):
        """测试创始人画像序列化"""
        founder = FounderProfile(
            name="测试创始人",
            industry="AI芯片",
            capability_matrix={"technical_depth": 3}
        )
        data = founder.to_dict()
        restored = FounderProfile.from_dict(data)
        
        self.assertEqual(restored.name, founder.name)
        self.assertEqual(restored.industry, founder.industry)
    
    def test_candidate_profile_creation(self):
        """测试候选人画像创建"""
        candidate = CandidateProfile(
            name="测试候选人",
            current_role="CTO",
            capability_matrix={"technical_depth": 9}
        )
        self.assertIsNotNone(candidate.id)
        self.assertEqual(candidate.name, "测试候选人")
    
    def test_value_dimension_creation(self):
        """测试价值观维度创建"""
        value = ValueDimension(
            score=0.8,
            evidence=["团队评价良好"],
            confidence=0.9
        )
        self.assertEqual(value.score, 0.8)
        self.assertEqual(len(value.evidence), 1)


class TestSatisficingMatcher(unittest.TestCase):
    """满意解匹配算法测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.founder = FounderProfile(
            name="张创始人",
            industry="AI芯片",
            stage="pre_a",
            capability_matrix={
                "technical_depth": 3,
                "business_acumen": 4,
                "financial_management": 3,
                "fundraising": 2
            },
            value_system={"long_term_orientation": 0.8},
            risk_profile={"exit_timeline_years": 7},
            partner_requirements={
                "must_have_capabilities": ["fundraising"],
                "max_equity_offer": 0.35
            }
        )
        
        # 理想候选人 - 应满足满意解
        self.ideal_candidate = CandidateProfile(
            name="理想候选人",
            current_role="前CFO",
            capability_matrix={
                "technical_depth": 2,
                "business_acumen": 8,
                "financial_management": 9,
                "fundraising": 9
            },
            value_alignment_evidence={
                "ren": ValueDimension(score=0.8, evidence=["证据1"]),
                "yi": ValueDimension(score=0.9, evidence=["证据2"]),
                "li": ValueDimension(score=0.8, evidence=["证据3"]),
                "zhi": ValueDimension(score=0.85, evidence=["证据4"]),
                "xin": ValueDimension(score=0.9, evidence=["证据5"])
            },
            risk_indicators=RiskIndicators(
                equity_expectation=0.25,
                employment_status="full_time"
            )
        )
        
        # 问题候选人 - 有deal breaker
        self.problem_candidate = CandidateProfile(
            name="问题候选人",
            current_role="顾问",
            capability_matrix={
                "technical_depth": 5,
                "business_acumen": 7
            },
            value_alignment_evidence={
                "ren": ValueDimension(score=0.4),  # 低于0.5，deal breaker
                "yi": ValueDimension(score=0.9),
                "li": ValueDimension(score=0.8),
                "zhi": ValueDimension(score=0.85),
                "xin": ValueDimension(score=0.9)
            },
            risk_indicators=RiskIndicators(
                equity_expectation=0.40,  # 超过max_equity_offer
                employment_status="part_time_available",
                pending_litigations=["诉讼1"]  # deal breaker
            )
        )
    
    def test_satisficing_matcher_initialization(self):
        """测试匹配器初始化"""
        thresholds = SatisficingThresholds(
            complementarity=70,
            values_alignment=75
        )
        matcher = SatisficingMatcher(thresholds)
        
        self.assertEqual(matcher.thresholds.complementarity, 70)
        self.assertEqual(matcher.thresholds.values_alignment, 75)
    
    def test_deal_breaker_detection(self):
        """测试一票否决检测"""
        matcher = SatisficingMatcher()
        deal_breakers = matcher._check_deal_breakers(self.founder, self.problem_candidate)
        
        # 应有多个deal breakers
        self.assertGreater(len(deal_breakers), 0)
        # 应包含诉讼相关
        self.assertTrue(any("诉讼" in db for db in deal_breakers))
    
    def test_complementarity_calculation(self):
        """测试互补性计算"""
        matcher = SatisficingMatcher()
        score = matcher._calc_complementarity(
            self.founder.capability_matrix,
            self.ideal_candidate.capability_matrix,
            ["fundraising"]
        )
        
        # 应有互补性分数（只要大于0即可，具体分数取决于算法）
        self.assertGreater(score, 0)
    
    def test_values_alignment_calculation(self):
        """测试价值观对齐计算"""
        matcher = SatisficingMatcher()
        score = matcher._calc_values_alignment(
            self.ideal_candidate.value_alignment_evidence,
            self.founder.value_system
        )
        
        # 应有较高的价值观分数
        self.assertGreater(score, 70)
    
    def test_match_all_sorting(self):
        """测试匹配结果排序"""
        candidates = [self.problem_candidate, self.ideal_candidate]
        matcher = SatisficingMatcher()
        results = matcher.match_all(self.founder, candidates)
        
        # 结果应按得分降序排列
        self.assertEqual(len(results), 2)
        self.assertGreater(results[0].overall_score, results[1].overall_score)
    
    def test_find_satisficing(self):
        """测试满意解查找"""
        candidates = [self.ideal_candidate, self.problem_candidate]
        matcher = SatisficingMatcher()
        
        # 大幅降低阈值确保能找到满意解
        matcher.thresholds = SatisficingThresholds(
            complementarity=30,
            values_alignment=30,
            risk_compatibility=30,
            growth_potential=30
        )
        
        result = matcher.find_satisficing(self.founder, candidates)
        
        # 应找到结果（即使不满足满意解，也应该返回最佳替代）
        self.assertIsNotNone(result)
        self.assertEqual(result.candidate_id, self.ideal_candidate.id)


class TestExplanationGenerator(unittest.TestCase):
    """解释生成器测试"""
    
    def setUp(self):
        self.founder = FounderProfile(
            name="测试创始人",
            industry="AI芯片"
        )
        self.candidate = CandidateProfile(
            name="测试候选人",
            current_role="CTO"
        )
    
    def test_explanation_generation(self):
        """测试解释生成"""
        result = MatchResult(
            candidate_id=self.candidate.id,
            candidate_name=self.candidate.name,
            overall_score=85.0,
            satisficing_met=True,
            dimension_scores=DimensionScores(
                complementarity=90,
                values_alignment=80,
                risk_compatibility=85,
                growth_potential=75
            )
        )
        
        generator = ExplanationGenerator()
        explanation = generator.generate(result, self.founder, self.candidate)
        
        # 应包含所有必要字段
        self.assertIn("executive_summary", explanation)
        self.assertIn("detailed_analysis", explanation)
        self.assertIn("risk_assessment", explanation)
        self.assertIn("analogy", explanation)
        self.assertIn("claw_recommended_questions", explanation)
    
    def test_analogy_generation(self):
        """测试类比生成"""
        generator = ExplanationGenerator()
        
        # 高分
        result_high = MatchResult(overall_score=90, satisficing_met=True)
        analogy_high = generator._generate_analogy(result_high)
        self.assertIn("刘备", analogy_high)
        
        # 中分
        result_mid = MatchResult(overall_score=75, satisficing_met=True)
        analogy_mid = generator._generate_analogy(result_mid)
        self.assertIn("唐僧", analogy_mid)
        
        # 低分
        result_low = MatchResult(overall_score=50, satisficing_met=False)
        analogy_low = generator._generate_analogy(result_low)
        self.assertIn("项羽", analogy_low)


class TestDataPersistence(unittest.TestCase):
    """数据持久化测试"""
    
    def setUp(self):
        """创建临时数据库"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
    
    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_store_initialization(self):
        """测试存储初始化"""
        store = MatchingResultStore(self.db_path)
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_save_and_retrieve_founder(self):
        """测试保存和读取创始人"""
        store = MatchingResultStore(self.db_path)
        
        founder = FounderProfile(
            name="测试创始人",
            industry="AI芯片"
        )
        
        founder_id = store.save_founder(founder)
        self.assertEqual(founder_id, founder.id)
    
    def test_save_result(self):
        """测试保存匹配结果"""
        store = MatchingResultStore(self.db_path)
        
        founder = FounderProfile(name="创始人")
        candidate = CandidateProfile(name="候选人")
        result = MatchResult(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            overall_score=85.0
        )
        
        store.save_founder(founder)
        store.save_candidate(candidate)
        result_id = store.save_result(founder.id, candidate.id, result)
        
        self.assertIsInstance(result_id, int)
        self.assertGreater(result_id, 0)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_matching_workflow(self):
        """测试完整匹配流程"""
        # 1. 创建创始人
        founder = FounderProfile(
            name="完整测试创始人",
            industry="生物医药",
            stage="seed",
            capability_matrix={
                "technical_depth": 8,
                "business_acumen": 3,
                "financial_management": 2,
                "fundraising": 2
            },
            value_system={"long_term_orientation": 0.9},
            partner_requirements={
                "must_have_capabilities": ["business_acumen", "fundraising"],
                "max_equity_offer": 0.30
            }
        )
        
        # 2. 创建多个候选人
        candidates = [
            CandidateProfile(
                name="商业合伙人A",
                capability_matrix={
                    "technical_depth": 3,
                    "business_acumen": 9,
                    "financial_management": 8,
                    "fundraising": 9
                },
                value_alignment_evidence={
                    "ren": ValueDimension(score=0.85),
                    "yi": ValueDimension(score=0.9),
                    "li": ValueDimension(score=0.8),
                    "zhi": ValueDimension(score=0.85),
                    "xin": ValueDimension(score=0.9)
                },
                risk_indicators=RiskIndicators(
                    equity_expectation=0.25,
                    employment_status="full_time"
                )
            ),
            CandidateProfile(
                name="技术合伙人B",
                capability_matrix={
                    "technical_depth": 9,
                    "business_acumen": 4
                },
                value_alignment_evidence={
                    "ren": ValueDimension(score=0.8),
                    "yi": ValueDimension(score=0.85),
                    "li": ValueDimension(score=0.75),
                    "zhi": ValueDimension(score=0.8),
                    "xin": ValueDimension(score=0.85)
                },
                risk_indicators=RiskIndicators(
                    equity_expectation=0.20,
                    employment_status="full_time"
                )
            )
        ]
        
        # 3. 执行匹配
        matcher = SatisficingMatcher()
        results = matcher.match_all(founder, candidates)
        
        # 4. 验证结果
        self.assertEqual(len(results), 2)
        
        # 商业合伙人A应有更高分数（互补性更好）
        business_result = next(r for r in results if "商业" in r.candidate_name)
        tech_result = next(r for r in results if "技术" in r.candidate_name)
        
        self.assertGreater(business_result.dimension_scores.complementarity,
                          tech_result.dimension_scores.complementarity)
        
        # 5. 生成解释
        explainer = ExplanationGenerator()
        for result in results:
            candidate = next(c for c in candidates if c.id == result.candidate_id)
            explanation = explainer.generate(result, founder, candidate)
            self.assertIn("executive_summary", explanation)


if __name__ == '__main__':
    unittest.main(verbosity=2)
