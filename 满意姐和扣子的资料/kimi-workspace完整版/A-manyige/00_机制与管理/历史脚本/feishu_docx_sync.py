#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown转飞书云文档同步工具
支持图片上传、断点续传、批量处理
"""

import hashlib
import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urlparse

from feishu_api_client import FeishuDriveAPI, FeishuConfig, FeishuAPIError, create_client

logger = logging.getLogger('feishu_docx_sync')


# Block类型映射
BLOCK_TYPE_MAP = {
    'heading1': 1,
    'heading2': 2,
    'heading3': 3,
    'text': 4,
    'bullet': 5,
    'ordered': 6,
    'code': 7,
    'quote': 8,
    'divider': 9,
    'image': 11,
    'table': 12,
    'callout': 13,
}


@dataclass
class SyncProgress:
    """同步进度记录"""
    document_id: str = ""
    markdown_file: str = ""
    current_line: int = 0
    total_lines: int = 0
    uploaded_images: Dict[str, str] = field(default_factory=dict)  # 本地路径 -> file_token
    block_ids: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    error_message: str = ""
    last_update: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'document_id': self.document_id,
            'markdown_file': self.markdown_file,
            'current_line': self.current_line,
            'total_lines': self.total_lines,
            'uploaded_images': self.uploaded_images,
            'block_ids': self.block_ids,
            'status': self.status,
            'error_message': self.error_message,
            'last_update': self.last_update
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncProgress':
        return cls(**data)
    
    def save(self, filepath: str):
        """保存进度到文件"""
        self.last_update = time.time()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> Optional['SyncProgress']:
        """从文件加载进度"""
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_dict(json.load(f))


class MarkdownParser:
    """Markdown解析器"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        
    def parse(self, content: str) -> Iterator[Dict[str, Any]]:
        """
        解析Markdown内容，生成文档块
        
        Yields:
            文档块字典
        """
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 空行跳过
            if not line.strip():
                i += 1
                continue
            
            # 代码块
            if line.strip().startswith('```'):
                block, i = self._parse_code_block(lines, i)
                yield block
                continue
            
            # 标题
            heading_match = re.match(r'^(#{1,3})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2).strip()
                yield {
                    'type': f'heading{level}',
                    'content': content
                }
                i += 1
                continue
            
            # 分割线
            if re.match(r'^-{3,}$', line.strip()) or re.match(r'^\*{3,}$', line.strip()):
                yield {'type': 'divider'}
                i += 1
                continue
            
            # 引用
            if line.strip().startswith('>'):
                block, i = self._parse_quote(lines, i)
                yield block
                continue
            
            # 无序列表
            if re.match(r'^[\s]*[-*+]\s+', line):
                block, i = self._parse_list(lines, i, 'bullet')
                yield block
                continue
            
            # 有序列表
            if re.match(r'^[\s]*\d+\.\s+', line):
                block, i = self._parse_list(lines, i, 'ordered')
                yield block
                continue
            
            # 图片
            image_match = re.match(r'^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$', line)
            if image_match:
                alt_text = image_match.group(1)
                image_path = image_match.group(2)
                yield {
                    'type': 'image',
                    'alt': alt_text,
                    'path': image_path
                }
                i += 1
                continue
            
            # 普通段落（处理行内格式）
            block, i = self._parse_paragraph(lines, i)
            yield block
    
    def _parse_code_block(self, lines: List[str], start: int) -> Tuple[Dict[str, Any], int]:
        """解析代码块"""
        first_line = lines[start]
        lang_match = re.match(r'```(\w*)', first_line.strip())
        language = lang_match.group(1) if lang_match else ""
        
        code_lines = []
        i = start + 1
        
        while i < len(lines):
            if lines[i].strip() == '```':
                i += 1
                break
            code_lines.append(lines[i])
            i += 1
        
        return {
            'type': 'code',
            'language': language,
            'content': '\n'.join(code_lines)
        }, i
    
    def _parse_quote(self, lines: List[str], start: int) -> Tuple[Dict[str, Any], int]:
        """解析引用块"""
        quote_lines = []
        i = start
        
        while i < len(lines):
            line = lines[i]
            if not line.strip().startswith('>'):
                break
            # 移除引用标记
            content = re.sub(r'^\s*>\s?', '', line)
            quote_lines.append(content)
            i += 1
        
        return {
            'type': 'quote',
            'content': '\n'.join(quote_lines)
        }, i
    
    def _parse_list(self, lines: List[str], start: int, list_type: str) -> Tuple[Dict[str, Any], int]:
        """解析列表"""
        items = []
        i = start
        
        while i < len(lines):
            line = lines[i]
            
            if list_type == 'bullet':
                match = re.match(r'^([\s]*)[-*+]\s+(.+)$', line)
            else:
                match = re.match(r'^([\s]*)\d+\.\s+(.+)$', line)
            
            if not match:
                break
            
            content = match.group(2)
            items.append(content)
            i += 1
        
        return {
            'type': list_type,
            'items': items
        }, i
    
    def _parse_paragraph(self, lines: List[str], start: int) -> Tuple[Dict[str, Any], int]:
        """解析段落，处理行内格式"""
        para_lines = []
        i = start
        
        while i < len(lines):
            line = lines[i]
            
            # 遇到空行或特殊块结束
            if not line.strip() or line.strip().startswith(('#', '>', '```', '-', '*', '+', '1.', '2.', '![')):
                break
            
            para_lines.append(line)
            i += 1
        
        content = ' '.join(para_lines)
        
        # 解析行内元素
        elements = self._parse_inline(content)
        
        return {
            'type': 'text',
            'content': content,
            'elements': elements
        }, i
    
    def _parse_inline(self, text: str) -> List[Dict[str, Any]]:
        """解析行内格式（粗体、斜体、链接等）"""
        elements = []
        
        # 处理加粗 **text** 或 __text__
        parts = re.split(r'(\*\*[^*]+\*\*|__[^_]+__)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                elements.append({
                    'type': 'text_run',
                    'content': part[2:-2],
                    'bold': True
                })
            elif part.startswith('__') and part.endswith('__'):
                elements.append({
                    'type': 'text_run',
                    'content': part[2:-2],
                    'bold': True
                })
            elif part:  # 普通文本
                elements.append({
                    'type': 'text_run',
                    'content': part
                })
        
        return elements if elements else [{'type': 'text_run', 'content': text}]


class DocxBlockBuilder:
    """文档块构建器 - 将解析后的数据转换为飞书API格式"""
    
    @staticmethod
    def build_block(block_data: Dict[str, Any], image_token: str = None) -> Optional[Dict[str, Any]]:
        """
        构建飞书文档块
        
        Args:
            block_data: 解析后的块数据
            image_token: 已上传图片的token
            
        Returns:
            飞书API格式的块数据
        """
        block_type = block_data.get('type')
        
        if block_type == 'heading1':
            return DocxBlockBuilder._build_heading(block_data, 1)
        elif block_type == 'heading2':
            return DocxBlockBuilder._build_heading(block_data, 2)
        elif block_type == 'heading3':
            return DocxBlockBuilder._build_heading(block_data, 3)
        elif block_type == 'text':
            return DocxBlockBuilder._build_text(block_data)
        elif block_type == 'bullet':
            return DocxBlockBuilder._build_list(block_data, 'bullet')
        elif block_type == 'ordered':
            return DocxBlockBuilder._build_list(block_data, 'ordered')
        elif block_type == 'code':
            return DocxBlockBuilder._build_code(block_data)
        elif block_type == 'quote':
            return DocxBlockBuilder._build_quote(block_data)
        elif block_type == 'divider':
            return DocxBlockBuilder._build_divider()
        elif block_type == 'image':
            return DocxBlockBuilder._build_image(block_data, image_token)
        
        return None
    
    @staticmethod
    def _build_heading(block_data: Dict, level: int) -> Dict:
        content = block_data.get('content', '')
        return {
            "block_type": BLOCK_TYPE_MAP[f'heading{level}'],
            f"heading{level}": {
                "elements": [{"text_run": {"content": content}}]
            }
        }
    
    @staticmethod
    def _build_text(block_data: Dict) -> Dict:
        elements = block_data.get('elements', [])
        text_elements = []
        
        for elem in elements:
            if elem['type'] == 'text_run':
                text_run = {"content": elem['content']}
                if elem.get('bold'):
                    text_run["text_style"] = {"bold": True}
                text_elements.append({"text_run": text_run})
        
        if not text_elements:
            text_elements = [{"text_run": {"content": block_data.get('content', '')}}]
        
        return {
            "block_type": BLOCK_TYPE_MAP['text'],
            "text": {"elements": text_elements}
        }
    
    @staticmethod
    def _build_list(block_data: Dict, list_type: str) -> Dict:
        items = block_data.get('items', [])
        children = []
        
        for item in items:
            children.append({
                "block_type": BLOCK_TYPE_MAP[list_type],
                list_type: {
                    "elements": [{"text_run": {"content": item}}]
                }
            })
        
        # 飞书API需要嵌套结构
        if children:
            return {
                "block_type": BLOCK_TYPE_MAP[list_type],
                list_type: {
                    "elements": [{"text_run": {"content": ""}}]
                },
                "children": children
            }
        return None
    
    @staticmethod
    def _build_code(block_data: Dict) -> Dict:
        content = block_data.get('content', '')
        language = block_data.get('language', '')
        
        return {
            "block_type": BLOCK_TYPE_MAP['code'],
            "code": {
                "elements": [{"text_run": {"content": content}}],
                "language": language or "plain"
            }
        }
    
    @staticmethod
    def _build_quote(block_data: Dict) -> Dict:
        content = block_data.get('content', '')
        return {
            "block_type": BLOCK_TYPE_MAP['quote'],
            "quote": {
                "elements": [{"text_run": {"content": content}}]
            }
        }
    
    @staticmethod
    def _build_divider() -> Dict:
        return {
            "block_type": BLOCK_TYPE_MAP['divider'],
            "divider": {}
        }
    
    @staticmethod
    def _build_image(block_data: Dict, image_token: str) -> Dict:
        if not image_token:
            # 没有图片token，转为文本提示
            alt = block_data.get('alt', '图片')
            return {
                "block_type": BLOCK_TYPE_MAP['text'],
                "text": {
                    "elements": [{"text_run": {"content": f"[图片: {alt}]"}}]
                }
            }
        
        return {
            "block_type": BLOCK_TYPE_MAP['image'],
            "image": {
                "token": image_token
            }
        }


class MarkdownToDocxSyncer:
    """Markdown到飞书文档同步器"""
    
    def __init__(self, client: FeishuDriveAPI, max_workers: int = 4):
        self.client = client
        self.max_workers = max_workers
        self.parser = MarkdownParser()
        self.block_builder = DocxBlockBuilder()
        
    def sync(self, 
             markdown_path: str, 
             document_id: str = None,
             title: str = None,
             folder_token: str = None,
             progress_file: str = None) -> Dict[str, Any]:
        """
        同步Markdown文件到飞书文档
        
        Args:
            markdown_path: Markdown文件路径
            document_id: 现有文档ID（可选，用于续传）
            title: 文档标题（可选，默认使用文件名）
            folder_token: 文件夹token（可选）
            progress_file: 进度文件路径（可选）
            
        Returns:
            同步结果
        """
        markdown_path = os.path.abspath(markdown_path)
        base_dir = os.path.dirname(markdown_path)
        
        # 确定进度文件路径
        if not progress_file:
            progress_file = f"{markdown_path}.feishu_progress.json"
        
        # 加载或创建进度
        progress = SyncProgress.load(progress_file)
        if progress and progress.status == "completed":
            logger.info(f"文档已同步完成: {progress.document_id}")
            return {"success": True, "document_id": progress.document_id, "message": "已完成"}
        
        if not progress:
            progress = SyncProgress(
                markdown_file=markdown_path,
                status="running"
            )
        else:
            progress.status = "running"
            progress.error_message = ""
        
        try:
            # 读取Markdown内容
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            progress.total_lines = len(lines)
            
            # 创建文档或验证现有文档
            if not document_id:
                doc_title = title or os.path.splitext(os.path.basename(markdown_path))[0]
                result = self.client.create_document(doc_title, folder_token)
                document_id = result['data']['document']['document_id']
                progress.document_id = document_id
                logger.info(f"创建文档成功: {document_id}")
            else:
                progress.document_id = document_id
                logger.info(f"使用现有文档: {document_id}")
            
            # 解析Markdown
            parser = MarkdownParser(base_dir)
            blocks = list(parser.parse(content))
            
            # 收集所有图片路径
            image_blocks = [(i, b) for i, b in enumerate(blocks) if b['type'] == 'image']
            
            # 并发上传图片
            if image_blocks:
                logger.info(f"发现 {len(image_blocks)} 张图片，开始上传...")
                self._upload_images_parallel(image_blocks, base_dir, progress)
            
            # 批量插入文档块
            self._insert_blocks_batch(document_id, blocks, progress, progress_file)
            
            # 更新状态为完成
            progress.status = "completed"
            progress.current_line = progress.total_lines
            progress.save(progress_file)
            
            return {
                "success": True,
                "document_id": document_id,
                "blocks_count": len(blocks),
                "images_count": len(image_blocks)
            }
            
        except Exception as e:
            progress.status = "failed"
            progress.error_message = str(e)
            progress.save(progress_file)
            logger.error(f"同步失败: {e}")
            raise
    
    def _upload_images_parallel(self, 
                               image_blocks: List[Tuple[int, Dict]], 
                               base_dir: str,
                               progress: SyncProgress):
        """并行上传图片"""
        
        def upload_single(item: Tuple[int, Dict]) -> Tuple[int, Optional[str]]:
            idx, block = item
            img_path = block['path']
            
            # 解析相对路径
            if not os.path.isabs(img_path):
                img_path = os.path.join(base_dir, img_path)
            
            img_path = os.path.abspath(img_path)
            
            # 检查是否已上传
            if img_path in progress.uploaded_images:
                return idx, progress.uploaded_images[img_path]
            
            # 检查文件是否存在
            if not os.path.exists(img_path):
                logger.warning(f"图片不存在: {img_path}")
                return idx, None
            
            try:
                result = self.client.upload_media(img_path, "image")
                file_token = result['data']['file_token']
                progress.uploaded_images[img_path] = file_token
                logger.info(f"图片上传成功: {img_path}")
                return idx, file_token
            except Exception as e:
                logger.error(f"图片上传失败 {img_path}: {e}")
                return idx, None
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(upload_single, item): item for item in image_blocks}
            
            for future in as_completed(futures):
                idx, token = future.result()
                if token:
                    progress.uploaded_images[image_blocks[idx][1]['path']] = token
    
    def _insert_blocks_batch(self, 
                            document_id: str, 
                            blocks: List[Dict],
                            progress: SyncProgress,
                            progress_file: str):
        """批量插入文档块"""
        
        batch_size = 50  # 每批最多50个块
        base_dir = os.path.dirname(progress.markdown_file)
        
        # 从断点继续
        start_idx = len(progress.block_ids)
        
        for i in range(start_idx, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            requests_data = []
            
            for block_data in batch:
                # 处理图片
                image_token = None
                if block_data['type'] == 'image':
                    img_path = block_data['path']
                    if not os.path.isabs(img_path):
                        img_path = os.path.join(base_dir, img_path)
                    img_path = os.path.abspath(img_path)
                    image_token = progress.uploaded_images.get(img_path)
                
                # 构建block
                feishu_block = self.block_builder.build_block(block_data, image_token)
                
                if feishu_block:
                    requests_data.append({
                        "insert_block": feishu_block
                    })
            
            if requests_data:
                try:
                    result = self.client.batch_update_blocks(document_id, requests_data)
                    
                    # 记录block ID
                    if 'data' in result and 'block_ids' in result['data']:
                        progress.block_ids.extend(result['data']['block_ids'])
                    
                    logger.info(f"已插入块 {i+1}/{len(blocks)}")
                    
                except Exception as e:
                    logger.error(f"插入块失败: {e}")
                    raise
            
            # 更新进度
            progress.current_line = min(i + batch_size, len(blocks))
            progress.save(progress_file)
            
            # 避免触发限流
            time.sleep(0.1)
    
    def batch_sync(self, 
                  markdown_files: List[str],
                  folder_token: str = None,
                  progress_dir: str = None) -> List[Dict[str, Any]]:
        """
        批量同步多个Markdown文件
        
        Args:
            markdown_files: Markdown文件路径列表
            folder_token: 文件夹token
            progress_dir: 进度文件保存目录
            
        Returns:
            每个文件的同步结果
        """
        results = []
        
        for md_file in markdown_files:
            logger.info(f"开始同步: {md_file}")
            
            progress_file = None
            if progress_dir:
                filename = os.path.basename(md_file)
                progress_file = os.path.join(progress_dir, f"{filename}.progress.json")
            
            try:
                result = self.sync(
                    markdown_path=md_file,
                    folder_token=folder_token,
                    progress_file=progress_file
                )
                results.append({"file": md_file, **result})
                
            except Exception as e:
                results.append({
                    "file": md_file,
                    "success": False,
                    "error": str(e)
                })
        
        return results


def sync_markdown_to_feishu(
    markdown_path: str,
    app_id: str = None,
    app_secret: str = None,
    config_path: str = None,
    document_id: str = None,
    title: str = None,
    folder_token: str = None,
    progress_file: str = None,
    max_workers: int = 4
) -> Dict[str, Any]:
    """
    便捷函数：同步Markdown到飞书文档
    
    Args:
        markdown_path: Markdown文件路径
        app_id: 飞书应用ID
        app_secret: 飞书应用密钥
        config_path: 配置文件路径
        document_id: 现有文档ID
        title: 文档标题
        folder_token: 文件夹token
        progress_file: 进度文件路径
        max_workers: 并发上传数
        
    Returns:
        同步结果
    """
    # 创建客户端
    if config_path:
        client = create_client(config_path)
    else:
        client = create_client(app_id=app_id, app_secret=app_secret)
    
    # 创建同步器
    syncer = MarkdownToDocxSyncer(client, max_workers=max_workers)
    
    # 执行同步
    return syncer.sync(
        markdown_path=markdown_path,
        document_id=document_id,
        title=title,
        folder_token=folder_token,
        progress_file=progress_file
    )


if __name__ == "__main__":
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("用法: python feishu_docx_sync.py <markdown文件> [config.json]")
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else "config/feishu_config.json"
    
    if not os.path.exists(markdown_file):
        print(f"错误: 文件不存在 {markdown_file}")
        sys.exit(1)
    
    if not os.path.exists(config_file):
        print(f"错误: 配置文件不存在 {config_file}")
        sys.exit(1)
    
    try:
        result = sync_markdown_to_feishu(
            markdown_path=markdown_file,
            config_path=config_file
        )
        print(f"\n同步成功!")
        print(f"文档ID: {result['document_id']}")
        print(f"块数量: {result['blocks_count']}")
    except Exception as e:
        print(f"\n同步失败: {e}")
        sys.exit(1)
