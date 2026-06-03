#!/usr/bin/env python3
"""
Sentinel Guard - 哨兵守卫系统
守护系统安全，防止违规操作
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

WORKSPACE = Path("/root/.openclaw/workspace")
GUARD_DB = WORKSPACE / "memory" / "sentinel-guard-db.json"

class SentinelGuard:
    """哨兵守卫 - 守护系统安全"""
    
    def __init__(self):
        self.db_path = GUARD_DB
        self.violations = self._load_db()
        self.rules = self._load_rules()
    
    def _load_db(self) -> Dict:
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {"violations": [], "blocks": []}
    
    def _load_rules(self) -> List[Dict]:
        """加载安全规则"""
        return [
            {"id": "R1", "name": "禁止rm -rf", "pattern": "rm -rf", "severity": "critical"},
            {"id": "R2", "name": "禁止删除.git", "pattern": "rm.*\.git", "severity": "high"},
            {"id": "R3", "name": "禁止覆盖SOUL.md", "pattern": "write.*SOUL\.md", "severity": "high"}
        ]
    
    def _save_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.violations, f, indent=2)
    
    def check_command(self, command: str) -> Optional[Dict]:
        """检查命令是否违规"""
        for rule in self.rules:
            if rule["pattern"] in command:
                return rule
        return None
    
    def record_violation(self, command: str, rule: Dict, blocked: bool = True):
        """记录违规"""
        violation = {
            "id": f"VIO-{len(self.violations['violations'])}",
            "command": command[:100],  # 限制长度
            "rule": rule["id"],
            "severity": rule["severity"],
            "blocked": blocked,
            "timestamp": datetime.now().isoformat()
        }
        self.violations["violations"].append(violation)
        self._save_db()
        return violation["id"]
    
    def get_status(self) -> Dict:
        """获取状态"""
        violations = self.violations["violations"]
        return {
            "total_violations": len(violations),
            "blocked": len([v for v in violations if v["blocked"]]),
            "critical": len([v for v in violations if v["severity"] == "critical"])
        }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("="*60)
        print("🧪 Sentinel Guard S5/S7 验证")
        print("="*60)
        
        guard = SentinelGuard()
        
        # S7: 对抗测试
        print("\n[S7] 对抗测试...")
        
        # 测试1: 检查安全命令
        result = guard.check_command("ls -la")
        assert result is None, "安全命令应返回None"
        print("  ✅ 安全命令测试通过")
        
        # 测试2: 检查危险命令
        result = guard.check_command("rm -rf /")
        assert result is not None, "危险命令应检测到"
        assert result["severity"] == "critical", "应是critical级别"
        print("  ✅ 危险命令检测测试通过")
        
        # 测试3: 空命令
        result = guard.check_command("")
        assert result is None, "空命令应返回None"
        print("  ✅ 空命令测试通过")
        
        # 测试4: 记录违规
        rule = {"id": "TEST", "severity": "high"}
        vio_id = guard.record_violation("test cmd", rule)
        assert vio_id, "应记录违规"
        print("  ✅ 违规记录测试通过")
        
        # S5: 自我验证
        print("\n[S5] 自我验证...")
        status = guard.get_status()
        assert "total_violations" in status, "状态应有total_violations"
        print("  ✅ 状态统计正确")
        
        print("\n" + "="*60)
        print("✅ S5/S7验证通过")
        print("="*60)
        return 0
    else:
        guard = SentinelGuard()
        print(f"Sentinel Guard 初始化完成")
        print(f"违规记录: {guard.get_status()['total_violations']}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
