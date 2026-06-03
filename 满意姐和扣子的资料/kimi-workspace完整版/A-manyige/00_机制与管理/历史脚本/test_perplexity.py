#!/usr/bin/env python3
"""
Perplexity API 测试脚本
功能：测试Perplexity AI搜索功能
"""

import json
import os
import sys
from datetime import datetime
import requests

# 配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "perplexity_config.json")
RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "test_results.json")


def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 配置文件加载成功: {CONFIG_PATH}")
        return config
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return None


def test_api_connection(config):
    """测试API连接"""
    print("\n" + "="*50)
    print("🔍 测试1: API连接测试")
    print("="*50)
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    test_payload = {
        "model": config.get("model", "sonar"),
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": "Say 'Hello, Perplexity API is working!'"}
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            config["endpoint"],
            headers=headers,
            json=test_payload,
            timeout=config.get("timeout", 30)
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"✅ API连接成功!")
            print(f"   响应: {content[:100]}...")
            return True, "连接成功"
        else:
            print(f"❌ API连接失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        print(f"❌ API连接异常: {e}")
        return False, str(e)


def test_ai_search(config, query):
    """测试AI搜索功能"""
    print("\n" + "="*50)
    print(f"🔍 测试2: AI搜索功能测试")
    print(f"   搜索关键词: {query}")
    print("="*50)
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    search_payload = {
        "model": config.get("model", "sonar-pro"),
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful assistant with access to real-time information. Provide comprehensive answers with citations when available."
            },
            {
                "role": "user", 
                "content": query
            }
        ],
        "max_tokens": config.get("max_tokens", 2048),
        "temperature": config.get("temperature", 0.7),
        "return_citations": config.get("return_citations", True),
        "return_images": config.get("return_images", False),
        "return_related_questions": config.get("return_related_questions", True),
        "search_recency_filter": config.get("search_recency_filter", "month")
    }
    
    try:
        response = requests.post(
            config["endpoint"],
            headers=headers,
            json=search_payload,
            timeout=config.get("timeout", 60)
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # 提取回答内容
            choices = result.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                citations = result.get("citations", [])
                related_questions = result.get("related_questions", [])
                usage = result.get("usage", {})
                
                print(f"✅ 搜索成功!")
                print(f"\n📄 搜索结果:")
                print("-" * 50)
                print(content)
                print("-" * 50)
                
                if citations:
                    print(f"\n📚 引用来源 ({len(citations)}个):")
                    for i, citation in enumerate(citations[:5], 1):
                        print(f"   [{i}] {citation}")
                
                if related_questions:
                    print(f"\n💡 相关问题:")
                    for i, q in enumerate(related_questions[:3], 1):
                        print(f"   {i}. {q}")
                
                print(f"\n📊 Token使用情况:")
                print(f"   输入: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   输出: {usage.get('completion_tokens', 'N/A')}")
                print(f"   总计: {usage.get('total_tokens', 'N/A')}")
                
                return True, {
                    "query": query,
                    "content": content,
                    "citations": citations,
                    "related_questions": related_questions,
                    "usage": usage
                }
            else:
                return False, "无有效响应内容"
        else:
            print(f"❌ 搜索失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:500]}")
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        print(f"❌ 搜索异常: {e}")
        return False, str(e)


def save_results(results):
    """保存测试结果"""
    try:
        with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 测试结果已保存: {RESULTS_PATH}")
    except Exception as e:
        print(f"\n❌ 测试结果保存失败: {e}")


def main():
    print("="*50)
    print("🚀 Perplexity API 测试启动")
    print("="*50)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载配置
    config = load_config()
    if not config:
        sys.exit(1)
    
    # 初始化结果
    results = {
        "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "config_loaded": True,
        "api_key": config['api_key'][:10] + "..." + config['api_key'][-4:],
        "endpoint": config['endpoint'],
        "model": config.get('model', 'sonar'),
        "tests": []
    }
    
    # 测试1: API连接
    conn_success, conn_msg = test_api_connection(config)
    results["tests"].append({
        "name": "API连接测试",
        "success": conn_success,
        "message": conn_msg
    })
    
    if not conn_success:
        print("\n❌ API连接失败，停止测试")
        save_results(results)
        sys.exit(1)
    
    # 测试2: AI搜索
    search_query = "满意解理论西蒙"
    search_success, search_data = test_ai_search(config, search_query)
    results["tests"].append({
        "name": "AI搜索测试",
        "query": search_query,
        "success": search_success,
        "data": search_data if isinstance(search_data, dict) else {"error": search_data}
    })
    
    # 总结
    print("\n" + "="*50)
    print("📋 测试总结")
    print("="*50)
    
    passed = sum(1 for t in results["tests"] if t["success"])
    total = len(results["tests"])
    
    print(f"   通过: {passed}/{total}")
    print(f"   失败: {total - passed}/{total}")
    
    results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "status": "成功" if passed == total else "部分失败"
    }
    
    if passed == total:
        print("\n✅ 所有测试通过！Perplexity API 配置正确")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
    
    # 保存结果
    save_results(results)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
