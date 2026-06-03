#!/usr/bin/env python3
"""
theory-miner 功能测试
测试真实实现
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from theory_miner import (
    TheoryMiner, TheoryNode, Concept, Source,
    TheoryType, SourceType, TheoryRelation
)


class TestTheoryMinerReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.miner = TheoryMiner(self.temp_dir)
    
    def tearDown(self):
        """清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_01_extract_from_markdown(self):
        """测试从Markdown提取理论"""
        # 创建测试文档
        test_doc = Path(self.temp_dir) / "test_theory.md"
        test_doc.write_text("""
# 满意解决策理论

## 核心概念

满意解(Satisficing): 在满足最低标准的前提下停止搜索，而非追求最优解。

**决策成本**: 搜索最优解的成本可能超过收益。

## 应用场景

适用: 硬科技合伙人匹配决策
适用: 资源受限情况下的快速决策

## 相关理论

- 前景理论
- 双系统理论
""", encoding='utf-8')
        
        result = self.miner.extract_from_document(str(test_doc))
        
        self.assertGreater(len(result.theories_found), 0)
        self.assertGreater(result.confidence_score, 0)
    
    def test_02_search_theories(self):
        """测试搜索理论"""
        # 先添加一个理论
        theory = TheoryNode(
            theory_id="TEST-001",
            name="满意解决策",
            theory_type=TheoryType.DECISION_MODEL.value,
            description="在满足最低标准的前提下停止搜索",
            core_concepts=[Concept(name="满意解", definition="满足最低标准的解")],
            source=Source(title="Test", author="Test", source_type=SourceType.INTERNAL.value),
            tags=["决策", "匹配"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        self.miner.theories["TEST-001"] = theory
        self.miner._save_theories()
        
        # 搜索
        results = self.miner.search_theories("满意解")
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0].name, "满意解决策")
    
    def test_03_export_theory_summary(self):
        """测试导出理论摘要"""
        theory = TheoryNode(
            theory_id="TEST-002",
            name="测试理论",
            theory_type=TheoryType.FRAMEWORK.value,
            description="这是一个测试理论",
            core_concepts=[Concept(name="概念A", definition="定义A")],
            source=Source(title="测试来源", author="测试作者", source_type=SourceType.INTERNAL.value),
            applications=["场景1", "场景2"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        self.miner.theories["TEST-002"] = theory
        
        summary = self.miner.export_theory_summary("TEST-002")
        
        self.assertIn("测试理论", summary)
        self.assertIn("概念A", summary)
    
    def test_04_generate_theory_map(self):
        """测试生成理论图谱"""
        # 添加两个理论
        for i in range(2):
            theory = TheoryNode(
                theory_id=f"TEST-{i+3}",
                name=f"理论{i+1}",
                theory_type=TheoryType.CONCEPT.value if i == 0 else TheoryType.FRAMEWORK.value,
                description=f"描述{i+1}",
                core_concepts=[],
                source=Source(title="Test", author="Test", source_type=SourceType.INTERNAL.value),
                tags=["测试"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            self.miner.theories[f"TEST-{i+3}"] = theory
        
        map_md = self.miner.generate_theory_map()
        
        self.assertIn("理论图谱", map_md)
        self.assertIn("理论1", map_md)
    
    def test_05_get_statistics(self):
        """测试获取统计"""
        # 添加理论
        theory = TheoryNode(
            theory_id="TEST-005",
            name="统计测试",
            theory_type=TheoryType.PRINCIPLE.value,
            description="测试",
            core_concepts=[Concept(name="C1", definition="D1"), Concept(name="C2", definition="D2")],
            source=Source(title="Test", author="Test", source_type=SourceType.INTERNAL.value),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        self.miner.theories["TEST-005"] = theory
        
        stats = self.miner.get_statistics()
        
        self.assertEqual(stats['total_theories'], 1)
        self.assertEqual(stats['total_concepts'], 2)
    
    def test_06_persistence(self):
        """测试数据持久化"""
        theory = TheoryNode(
            theory_id="TEST-006",
            name="持久化测试",
            theory_type=TheoryType.METHODOLOGY.value,
            description="测试持久化",
            core_concepts=[],
            source=Source(title="Test", author="Test", source_type=SourceType.INTERNAL.value),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        self.miner.theories["TEST-006"] = theory
        self.miner._save_theories()
        
        # 重新加载
        miner2 = TheoryMiner(self.temp_dir)
        loaded = miner2.get_theory("TEST-006")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "持久化测试")


class TestTheoryMinerIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cli_extract_and_search(self):
        """测试CLI提取和搜索"""
        import subprocess
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            # 创建测试文档
            test_doc = Path(temp_dir) / "theory.md"
            test_doc.write_text("""
# 测试决策模型

**满意解**: 在满足最低标准时停止搜索。

适用: 硬科技项目决策
""")
            
            # 提取
            result = subprocess.run(
                ["python3", "scripts/main.py", "--extract", str(test_doc),
                 "--source-title", "测试文档", "--data-dir", temp_dir],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn("提取完成", result.stdout)
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
