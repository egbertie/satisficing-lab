#!/usr/bin/env python3
"""
飞书 OAuth2 Token 换取脚本
使用 Authorization Code 换取 User Access Token
"""

import os
import sys
import requests
from typing import Dict, Any

# 配置
APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"

def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """
    使用 Authorization Code 换取 User Access Token
    """
    url = "https://open.feishu.cn/open-apis/oauthen/v1/access_token"
    
    payload = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "code": code,
        "redirect_uri": "https://mushroomlike-nonextensively-arleen.ngrok-free.dev"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        return result
    except Exception as e:
        return {"error": str(e)}

def print_token_info(token_data: Dict[str, Any]):
    """
    打印Token信息
    """
    if token_data.get("code") == 0:
        data = token_data.get("data", {})
        
        print("="*60)
        print("🎉 成功获取 User Access Token!")
        print("="*60)
        print(f"\naccess_token: {data.get('access_token', '')}")
        print(f"token_type: {data.get('token_type', '')}")
        print(f"expires_in: {data.get('expires_in', 0)} 秒 ({data.get('expires_in', 0)//3600} 小时)")
        print(f"\nrefresh_token: {data.get('refresh_token', '')}")
        print(f"refresh_token_expires_in: {data.get('refresh_token_expires_in', 0)} 秒")
        print(f"\n权限范围: {data.get('scope', '')}")
        print("="*60)
        print("\n⚠️  请保存 access_token，2小时后需要用 refresh_token 续期")
        
        return data.get('access_token')
    else:
        print(f"❌ 获取失败: {token_data.get('msg', '未知错误')}")
        print(f"错误码: {token_data.get('code', 'N/A')}")
        return None

def main():
    """
    主函数
    """
    # 从命令行参数或输入获取code
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = input("请输入 Authorization Code: ").strip()
    
    if not code:
        print("❌ 未提供 Authorization Code")
        return
    
    print(f"正在用 code 换取 token...")
    print(f"Code: {code[:20]}...")
    
    # 换取token
    result = exchange_code_for_token(code)
    
    # 打印结果
    token = print_token_info(result)
    
    if token:
        # 保存到文件
        with open("/root/.openclaw/workspace/.feishu_user_token", "w") as f:
            f.write(token)
        print("\n✅ Token 已保存到 .feishu_user_token")

if __name__ == "__main__":
    main()
