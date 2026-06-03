#!/usr/bin/env python3
"""
严格按照用户提供的正确格式测试
"""

import json
import requests

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"

DOCUMENT_ID = "GDtmdVaxroOf7jxR80ycb3Kcnhb"
USER_ID = "ou_aea2e859a6cee1f3a11e8c018eb88ec9"

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    return resp.json()["tenant_access_token"]

def add_permission_exact_format():
    """严格按照用户提供的格式"""
    token = get_tenant_token()
    
    url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{DOCUMENT_ID}/members"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # ✅ 用户提供的正确格式
    data = {
        "type": "user",
        "member_id": USER_ID,
        "perm": "full_access"
    }
    
    print("="*60)
    print("严格按照正确格式调用")
    print("="*60)
    print(f"\nURL: {url}")
    print(f"Headers: {headers}")
    print(f"Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    resp = requests.post(url, headers=headers, json=data)
    
    print(f"\n状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
    
    try:
        result = resp.json()
        print(f"\n解析结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except:
        print("无法解析JSON")
        return None

def main():
    result = add_permission_exact_format()
    
    print("\n" + "="*60)
    if result and result.get("code") == 0:
        print("✅ 成功！权限已添加")
    else:
        print(f"❌ 失败: {result.get('msg', '未知错误') if result else '解析失败'}")
        print("\n说明：即使格式正确，tenant_token仍可能无法修改权限")
        print("需要 user_token 或飞书后台的特殊设置")
    print("="*60)

if __name__ == "__main__":
    main()
