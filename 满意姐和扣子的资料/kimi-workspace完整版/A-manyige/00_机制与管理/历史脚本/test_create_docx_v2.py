#!/usr/bin/env python3
"""
飞书云文档创建测试 - 使用正确端点
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

def create_docx(title="测试文档"):
    """使用正确端点创建飞书云文档"""
    token = get_token()
    
    # 正确的端点
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 正确的请求体
    data = {
        "title": title,
        "folder_token": ""  # 可选，指定文件夹
    }
    
    print(f"创建文档: {title}")
    print(f"URL: {url}")
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"状态码: {response.status_code}")
    
    try:
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('code') == 0:
            doc_id = result['data']['document']['document_id']
            title = result['data']['document']['title']
            url = result['data']['document']['url']
            print(f"\n✅ 创建成功!")
            print(f"文档ID: {doc_id}")
            print(f"标题: {title}")
            print(f"URL: {url}")
            return True
        else:
            print(f"\n❌ 创建失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"\n❌ 异常: {e}")
        print(f"响应内容: {response.text[:500]}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("飞书云文档创建测试")
    print("="*60)
    success = create_docx("满意解研究所-测试文档")
    print("="*60)
    exit(0 if success else 1)
