#!/usr/bin/env python3
"""
飞书文档权限修复方案 - 添加用户访问权限
"""

import json
import requests

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
BASE_URL = "https://open.feishu.cn/open-apis"

# 已创建的文档ID
DOCUMENT_ID = "GDtmdVaxroOf7jxR80ycb3Kcnhb"

# 用户ID（从metadata中获取）
USER_ID = "ou_aea2e859a6cee1f3a11e8c018eb88ec9"

def get_tenant_token():
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }, timeout=30)
    return resp.json()["tenant_access_token"]

def add_member_permission(doc_id, user_id):
    """
    添加成员权限 - 关键：需要 type: "user"
    """
    token = get_tenant_token()
    
    url = f"{BASE_URL}/drive/v1/permissions/{doc_id}/members"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 关键：需要 type 字段！
    data = {
        "members": [
            {
                "type": "user",  # ← 必填！
                "member_id": user_id,
                "perm": "full_access"  # full_access 或 read
            }
        ]
    }
    
    print(f"正在添加成员权限...")
    print(f"文档ID: {doc_id}")
    print(f"用户ID: {user_id}")
    
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    result = resp.json()
    
    print(f"状态码: {resp.status_code}")
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get("code") == 0:
        print("✅ 成员权限添加成功！")
        return True
    else:
        print(f"❌ 添加失败: {result.get('msg')}")
        return False

def set_link_permission(doc_id):
    """
    设置链接权限 - 让任何人可查看
    """
    token = get_tenant_token()
    
    url = f"{BASE_URL}/drive/v1/permissions/{doc_id}/link"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "anyone_can_view"  # 任何人可查看
    }
    
    print(f"\n正在设置链接权限...")
    
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    result = resp.json()
    
    print(f"状态码: {resp.status_code}")
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get("code") == 0:
        print("✅ 链接权限设置成功！")
        return True
    else:
        print(f"⚠️ 设置失败: {result.get('msg')}")
        return False

def get_doc_url(doc_id):
    """
    获取文档访问链接
    """
    token = get_tenant_token()
    
    url = f"{BASE_URL}/drive/v1/files/{doc_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n正在获取文档信息...")
    
    resp = requests.get(url, headers=headers, timeout=30)
    result = resp.json()
    
    if result.get("code") == 0:
        file_info = result["data"]
        doc_url = file_info.get("url", "")
        print(f"✅ 获取成功!")
        print(f"文档URL: {doc_url}")
        return doc_url
    else:
        print(f"❌ 获取失败: {result.get('msg')}")
        return None

def main():
    print("="*60)
    print("飞书文档权限修复")
    print("="*60)
    
    # Step 1: 添加成员权限
    success1 = add_member_permission(DOCUMENT_ID, USER_ID)
    
    # Step 2: 设置链接权限（可选）
    success2 = set_link_permission(DOCUMENT_ID)
    
    # Step 3: 获取文档URL
    doc_url = get_doc_url(DOCUMENT_ID)
    
    print("\n" + "="*60)
    if success1:
        print("✅ 权限修复完成！")
        print("\n你现在应该可以在飞书云文档中看到该文档了。")
        if doc_url:
            print(f"\n文档链接: {doc_url}")
    else:
        print("❌ 权限修复失败，请检查错误信息")
    print("="*60)

if __name__ == "__main__":
    main()
