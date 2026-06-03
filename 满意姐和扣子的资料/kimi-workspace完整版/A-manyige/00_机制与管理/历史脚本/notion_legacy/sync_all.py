#!/usr/bin/env python3
"""
Notion批量同步脚本 - 执行所有批次
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
        return {'error': f'{resp.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def md_to_blocks(content):
    blocks = []
    in_code = False
    for line in content.split('\n')[:400]:
        s = line.strip()
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if s.startswith('# '):
            blocks.append({'object': 'block', 'type': 'heading_1', 'heading_1': {'rich_text': [{'type': 'text', 'text': {'content': s[2:][:2000]}}]}})
        elif s.startswith('## '):
            blocks.append({'object': 'block', 'type': 'heading_2', 'heading_2': {'rich_text': [{'type': 'text', 'text': {'content': s[3:][:2000]}}]}})
        elif s.startswith('### '):
            blocks.append({'object': 'block', 'type': 'heading_3', 'heading_3': {'rich_text': [{'type': 'text', 'text': {'content': s[4:][:2000]}}]}})
        elif s.startswith('- ') or s.startswith('* '):
            blocks.append({'object': 'block', 'type': 'bulleted_list_item', 'bulleted_list_item': {'rich_text': [{'type': 'text', 'text': {'content': s[2:][:2000]}}]}})
        elif s and not s.startswith('---'):
            blocks.append({'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': s[:2000]}}]}})
    if len(content.split('\n')) > 400:
        blocks.append({'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': '... (内容已截断)'}}]}})
    return blocks

def get_existing_pages():
    """获取已同步的页面"""
    url = 'https://api.notion.com/v1/search'
    payload = {'query': '', 'filter': {'value':'page','property':'object'}, 'page_size': 100}
    resp = requests.post(url, headers=headers, json=payload)
    time.sleep(0.35)
    
    existing = set()
    if resp.status_code == 200:
        for p in resp.json().get('results', []):
            if p.get('parent', {}).get('page_id') == PARENT_PAGE_ID:
                # Try to get file path from properties
                props = p.get('properties', {})
                file_path = ''
                if '文件路径' in props:
                    rich_text = props['文件路径'].get('rich_text', [])
                    if rich_text:
                        file_path = rich_text[0].get('text', {}).get('content', '')
                if file_path:
                    existing.add(file_path)
    return existing

def sync_batch(batch_name, files, workspace, existing):
    results = {'batch_name': batch_name, 'total': len(files), 'success': [], 'failed': [], 'skipped': []}
    
    print(f"\n{'='*60}")
    print(f"同步 {batch_name}: {len(files)} 个文件")
    print(f"{'='*60}\n")
    
    for i, f in enumerate(files, 1):
        # Skip if already exists
        if f in existing:
            results['skipped'].append(f)
            print(f"[{i}/{len(files)}] ⊘ {f} (已存在)")
            continue
            
        try:
            full_path = os.path.join(workspace, f)
            if not os.path.exists(full_path):
                results['failed'].append({'file': f, 'error': 'File not found'})
                print(f"[{i}/{len(files)}] ✗ {f} (文件不存在)")
                continue
                
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            title = os.path.basename(f).replace('.md', '')
            blocks = md_to_blocks(content)
            page = create_page(title, f, blocks)
            
            if page and 'id' in page:
                results['success'].append({'file': f, 'page_id': page['id']})
                print(f"[{i}/{len(files)}] ✓ {f}")
                existing.add(f)
            else:
                error = page.get('error', 'Unknown') if isinstance(page, dict) else 'Failed'
                results['failed'].append({'file': f, 'error': error})
                print(f"[{i}/{len(files)}] ✗ {f} - {error}")
        except Exception as e:
            results['failed'].append({'file': f, 'error': str(e)})
            print(f"[{i}/{len(files)}] ✗ {f} - {e}")
    
    print(f"\n{batch_name} 完成: {len(results['success'])} 成功, {len(results['skipped'])} 跳过, {len(results['failed'])} 失败")
    return results

def main():
    workspace = '/root/.openclaw/workspace'
    
    # Load batches
    with open(f'{workspace}/.notion_sync_batches.json', 'r') as f:
        data = json.load(f)
    batches = data['batches']
    
    # Get existing pages
    print("检查已同步页面...")
    existing = get_existing_pages()
    print(f"找到 {len(existing)} 个已同步页面")
    
    # Load progress
    progress_file = f'{workspace}/.notion_sync_progress.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
    else:
        progress = {'completed_batches': [], 'results': {}, 'existing_pages': list(existing)}
    
    batch_order = ['batch_1', 'batch_2', 'batch_3', 'batch_4', 'batch_5']
    
    for batch_name in batch_order:
        if batch_name in progress['completed_batches']:
            print(f"\n{batch_name} 已标记完成，跳过")
            continue
        
        file_list = batches.get(batch_name, [])
        if not file_list:
            continue
        
        # Split large batches
        if len(file_list) > 50:
            chunks = [file_list[i:i+50] for i in range(0, len(file_list), 50)]
            for idx, chunk in enumerate(chunks):
                sub_batch = f"{batch_name}_{chr(97+idx)}"  # batch_4_a, batch_4_b, etc.
                result = sync_batch(sub_batch, chunk, workspace, existing)
                progress['results'][sub_batch] = result
                
                with open(progress_file, 'w') as f:
                    json.dump(progress, f, ensure_ascii=False, indent=2)
            progress['completed_batches'].append(batch_name)
        else:
            result = sync_batch(batch_name, file_list, workspace, existing)
            progress['results'][batch_name] = result
            progress['completed_batches'].append(batch_name)
        
        with open(progress_file, 'w') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("同步完成！")
    print("="*60)

if __name__ == '__main__':
    main()
