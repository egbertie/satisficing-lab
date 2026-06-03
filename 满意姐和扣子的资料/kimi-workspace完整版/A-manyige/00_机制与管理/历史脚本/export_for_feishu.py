#!/usr/bin/env python3
"""
导出Markdown为飞书可导入的HTML
"""

import os
import markdown
import argparse
from pathlib import Path

def md_to_html(md_content, title=""):
    """Markdown转HTML（飞书兼容格式）"""
    
    # 飞书兼容的HTML模板
    html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; padding: 40px; max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #1f2329; border-bottom: 2px solid #3370ff; padding-bottom: 10px; }}
        h2 {{ color: #1f2329; margin-top: 30px; }}
        h3 {{ color: #3370ff; }}
        code {{ background: #f5f6f7; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
        pre {{ background: #f5f6f7; padding: 16px; border-radius: 6px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #3370ff; margin: 0; padding-left: 16px; color: #646a73; }}
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        th, td {{ border: 1px solid #dee0e3; padding: 8px 12px; text-align: left; }}
        th {{ background: #f5f6f7; font-weight: 600; }}
        ul, ol {{ padding-left: 24px; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    # Markdown转HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc']
    )
    
    return html_template.format(title=title, content=html_content)

def export_single_file(md_path, output_dir):
    """导出单个Markdown文件"""
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    title = Path(md_path).stem
    html = md_to_html(md_content, title)
    
    # 生成输出文件名
    output_name = f"{title}.html"
    output_path = os.path.join(output_dir, output_name)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 导出: {md_path} → {output_path}")
    return output_path

def export_directory(input_dir, output_dir):
    """导出整个目录"""
    
    os.makedirs(output_dir, exist_ok=True)
    exported_files = []
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                
                # 保持目录结构
                rel_path = os.path.relpath(root, input_dir)
                sub_output_dir = os.path.join(output_dir, rel_path)
                os.makedirs(sub_output_dir, exist_ok=True)
                
                output_path = export_single_file(md_path, sub_output_dir)
                exported_files.append(output_path)
    
    return exported_files

def main():
    parser = argparse.ArgumentParser(description='导出Markdown为飞书HTML')
    parser.add_argument('input', help='输入文件或目录')
    parser.add_argument('--output', '-o', default='./feishu_export', help='输出目录')
    
    args = parser.parse_args()
    
    print("="*60)
    print("Markdown导出为飞书HTML")
    print("="*60)
    
    if os.path.isfile(args.input):
        export_single_file(args.input, args.output)
    elif os.path.isdir(args.input):
        files = export_directory(args.input, args.output)
        print(f"\n✅ 共导出 {len(files)} 个文件")
    else:
        print(f"❌ 路径不存在: {args.input}")
        return 1
    
    print(f"\n输出目录: {os.path.abspath(args.output)}")
    print("\n导入方法:")
    print("1. 打开飞书云文档")
    print("2. 点击'新建' → '导入文档'")
    print("3. 选择导出的HTML文件")
    print("4. 点击'导入'")
    
    return 0

if __name__ == '__main__':
    exit(main())
