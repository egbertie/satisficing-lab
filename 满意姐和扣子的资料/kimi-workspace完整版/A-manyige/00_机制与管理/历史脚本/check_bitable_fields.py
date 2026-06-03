#!/usr/bin/env python3
"""
检查飞书多维表格字段结构
"""

import json
import requests

APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
BASE_ID = "YVHyblEsDakryasCJpxcrh6xnTb"
TABLE_ID = "tblkrnQJZPbHU5KE"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    response = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }, timeout=30)
    return response.json()['tenant_access_token']

def get_table_fields():
    """获取表格字段信息"""
    token = get_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_ID}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, timeout=30)
    return response.json()

if __name__ == "__main__":
    print("查询表格字段结构...")
    result = get_table_fields()
    print(json.dumps(result, indent=2, ensure_ascii=False))
