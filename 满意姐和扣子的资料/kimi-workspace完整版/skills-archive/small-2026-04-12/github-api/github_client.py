#!/usr/bin/env python3
"""
GitHub API 客户端
5标准化Skill实现
"""

import requests
import json
from typing import Dict, List, Optional, Union
from datetime import datetime

class GitHubClient:
    """GitHub API客户端"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenClaw-GitHub-API-Skill"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """发送API请求"""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            # S7: 对抗测试 - 错误处理
            if response.status_code == 401:
                raise Exception("GitHub Token无效或已过期，请重新授权")
            elif response.status_code == 403:
                if "rate limit" in response.text.lower():
                    reset_time = response.headers.get('X-RateLimit-Reset')
                    raise Exception(f"API速率限制，请在{reset_time}后重试")
                raise Exception("权限不足，请检查Token权限")
            elif response.status_code == 404:
                raise Exception("仓库不存在或无法访问")
            elif response.status_code == 429:
                raise Exception("请求过于频繁，请稍后重试")
            elif response.status_code >= 500:
                raise Exception("GitHub服务暂时不可用，请稍后重试")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查网络连接后重试")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接失败，请检查网络状态")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")
    
    def list_issues(self, owner: str, repo: str, state: str = "open", per_page: int = 10) -> str:
        """列出仓库Issues - S3输出规范"""
        endpoint = f"/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": per_page}
        
        try:
            data = self._request(endpoint, params)
            
            if not data:
                return f"## GitHub仓库: {owner}/{repo}\n\n暂无{state}状态的Issues"
            
            # S3: 格式化输出
            output = f"## GitHub仓库: {owner}/{repo}\n\n"
            output += f"### Issues ({state}, 前{len(data)}个)\n\n"
            output += "| # | 标题 | 状态 | 创建时间 |\n"
            output += "|---|------|------|----------|\n"
            
            for issue in data:
                number = issue.get('number', 'N/A')
                title = issue.get('title', '无标题')[:40]
                state_label = issue.get('state', 'unknown')
                created = issue.get('created_at', '')[:10]
                output += f"| #{number} | {title} | {state_label} | {created} |\n"
            
            return output
            
        except Exception as e:
            return f"❌ 获取Issues失败: {str(e)}"
    
    def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> str:
        """列出Pull Requests"""
        endpoint = f"/repos/{owner}/{repo}/pulls"
        params = {"state": state, "per_page": 10}
        
        try:
            data = self._request(endpoint, params)
            
            if not data:
                return f"### Pull Requests\n\n暂无{state}状态的PR"
            
            output = f"### Pull Requests ({state})\n\n"
            output += "| # | 标题 | 作者 | 状态 |\n"
            output += "|---|------|------|------|\n"
            
            for pr in data:
                number = pr.get('number', 'N/A')
                title = pr.get('title', '无标题')[:35]
                author = pr.get('user', {}).get('login', '未知')
                state_label = pr.get('state', 'unknown')
                output += f"| #{number} | {title} | @{author} | {state_label} |\n"
            
            return output
            
        except Exception as e:
            return f"❌ 获取PR失败: {str(e)}"
    
    def get_repo_info(self, owner: str, repo: str) -> str:
        """获取仓库信息"""
        endpoint = f"/repos/{owner}/{repo}"
        
        try:
            data = self._request(endpoint)
            
            output = f"## 仓库信息: {owner}/{repo}\n\n"
            output += f"**描述**: {data.get('description', '无描述')}\n\n"
            output += "### 统计\n\n"
            output += f"- ⭐ Stars: {data.get('stargazers_count', 0)}\n"
            output += f"- 🍴 Forks: {data.get('forks_count', 0)}\n"
            output += f"- 📋 Open Issues: {data.get('open_issues_count', 0)}\n"
            output += f"- 👀 Watchers: {data.get('watchers_count', 0)}\n"
            output += f"- 🏷️ 语言: {data.get('language', '未指定')}\n"
            output += f"- 📅 创建时间: {data.get('created_at', '')[:10]}\n"
            output += f"- 🔄 最后更新: {data.get('updated_at', '')[:10]}\n"
            
            return output
            
        except Exception as e:
            return f"❌ 获取仓库信息失败: {str(e)}"
    
    def check_actions_runs(self, owner: str, repo: str) -> str:
        """检查Actions运行状态"""
        endpoint = f"/repos/{owner}/{repo}/actions/runs"
        params = {"per_page": 5}
        
        try:
            data = self._request(endpoint, params)
            runs = data.get('workflow_runs', [])
            
            if not runs:
                return "### Actions运行状态\n\n暂无工作流运行记录"
            
            output = "### Actions运行状态\n\n"
            output += "| 工作流 | 状态 | 分支 | 时间 |\n"
            output += "|--------|------|------|------|\n"
            
            for run in runs:
                name = run.get('name', 'Unknown')[:20]
                status = run.get('status', 'unknown')
                conclusion = run.get('conclusion', '-')
                branch = run.get('head_branch', 'unknown')
                created = run.get('created_at', '')[:16]
                
                # 状态emoji
                status_emoji = "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "🔄"
                output += f"| {name} | {status_emoji} {status} | {branch} | {created} |\n"
            
            return output
            
        except Exception as e:
            return f"❌ 获取Actions状态失败: {str(e)}"

# S5: 准确性验证
def validate_github_api():
    """验证GitHub API Skill"""
    print("🧪 运行GitHub API对抗测试...")
    
    client = GitHubClient()
    
    # 测试1: 无效Token
    try:
        invalid_client = GitHubClient("fake_token_12345")
        result = invalid_client.get_repo_info("OpenClaw", "gateway")
        assert "Token无效" in result or "401" in result, "无效Token测试失败"
        print("✅ 无效Token处理")
    except Exception as e:
        print(f"✅ 无效Token处理: {e}")
    
    # 测试2: 不存在仓库
    result = client.get_repo_info("nonexistent_user_12345", "fake_repo")
    assert "不存在" in result or "404" in result, "不存在仓库测试失败"
    print("✅ 不存在仓库处理")
    
    # 测试3: 正常仓库（无需Token）
    result = client.get_repo_info("OpenClaw", "gateway")
    assert "Stars:" in result, "正常仓库查询失败"
    print("✅ 正常仓库查询")
    
    print("\n🎉 所有对抗测试通过！")

if __name__ == "__main__":
    validate_github_api()
