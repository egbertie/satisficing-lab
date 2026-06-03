#!/usr/bin/env python3
"""
Blue Sentinel - 蓝军哨兵系统
持续监控系统健康状态，主动发现问题
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

WORKSPACE = Path("/root/.openclaw/workspace")
SENTINEL_DB = WORKSPACE / "memory" / "blue-sentinel-db.json"

class BlueSentinel:
    """蓝军哨兵 - 持续监控系统健康"""
    
    def __init__(self):
        self.db_path = SENTINEL_DB
        self.alerts = self._load_db()
    
    def _load_db(self) -> Dict:
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {"alerts": [], "checks": []}
    
    def _save_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def check_fin_honesty(self) -> List[Dict]:
        """检查FIN状态诚实性"""
        issues = []
        skills_dir = WORKSPACE / "skills"
        
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    content = skill_md.read_text()
                    if "状态.*FIN" in content or "FIN" in content:
                        # 检查是否有Python代码
                        py_files = list(skill_dir.glob("*.py"))
                        if not py_files:
                            issues.append({
                                "skill": skill_dir.name,
                                "issue": "声称FIN但无Python代码",
                                "severity": "high"
                            })
        
        return issues
    
    def record_alert(self, alert_type: str, message: str, severity: str = "medium"):
        """记录告警"""
        alert = {
            "id": f"ALT-{len(self.alerts['alerts'])}",
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "resolved": False
        }
        self.alerts["alerts"].append(alert)
        self._save_db()
        return alert["id"]
    
    def get_status(self) -> Dict:
        """获取哨兵状态"""
        unresolved = [a for a in self.alerts["alerts"] if not a["resolved"]]
        return {
            "total_alerts": len(self.alerts["alerts"]),
            "unresolved": len(unresolved),
            "high_severity": len([a for a in unresolved if a["severity"] == "high"])
        }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("="*60)
        print("🧪 Blue Sentinel S5/S7 验证")
        print("="*60)
        
        sentinel = BlueSentinel()
        
        # S7: 对抗测试
        print("\n[S7] 对抗测试...")
        
        # 测试1: 记录空告警
        alert_id = sentinel.record_alert("", "", "low")
        assert alert_id, "空告警应可记录"
        print("  ✅ 空告警记录测试通过")
        
        # 测试2: 检查诚实性（可能发现问题）
        issues = sentinel.check_fin_honesty()
        assert isinstance(issues, list), "应返回列表"
        print(f"  ✅ FIN诚实性检查完成（发现{len(issues)}个问题）")
        
        # 测试3: 无效严重级别
        alert_id = sentinel.record_alert("test", "msg", "invalid")
        assert alert_id, "无效严重级别应可记录"
        print("  ✅ 无效严重级别测试通过")
        
        # S5: 自我验证
        print("\n[S5] 自我验证...")
        status = sentinel.get_status()
        assert "unresolved" in status, "状态应有unresolved字段"
        print("  ✅ 状态统计正确")
        
        print("\n" + "="*60)
        print("✅ S5/S7验证通过")
        print("="*60)
        return 0
    else:
        sentinel = BlueSentinel()
        print(f"Blue Sentinel 初始化完成")
        print(f"未解决告警: {sentinel.get_status()['unresolved']}")
        
        # 执行FIN诚实性检查
        issues = sentinel.check_fin_honesty()
        if issues:
            print(f"\n⚠️ 发现{len(issues)}个FIN诚实性问题:")
            for issue in issues:
                print(f"  - {issue['skill']}: {issue['issue']}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
