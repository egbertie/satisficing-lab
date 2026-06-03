#!/usr/bin/env python3
"""
disaster-recovery-auditor 单元测试
"""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from disaster_recovery_auditor import DisasterRecoveryAuditor


class TestDisasterRecoveryAuditor(unittest.TestCase):
    """DisasterRecoveryAuditor单元测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.auditor = DisasterRecoveryAuditor(
            checkpoint_dir=f"{self.temp_dir}/checkpoints",
            audit_log_path=f"{self.temp_dir}/audit.json",
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_audit_no_checkpoints(self):
        """测试无检查点时的审计"""
        audit = self.auditor.audit_checkpoint()
        
        self.assertEqual(audit.status, "FAIL")
        self.assertIn("无可用检查点", audit.issues)
    
    def test_get_audit_summary_no_data(self):
        """测试无数据时的汇总"""
        summary = self.auditor.get_audit_summary()
        
        self.assertEqual(summary["status"], "NO_DATA")
    
    def test_rpo_target(self):
        """测试RPO目标值"""
        self.assertEqual(self.auditor.RPO_TARGET, 300)  # 5分钟
    
    def test_rto_target(self):
        """测试RTO目标值"""
        self.assertEqual(self.auditor.RTO_TARGET, 600)  # 10分钟


if __name__ == "__main__":
    unittest.main(verbosity=2)
