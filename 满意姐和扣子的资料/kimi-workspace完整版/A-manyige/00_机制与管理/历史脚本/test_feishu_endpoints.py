#!/usr/bin/env python3
"""
飞书API测试 - 尝试不同端点
"""

import json
import requests

def get_token():
    with open('/root/.openclaw/workspace/config/feishu_config.json', 'r') as f:
        config = json.load(f)
    
    response = requests.post(
        f"{config['base_url']}/auth/v3/tenant_access_token/internal",
        json={"app_id": config['app_id'], "app_secret": config['app_secret']},
        timeout=30
    )
    return response.json()['tenant_access_token']

def test_endpoints():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试不同的API端点
    endpoints = [
        ("获取用户列表", "GET", "https://open.feishu.cn/open-apis/contact/v3/users"),
        ("获取我的信息", "GET", "https://open.feishu.cn/open-apis/authen/v1/user_info"),
        ("创建文档-v1", "POST", "https://open.feishu.cn/open-apis/docx/v1/documents"),
        ("创建文件-v1", "POST", "https://open.feishu.cn/open-apis/drive/v1/files/create"),
    ]
    
    print("="*60)
    print("测试飞书API端点")
    print("="*60)
    
    for name, method, url in endpoints:
        print(f"\n测试: {name}")
        print(f"URL: {url}")
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, json={}, timeout=10)
            
            print(f"状态: {response.status_code}")
            if response.status_code in [200, 201]:
                print("✅ 成功")
            elif response.status_code == 400:
                print("⚠️ 参数错误（端点存在，需要正确参数）")
            elif response.status_code == 403:
                print("❌ 权限不足")
            else:
                print(f"⚠️ 其他: {response.text[:100]}")
        except Exception as e:
            print(f"❌ 异常: {e}")

if __name__ == "__main__":
    test_endpoints()
