#!/usr/bin/env python3
"""
测试用户提供的权限设置代码
"""

import json
import requests

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"

DOCUMENT_ID = "GDtmdVaxroOf7jxR80ycb3Kcnhb"
USER_OPEN_ID = "ou_aea2e859a6cee1f3a11e8c018eb88ec9"

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    return resp.json()["tenant_access_token"]

def set_document_permission(token, document_id, user_open_id):
    """用户提供的代码"""
    url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{document_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "type": "user",
        "member_id": user_open_id,
        "perm": "full_access"
    }
    
    print(f"请求URL: {url}")
    print(f"请求头: {headers}")
    print(f"请求体: {json.dumps(data, ensure_ascii=False)}")
    
    response = requests.post(url, headers=headers, json=data)
    print(f"\n状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应体: {response.text}")
    
    try:
        return response.json()
    except:
        return {"error": "无法解析JSON", "raw": response.text}

def main():
    print("="*60)
    print("测试用户提供的权限设置代码")
    print("="*60)
    
    token = get_tenant_token()
    print(f"Token获取成功: {token[:20]}...")
    
    result = set_document_permission(token, DOCUMENT_ID, USER_OPEN_ID)
    
    print("\n" + "="*60)
    print("结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("code") == 0:
        print("\n✅ 成功！权限已设置")
    else:
        print(f"\n❌ 失败: {result.get('msg', '未知错误')}")
        print("\n可能的解决方案:")
        print("1. 检查飞书开放平台是否申请了 drive:permission 权限")
        print("2. 确认文档ID和用户ID正确")
        print("3. 尝试使用 user_access_token 而非 tenant_access_token")
    
    print("="*60)

if __name__ == "__main__":
    main()
