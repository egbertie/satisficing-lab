#!/usr/bin/env python3
"""
飞书云文档创建测试
"""

import json
import requests

def get_token():
    """获取Access Token"""
    with open('/root/.openclaw/workspace/config/feishu_config.json', 'r') as f:
        config = json.load(f)
    
    response = requests.post(
        f"{config['base_url']}/auth/v3/tenant_access_token/internal",
        json={"app_id": config['app_id'], "app_secret": config['app_secret']},
        timeout=30
    )
    return response.json()['tenant_access_token']

def create_doc(title="测试文档"):
    """创建飞书云文档"""
    token = get_token()
    
    url = "https://open.feishu.cn/open-apis/drive/v1/files/create"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "type": "docx",
        "title": title
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应内容:\n{response.text[:500]}")
    
    try:
        return response.json()
    except:
        return {"error": "无法解析JSON", "text": response.text[:200]}

if __name__ == "__main__":
    print("创建飞书云文档测试...\n")
    result = create_doc("满意解研究所-测试文档")
    print(f"\n结果:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
