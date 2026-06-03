#!/usr/bin/env python3
"""
查询飞书文档列表
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

def list_docs():
    """获取文档列表"""
    token = get_token()
    
    # 尝试不同的API获取文档列表
    urls = [
        "https://open.feishu.cn/open-apis/drive/v1/files",
        "https://open.feishu.cn/open-apis/docx/v1/documents",
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("="*60)
    print("查询飞书文档列表")
    print("="*60)
    
    for url in urls:
        print(f"\n尝试: {url}")
        try:
            response = requests.get(url, headers=headers, params={"page_size": 10}, timeout=30)
            print(f"状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    print(f"✅ 成功")
                    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                else:
                    print(f"⚠️ 业务错误: {data.get('msg')}")
            else:
                print(f"⚠️ HTTP错误: {response.text[:200]}")
        except Exception as e:
            print(f"❌ 异常: {e}")

def get_doc_detail(doc_id="GDtmdVaxroOf7jxR80ycb3Kcnhb"):
    """获取指定文档详情"""
    token = get_token()
    
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n{'='*60}")
    print(f"查询文档详情: {doc_id}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态: {response.status_code}")
        
        try:
            data = response.json()
            print(f"响应:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"响应内容: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    # 查询文档列表
    list_docs()
    
    # 查询刚才创建的文档详情
    get_doc_detail()
