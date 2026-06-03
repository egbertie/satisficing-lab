#!/usr/bin/env python3
"""
测试 parent_token 方案 - 创建文档到指定文件夹
"""

import json
import requests

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    return resp.json()["tenant_access_token"]

def get_folders():
    """获取所有文件夹"""
    token = get_tenant_token()
    
    url = "https://open.feishu.cn/open-apis/drive/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 100, "type": "folder"}
    
    resp = requests.get(url, headers=headers, params=params)
    result = resp.json()
    
    if result.get("code") == 0:
        return result.get("data", {}).get("files", [])
    return []

def create_doc_with_parent(title, parent_token):
    """在指定文件夹下创建文档"""
    token = get_tenant_token()
    
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 关键：指定 parent_token
    data = {
        "title": title,
        "folder_token": parent_token  # 或 parent_token，看API要求
    }
    
    print(f"\n创建文档: {title}")
    print(f"父文件夹: {parent_token}")
    print(f"请求体: {json.dumps(data, indent=2)}")
    
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()
    
    print(f"状态码: {resp.status_code}")
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    return result

def main():
    print("="*60)
    print("测试 parent_token 方案")
    print("="*60)
    
    # 1. 获取所有文件夹
    folders = get_folders()
    print(f"\n找到 {len(folders)} 个文件夹：")
    
    for i, f in enumerate(folders[:5], 1):
        print(f"{i}. {f.get('name')} (token: {f.get('token')[:20]}...)")
    
    if not folders:
        print("没有文件夹，测试失败")
        return
    
    # 2. 使用第一个文件夹创建文档
    parent_token = folders[0].get("token")
    print(f"\n使用第一个文件夹: {folders[0].get('name')}")
    
    result = create_doc_with_parent("parent_token测试文档", parent_token)
    
    print("\n" + "="*60)
    if result.get("code") == 0:
        doc = result.get("data", {}).get("document", {})
        print("✅ 创建成功!")
        print(f"文档ID: {doc.get('document_id')}")
        print(f"标题: {doc.get('title')}")
        print("\n请检查该文件夹下是否能看到此文档！")
    else:
        print(f"❌ 创建失败: {result.get('msg')}")
    print("="*60)

if __name__ == "__main__":
    main()
