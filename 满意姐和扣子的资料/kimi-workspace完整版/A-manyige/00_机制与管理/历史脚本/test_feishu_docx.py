#!/usr/bin/env python3
"""
飞书云文档创建测试 - 使用正确API
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

def create_docx(title="测试文档"):
    """创建飞书云文档 - 使用docx API"""
    token = get_token()
    
    # 创建docx文档的正确API
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": title
    }
    
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"\n状态码: {response.status_code}")
    print(f"响应:\n{response.text}")
    
    try:
        return response.json()
    except:
        return {"error": "解析失败", "text": response.text[:300]}

def list_docs():
    """列出用户文档"""
    token = get_token()
    
    url = "https://open.feishu.cn/open-apis/drive/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, timeout=30)
    print(f"\n列出文档 - 状态码: {response.status_code}")
    try:
        return response.json()
    except:
        return {"error": "解析失败"}

if __name__ == "__main__":
    print("="*60)
    print("飞书云文档API测试")
    print("="*60)
    
    print("\n[测试1] 创建云文档...")
    result1 = create_docx("满意解研究所-测试文档")
    
    print("\n[测试2] 列出文档...")
    result2 = list_docs()
    print(json.dumps(result2, indent=2, ensure_ascii=False)[:500])
