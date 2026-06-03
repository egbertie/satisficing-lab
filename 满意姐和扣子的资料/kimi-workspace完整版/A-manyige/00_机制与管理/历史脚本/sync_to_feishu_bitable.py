#!/usr/bin/env python3
"""
飞书多维表格同步 - 适配用户提供的表格
"""

import json
import requests
import os
from pathlib import Path

# 飞书配置
APP_ID = "cli_a927c5dfa4381cc6"
APP_SECRET = "8950yzh6jj17nQkKBjvGIdRocdrslhjI"
BASE_URL = "https://open.feishu.cn/open-apis"

# 表格信息
BASE_ID = "YVHyblEsDakryasCJpxcrh6xnTb"
TABLE_ID = "tblkrnQJZPbHU5KE"

def get_token():
    """获取Tenant Access Token"""
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    response = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }, timeout=30)
    return response.json()['tenant_access_token']

def list_tables():
    """列出表格中的所有表"""
    token = get_token()
    url = f"{BASE_URL}/bitable/v1/apps/{BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, timeout=30)
    return response.json()

def add_record(title, content, category="", file_path=""):
    """添加记录到表格"""
    token = get_token()
    url = f"{BASE_URL}/bitable/v1/apps/{BASE_ID}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 根据表格字段构建数据
    data = {
        "fields": {
            "文件名": title,
            "内容": content[:5000] if content else "",  # 限制长度
            "分类": category,
            "文件路径": file_path
        }
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    return response.json()

def sync_markdown_files(input_dir="./docs"):
    """同步Markdown文件到多维表格"""
    
    print("="*60)
    print("飞书多维表格同步")
    print(f"表格: {BASE_ID}")
    print("="*60)
    
    success_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, input_dir)
                
                # 读取内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"❌ 读取失败: {rel_path} - {e}")
                    error_count += 1
                    continue
                
                # 确定分类
                category = "其他"
                if '核心' in rel_path or 'CORE' in rel_path:
                    category = "核心"
                elif '战略' in rel_path or 'STRATEGY' in rel_path:
                    category = "战略"
                elif '文化' in rel_path or 'CULTURE' in rel_path:
                    category = "文化"
                elif '执行' in rel_path or 'EXECUTION' in rel_path:
                    category = "执行"
                elif '专家' in rel_path or 'EXPERT' in rel_path:
                    category = "专家"
                
                # 添加到表格
                title = file.replace('.md', '')
                result = add_record(title, content, category, rel_path)
                
                if result.get('code') == 0:
                    print(f"✅ 已同步: {rel_path}")
                    success_count += 1
                else:
                    print(f"❌ 失败: {rel_path} - {result.get('msg')}")
                    error_count += 1
    
    print(f"\n{'='*60}")
    print(f"同步完成: 成功 {success_count}, 失败 {error_count}")
    print(f"{'='*60}")
    
    return success_count, error_count

if __name__ == "__main__":
    import sys
    
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "./docs"
    
    # 先列出表格信息
    print("查询表格信息...")
    tables = list_tables()
    print(f"表格信息: {json.dumps(tables, indent=2, ensure_ascii=False)[:500]}")
    
    # 开始同步
    print(f"\n开始同步目录: {input_dir}\n")
    sync_markdown_files(input_dir)
