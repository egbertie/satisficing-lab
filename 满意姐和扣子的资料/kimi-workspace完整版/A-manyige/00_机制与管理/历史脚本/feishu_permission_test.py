#!/usr/bin/env python3
"""
飞书文档权限修复 - 根据官方文档调整API格式
参考：https://open.feishu.cn/document/server-docs/docs/drive-v1/permission/permission-member/create
"""

import json
import requests

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
BASE_URL = "https://open.feishu.cn/open-apis"

DOCUMENT_ID = "GDtmdVaxroOf7jxR80ycb3Kcnhb"
USER_ID = "ou_aea2e859a6cee1f3a11e8c018eb88ec9"

def get_tenant_token():
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }, timeout=30)
    return resp.json()["tenant_access_token"]

def check_doc_permissions(doc_id):
    """查看文档当前权限"""
    token = get_tenant_token()
    
    url = f"{BASE_URL}/drive/v1/permissions/{doc_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("查看当前权限...")
    resp = requests.get(url, headers=headers, timeout=30)
    print(f"状态: {resp.status_code}")
    try:
        print(f"响应: {resp.text[:500]}")
    except:
        pass

def add_permission_v2(doc_id, user_id):
    """
    尝试不同的API格式
    """
    token = get_tenant_token()
    
    # 尝试格式1: 官方文档格式
    url = f"{BASE_URL}/drive/v1/permissions/{doc_id}/members"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 格式1: members数组
    data1 = {
        "members": [
            {
                "type": "user",
                "member_id": user_id,
                "perm": "full_access"
            }
        ]
    }
    
    print("\n尝试格式1: members数组...")
    print(f"请求体: {json.dumps(data1, ensure_ascii=False)}")
    
    resp = requests.post(url, headers=headers, json=data1, timeout=30)
    print(f"状态: {resp.status_code}")
    print(f"响应: {resp.text[:500]}")
    
    if resp.status_code == 200:
        return True
    
    # 格式2: 单个成员（非数组）
    data2 = {
        "type": "user",
        "member_id": user_id,
        "perm": "full_access"
    }
    
    print("\n尝试格式2: 单个成员...")
    print(f"请求体: {json.dumps(data2, ensure_ascii=False)}")
    
    resp = requests.post(url, headers=headers, json=data2, timeout=30)
    print(f"状态: {resp.status_code}")
    print(f"响应: {resp.text[:500]}")
    
    return resp.status_code == 200

def main():
    print("="*60)
    print("飞书权限修复 - 多格式尝试")
    print("="*60)
    
    # 先查看当前权限
    check_doc_permissions(DOCUMENT_ID)
    
    # 尝试添加权限
    success = add_permission_v2(DOCUMENT_ID, USER_ID)
    
    print("\n" + "="*60)
    if success:
        print("✅ 权限添加成功！")
    else:
        print("❌ 所有格式都失败")
        print("\n建议：")
        print("1. 检查飞书开放平台权限配置")
        print("2. 联系飞书技术支持")
        print("3. 使用云盘共享文件夹方案")
    print("="*60)

if __name__ == "__main__":
    main()
