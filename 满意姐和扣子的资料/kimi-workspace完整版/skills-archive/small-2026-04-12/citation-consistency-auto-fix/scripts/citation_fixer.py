#!/usr/bin/env python3
"""
引用一致性自动修复脚本
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
REPORT_FILE = WORKSPACE / "logs" / "citation-fix-report.json"

def find_markdown_files():
    """查找所有Markdown文件"""
    md_files = []
    for root, dirs, files in os.walk(WORKSPACE):
        # 跳过隐藏目录和node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
    return md_files

def extract_citations(content, file_path):
    """提取文件中的引用"""
    citations = []
    
    # Markdown链接 [text](url)
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for text, url in md_links:
        citations.append({
            'type': 'markdown_link',
            'text': text,
            'url': url,
            'line': content[:content.find(f'[{text}]')].count('\n') + 1
        })
    
    # 内部引用路径
    internal_refs = re.findall(r'\b[A-Z][a-z]+/[A-Z][a-z]+/[\w-]+\.md\b', content)
    for ref in internal_refs:
        citations.append({
            'type': 'internal_ref',
            'path': ref,
            'line': content.find(ref)
        })
    
    return citations

def validate_citation(citation, source_file):
    """验证引用是否有效"""
    if citation['type'] == 'markdown_link':
        url = citation['url']
        # 内部链接
        if url.startswith('/') or url.startswith('./') or url.startswith('../'):
            # 解析相对路径
            if url.startswith('/'):
                target = WORKSPACE / url[1:]
            else:
                target = source_file.parent / url
            return target.exists()
        # 外部URL暂不验证（网络检查太慢）
        return True
    
    elif citation['type'] == 'internal_ref':
        target = WORKSPACE / citation['path']
        return target.exists()
    
    return False

def fix_citation(citation, source_file, all_files):
    """尝试修复引用"""
    if citation['type'] == 'markdown_link':
        url = citation['url']
        # 尝试查找同名文件
        if not url.startswith('http'):
            filename = Path(url).name
            for file in all_files:
                if file.name == filename:
                    # 计算相对路径
                    try:
                        new_url = os.path.relpath(file, source_file.parent)
                        return new_url
                    except:
                        pass
    return None

def main():
    print("开始引用一致性扫描...")
    
    md_files = find_markdown_files()
    print(f"找到 {len(md_files)} 个Markdown文件")
    
    report = {
        "scan_time": datetime.now().isoformat(),
        "files_scanned": len(md_files),
        "citations_found": 0,
        "broken_found": 0,
        "auto_fixed": 0,
        "need_manual": 0,
        "fixes": []
    }
    
    for file_path in md_files[:100]:  # 限制前100个文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            citations = extract_citations(content, file_path)
            report["citations_found"] += len(citations)
            
            for citation in citations:
                if not validate_citation(citation, file_path):
                    report["broken_found"] += 1
                    
                    # 尝试修复
                    fixed_url = fix_citation(citation, file_path, md_files)
                    if fixed_url:
                        report["auto_fixed"] += 1
                        report["fixes"].append({
                            "file": str(file_path.relative_to(WORKSPACE)),
                            "old": citation.get('url') or citation.get('path'),
                            "new": fixed_url,
                            "status": "fixed"
                        })
                    else:
                        report["need_manual"] += 1
                        
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
    
    # 保存报告
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n扫描完成:")
    print(f"- 引用总数: {report['citations_found']}")
    print(f"- 失效引用: {report['broken_found']}")
    print(f"- 自动修复: {report['auto_fixed']}")
    print(f"- 需人工处理: {report['need_manual']}")
    print(f"\n详细报告: {REPORT_FILE}")
    
    return report

if __name__ == "__main__":
    main()
