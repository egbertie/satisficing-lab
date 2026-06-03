#!/usr/bin/env python3
"""
添加文档协作者（解决权限问题）
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

def add_collaborator(doc_token, user_id="ou_aea2e859a6cee1f3a11e8c018eb88ec9"):
    """
    添加协作者到文档
    user_id: 从metadata中获取的user_id
    """
    token = get_token()
    
    url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_token}/members"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "members": [
            {
                "member_id": user_id,
                "member_type": "user",
                "perm": "full_access"  # 完全访问权限
            }
        ],
        "notify_lark": True  # 通知用户
    }
    
    print(f"添加协作者到文档: {doc_token}")
    print(f"用户ID: {user_id}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"状态: {response.status_code}")
        
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('code') == 0:
            print("✅ 添加协作者成功！")
            return True
        else:
            print(f"⚠️ 添加失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def try_different_user_ids(doc_token):
    """尝试不同的用户ID格式"""
    
    # 可能的用户ID格式
    user_ids = [
        "ou_aea2e859a6cee1f3a11e8c018eb88ec9",  # 从metadata来的
        "Egbertie",  # 用户名
        "egbertie",  # 小写用户名
    ]
    
    for user_id in user_ids:
        print(f"\n{'='*60}")
        print(f"尝试用户ID: {user_id}")
        print(f"{'='*60}")
        if add_collaborator(doc_token, user_id):
            return True
    
    return False

if __name__ == "__main__":
    doc_token = "GDtmdVaxroOf7jxR80ycb3Kcnhb"
    
    print("="*60)
    print("添加文档协作者")
    print("="*60)
    
    success = try_different_user_ids(doc_token)
    
    if success:
        print("\n✅ 完成！请刷新飞书文档查看")
    else:
        print("\n⚠️ 需要确认正确的用户ID")
        print("请提供你的飞书用户ID（可以在飞书个人资料中查看）")
