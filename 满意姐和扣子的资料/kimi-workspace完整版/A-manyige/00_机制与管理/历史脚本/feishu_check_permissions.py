#!/usr/bin/env python3
"""
验证飞书应用当前权限列表
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

def check_permissions():
    """检查应用权限列表"""
    token = get_tenant_token()
    
    url = "https://open.feishu.cn/open-apis/auth/v3/permissions/list"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("="*60)
    print("检查应用权限列表")
    print("="*60)
    
    resp = requests.get(url, headers=headers)
    result = resp.json()
    
    if result.get("code") == 0:
        permissions = result.get("data", {}).get("permissions", [])
        
        print(f"\n✅ 获取成功，共 {len(permissions)} 个权限：\n")
        
        # 关键权限检查
        key_permissions = [
            "drive:file:read",
            "drive:file:write", 
            "drive:permission",
            "drive:permission:member",
            "docx:document:read",
            "docx:document:write",
            "bitable:app:read",
            "bitable:app:write",
            "bitable:table:record:read",
            "bitable:table:record:write"
        ]
        
        permission_dict = {p.get("permission_code"): p for p in permissions}
        
        print("关键权限检查：")
        print("-"*60)
        for key in key_permissions:
            status = "✅ 已开通" if key in permission_dict else "❌ 未开通"
            print(f"{key:40} {status}")
        
        print("\n" + "="*60)
        print("完整权限列表：")
        print("-"*60)
        for p in permissions:
            code = p.get("permission_code", "")
            name = p.get("permission_name", "")
            print(f"{code:40} {name}")
            
        return permission_dict
    else:
        print(f"❌ 获取失败: {result.get('msg')}")
        return {}

if __name__ == "__main__":
    check_permissions()
