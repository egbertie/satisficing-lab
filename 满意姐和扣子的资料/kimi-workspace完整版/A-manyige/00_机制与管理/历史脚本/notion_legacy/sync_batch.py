#!/usr/bin/env python3
"""
Notion同步 - 单批次执行脚本
"""
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
            '文件路径': {'rich_text': [{'text': {'content': file_path[:2000]}}]}
        },
        'children': blocks[:100] if blocks else []
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        time.sleep(0.35)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {'error': f'{resp.status_code}: {resp.text[:200]}'}
    except Exception as e:
        return {'error': str(e)}

def md_to_blocks(content):
    blocks = []
    lines = content.split('\n')
    in_code = False
    
    for line in lines[:400]:
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
        elif stripped and not stripped.startswith('---') and not stripped.startswith('```'):
            blocks.append({'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': stripped[:2000]}}]}})
    
    if len(lines) > 400:
        blocks.append({'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': '... (内容已截断)'}}]}})
    
    return blocks

def sync_single_batch(batch_name, files, workspace):
    results = {'batch_name': batch_name, 'total': len(files), 'success': [], 'failed': []}
    
    print(f"\n{'='*60}")
    print(f"同步 {batch_name}: {len(files)} 个文件")
    print(f"{'='*60}\n")
    
    for i, f in enumerate(files, 1):
        try:
            full_path = os.path.join(workspace, f)
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            title = os.path.basename(f).replace('.md', '')
            blocks = md_to_blocks(content)
            page = create_page(title, f, blocks)
            
            if page and 'id' in page:
                results['success'].append({'file': f, 'page_id': page['id']})
                print(f"[{i}/{len(files)}] ✓ {f}")
            else:
                error = page.get('error', 'Unknown error') if isinstance(page, dict) else 'Failed'
                results['failed'].append({'file': f, 'error': error})
                print(f"[{i}/{len(files)}] ✗ {f} - {error}")
        except Exception as e:
            results['failed'].append({'file': f, 'error': str(e)})
            print(f"[{i}/{len(files)}] ✗ {f} - {e}")
    
    print(f"\n{batch_name} 完成: {len(results['success'])}/{len(files)} 成功")
    return results

def main():
    workspace = '/root/.openclaw/workspace'
    
    # Load batch files
    batch_name = 'batch_1'
    batch_file = f'{workspace}/.notion_sync_{batch_name}.txt'
    
    if not os.path.exists(batch_file):
        print(f"Batch file not found: {batch_file}")
        return
    
    with open(batch_file, 'r', encoding='utf-8') as f:
        files = [line.strip() for line in f if line.strip()]
    
    result = sync_single_batch(batch_name, files, workspace)
    
    # Save result
    with open(f'{workspace}/.notion_sync_result_{batch_name}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 .notion_sync_result_{batch_name}.json")

if __name__ == '__main__':
    main()
