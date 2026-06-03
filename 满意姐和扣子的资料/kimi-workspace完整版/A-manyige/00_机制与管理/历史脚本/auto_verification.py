#!/usr/bin/env python3
"""
自动化验证脚本 - Automated Verification Script
自动验证声称vs实际，防止虚报
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

class AutomatedVerifier:
    """自动化验证器"""
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.report_file = self.workspace / "diary" / "auto_verification_reports" / f"verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        self.results = []
    
    def verify_file_exists(self, file_path, claim_name):
        """验证文件是否存在"""
        full_path = self.workspace / file_path
        exists = full_path.exists()
        size = full_path.stat().st_size if exists else 0
        
        result = {
            "type": "file_exists",
            "claim": claim_name,
            "path": str(file_path),
            "exists": exists,
            "size": size,
            "status": "✅ PASS" if exists else "❌ FAIL"
        }
        self.results.append(result)
        return exists
    
    def verify_cron_deployed(self, script_name, claim_name):
        """验证Cron是否部署"""
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            deployed = script_name in result.stdout
            
            result = {
                "type": "cron_deployed",
                "claim": claim_name,
                "script": script_name,
                "deployed": deployed,
                "status": "✅ PASS" if deployed else "❌ FAIL"
            }
            self.results.append(result)
            return deployed
        except Exception as e:
            self.results.append({
                "type": "cron_deployed",
                "claim": claim_name,
                "script": script_name,
                "error": str(e),
                "status": "❌ ERROR"
            })
            return False
    
    def verify_code_executable(self, file_path, claim_name):
        """验证代码是否可执行"""
        full_path = self.workspace / file_path
        
        # 检查文件存在
        if not full_path.exists():
            self.results.append({
                "type": "code_executable",
                "claim": claim_name,
                "path": str(file_path),
                "status": "❌ FAIL - 文件不存在"
            })
            return False
        
        # 检查是否有执行权限或是Python脚本
        is_executable = os.access(full_path, os.X_OK)
        is_python = str(file_path).endswith('.py')
        
        can_execute = is_executable or is_python
        
        self.results.append({
            "type": "code_executable",
            "claim": claim_name,
            "path": str(file_path),
            "is_executable": is_executable,
            "is_python": is_python,
            "status": "✅ PASS" if can_execute else "❌ FAIL - 无执行权限"
        })
        return can_execute
    
    def verify_skill_exists(self, skill_name, claim_name):
        """验证Skill是否存在"""
        skill_path = self.workspace / "skills" / skill_name
        exists = skill_path.exists()
        has_skill_md = (skill_path / "SKILL.md").exists() if exists else False
        
        self.results.append({
            "type": "skill_exists",
            "claim": claim_name,
            "skill": skill_name,
            "exists": exists,
            "has_skill_md": has_skill_md,
            "status": "✅ PASS" if (exists and has_skill_md) else "❌ FAIL"
        })
        return exists and has_skill_md
    
    def run_all_verifications(self):
        """运行所有验证"""
        print("="*60)
        print("🔍 自动化验证开始")
        print("="*60)
        
        # 验证V3.0文件
        print("\n📁 验证V3.0文件...")
        self.verify_file_exists("skills/universal-task-executor-v3/core/engine.py", "Core Engine")
        self.verify_file_exists("skills/universal-task-executor-v3/handlers/category6_mechanism_handler.py", "C6 Handler")
        
        # 验证Cron部署
        print("\n⏰ 验证Cron部署...")
        self.verify_cron_deployed("punishment_enforcer.sh", "惩罚执行器Cron")
        self.verify_cron_deployed("checkpoint-health-check.py", "检查点健康验证Cron")
        self.verify_cron_deployed("backup_to_external.py", "外部备份Cron")
        self.verify_cron_deployed("token_monitor.py", "Token监控Cron")
        
        # 验证代码可执行
        print("\n🐍 验证代码可执行...")
        self.verify_code_executable("scripts/false_claim_circuit_breaker.py", "虚报熔断机制")
        
        # 验证Skill
        print("\n📚 验证Skill...")
        self.verify_skill_exists("universal-task-executor-v3", "V3.0 Skill")
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成验证报告"""
        passed = sum(1 for r in self.results if r["status"].startswith("✅"))
        failed = sum(1 for r in self.results if r["status"].startswith("❌"))
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.results),
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed/len(self.results)*100:.1f}%" if self.results else "0%"
            },
            "details": self.results
        }
        
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*60)
        print("📊 验证报告")
        print("="*60)
        print(f"总计: {len(self.results)} 项")
        print(f"通过: {passed} 项 ✅")
        print(f"失败: {failed} 项 ❌")
        print(f"通过率: {report['summary']['pass_rate']}")
        print(f"\n报告保存: {self.report_file}")
        
        # 打印失败项
        if failed > 0:
            print("\n❌ 失败项:")
            for r in self.results:
                if r["status"].startswith("❌"):
                    print(f"  - {r['claim']}: {r['status']}")

if __name__ == "__main__":
    verifier = AutomatedVerifier()
    verifier.run_all_verifications()
