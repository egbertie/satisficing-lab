#!/usr/bin/env python3
"""
上传文件到飞书云盘 - 使用drive:file:upload权限
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

def upload_file_v2(file_path, folder_token):
    """使用正确的API格式上传"""
    token = get_tenant_token()
    
    # 方法1: 使用 upload_all API，不带parent_type
    url = f"{BASE_URL}/drive/v1/files/upload_all"
    headers = {"Authorization": f"Bearer {token}"}
    
    filename = os.path.basename(file_path)
    
    with open(file_path, 'rb') as f:
        files = {'file': (filename, f, 'text/html')}
        data = {'parent_node': folder_token}  # 只传folder_token
        
        try:
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            return resp.json()
        except Exception as e:
            return {"code": -1, "msg": str(e)}

def main():
    print("="*60)
    print("飞书云盘文件同步 V2")
    print("="*60)
    
    files = list(Path(FILE_DIR).glob("*.html"))
    print(f"目标文件夹: {FOLDER_TOKEN}")
    print(f"待上传文件: {len(files)} 个\n")
    
    success_count = 0
    
    # 先测试上传1个文件
    test_file = files[0]
    print(f"测试上传: {test_file.name}")
    
    result = upload_file_v2(str(test_file), FOLDER_TOKEN)
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    
    if result.get("code") == 0:
        print("✅ 测试成功，开始批量上传...\n")
        success_count = 1
        
        # 上传剩余文件
        for i, file_path in enumerate(files[1:], 2):
            print(f"[{i}/{len(files)}] {file_path.name}...", end=" ")
            result = upload_file_v2(str(file_path), FOLDER_TOKEN)
            
            if result.get("code") == 0:
                print("✅")
                success_count += 1
            else:
                print(f"❌ {result.get('msg', '错误')}")
    else:
        print("\n❌ 测试失败，尝试其他方法...")
        print("建议：手动上传到云盘，或明天再调试")
    
    print(f"\n成功上传: {success_count}/{len(files)}")

if __name__ == "__main__":
    main()
