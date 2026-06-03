#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书多维表格同步脚本

功能：
- 将本地 Markdown 文件同步到飞书多维表格（Bitable）
- 支持双向同步（本地 → 飞书 / 飞书 → 本地）
- 适合结构化知识管理

使用方法：
    python scripts/feishu_bitable_sync.py --mode push --source ./notes --table_url "https://..."
    python scripts/feishu_bitable_sync.py --mode pull --target ./backup --table_url "https://..."

环境变量：
    FEISHU_APP_ID - 飞书应用 ID
    FEISHU_APP_SECRET - 飞书应用密钥
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class NoteRecord:
    """笔记记录数据结构"""
    title: str
    content: str
    tags: List[str]
    category: str
    created_at: str
    updated_at: str
    source_file: Optional[str] = None


class FeishuBitableSync:
    """飞书多维表格同步器"""
    
    # 标准字段映射
    FIELD_MAPPING = {
        "标题": "title",
        "内容": "content",
        "标签": "tags",
        "分类": "category",
        "创建时间": "created_at",
        "更新时间": "updated_at",
        "来源文件": "source_file"
    }
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        self.access_token = None
        
        if not self.app_id or not self.app_secret:
            raise ValueError("缺少飞书应用凭证，请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
    
    def _get_access_token(self) -> str:
        """获取飞书 tenant_access_token"""
        import requests
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            result = resp.json()
            
            if result.get("code") == 0:
                self.access_token = result["tenant_access_token"]
                return self.access_token
            else:
                raise Exception(f"获取 token 失败: {result}")
        except Exception as e:
            raise Exception(f"获取 access_token 失败: {e}")
    
    def _parse_bitable_url(self, url: str) -> Tuple[str, str]:
        """解析飞书多维表格 URL，获取 app_token 和 table_id"""
        # 支持格式：
        # https://xxx.feishu.cn/base/APP_TOKEN?table=TABLE_ID
        # https://xxx.feishu.cn/wiki/WIKI_TOKEN?table=TABLE_ID
        
        patterns = [
            r'/base/([a-zA-Z0-9]+).*?[?&]table=([a-zA-Z0-9]+)',
            r'/wiki/([a-zA-Z0-9]+).*?[?&]table=([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2)
        
        raise ValueError(f"无法解析多维表格 URL: {url}")
    
    def _get_headers(self) -> Dict:
        """获取请求头"""
        if not self.access_token:
            self._get_access_token()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def list_records(self, app_token: str, table_id: str, page_size: int = 500) -> List[Dict]:
        """获取多维表格中的所有记录"""
        import requests
        
        records = []
        page_token = None
        
        while True:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            params = {"page_size": min(page_size, 500)}
            if page_token:
                params["page_token"] = page_token
            
            try:
                resp = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
                result = resp.json()
                
                if result.get("code") != 0:
                    raise Exception(f"获取记录失败: {result}")
                
                items = result["data"]["items"]
                records.extend(items)
                
                if not result["data"].get("has_more"):
                    break
                page_token = result["data"]["page_token"]
                
            except Exception as e:
                raise Exception(f"获取记录失败: {e}")
        
        return records
    
    def create_record(self, app_token: str, table_id: str, fields: Dict) -> Dict:
        """创建新记录"""
        import requests
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        data = {"fields": fields}
        
        try:
            resp = requests.post(url, headers=self._get_headers(), json=data, timeout=30)
            result = resp.json()
            
            if result.get("code") != 0:
                raise Exception(f"创建记录失败: {result}")
            return result["data"]
        except Exception as e:
            raise Exception(f"创建记录失败: {e}")
    
    def update_record(self, app_token: str, table_id: str, record_id: str, fields: Dict) -> Dict:
        """更新现有记录"""
        import requests
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        data = {"fields": fields}
        
        try:
            resp = requests.put(url, headers=self._get_headers(), json=data, timeout=30)
            result = resp.json()
            
            if result.get("code") != 0:
                raise Exception(f"更新记录失败: {result}")
            return result["data"]
        except Exception as e:
            raise Exception(f"更新记录失败: {e}")
    
    def delete_record(self, app_token: str, table_id: str, record_id: str) -> None:
        """删除记录"""
        import requests
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        
        try:
            resp = requests.delete(url, headers=self._get_headers(), timeout=30)
            result = resp.json()
            
            if result.get("code") != 0:
                raise Exception(f"删除记录失败: {result}")
        except Exception as e:
            raise Exception(f"删除记录失败: {e}")
    
    def parse_markdown_file(self, file_path: Path) -> NoteRecord:
        """解析 Markdown 文件，提取元数据"""
        content = file_path.read_text(encoding='utf-8')
        
        # 提取标题（第一个 # 开头的行）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        # 提取 YAML frontmatter（如果有）
        frontmatter = {}
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if fm_match:
            try:
                import yaml
                frontmatter = yaml.safe_load(fm_match.group(1)) or {}
            except ImportError:
                pass
        
        # 获取文件时间
        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
        updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # 提取标签（从 frontmatter 或内容中的 #标签）
        tags = frontmatter.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]
        
        if not tags:
            # 从内容中提取 #标签 格式
            tags = re.findall(r'#(\w+)', content)
        
        # 分类（从 frontmatter 或文件夹名）
        category = frontmatter.get('category', file_path.parent.name)
        
        return NoteRecord(
            title=title,
            content=content,
            tags=tags,
            category=category,
            created_at=created_at,
            updated_at=updated_at,
            source_file=str(file_path.relative_to(PROJECT_ROOT))
        )
    
    def record_to_fields(self, record: NoteRecord) -> Dict:
        """将 NoteRecord 转换为多维表格字段格式"""
        return {
            "标题": record.title,
            "内容": record.content[:100000],  # 飞书有字段长度限制
            "标签": ", ".join(record.tags) if record.tags else "",
            "分类": record.category,
            "创建时间": int(datetime.fromisoformat(record.created_at).timestamp() * 1000),
            "更新时间": int(datetime.fromisoformat(record.updated_at).timestamp() * 1000),
            "来源文件": record.source_file or ""
        }
    
    def fields_to_record(self, fields: Dict) -> NoteRecord:
        """将多维表格字段转换为 NoteRecord"""
        # 处理时间戳
        created_at = fields.get("创建时间", datetime.now().timestamp() * 1000)
        updated_at = fields.get("更新时间", datetime.now().timestamp() * 1000)
        
        if isinstance(created_at, (int, float)):
            created_at = datetime.fromtimestamp(created_at / 1000).isoformat()
        if isinstance(updated_at, (int, float)):
            updated_at = datetime.fromtimestamp(updated_at / 1000).isoformat()
        
        # 处理标签
        tags_str = fields.get("标签", "")
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
        return NoteRecord(
            title=fields.get("标题", ""),
            content=fields.get("内容", ""),
            tags=tags,
            category=fields.get("分类", ""),
            created_at=created_at,
            updated_at=updated_at,
            source_file=fields.get("来源文件", "")
        )
    
    def push_to_bitable(self, source_dir: Path, table_url: str, dry_run: bool = False) -> Dict:
        """
        将本地 Markdown 文件推送到飞书多维表格
        
        Args:
            source_dir: 本地笔记目录
            table_url: 多维表格 URL
            dry_run: 仅预览，不实际执行
        
        Returns:
            同步统计信息
        """
        app_token, table_id = self._parse_bitable_url(table_url)
        
        # 获取现有记录
        print(f"📥 获取现有记录...")
        existing_records = self.list_records(app_token, table_id)
        
        # 建立标题到记录的映射
        title_to_record = {}
        for rec in existing_records:
            title = rec.get("fields", {}).get("标题", "")
            if title:
                title_to_record[title] = rec
        
        # 扫描本地文件
        print(f"📂 扫描本地文件: {source_dir}")
        md_files = list(source_dir.rglob("*.md"))
        print(f"   找到 {len(md_files)} 个 Markdown 文件")
        
        stats = {"created": 0, "updated": 0, "unchanged": 0, "errors": []}
        
        for file_path in md_files:
            try:
                record = self.parse_markdown_file(file_path)
                fields = self.record_to_fields(record)
                
                existing = title_to_record.get(record.title)
                
                if dry_run:
                    action = "更新" if existing else "创建"
                    print(f"   [预览] {action}: {record.title}")
                    continue
                
                if existing:
                    # 检查是否需要更新
                    existing_updated = existing["fields"].get("更新时间", 0)
                    local_updated = int(datetime.fromisoformat(record.updated_at).timestamp() * 1000)
                    
                    if isinstance(existing_updated, dict):
                        existing_updated = existing_updated.get("value", 0)
                    
                    if local_updated > existing_updated:
                        self.update_record(app_token, table_id, existing["record_id"], fields)
                        print(f"   ✅ 更新: {record.title}")
                        stats["updated"] += 1
                    else:
                        print(f"   ⏭️  跳过: {record.title} (未变更)")
                        stats["unchanged"] += 1
                else:
                    self.create_record(app_token, table_id, fields)
                    print(f"   ✅ 创建: {record.title}")
                    stats["created"] += 1
                    
            except Exception as e:
                print(f"   ❌ 错误: {file_path} - {e}")
                stats["errors"].append(f"{file_path}: {e}")
        
        return stats
    
    def pull_from_bitable(self, table_url: str, target_dir: Path, dry_run: bool = False) -> Dict:
        """
        从飞书多维表格拉取到本地
        
        Args:
            table_url: 多维表格 URL
            target_dir: 目标本地目录
            dry_run: 仅预览，不实际执行
        
        Returns:
            同步统计信息
        """
        app_token, table_id = self._parse_bitable_url(table_url)
        
        # 获取所有记录
        print(f"📥 获取多维表格记录...")
        records = self.list_records(app_token, table_id)
        print(f"   找到 {len(records)} 条记录")
        
        stats = {"created": 0, "updated": 0, "unchanged": 0, "errors": []}
        
        for rec in records:
            try:
                fields = rec.get("fields", {})
                record = self.fields_to_record(fields)
                
                if not record.title:
                    continue
                
                # 确定文件路径
                if record.source_file:
                    file_path = target_dir / record.source_file
                else:
                    # 根据分类创建子目录
                    category_dir = target_dir / (record.category or "uncategorized")
                    safe_title = re.sub(r'[^\w\u4e00-\u9fa5-]', '_', record.title)
                    file_path = category_dir / f"{safe_title}.md"
                
                if dry_run:
                    exists = "更新" if file_path.exists() else "创建"
                    print(f"   [预览] {exists}: {file_path}")
                    continue
                
                # 确保目录存在
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 写入文件
                file_path.write_text(record.content, encoding='utf-8')
                
                # 更新时间戳
                if record.updated_at:
                    try:
                        mtime = datetime.fromisoformat(record.updated_at).timestamp()
                        os.utime(file_path, (mtime, mtime))
                    except:
                        pass
                
                if file_path.exists():
                    print(f"   ✅ 更新: {file_path}")
                    stats["updated"] += 1
                else:
                    print(f"   ✅ 创建: {file_path}")
                    stats["created"] += 1
                    
            except Exception as e:
                print(f"   ❌ 错误: {e}")
                stats["errors"].append(str(e))
        
        return stats
    
    def sync_bidirectional(self, source_dir: Path, table_url: str, 
                          conflict_resolution: str = "newer") -> Dict:
        """
        双向同步（实验性功能）
        
        Args:
            source_dir: 本地笔记目录
            table_url: 多维表格 URL
            conflict_resolution: 冲突解决策略 (newer/ local/ remote)
        """
        # 先 pull 再 push，根据时间戳合并
        print("🔄 双向同步模式")
        print("   注意：此功能为实验性，建议先备份数据")
        
        # TODO: 实现完整的双向同步逻辑
        # 目前简单实现：先 pull 到临时目录，再 push
        
        return self.push_to_bitable(source_dir, table_url)


def main():
    parser = argparse.ArgumentParser(
        description="飞书多维表格同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 推送本地笔记到多维表格
  python scripts/feishu_bitable_sync.py push ./notes "https://xxx.feishu.cn/base/XXX?table=YYY"
  
  # 从多维表格拉取到本地
  python scripts/feishu_bitable_sync.py pull "https://xxx.feishu.cn/base/XXX?table=YYY" ./backup
  
  # 预览模式（不实际执行）
  python scripts/feishu_bitable_sync.py push ./notes "URL" --dry-run
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # push 命令
    push_parser = subparsers.add_parser("push", help="推送本地文件到多维表格")
    push_parser.add_argument("source", help="本地笔记目录路径")
    push_parser.add_argument("table_url", help="飞书多维表格 URL")
    push_parser.add_argument("--dry-run", action="store_true", help="仅预览，不执行")
    
    # pull 命令
    pull_parser = subparsers.add_parser("pull", help="从多维表格拉取到本地")
    pull_parser.add_argument("table_url", help="飞书多维表格 URL")
    pull_parser.add_argument("target", help="目标本地目录路径")
    pull_parser.add_argument("--dry-run", action="store_true", help="仅预览，不执行")
    
    # sync 命令
    sync_parser = subparsers.add_parser("sync", help="双向同步（实验性）")
    sync_parser.add_argument("source", help="本地笔记目录路径")
    sync_parser.add_argument("table_url", help="飞书多维表格 URL")
    sync_parser.add_argument("--conflict", choices=["newer", "local", "remote"], 
                            default="newer", help="冲突解决策略")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        sync = FeishuBitableSync()
        
        if args.command == "push":
            stats = sync.push_to_bitable(Path(args.source), args.table_url, args.dry_run)
            print(f"\n📊 同步结果:")
            print(f"   创建: {stats['created']}")
            print(f"   更新: {stats['updated']}")
            print(f"   跳过: {stats['unchanged']}")
            if stats['errors']:
                print(f"   错误: {len(stats['errors'])}")
        
        elif args.command == "pull":
            stats = sync.pull_from_bitable(args.table_url, Path(args.target), args.dry_run)
            print(f"\n📊 同步结果:")
            print(f"   创建: {stats['created']}")
            print(f"   更新: {stats['updated']}")
            if stats['errors']:
                print(f"   错误: {len(stats['errors'])}")
        
        elif args.command == "sync":
            stats = sync.sync_bidirectional(Path(args.source), args.table_url, args.conflict)
            print(f"\n📊 同步完成")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
