#!/usr/bin/env python3
"""
安全审计脚本 - 企业级安全基线检查
7x24可执行，纯本地操作（零Token）
"""

import os
import sys
import json
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

class SecurityAuditor:
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.vault = Path.home() / ".openclaw" / "security" / "vault"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "score": 100,
            "critical": [],
            "warnings": []
        }
    
    def check_file_permissions(self):
        """检查敏感文件权限"""
        sensitive_files = [
            self.workspace / ".env",
            self.workspace / ".env.github",
            Path.home() / ".openclaw" / ".env"
        ]
        
        for file in sensitive_files:
            if file.exists():
                stat = file.stat()
                mode = oct(stat.st_mode)[-3:]
                if mode != "600":
                    self.results["warnings"].append(f"{file} 权限为 {mode}，建议改为 600")
                    self.results["score"] -= 5
                else:
                    self.results["checks"].append(f"✓ {file} 权限正确 (600)")
    
    def check_git_hooks(self):
        """检查Git Hooks是否部署"""
        hook_file = self.workspace / ".git" / "hooks" / "pre-commit"
        if hook_file.exists():
            content = hook_file.read_text()
            if "安全扫描" in content:
                self.results["checks"].append("✓ Git pre-commit hook 已部署")
            else:
                self.results["warnings"].append("Git hook 存在但未配置安全扫描")
        else:
            self.results["critical"].append("✗ Git pre-commit hook 未部署")
            self.results["score"] -= 20
    
    def check_gitignore(self):
        """检查.gitignore是否包含敏感模式"""
        gitignore = self.workspace / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            required_patterns = [".env*", "*.key", ".vault-keys/"]
            missing = [p for p in required_patterns if p not in content]
            if missing:
                self.results["warnings"].append(f".gitignore 缺少: {', '.join(missing)}")
            else:
                self.results["checks"].append("✓ .gitignore 配置完整")
        else:
            self.results["critical"].append("✗ .gitignore 不存在")
            self.results["score"] -= 15
    
    def check_secrets_in_git_history(self):
        """扫描Git历史中的密钥"""
        try:
            result = subprocess.run(
                ["git", "log", "--all", "--full-history", "-p", "--"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 简单扫描敏感模式
            patterns = ["sk-", "ghp_", "github_pat_", "AKIA"]
            found = []
            for pattern in patterns:
                if pattern in result.stdout:
                    found.append(pattern)
            
            if found:
                self.results["critical"].append(f"⚠️  Git历史可能包含敏感信息: {', '.join(found)}")
                self.results["score"] -= 30
            else:
                self.results["checks"].append("✓ Git历史未发现明显敏感信息")
        except Exception as e:
            self.results["warnings"].append(f"Git历史扫描失败: {e}")
    
    def check_encrypted_files(self):
        """检查加密文件状态"""
        encrypted_files = list(self.vault.glob("*.gpg")) if self.vault.exists() else []
        if encrypted_files:
            self.results["checks"].append(f"✓ 发现 {len(encrypted_files)} 个加密文件")
        else:
            self.results["warnings"].append("未使用GPG加密存储")
    
    def generate_report(self):
        """生成审计报告"""
        print("=" * 60)
        print("🔐 安全审计报告")
        print("=" * 60)
        print(f"时间: {self.results['timestamp']}")
        print(f"安全评分: {self.results['score']}/100")
        print("")
        
        if self.results["critical"]:
            print("🚨 严重问题:")
            for item in self.results["critical"]:
                print(f"   {item}")
            print("")
        
        if self.results["warnings"]:
            print("⚠️  警告:")
            for item in self.results["warnings"]:
                print(f"   {item}")
            print("")
        
        if self.results["checks"]:
            print("✓ 通过项:")
            for item in self.results["checks"]:
                print(f"   {item}")
            print("")
        
        # 保存报告
        report_file = self.vault / "audit-reports" / f"audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 报告已保存: {report_file}")
        print("=" * 60)
        
        return self.results["score"]
    
    def run_all(self):
        """执行全部检查"""
        self.check_file_permissions()
        self.check_git_hooks()
        self.check_gitignore()
        self.check_secrets_in_git_history()
        self.check_encrypted_files()
        return self.generate_report()

if __name__ == "__main__":
    auditor = SecurityAuditor()
    score = auditor.run_all()
    sys.exit(0 if score >= 80 else 1)
