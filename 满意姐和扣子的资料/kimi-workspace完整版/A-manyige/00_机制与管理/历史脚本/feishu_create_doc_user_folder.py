#!/usr/bin/env python3
"""
飞书文档创建方案 - 使用用户个人文件夹（无需OAuth2）

原理：
1. 使用 tenant_token 获取用户的文件夹列表
2. 找到 parent_type="user" 的文件夹（用户的个人文件夹）
3. 在该文件夹下创建文档，用户就能看到了
"""

import json
import requests

# 飞书配置
APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
BASE_URL = "https://open.feishu.cn/open-apis"

def get_tenant_token():
    """获取 Tenant Access Token"""
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }, timeout=30)
    return resp.json()["tenant_access_token"]

def get_user_folder():
    """
    获取用户的个人文件夹
    返回：folder_token
    """
    token = get_tenant_token()
    
    # 1. 获取文件夹列表
    url = f"{BASE_URL}/drive/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "page_size": 100,
        "type": "folder"
    }
    
    print("正在获取文件夹列表...")
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    result = resp.json()
    
    if result.get("code") != 0:
        print(f"❌ 获取文件夹失败: {result.get('msg')}")
        return None
    
    files = result.get("data", {}).get("files", [])
    
    print(f"找到 {len(files)} 个文件夹")
    
    # 2. 查找 parent_type="user" 的文件夹（用户的个人文件夹）
    for file in files:
        name = file.get("name", "")
        token = file.get("token", "")
        parent_type = file.get("parent_type", "")
        
        print(f"  - {name} (parent_type: {parent_type})")
        
        # 找到用户的个人文件夹
        if parent_type == "user" or name == "我的文件" or name == "我的云文档":
            print(f"✅ 找到用户文件夹: {name}, token: {token}")
            return token
    
    # 如果没找到，返回第一个文件夹（通常是用户根目录）
    if files:
        first_folder = files[0]
        print(f"⚠️ 未找到明确的用户文件夹，使用第一个: {first_folder.get('name')}")
        return first_folder.get("token")
    
    return None

def create_doc_in_folder(title, folder_token):
    """
    在指定文件夹下创建文档
    """
    token = get_tenant_token()
    
    url = f"{BASE_URL}/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": title,
        "folder_token": folder_token  # ← 关键参数！
    }
    
    print(f"\n正在创建文档: {title}")
    print(f"在文件夹: {folder_token}")
    
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    result = resp.json()
    
    if result.get("code") == 0:
        doc = result["data"]["document"]
        print(f"✅ 创建成功!")
        print(f"   文档ID: {doc['document_id']}")
        print(f"   标题: {doc['title']}")
        return doc
    else:
        print(f"❌ 创建失败: {result.get('msg')}")
        return None

def main():
    print("="*60)
    print("飞书文档创建 - 用户文件夹方案")
    print("="*60)
    
    # Step 1: 获取用户文件夹
    folder_token = get_user_folder()
    
    if not folder_token:
        print("❌ 无法获取用户文件夹")
        return
    
    # Step 2: 在该文件夹下创建文档
    doc = create_doc_in_folder("满意解研究所-测试文档", folder_token)
    
    if doc:
        print("\n" + "="*60)
        print("✅ 完成！文档应该可以在你的云文档中看到了")
        print("="*60)
    else:
        print("\n创建失败，请检查日志")

if __name__ == "__main__":
    main()
