#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Models API 测试脚本
用于验证GPT-4o API配置是否正确

使用方法:
1. 设置环境变量: export GITHUB_TOKEN="your_github_token"
2. 运行脚本: python3 test_github_models.py
"""

import os
import sys
import requests

# API配置
API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL = "gpt-4o"

def test_github_models():
    """测试GitHub Models API连接"""
    
    # 从环境变量获取Token
    api_key = os.environ.get('GITHUB_TOKEN')
    
    if not api_key:
        print("❌ 错误: 未设置GITHUB_TOKEN环境变量")
        print("请设置环境变量: export GITHUB_TOKEN='your_github_token'")
        print("\n获取Token步骤:")
        print("1. 访问 https://github.com/settings/tokens")
        print("2. 创建Fine-grained token")
        print("3. 设置环境变量后重新运行脚本")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试消息
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是一个简洁的助手，用一句话回答问题。"},
            {"role": "user", "content": "你好！请用一句话介绍自己。"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    print("=" * 50)
    print("🧪 GitHub Models API 测试")
    print("=" * 50)
    print(f"模型: {MODEL}")
    print(f"API URL: {API_URL}")
    print("-" * 50)
    
    try:
        print("📡 发送请求...")
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            
            print("✅ 连接成功!")
            print("-" * 50)
            print("🤖 AI回复:")
            print(f"  {reply}")
            print("-" * 50)
            
            # 显示使用量
            if 'usage' in result:
                usage = result['usage']
                print("📊 Token使用量:")
                print(f"  输入: {usage.get('prompt_tokens', 'N/A')}")
                print(f"  输出: {usage.get('completion_tokens', 'N/A')}")
                print(f"  总计: {usage.get('total_tokens', 'N/A')}")
            
            return True
            
        elif response.status_code == 401:
            print("❌ 认证失败: Token无效或已过期")
            print("请检查GITHUB_TOKEN是否正确设置")
            return False
            
        elif response.status_code == 403:
            print("❌ 权限不足: 可能需要申请GitHub Models访问权限")
            print("请访问 https://github.com/marketplace/models 申请访问")
            return False
            
        elif response.status_code == 429:
            print("❌ 请求过于频繁: 已达到速率限制")
            print("GitHub Models限制: GPT-4o ≤50次/天, ≤10次/分钟")
            return False
            
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 请检查网络连接")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    success = test_github_models()
    sys.exit(0 if success else 1)
