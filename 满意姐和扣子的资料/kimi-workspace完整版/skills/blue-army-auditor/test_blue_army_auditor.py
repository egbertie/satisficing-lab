#!/usr/bin/env python3
"""
blue-army-auditor 单元测试
"""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from blue_army_auditor import BlueArmyAuditor, Priority, AuditStatus


class TestBlueArmyAuditor(unittest.TestCase):
    """BlueArmyAuditor单元测试"""
    
    def setUp(self):
        self.auditor = BlueArmyAuditor(skills_dir="~/.openclaw/workspace/skills")
    
    def test_audit_existing_skill(self):
        """测试审计已存在的Skill"""
        record = self.auditor.audit_skill("checkpoint-manager")
        
        self.assertEqual(record.skill_name, "checkpoint-manager")
        self.assertIn(record.status, [AuditStatus.PASS, AuditStatus.CONDITIONAL, AuditStatus.FAIL])
        self.assertGreater(len(record.items), 0)
    
    def test_audit_nonexistent_skill(self):
        """测试审计不存在的Skill"""
        record = self.auditor.audit_skill("nonexistent-skill-xyz")
        
        self.assertEqual(record.status, AuditStatus.FAIL)
        self.assertIn("error", record.summary)
    
    def test_audit_summary(self):
        """测试审计汇总"""
        record = self.auditor.audit_skill("blackboard-manager")
        
        summary = record.summary
        self.assertIn("total", summary)
        self.assertIn("passed", summary)
        self.assertIn("failed", summary)
        self.assertGreaterEqual(summary["total"], summary["passed"])
    
    def test_audit_items_have_priority(self):
        """测试审计项都有优先级"""
        record = self.auditor.audit_skill("worker-orchestrator")
        
        for item in record.items:
            self.assertIn(item.priority, [Priority.P0, Priority.P1, Priority.P2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
