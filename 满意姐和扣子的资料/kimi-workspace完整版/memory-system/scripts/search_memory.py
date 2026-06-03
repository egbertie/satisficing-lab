#!/usr/bin/env python3
"""
记忆检索脚本 - 解决"想不起来"

用法:
    python3 search_memory.py --query "关键词"
    python3 search_memory.py --query "关键词" --from-date 2026-04-01 --to-date 2026-04-20
    python3 search_memory.py --query "关键词" --scope memory,knowledge
    python3 search_memory.py --list-all  # 列出所有归档
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# 基础目录
BASE_DIR = Path(__file__).parent.parent.resolve()
MEMORY_DIR = BASE_DIR / "memory"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
PROJECTS_DIR = BASE_DIR / "projects"


def parse_date_from_filename(filename: str) -> datetime:
    """从文件名解析日期"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d')
    return datetime.min


def search_in_directory(directory: Path, query: str, from_date=None, to_date=None):
    """
    在指定目录中搜索
    
    Args:
        directory: 搜索目录
        query: 搜索关键词
        from_date: 起始日期 (datetime)
        to_date: 结束日期 (datetime)
    
    Returns:
        结果列表 [(filepath, title, matched_lines, date)]
    """
    results = []
    query_lower = query.lower()
    
    if not directory.exists():
        return results
    
    for filepath in sorted(directory.glob('*.md'), reverse=True):
        try:
            file_date = parse_date_from_filename(filepath.name)
            
            # 日期过滤
            if from_date and file_date < from_date:
                continue
            if to_date and file_date > to_date:
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题 (第一行 # 开头)
            title = filepath.stem
            for line in content.split('\n')[:5]:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            # 搜索匹配
            matched_lines = []
            content_lower = content.lower()
            
            if query_lower in content_lower:
                # 找到匹配行及上下文
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        # 取前后各1行作为上下文
                        start = max(0, i - 1)
                        end = min(len(lines), i + 2)
                        context = '\n'.join(lines[start:end])
                        matched_lines.append(context)
            
            if matched_lines:
                results.append({
                    'filepath': str(filepath),
                    'filename': filepath.name,
                    'title': title,
                    'matches': matched_lines,
                    'date': file_date,
                    'size': len(content)
                })
                
        except Exception as e:
            print(f"警告: 读取文件 {filepath} 失败: {e}", file=sys.stderr)
            continue
    
    return results


def format_results(results, query, page=1, page_size=10):
    """格式化输出搜索结果"""
    if not results:
        print(f'未找到包含 "{query}" 的记忆')
        return
    
    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size
    page_results = results[start:end]
    
    print(f'\n🔍 搜索 "{query}" 找到 {total} 条记忆 (显示第 {page}-{min(end, total)} 条)')
    print('=' * 60)
    
    for i, result in enumerate(page_results, start + 1):
        date_str = result['date'].strftime('%Y-%m-%d') if result['date'] != datetime.min else '未知'
        print(f'\n[{i}] {result["title"]}')
        print(f'    📅 {date_str} | 📄 {result["filename"]} | 📊 {result["size"]} 字符')
        print(f'    匹配内容:')
        for match in result['matches'][:3]:  # 最多显示3处匹配
            # 高亮关键词
            highlighted = match
            try:
                # 简单高亮
                import re as re_module
                highlighted = re_module.sub(
                    f'({re_module.escape(query)})', 
                    r'\033[1;33m\1\033[0m', 
                    match, 
                    flags=re_module.IGNORECASE
                )
            except:
                pass
            for line in highlighted.split('\n')[:4]:  # 每处最多4行
                print(f'      | {line[:100]}')  # 限制行长度
        print(f'    📂 {result["filepath"]}')
    
    if total > end:
        print(f'\n... 还有 {total - end} 条结果 (使用 --page {page + 1} 查看)')


def list_all_archives():
    """列出所有归档"""
    if not MEMORY_DIR.exists():
        print("暂无归档记忆")
        return
    
    files = sorted(MEMORY_DIR.glob('*.md'), reverse=True)
    if not files:
        print("暂无归档记忆")
        return
    
    print(f'\n📚 所有归档记忆 ({len(files)} 条)')
    print('=' * 60)
    
    for i, filepath in enumerate(files[:50], 1):  # 最多显示50条
        file_date = parse_date_from_filename(filepath.name)
        date_str = file_date.strftime('%Y-%m-%d') if file_date != datetime.min else '未知'
        
        # 读取标题
        title = filepath.stem
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('# '):
                    title = first_line[2:]
        except:
            pass
        
        print(f'{i}. [{date_str}] {title}')


def main():
    parser = argparse.ArgumentParser(description='记忆检索工具')
    parser.add_argument('--query', '-q', help='搜索关键词')
    parser.add_argument('--from-date', help='起始日期 (YYYY-MM-DD)')
    parser.add_argument('--to-date', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--scope', '-s', default='memory,knowledge', 
                       help='搜索范围: memory,knowledge,projects (逗号分隔)')
    parser.add_argument('--page', '-p', type=int, default=1, help='页码')
    parser.add_argument('--page-size', '-n', type=int, default=10, help='每页条数')
    parser.add_argument('--list-all', '-l', action='store_true', help='列出所有归档')
    
    args = parser.parse_args()
    
    # 解析日期
    from_date = None
    to_date = None
    if args.from_date:
        from_date = datetime.strptime(args.from_date, '%Y-%m-%d')
    if args.to_date:
        to_date = datetime.strptime(args.to_date, '%Y-%m-%d')
    
    # 列出所有
    if args.list_all:
        list_all_archives()
        return
    
    # 必须提供关键词
    if not args.query:
        print("错误: 请提供搜索关键词 (--query)", file=sys.stderr)
        sys.exit(1)
    
    # 搜索
    all_results = []
    scopes = [s.strip() for s in args.scope.split(',')]
    
    scope_dirs = {
        'memory': MEMORY_DIR,
        'knowledge': KNOWLEDGE_DIR,
        'projects': PROJECTS_DIR,
    }
    
    for scope in scopes:
        if scope in scope_dirs:
            results = search_in_directory(
                scope_dirs[scope], 
                args.query, 
                from_date, 
                to_date
            )
            all_results.extend(results)
    
    # 按日期排序 (最新的在前)
    all_results.sort(key=lambda x: x['date'], reverse=True)
    
    # 输出
    format_results(all_results, args.query, args.page, args.page_size)


if __name__ == '__main__':
    main()
