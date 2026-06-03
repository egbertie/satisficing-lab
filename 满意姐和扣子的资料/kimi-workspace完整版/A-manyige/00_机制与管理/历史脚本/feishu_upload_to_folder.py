#!/usr/bin/env python3
"""
上传文件到飞书云盘共享文件夹
"""

import os
import json
import requests
from pathlib import Path

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
FOLDER_TOKEN = "DNKFfMXLGlIEp7dE6sFcPYJFnih"

BASE_URL = "https://open.feishu.cn/open-apis"
FILE_DIR = "/root/.openclaw/workspace/feishu_export"

def get_tenant_token():
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    return resp.json()["tenant_access_token"]

def upload_file(file_path, folder_token):
    """上传单个文件到云盘"""
    token = get_tenant_token()
    
    url = f"{BASE_URL}/drive/v1/files/upload_all"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'parent_type': 'folder',
            'parent_node': folder_token
        }
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=60)
    
    return resp.json()

def main():
    print("="*60)
    print("飞书云盘文件同步")
    print("="*60)
    print(f"目标文件夹: {FOLDER_TOKEN}")
    
    # 获取所有HTML文件
    files = list(Path(FILE_DIR).glob("*.html"))
    print(f"\n找到 {len(files)} 个文件")
    
    success_count = 0
    failed_files = []
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 上传: {file_path.name}")
        
        try:
            result = upload_file(str(file_path), FOLDER_TOKEN)
            
            if result.get("code") == 0:
                file_info = result.get("data", {})
                print(f"  ✅ 成功: {file_info.get('name', file_path.name)}")
                success_count += 1
            else:
                print(f"  ❌ 失败: {result.get('msg', '未知错误')}")
                failed_files.append(file_path.name)
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            failed_files.append(file_path.name)
    
    print("\n" + "="*60)
    print(f"同步完成: {success_count}/{len(files)} 成功")
    if failed_files:
        print(f"失败文件: {', '.join(failed_files)}")
    print("="*60)

if __name__ == "__main__":
    main()
