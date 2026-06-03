#!/usr/bin/env python3
"""
case-repository 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from case_repository import (
    CaseRepository, PartnerMatchingCase, FounderProfile,
    PartnerRequirements, MatchingProcess, SelectedPartner, Outcome,
    Industry, Stage, PartnerType, CaseOutcome
)


class TestCaseRepositoryReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = CaseRepository(self.temp_dir)
    
    def tearDown(self):
        """清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_01_create_case(self):
        """测试创建案例"""
        case = self.repo.create_case(
            case_name="测试案例",
            industry="AI芯片",
            stage="天使轮",
            partner_type="商业合伙人",
            founder_bg="技术",
            core_tech="测试技术",
            main_strength="技术优势",
            main_weakness="商业弱势"
        )
        
        self.assertIsInstance(case, PartnerMatchingCase)
        self.assertTrue(case.case_id.startswith("CASE-"))
        self.assertEqual(case.industry, "AI芯片")
    
    def test_02_get_case(self):
        """测试获取案例"""
        case = self.repo.create_case("测试", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        retrieved = self.repo.get_case(case.case_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.case_id, case.case_id)
    
    def test_03_list_cases(self):
        """测试列出案例"""
        self.repo.create_case("案例1", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        self.repo.create_case("案例2", "生物医药", "A轮", "技术合伙人", "商业", "", "", "")
        
        all_cases = self.repo.list_cases()
        ai_cases = self.repo.list_cases(industry="AI芯片")
        
        self.assertEqual(len(all_cases), 2)
        self.assertEqual(len(ai_cases), 1)
    
    def test_04_search_cases(self):
        """测试搜索案例"""
        self.repo.create_case("深圳芯片项目", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        self.repo.create_case("北京医药项目", "生物医药", "A轮", "技术合伙人", "商业", "", "", "")
        
        results = self.repo.search_cases("芯片")
        
        self.assertGreater(len(results), 0)
        # 第一个应该是芯片案例
        self.assertIn("芯片", results[0][0].case_name)
    
    def test_05_find_similar_cases(self):
        """测试查找相似案例"""
        # 创建几个案例
        self.repo.create_case("芯片案例1", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        self.repo.create_case("芯片案例2", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        self.repo.create_case("医药案例", "生物医药", "A轮", "技术合伙人", "商业", "", "", "")
        
        # 更新一个为成功状态
        case = self.repo.cases[0]
        case.outcome = CaseOutcome.SUCCESS.value
        self.repo._save_cases()
        
        # 重新加载以获取更新
        repo2 = CaseRepository(self.temp_dir)
        similar = repo2.find_similar_cases("技术", "AI芯片", "天使轮", "商业合伙人")
        
        self.assertGreater(len(similar), 0)
        # 相似案例应该包含芯片相关
        self.assertIn("芯片", similar[0][0].case_name)
    
    def test_06_get_statistics(self):
        """测试获取统计"""
        # 创建几个不同结果的案例
        case1 = self.repo.create_case("成功案例", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        case1.outcome = CaseOutcome.SUCCESS.value
        
        case2 = self.repo.create_case("失败案例", "生物医药", "A轮", "技术合伙人", "商业", "", "", "")
        case2.outcome = CaseOutcome.FAILURE.value
        
        self.repo._save_cases()
        
        stats = self.repo.get_statistics()
        
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['success'], 1)
        self.assertEqual(stats['failure'], 1)
        self.assertEqual(stats['success_rate'], 0.5)
    
    def test_07_persistence(self):
        """测试数据持久化"""
        case = self.repo.create_case("持久化测试", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        case_id = case.case_id
        
        # 重新加载
        repo2 = CaseRepository(self.temp_dir)
        loaded = repo2.get_case(case_id)
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.case_name, "持久化测试")
    
    def test_08_export_for_matching_engine(self):
        """测试导出给匹配引擎"""
        case1 = self.repo.create_case("案例1", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        case1.outcome = CaseOutcome.SUCCESS.value
        
        case2 = self.repo.create_case("案例2", "生物医药", "A轮", "技术合伙人", "商业", "", "", "")
        # 保持pending状态
        
        self.repo._save_cases()
        
        exported = self.repo.export_for_matching_engine()
        
        # 只导出非pending的案例
        self.assertEqual(len(exported), 1)
    
    def test_09_generate_lessons_report(self):
        """测试生成经验教训报告"""
        case = self.repo.create_case("测试", "AI芯片", "天使轮", "商业合伙人", "技术", "", "", "")
        case.outcome_details.key_success_factors = ["因素1", "因素2"]
        case.outcome_details.lessons_learned = ["教训1", "教训2"]
        self.repo._save_cases()
        
        report = self.repo.generate_lessons_report()
        
        self.assertIn("经验教训报告", report)
        self.assertIn("因素1", report)
        self.assertIn("教训1", report)


class TestCaseRepositoryIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cli_create_and_list(self):
        """测试CLI创建和列出"""
        import subprocess
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            # 创建案例
            result = subprocess.run(
                ["python3", "scripts/main.py", "--create", "CLI测试", "AI芯片", "天使轮", "商业合伙人",
                 "--founder-bg", "技术", "--core-tech", "测试", "--strength", "优势", "--weakness", "弱势",
                 "--data-dir", temp_dir],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn("案例已创建", result.stdout)
            
            # 列出案例
            result2 = subprocess.run(
                ["python3", "scripts/main.py", "--list", "--data-dir", temp_dir],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            self.assertEqual(result2.returncode, 0)
            self.assertIn("CLI测试", result2.stdout)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
