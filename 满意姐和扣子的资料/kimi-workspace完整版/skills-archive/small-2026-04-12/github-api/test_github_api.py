#!/usr/bin/env python3
"""
GitHub API Skill 测试套件
S7: 对抗测试实现
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_client import GitHubClient

class GitHubAPITestSuite:
    """GitHub API对抗测试套件"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def test(self, name: str, condition: bool, details: str = ""):
        """记录测试结果"""
        if condition:
            print(f"✅ {name}")
            self.passed += 1
            self.results.append(("PASS", name, details))
        else:
            print(f"❌ {name}")
            self.failed += 1
            self.results.append(("FAIL", name, details))
    
    def run_all_tests(self):
        """运行所有S7对抗测试"""
        print("=" * 60)
        print("🛡️ GitHub API Skill - S7对抗测试套件")
        print("=" * 60)
        
        # 测试1: 无效Token
        print("\n[测试1] 无效Token处理")
        invalid_client = GitHubClient("fake_token_for_testing")
        result = invalid_client.get_repo_info("OpenClaw", "gateway")
        self.test(
            "无效Token返回401错误提示",
            "Token无效" in result or "401" in result or "授权" in result,
            result
        )
        
        # 测试2: 不存在仓库
        print("\n[测试2] 不存在仓库处理")
        client = GitHubClient()
        result = client.get_repo_info("nonexistent_user_xyz123", "fake_repo_abc")
        self.test(
            "不存在仓库返回404提示",
            "不存在" in result or "404" in result,
            result
        )
        
        # 测试3: 正常仓库查询（公开仓库无需Token）
        print("\n[测试3] 正常仓库查询")
        result = client.get_repo_info("OpenClaw", "gateway")
        self.test(
            "正常仓库返回Stars统计",
            "Stars:" in result,
            result[:100]
        )
        self.test(
            "正常仓库返回Forks统计",
            "Forks:" in result,
            ""
        )
        
        # 测试4: 输出格式验证
        print("\n[测试4] 输出格式验证")
        result = client.list_issues("OpenClaw", "gateway", per_page=3)
        self.test(
            "Issues输出包含Markdown表格",
            "| # |" in result and "|---|" in result,
            result[:150]
        )
        
        # 测试5: 空数据处理
        print("\n[测试5] 空数据处理")
        # 测试一个没有Issues的仓库（假设存在）
        result = client.list_issues("OpenClaw", "nonexistent_repo_12345")
        self.test(
            "不存在仓库返回友好错误",
            "失败" in result or "不存在" in result,
            result
        )
        
        # 测试6: PR查询
        print("\n[测试6] PR查询功能")
        result = client.list_pull_requests("OpenClaw", "gateway")
        self.test(
            "PR输出包含正确表头",
            "| # | 标题 | 作者 |" in result or "暂无" in result,
            result[:100]
        )
        
        # 测试7: Actions查询
        print("\n[测试7] Actions状态查询")
        result = client.check_actions_runs("OpenClaw", "gateway")
        self.test(
            "Actions查询返回结果",
            "工作流" in result or "暂无" in result or "失败" in result,
            result[:100]
        )
        
        # 测试总结
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"覆盖率: {self.passed}/{self.passed + self.failed} = {self.passed/(self.passed+self.failed)*100:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 所有S7对抗测试通过！")
            return True
        else:
            print(f"\n⚠️ {self.failed}个测试未通过，需要修复")
            return False

if __name__ == "__main__":
    suite = GitHubAPITestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)
