#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书云文档导入脚本

功能：
- 将本地 Markdown 文件转换为飞书可导入的格式
- 生成导入包供用户手动导入
- 作为权限受限时的保底方案

使用方法：
    python scripts/feishu_doc_import.py export ./notes --output ./feishu_export
    python scripts/feishu_doc_import.py preview ./notes/article.md

环境变量：
    FEISHU_APP_ID - 飞书应用 ID（可选，用于直接导入）
    FEISHU_APP_SECRET - 飞书应用密钥（可选）
"""

import os
import sys
import json
import re
import zipfile
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class FeishuDoc:
    """飞书文档结构"""
    title: str
    content: str  # HTML 格式
    markdown: str  # 原始 Markdown
    file_path: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MarkdownToFeishuConverter:
    """Markdown 转飞书文档格式"""
    
    def __init__(self):
        self.image_refs = []  # 记录引用的图片
    
    def convert(self, markdown_content: str, title: str = None) -> FeishuDoc:
        """将 Markdown 转换为飞书文档格式"""
        # 提取标题
        if not title:
            title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
            title = title_match.group(1) if title_match else "未命名文档"
        
        # 转换为 HTML（飞书支持 HTML 导入）
        html_content = self._markdown_to_html(markdown_content)
        
        return FeishuDoc(
            title=title,
            content=html_content,
            markdown=markdown_content
        )
    
    def _markdown_to_html(self, md: str) -> str:
        """简单的 Markdown 转 HTML"""
        import html
        
        html_content = md
        
        # 转义 HTML 特殊字符
        # 但保留代码块
        def escape_outside_code(text):
            # 先处理代码块
            parts = re.split(r'(```[\s\S]*?```)', text)
            result = []
            for i, part in enumerate(parts):
                if i % 2 == 0:  # 非代码块
                    result.append(html.escape(part))
                else:  # 代码块
                    result.append(part)
            return ''.join(result)
        
        # 标题
        html_content = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # 粗体和斜体
        html_content = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html_content)
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
        html_content = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', html_content)
        html_content = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'_(.+?)_', r'<em>\1</em>', html_content)
        
        # 代码块
        def code_block_replacer(match):
            lang = match.group(1) or ""
            code = html.escape(match.group(2))
            return f'<pre><code class="language-{lang}">{code}</code></pre>'
        
        html_content = re.sub(r'```(\w*)?\n(.*?)```', code_block_replacer, html_content, flags=re.DOTALL)
        
        # 行内代码
        html_content = re.sub(r'`([^`]+)`', lambda m: f'<code>{html.escape(m.group(1))}</code>', html_content)
        
        # 引用块
        def blockquote_replacer(match):
            content = match.group(1)
            content = re.sub(r'^>\s?', '', content, flags=re.MULTILINE)
            return f'<blockquote>{content}</blockquote>'
        
        html_content = re.sub(r'(^>.*(?:\n^>.*)*)', blockquote_replacer, html_content, flags=re.MULTILINE)
        
        # 列表
        html_content = self._convert_lists(html_content)
        
        # 链接
        html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
        
        # 图片
        def image_replacer(match):
            alt = match.group(1)
            src = match.group(2)
            self.image_refs.append(src)
            return f'<img src="{src}" alt="{alt}" />'
        
        html_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', image_replacer, html_content)
        
        # 水平线
        html_content = re.sub(r'^---+$', '<hr>', html_content, flags=re.MULTILINE)
        
        # 表格
        html_content = self._convert_tables(html_content)
        
        # 段落
        paragraphs = html_content.split('\n\n')
        new_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<') and not p.startswith('```'):
                p = f'<p>{p}</p>'
            new_paragraphs.append(p)
        
        html_content = '\n\n'.join(new_paragraphs)
        
        # 清理多余的换行
        html_content = re.sub(r'\n+', '\n', html_content)
        
        return html_content
    
    def _convert_lists(self, html_content: str) -> str:
        """转换列表"""
        lines = html_content.split('\n')
        result = []
        in_ul = False
        in_ol = False
        
        for line in lines:
            ul_match = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
            ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
            
            if ul_match:
                content = ul_match.group(2)
                if not in_ul:
                    if in_ol:
                        result.append('</ol>')
                        in_ol = False
                    result.append('<ul>')
                    in_ul = True
                result.append(f'<li>{content}</li>')
            elif ol_match:
                content = ol_match.group(2)
                if not in_ol:
                    if in_ul:
                        result.append('</ul>')
                        in_ul = False
                    result.append('<ol>')
                    in_ol = True
                result.append(f'<li>{content}</li>')
            else:
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append(line)
        
        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')
        
        return '\n'.join(result)
    
    def _convert_tables(self, html_content: str) -> str:
        """转换 Markdown 表格为 HTML 表格"""
        lines = html_content.split('\n')
        result = []
        in_table = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 检测表格分隔行
            if re.match(r'^(\|[-:]+)+\|$', line.strip()):
                i += 1
                continue
            
            # 检测表格行
            if line.strip().startswith('|') and line.strip().endswith('|'):
                if not in_table:
                    result.append('<table>')
                    in_table = True
                
                cells = [c.strip() for c in line.strip()[1:-1].split('|')]
                row = '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'
                result.append(row)
            else:
                if in_table:
                    result.append('</table>')
                    in_table = False
                result.append(line)
            
            i += 1
        
        if in_table:
            result.append('</table>')
        
        return '\n'.join(result)


class FeishuDocImporter:
    """飞书文档导入器"""
    
    def __init__(self):
        self.converter = MarkdownToFeishuConverter()
    
    def export_single(self, md_file: Path) -> FeishuDoc:
        """导出单个 Markdown 文件"""
        content = md_file.read_text(encoding='utf-8')
        return self.converter.convert(content, md_file.stem)
    
    def export_directory(self, source_dir: Path, output_dir: Path) -> Dict:
        """
        导出整个目录为飞书导入格式
        
        Returns:
            导出统计信息
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建 HTML 导出目录
        html_dir = output_dir / "html"
        html_dir.mkdir(exist_ok=True)
        
        # 创建 Markdown 备份目录
        md_backup_dir = output_dir / "markdown"
        md_backup_dir.mkdir(exist_ok=True)
        
        # 扫描文件
        md_files = list(source_dir.rglob("*.md"))
        print(f"📂 找到 {len(md_files)} 个 Markdown 文件")
        
        exported = []
        errors = []
        
        for md_file in md_files:
            try:
                doc = self.export_single(md_file)
                
                # 计算相对路径
                rel_path = md_file.relative_to(source_dir)
                
                # 生成安全文件名
                safe_name = re.sub(r'[^\w\u4e00-\u9fa5-]', '_', doc.title)
                
                # 保存 HTML 版本（飞书可直接导入）
                html_path = html_dir / f"{safe_name}.html"
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{doc.title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ border-bottom: 2px solid #3370ff; padding-bottom: 10px; }}
        h2 {{ border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
        pre {{ background: #f8f8f8; padding: 16px; border-radius: 6px; overflow-x: auto; }}
        pre code {{ background: none; padding: 0; }}
        blockquote {{ border-left: 4px solid #3370ff; margin: 0; padding-left: 16px; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f5f5f5; }}
        img {{ max-width: 100%; }}
    </style>
</head>
<body>
{doc.content}
</body>
</html>"""
                html_path.write_text(html_content, encoding='utf-8')
                
                # 保存原始 Markdown
                md_backup_path = md_backup_dir / f"{safe_name}.md"
                md_backup_path.write_text(doc.markdown, encoding='utf-8')
                
                exported.append({
                    "title": doc.title,
                    "original": str(rel_path),
                    "html": str(html_path.relative_to(output_dir)),
                    "markdown": str(md_backup_path.relative_to(output_dir))
                })
                print(f"   ✅ {doc.title}")
                
            except Exception as e:
                print(f"   ❌ 错误: {md_file} - {e}")
                errors.append(f"{md_file}: {e}")
        
        # 生成索引文件
        index = {
            "export_time": datetime.now().isoformat(),
            "source_directory": str(source_dir),
            "total_files": len(md_files),
            "exported": len(exported),
            "errors": len(errors),
            "documents": exported
        }
        
        index_path = output_dir / "index.json"
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # 生成导入指南
        guide_path = output_dir / "导入指南.txt"
        guide_content = f"""飞书文档导入指南
================

导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
文件总数：{len(md_files)}
成功导出：{len(exported)}

目录结构：
- html/         HTML 格式文件（飞书可直接导入）
- markdown/     Markdown 原始文件（备份）
- index.json    导出索引

导入步骤：
==========

方法1：飞书网页版导入（推荐）
---------------------------
1. 打开飞书网页版：https://www.feishu.cn/
2. 进入「云文档」
3. 点击「新建」→「导入为在线文档」
4. 选择 html/ 目录下的 .html 文件
5. 等待导入完成

方法2：飞书客户端导入
-------------------
1. 打开飞书桌面客户端
2. 进入「云文档」
3. 点击右上角「...」→「导入」
4. 选择 html/ 目录下的文件
5. 确认导入

注意事项：
==========
- 图片需要手动重新上传（如需要）
- 复杂格式可能需要微调
- 建议导入后检查格式

文档列表：
==========
"""
        for doc in exported:
            guide_content += f"\n📄 {doc['title']}\n   原文件: {doc['original']}\n"
        
        guide_path.write_text(guide_content, encoding='utf-8')
        
        return index
    
    def create_import_package(self, source_dir: Path, output_file: Path) -> Path:
        """
        创建 ZIP 导入包
        
        Args:
            source_dir: 要打包的目录
            output_file: 输出 ZIP 文件路径
        
        Returns:
            ZIP 文件路径
        """
        output_file = Path(output_file)
        
        # 先导出到临时目录
        temp_dir = output_file.parent / f".temp_export_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            self.export_directory(source_dir, temp_dir)
            
            # 创建 ZIP
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zf.write(file_path, arcname)
            
            print(f"\n📦 导入包已创建: {output_file}")
            print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")
            
            return output_file
            
        finally:
            # 清理临时目录
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def preview(self, md_file: Path) -> None:
        """预览转换结果"""
        doc = self.export_single(md_file)
        
        print(f"\n📄 文档: {doc.title}")
        print("=" * 50)
        print("\n📝 HTML 预览（前 1000 字符）:")
        print("-" * 50)
        print(doc.content[:1000] + "..." if len(doc.content) > 1000 else doc.content)
        print("-" * 50)
        
        # 统计信息
        word_count = len(doc.markdown)
        line_count = doc.markdown.count('\n') + 1
        
        print(f"\n📊 统计:")
        print(f"   字符数: {word_count}")
        print(f"   行数: {line_count}")
        print(f"   图片引用: {len(self.converter.image_refs)}")


def main():
    parser = argparse.ArgumentParser(
        description="飞书文档导入工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览单个文件
  python scripts/feishu_doc_import.py preview ./article.md
  
  # 导出目录
  python scripts/feishu_doc_import.py export ./notes --output ./feishu_export
  
  # 创建 ZIP 导入包
  python scripts/feishu_doc_import.py package ./notes --output ./feishu_export.zip
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # preview 命令
    preview_parser = subparsers.add_parser("preview", help="预览转换结果")
    preview_parser.add_argument("file", help="Markdown 文件路径")
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出目录")
    export_parser.add_argument("source", help="源 Markdown 目录")
    export_parser.add_argument("--output", "-o", default="./feishu_export", 
                               help="输出目录 (默认: ./feishu_export)")
    
    # package 命令
    package_parser = subparsers.add_parser("package", help="创建 ZIP 导入包")
    package_parser.add_argument("source", help="源 Markdown 目录")
    package_parser.add_argument("--output", "-o", default="./feishu_export.zip", 
                               help="输出 ZIP 文件路径 (默认: ./feishu_export.zip)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        importer = FeishuDocImporter()
        
        if args.command == "preview":
            importer.preview(Path(args.file))
        
        elif args.command == "export":
            stats = importer.export_directory(Path(args.source), Path(args.output))
            print(f"\n✅ 导出完成!")
            print(f"   总计: {stats['total_files']}")
            print(f"   成功: {stats['exported']}")
            print(f"   失败: {stats['errors']}")
            print(f"\n📂 导出位置: {args.output}")
            print(f"\n下一步:")
            print(f"   1. 打开 {args.output}/导入指南.txt 查看详细说明")
            print(f"   2. 将 {args.output}/html/ 中的文件导入飞书")
        
        elif args.command == "package":
            importer.create_import_package(Path(args.source), Path(args.output))
            print(f"\n✅ 导入包已创建!")
            print(f"\n下一步:")
            print(f"   1. 解压 {args.output}")
            print(f"   2. 查看导入指南.txt")
            print(f"   3. 将 html/ 中的文件导入飞书")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
