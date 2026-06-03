#!/usr/bin/env python3
"""
飞书API连接测试脚本
"""

import json
import requests
import sys

def test_connection():
    # 读取配置
    with open('/root/.openclaw/workspace/config/feishu_config.json', 'r') as f:
        config = json.load(f)
    
    app_id = config['app_id']
    app_secret = config['app_secret']
    base_url = config['base_url']
    
    print("="*60)
    print("飞书API连接测试")
    print("="*60)
    print(f"App ID: {app_id}")
    print(f"Base URL: {base_url}")
    print("-"*60)
    
    # 1. 获取Tenant Access Token
    print("\n[1/3] 获取Tenant Access Token...")
    token_url = f"{base_url}/auth/v3/tenant_access_token/internal"
    
    try:
        response = requests.post(token_url, json={
            "app_id": app_id,
            "app_secret": app_secret
        }, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                token = data["tenant_access_token"]
                expire = data["expire"]
                print(f"✅ 成功! Token有效期: {expire}秒")
                
                # 2. 测试获取用户信息
                print("\n[2/3] 测试获取应用信息...")
                app_info_url = f"{base_url}/application/v3/apps/{app_id}"
                headers = {"Authorization": f"Bearer {token}"}
                
                response2 = requests.get(app_info_url, headers=headers, timeout=30)
                if response2.status_code == 200:
                    print("✅ 应用信息获取成功")
                else:
                    print(f"⚠️ 应用信息获取失败: {response2.status_code}")
                
                # 3. 测试文档API权限
                print("\n[3/3] 测试文档API权限...")
                # 尝试获取应用拥有的权限
                permission_url = f"{base_url}/application/v6/apps/{app_id}/attributes"
                response3 = requests.get(permission_url, headers=headers, timeout=30)
                
                if response3.status_code == 200:
                    print("✅ 权限验证通过")
                else:
                    print(f"⚠️ 权限验证: {response3.status_code}")
                
                print("\n" + "="*60)
                print("✅ 飞书API连接测试通过!")
                print("="*60)
                return True
                
            else:
                print(f"❌ 获取Token失败: {data.get('msg')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
