#!/usr/bin/env python3
import json
import os
import time
import requests

NOTION_TOKEN = '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'
PARENT_PAGE_ID = '31fa8a0e-2bba-81fa-b98a-d61da835051e'

headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def create_page(title, file_path, blocks):
    url = 'https://api.notion.com/v1/pages'
    payload = {
        'parent': {'page_id': PARENT_PAGE_ID},
        'properties': {
            'title': {'title': [{'text': {'content': title[:100]}}]},
            '文件路径': {'rich_text': [{'text': {'content': file_path}}]}
        },
        'children': blocks[:100] if blocks else []
    }
    resp = requests.post(url, headers=headers, json=payload)
    time.sleep(0.35)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"  API Error: {resp.status_code} - {resp.text[:200]}")
        return None

def md_to_blocks(content):
    blocks = []
    lines = content.split('\n')
    in_code = False
    
    for line in lines[:500]:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        
        if in_code:
            continue
        
        if stripped.startswith('# '):
            blocks.append({'object': 'block', 'type': 'heading_1', 'heading_1': {'rich_text': [{'type': 'text', 'text': {'content': stripped[2:][:2000]}}]}})
        elif stripped.startswith('## '):
            blocks.append({'object': 'block', 'type': 'heading_2', 'heading_2': {'rich_text': [{'type': 'text', 'text': {'content': stripped[3:][:2000]}}]}})
        elif stripped.startswith('### '):
            blocks.append({'object': 'block', 'type': 'heading_3', 'heading_3': {'rich_text': [{'type': 'text', 'text': {'content': stripped[4:][:2000]}}]}})
        elif stripped.startswith('- ') or stripped.startswith('* '):
            blocks.append({'object': 'block', 'type': 'bulleted_list_item', 'bulleted_list_item': {'rich_text': [{'type': 'text', 'text': {'content': stripped[2:][:2000]}}]}})
        elif stripped and not stripped.startswith('---'):
            blocks.append({'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': stripped[:2000]}}]}})
    
    return blocks

def sync_batch(batch_name, files, workspace):
    results = {'success': [], 'failed': []}
    
    print(f"\n{'='*60}")
    print(f"开始同步 {batch_name}: {len(files)} 个文件")
    print(f"{'='*60}\n")
    
    for i, f in enumerate(files, 1):
        try:
            full_path = os.path.join(workspace, f)
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            title = os.path.basename(f).replace('.md', '')
            blocks = md_to_blocks(content)
            page = create_page(title, f, blocks)
            
            if page:
                results['success'].append(f)
                print(f"[{i}/{len(files)}] ✓ {f}")
            else:
                results['failed'].append(f)
                print(f"[{i}/{len(files)}] ✗ {f}")
        except Exception as e:
            results['failed'].append(f"{f}: {e}")
            print(f"[{i}/{len(files)}] ✗ {f}: {e}")
    
    print(f"\n{batch_name} 完成: {len(results['success'])}/{len(files)} 成功")
    return results

def main():
    workspace = '/root/.openclaw/workspace'
    
    # Load batches
    with open(f'{workspace}/.notion_sync_batches.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    batches = data['batches']
    
    # Load progress
    progress_file = f'{workspace}/.notion_sync_progress.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
    else:
        progress = {'completed_batches': [], 'results': {}}
    
    batch_order = ['batch_1', 'batch_2', 'batch_3', 'batch_4', 'batch_5']
    
    for batch_name in batch_order:
        if batch_name in progress['completed_batches']:
            print(f"\n{batch_name} 已同步，跳过")
            continue
        
        file_list = batches.get(batch_name, [])
        if not file_list:
            continue
        
        # Limit batch 4 to avoid timeout (too many files)
        if batch_name == 'batch_4' and len(file_list) > 60:
            batch_4_a = file_list[:60]
            batch_4_b = file_list[60:]
            
            result = sync_batch('batch_4a', batch_4_a, workspace)
            progress['results']['batch_4a'] = result
            progress['completed_batches'].append('batch_4a')
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            
            result = sync_batch('batch_4b', batch_4_b, workspace)
            progress['results']['batch_4b'] = result
            progress['completed_batches'].append('batch_4b')
        else:
            result = sync_batch(batch_name, file_list, workspace)
            progress['results'][batch_name] = result
            progress['completed_batches'].append(batch_name)
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("所有批次同步完成！")
    print("="*60)

if __name__ == '__main__':
    main()
