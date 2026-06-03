#!/usr/bin/env python3
"""
quality-assessment 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from quality_assessment import QualityAssessor, AssessmentResult, DimensionScore, QualityGrade, DimensionType


class TestQualityAssessorReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置"""
        self.assessor = QualityAssessor()
    
    def test_01_assess_complete_deliverable(self):
        """测试完整交付物评估"""
        deliverable = {
            'name': '测试交付物',
            'content': '# 标题\n\n这是正文内容。包含完整的信息和结论。',
            'metadata': {'create_time': '2026-04-03T10:00:00'}
        }
        
        result = self.assessor.assess(deliverable)
        
        self.assertIsInstance(result, AssessmentResult)
        self.assertEqual(result.deliverable_name, '测试交付物')
        self.assertGreater(result.overall_score, 0)
    
    def test_02_completeness_assessment(self):
        """测试完整性评估"""
        deliverable = {
            'name': '测试',
            'content': '短内容',
            'metadata': {}
        }
        
        result = self.assessor.assess(deliverable)
        
        completeness = next((d for d in result.dimension_scores if d.dimension == DimensionType.COMPLETENESS.value), None)
        self.assertIsNotNone(completeness)
        self.assertLess(completeness.score, 100)  # 应该有问题
    
    def test_03_accuracy_assessment(self):
        """测试准确性评估"""
        deliverable = {
            'name': '测试',
            'content': '这是正确的内容，没有错误标记。',
            'metadata': {}
        }
        
        result = self.assessor.assess(deliverable)
        
        accuracy = next((d for d in result.dimension_scores if d.dimension == DimensionType.ACCURACY.value), None)
        self.assertIsNotNone(accuracy)
    
    def test_04_grade_calculation(self):
        """测试等级计算"""
        self.assertEqual(self.assessor._get_grade(95), QualityGrade.A.value)
        self.assertEqual(self.assessor._get_grade(85), QualityGrade.B.value)
        self.assertEqual(self.assessor._get_grade(75), QualityGrade.C.value)
        self.assertEqual(self.assessor._get_grade(65), QualityGrade.D.value)
        self.assertEqual(self.assessor._get_grade(50), QualityGrade.F.value)
    
    def test_05_overall_score_calculation(self):
        """测试总分计算"""
        dimensions = [
            DimensionScore(DimensionType.COMPLETENESS.value, 80, 100, 0.25, [], []),
            DimensionScore(DimensionType.ACCURACY.value, 90, 100, 0.30, [], []),
            DimensionScore(DimensionType.STANDARDIZATION.value, 85, 100, 0.20, [], []),
            DimensionScore(DimensionType.TIMELINESS.value, 95, 100, 0.15, [], []),
            DimensionScore(DimensionType.USABILITY.value, 88, 100, 0.10, [], [])
        ]
        
        score = self.assessor._calculate_overall_score(dimensions)
        expected = 80*0.25 + 90*0.30 + 85*0.20 + 95*0.15 + 88*0.10
        
        self.assertAlmostEqual(score, expected, places=1)
    
    def test_06_issue_counting(self):
        """测试问题统计"""
        deliverable = {
            'name': '测试',
            'content': '',  # 空内容，会有问题
            'metadata': {}
        }
        
        result = self.assessor.assess(deliverable)
        
        self.assertGreater(result.total_issues, 0)
    
    def test_07_generate_recommendations(self):
        """测试生成建议"""
        dimensions = [
            DimensionScore(DimensionType.COMPLETENESS.value, 60, 100, 0.25, ['问题1'], [])
        ]
        
        recommendations = self.assessor._generate_recommendations(dimensions, 60)
        
        self.assertGreater(len(recommendations), 0)
    
    def test_08_export_report_json(self):
        """测试JSON导出"""
        deliverable = {
            'name': '测试',
            'content': '测试内容',
            'metadata': {}
        }
        
        result = self.assessor.assess(deliverable)
        json_str = self.assessor.export_report(result, "json")
        data = json.loads(json_str)
        
        self.assertIn("overall_score", data)
        self.assertIn("grade", data)
    
    def test_09_export_report_markdown(self):
        """测试Markdown导出"""
        deliverable = {
            'name': '测试',
            'content': '测试内容',
            'metadata': {}
        }
        
        result = self.assessor.assess(deliverable)
        md = self.assessor.export_report(result, "markdown")
        
        self.assertIn("# 质量评估报告", md)
        self.assertIn("总体评分", md)
    
    def test_10_standardization_assessment(self):
        """测试规范性评估"""
        deliverable = {
            'name': '测试',
            'content': '没有标题的长文本' * 50,
            'metadata': {}
        }
        
        result = self.assessor.assess(deliverable)
        
        std = next((d for d in result.dimension_scores if d.dimension == DimensionType.STANDARDIZATION.value), None)
        self.assertIsNotNone(std)


class TestQualityAssessorIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cli_with_content(self):
        """测试CLI内容评估"""
        import subprocess
        
        result = subprocess.run(
            ["python3", "scripts/main.py", "--content", "# 测试文档\n\n这是测试内容。", "--name", "CLI测试"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0)
        output = result.stdout
        self.assertIn("质量评估报告", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
