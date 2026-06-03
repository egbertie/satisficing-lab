#!/usr/bin/env python3
"""
Notion Markdown同步脚本 - 优化版
分批同步，带进度记录
"""
import json
import os
import re
import time
import requests
from pathlib import Path

NOTION_TOKEN = "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"
PARENT_PAGE_ID = "31fa8a0e-2bba-81fa-b98a-d61da835051e"

class NotionSyncer:
    def __init__(self):
        self.token = NOTION_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.parent_page_id = PARENT_PAGE_ID
        self.rate_limit_delay = 0.35
        
    def create_page(self, title, content_blocks=None, file_path=None):
        """创建Notion页面"""
        url = "https://api.notion.com/v1/pages"
        
        properties = {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        }
        
        if file_path:
            properties["文件路径"] = {
                "rich_text": [{"text": {"content": file_path}}]
            }
        
        payload = {
            "parent": {"page_id": self.parent_page_id},
            "properties": properties
        }
        
        if content_blocks:
            payload["children"] = content_blocks[:100]
        
        resp = requests.post(url, headers=self.headers, json=payload)
        time.sleep(self.rate_limit_delay)
        
        if resp.status_code == 200:
            return resp.json()
        else:
            return None
    
    def append_blocks(self, page_id, blocks):
        """追加blocks"""
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        
        for i in range(0, len(blocks), 100):
            batch = blocks[i:i+100]
            payload = {"children": batch}
            resp = requests.patch(url, headers=self.headers, json=payload)
            time.sleep(self.rate_limit_delay)
            
            if resp.status_code != 200:
                return False
        return True
    
    def markdown_to_blocks(self, content):
        """Markdown转Notion blocks"""
        blocks = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 代码块
            if line.strip().startswith('```'):
                lang = line.strip()[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                code_content = '\n'.join(code_lines)[:2000]
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": code_content}}],
                        "language": lang if lang else "plain text"
                    }
                })
                i += 1
                continue
            
            # 标题
            if line.startswith('# '):
                blocks.append({
                    "object": "block", "type": "heading_1",
                    "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:].strip()[:2000]}}]}
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block", "type": "heading_2",
                    "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:].strip()[:2000]}}]}
                })
            elif line.startswith('### '):
                blocks.append({
                    "object": "block", "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:].strip()[:2000]}}]}
                })
            # 列表
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                blocks.append({
                    "object": "block", "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line.strip()[2:].strip()[:2000]}}]}
                })
            elif re.match(r'^\d+\.\s', line.strip()):
                text = re.sub(r'^\d+\.\s', '', line.strip())[:2000]
                blocks.append({
                    "object": "block", "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}
                })
            # 分隔线
            elif line.strip() == '---':
                blocks.append({"object": "block", "type": "divider", "divider": {}})
            # 引用
            elif line.strip().startswith('> '):
                blocks.append({
                    "object": "block", "type": "quote",
                    "quote": {"rich_text": [{"type": "text", "text": {"content": line.strip()[2:].strip()[:2000]}}]}
                })
            # 普通段落
            elif line.strip():
                blocks.append({
                    "object": "block", "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": line.strip()[:2000]}}]}
                })
            
            i += 1
            if len(blocks) >= 500:
                blocks.append({
                    "object": "block", "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": "... (内容已截断)"}}]}
                })
                break
        
        return blocks
    
    def sync_file(self, file_path, workspace):
        """同步单个文件"""
        full_path = os.path.join(workspace, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        title = os.path.basename(file_path).replace('.md', '')[:100]  # Notion标题限制
        blocks = self.markdown_to_blocks(content)
        
        page = self.create_page(title, blocks, file_path)
        
        if page:
            if len(blocks) > 100:
                self.append_blocks(page['id'], blocks[100:])
            return {'success': True, 'page_id': page['id']}
        else:
            return {'success': False, 'error': 'API error'}
    
    def sync_batch(self, batch_name, file_list, workspace):
        """同步一批文件"""
        results = {
            'batch_name': batch_name,
            'total': len(file_list),
            'success': [],
            'failed': []
        }
        
        print(f"\n{'='*60}")
        print(f"开始同步 {batch_name}: {len(file_list)} 个文件")
        print(f"{'='*60}\n")
        
        for i, file_path in enumerate(file_list, 1):
            print(f"[{i}/{len(file_list)}] {file_path}", end=" ")
            result = self.sync_file(file_path, workspace)
            
            if result['success']:
                results['success'].append({'file': file_path, 'page_id': result['page_id']})
                print("✓")
            else:
                results['failed'].append({'file': file_path, 'error': result['error']})
                print(f"✗ {result['error']}")
        
        return results

def main():
    syncer = NotionSyncer()
    
    # 加载批次
    with open('/root/.openclaw/workspace/.notion_sync_batches.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    workspace = data['workspace']
    batches = data['batches']
    
    # 加载进度
    progress_file = '/root/.openclaw/workspace/.notion_sync_progress.json'
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
        
        result = syncer.sync_batch(batch_name, file_list, workspace)
        progress['results'][batch_name] = result
        progress['completed_batches'].append(batch_name)
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        
        print(f"\n{batch_name} 完成: {len(result['success'])}/{result['total']} 成功")
    
    print("\n" + "="*60)
    print("同步完成！")
    print("="*60)

if __name__ == '__main__':
    main()
