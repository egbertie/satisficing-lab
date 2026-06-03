#!/usr/bin/env python3
"""
飞书多维表格同步 - 适配现有字段
"""

import json
import requests
import os

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
BASE_ID = "YVHyblEsDakryasCJpxcrh6xnTb"
TABLE_ID = "tblkrnQJZPbHU5KE"
FIELD_ID = "fldtN7nFBk"  # "文本"字段

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    response = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }, timeout=30)
    return response.json()['tenant_access_token']

def add_record_simple(content):
    """添加记录（只使用文本字段）"""
    token = get_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_ID}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "fields": {
            "文本": content[:50000]  # 限制长度
        }
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    return response.json()

def sync_files(input_dir="./docs"):
    """同步文件到表格"""
    
    print("="*60)
    print("飞书多维表格同步")
    print(f"表格ID: {BASE_ID}")
    print("="*60)
    
    success = 0
    failed = 0
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, input_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"❌ 读取失败: {rel_path}")
                    failed += 1
                    continue
                
                # 构建记录内容：文件名 + 内容
                record_content = f"【文件名】{file}\n【路径】{rel_path}\n\n【内容】\n{content}"
                
                result = add_record_simple(record_content)
                
                if result.get('code') == 0:
                    print(f"✅ 已同步: {rel_path}")
                    success += 1
                else:
                    print(f"❌ 失败: {rel_path} - {result.get('msg')}")
                    failed += 1
    
    print(f"\n{'='*60}")
    print(f"完成: 成功 {success}, 失败 {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    import sys
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "./docs"
    
    print(f"同步目录: {input_dir}\n")
    sync_files(input_dir)
