#!/usr/bin/env python3
"""
tavily_search.py - Tavily搜索API封装

功能:
- 基础搜索和深度搜索
- 结果格式化
- 错误处理
"""

import os
import sys
import time
from typing import Dict, List, Optional

# 尝试导入requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  requests模块未安装，使用模拟模式")


class TavilySearchError(Exception):
    """Tavily搜索错误"""
    pass


class TavilyAPIError(TavilySearchError):
    """API错误"""
    pass


class TavilyTimeoutError(TavilySearchError):
    """超时错误"""
    pass


def search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    include_answer: bool = True,
    timeout: int = 10
) -> Dict:
    """
    执行Tavily搜索
    
    Args:
        query: 搜索查询词
        max_results: 最大结果数 (1-20)
        search_depth: 搜索深度 (basic/advanced)
        include_answer: 是否包含AI答案
        timeout: 超时时间(秒)
    
    Returns:
        {
            "query": 查询词,
            "answer": AI答案(如适用),
            "results": [{"title": ..., "url": ..., "content": ..., "score": ...}],
            "sources": [来源列表]
        }
    
    Raises:
        TavilySearchError: 搜索错误
        ValueError: 参数错误
    """
    # 参数验证
    if not query or not query.strip():
        raise ValueError("查询词不能为空")
    
    if max_results < 1 or max_results > 20:
        raise ValueError("max_results必须在1-20之间")
    
    if search_depth not in ["basic", "advanced"]:
        raise ValueError("search_depth必须是basic或advanced")
    
    # 如果没有requests，使用模拟数据
    if not HAS_REQUESTS:
        return _mock_search(query, max_results, search_depth)
    
    # 获取API Key
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        # 尝试从配置文件读取
        config_path = os.path.expanduser("~/.openclaw/config/tavily.json")
        if os.path.exists(config_path):
            import json
            with open(config_path) as f:
                config = json.load(f)
                api_key = config.get("api_key", "")
    
    # 如果没有API Key，使用模拟数据
    if not api_key:
        print("⚠️  未配置TAVILY_API_KEY，使用模拟数据")
        return _mock_search(query, max_results, search_depth)
    
    # 调用API
    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": include_answer
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        
        # 处理HTTP错误
        if response.status_code == 429:
            raise TavilyAPIError("API限流，请稍后重试")
        elif response.status_code == 401:
            raise TavilyAPIError("API Key无效")
        elif response.status_code >= 500:
            raise TavilyAPIError(f"服务器错误: {response.status_code}")
        elif response.status_code != 200:
            raise TavilyAPIError(f"请求失败: {response.status_code}")
        
        data = response.json()
        
        # 格式化结果
        results = {
            "query": query,
            "answer": data.get("answer", ""),
            "results": [],
            "sources": []
        }
        
        for item in data.get("results", []):
            result = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0.0)
            }
            results["results"].append(result)
            results["sources"].append(item.get("source", ""))
        
        return results
        
    except requests.exceptions.Timeout:
        raise TavilyTimeoutError(f"请求超时({timeout}秒)")
    except requests.exceptions.ConnectionError:
        raise TavilyAPIError("网络连接错误，请检查网络")
    except requests.exceptions.RequestException as e:
        raise TavilyAPIError(f"请求异常: {e}")


def _mock_search(query: str, max_results: int, search_depth: str) -> Dict:
    """模拟搜索（用于测试或无API Key时）"""
    mock_results = []
    
    # 根据查询生成模拟结果
    for i in range(min(max_results, 3)):
        mock_results.append({
            "title": f"关于{query}的结果{i+1}",
            "url": f"http://example.com/result{i+1}",
            "content": f"这是关于{query}的第{i+1}条模拟搜索结果内容...",
            "score": 0.9 - (i * 0.1)
        })
    
    return {
        "query": query,
        "answer": f"关于{query}的AI总结答案（模拟数据）" if search_depth == "advanced" else "",
        "results": mock_results,
        "sources": ["example.com"] * len(mock_results)
    }


def format_results(results: Dict, format_type: str = "markdown") -> str:
    """
    格式化搜索结果
    
    Args:
        results: 搜索结果字典
        format_type: 输出格式 (markdown/text/json)
    
    Returns:
        格式化后的字符串
    """
    if format_type == "json":
        import json
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    elif format_type == "text":
        lines = [
            f"查询: {results['query']}",
            f"找到 {len(results['results'])} 个结果",
            ""
        ]
        for i, r in enumerate(results['results'], 1):
            lines.append(f"{i}. {r['title']}")
            lines.append(f"   URL: {r['url']}")
            lines.append(f"   摘要: {r['content'][:100]}...")
            lines.append("")
        return "\n".join(lines)
    
    else:  # markdown
        lines = [
            f"## 🔍 {results['query']} 搜索结果",
            "",
            f"找到 **{len(results['results'])}** 个相关结果",
            ""
        ]
        
        if results.get("answer"):
            lines.extend([
                "### 🤖 AI总结",
                results["answer"],
                ""
            ])
        
        lines.append("### 📄 搜索结果")
        lines.append("")
        
        for i, r in enumerate(results['results'], 1):
            lines.append(f"**{i}. [{r['title']}]({r['url']})**")
            lines.append(f"> {r['content'][:150]}...")
            lines.append(f"*相关度: {r['score']:.0%}*")
            lines.append("")
        
        return "\n".join(lines)


def run_tests():
    """运行基本测试"""
    print("🧪 Tavily Search - 基本测试\n")
    
    tests = [
        ("基础搜索", lambda: search("人工智能", max_results=2)),
        ("深度搜索", lambda: search("机器学习", search_depth="advanced")),
        ("格式化输出", lambda: format_results(search("测试", max_results=1))),
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            result = test_func()
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    
    print(f"\n📊 测试完成: {passed}/{len(tests)} 通过")
    return passed == len(tests)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tavily搜索")
    parser.add_argument("query", nargs="?", help="搜索查询词")
    parser.add_argument("--max-results", type=int, default=5, help="最大结果数")
    parser.add_argument("--depth", default="basic", help="搜索深度")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    if args.query:
        results = search(args.query, max_results=args.max_results, search_depth=args.depth)
        print(format_results(results))
    else:
        parser.print_help()
