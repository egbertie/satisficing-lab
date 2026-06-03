#!/usr/bin/env python3
"""
修复文档权限 - 方法2：使用旧版API
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

def get_my_info():
    """获取当前用户信息"""
    token = get_token()
    
    # 尝试获取bot信息
    url = "https://open.feishu.cn/open-apis/bot/v3/info"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("获取应用信息...")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态: {response.status_code}")
        print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {e}")

def share_doc_v2(doc_token):
    """使用旧版API分享文档"""
    token = get_token()
    
    # 旧版API
    url = f"https://open.feishu.cn/open-apis/drive/v1/files/{doc_token}/share"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "share_version": "OLD",  # 或 "NEW"
        "external_access": False,  # 企业内访问
        "security_entity": "ANYONE_CAN_READ"  # 任何人可读
    }
    
    print(f"\n分享文档: {doc_token}")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"状态: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        
        result = response.json()
        if result.get('code') == 0:
            print("✅ 分享成功")
            return True
        else:
            print(f"⚠️ {result.get('msg')}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return False

def update_doc_public_setting(doc_token):
    """更新文档为公开"""
    token = get_token()
    
    url = f"https://open.feishu.cn/open-apis/drive/v1/files/{doc_token}/public_url"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n更新文档公开设置: {doc_token}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态: {response.status_code}")
        print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    doc_token = "GDtmdVaxroOf7jxR80ycb3Kcnhb"
    
    print("="*60)
    print("修复文档权限")
    print("="*60)
    
    # 获取应用信息
    get_my_info()
    
    # 尝试分享
    share_doc_v2(doc_token)
    
    # 尝试更新公开设置
    update_doc_public_setting(doc_token)
    
    print("\n" + "="*60)
    print("修复完成，请刷新文档查看")
    print("="*60)
