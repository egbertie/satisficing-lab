#!/usr/bin/env python3
"""
quality-gate-system 功能测试
测试真实实现
"""

import unittest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from quality_gate_system import (
    QualityGateSystem, QualityGate, GatePipeline,
    GateLevel, GateStatus, CheckResult
)


class TestQualityGateSystemReal(unittest.TestCase):
    """真实功能测试"""
    
    def setUp(self):
        """设置"""
        self.system = QualityGateSystem()
    
    def test_01_load_gate_configs(self):
        """测试加载门禁配置"""
        configs = self.system.gate_configs
        
        self.assertIn(GateLevel.L1_SYNTAX.value, configs)
        self.assertIn(GateLevel.L2_UNIT.value, configs)
        self.assertIn(GateLevel.L5_PRODUCTION.value, configs)
    
    def test_02_run_pipeline(self):
        """测试运行流水线"""
        pipeline = self.system.run_pipeline("test-artifact")
        
        self.assertIsInstance(pipeline, GatePipeline)
        self.assertEqual(pipeline.artifact_name, "test-artifact")
        self.assertTrue(pipeline.pipeline_id.startswith("PIPE-"))
    
    def test_03_pipeline_contains_all_gates(self):
        """测试流水线包含所有门禁"""
        pipeline = self.system.run_pipeline("test")
        
        levels = [g.level for g in pipeline.gates]
        self.assertIn(GateLevel.L1_SYNTAX.value, levels)
        self.assertIn(GateLevel.L2_UNIT.value, levels)
    
    def test_04_gate_has_checks(self):
        """测试门禁包含检查项"""
        pipeline = self.system.run_pipeline("test")
        
        for gate in pipeline.gates:
            self.assertGreater(len(gate.checks), 0)
            for check in gate.checks:
                self.assertIn(check.status, [r.value for r in CheckResult])
    
    def test_05_gate_status_calculation(self):
        """测试门禁状态计算"""
        pipeline = self.system.run_pipeline("test")
        
        for gate in pipeline.gates:
            if gate.failed_checks > 0:
                # 有失败的门禁可能是FAILED或PASSED（非阻塞）
                self.assertIn(gate.overall_status, [GateStatus.FAILED.value, GateStatus.PASSED.value])
    
    def test_06_can_proceed(self):
        """测试是否可以继续"""
        pipeline = self.system.run_pipeline("test")
        
        # 对于通过的级别，应该可以继续
        for level in pipeline.completed_levels:
            can_go, msg = self.system.can_proceed(pipeline, level)
            self.assertTrue(can_go)
    
    def test_07_get_gate_summary(self):
        """测试获取门禁摘要"""
        pipeline = self.system.run_pipeline("test")
        summary = self.system.get_gate_summary(pipeline)
        
        self.assertIn('pipeline_id', summary)
        self.assertIn('artifact', summary)
        self.assertIn('status', summary)
        self.assertIn('progress', summary)
        self.assertIn('gates', summary)
    
    def test_08_export_report_json(self):
        """测试JSON导出"""
        pipeline = self.system.run_pipeline("test")
        json_str = self.system.export_report(pipeline, "json")
        data = json.loads(json_str)
        
        self.assertIn("pipeline_id", data)
        self.assertIn("overall_status", data)
        self.assertIn("gates", data)
    
    def test_09_export_report_markdown(self):
        """测试Markdown导出"""
        pipeline = self.system.run_pipeline("test")
        md = self.system.export_report(pipeline, "markdown")
        
        self.assertIn("# 质量门禁报告", md)
        self.assertIn("test", md)
    
    def test_10_pipeline_tracking(self):
        """测试流水线追踪"""
        pipeline1 = self.system.run_pipeline("artifact-1")
        pipeline2 = self.system.run_pipeline("artifact-2")
        
        self.assertEqual(len(self.system.pipeline_history), 2)
        self.assertIn(pipeline1, self.system.pipeline_history)
        self.assertIn(pipeline2, self.system.pipeline_history)
    
    def test_11_different_start_levels(self):
        """测试从不同级别开始"""
        pipeline = self.system.run_pipeline("test", GateLevel.L2_UNIT.value)
        
        levels = [g.level for g in pipeline.gates]
        self.assertNotIn(GateLevel.L1_SYNTAX.value, levels)
        self.assertIn(GateLevel.L2_UNIT.value, levels)


class TestQualityGateSystemIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_cli_run_pipeline(self):
        """测试CLI运行流水线"""
        import subprocess
        
        result = subprocess.run(
            ["python3", "scripts/main.py", "--run", "cli-test", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # 应该成功
        self.assertEqual(result.returncode, 0)
        output = result.stdout
        self.assertIn("pipeline_id", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
