#!/usr/bin/env python3
"""
obsidian_sync.py - Obsidian Vault 同步脚本
来源: 新媒体情报员_v1.0.docx - 知识库自动同步模块实用化改造
功能: 将 intelligence_collection_system.py 的采集结果同步到 Obsidian Vault 结构
创建时间: 2026-04-04
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class ObsidianSync:
    """
    Obsidian Vault 自动同步器
    实现文档中提出的:
    00-Inbox/ -> 01-Areas/ -> 03-Projects/ 的自动化流转
    """
    
    def __init__(
        self,
        vault_path: str = "/root/.openclaw/workspace/knowledge_base",
        intelligence_path: str = "/root/.openclaw/workspace/intelligence"
    ):
        self.vault_path = Path(vault_path)
        self.intelligence_path = Path(intelligence_path)
        
        # 创建标准 Vault 结构
        self.dirs = {
            "inbox": self.vault_path / "00-Inbox",
            "areas": {
                "social": self.vault_path / "01-Areas" / "新媒体情报",
                "academic": self.vault_path / "01-Areas" / "学术研究",
                "techfinance": self.vault_path / "01-Areas" / "财经科技",
                "cases": self.vault_path / "01-Areas" / "案例研究",
            },
            "resources": self.vault_path / "02-Resources",
            "projects": self.vault_path / "03-Projects",
        }
        
        for d in [self.dirs["inbox"], self.dirs["resources"], self.dirs["projects"]]:
            d.mkdir(parents=True, exist_ok=True)
        for d in self.dirs["areas"].values():
            d.mkdir(parents=True, exist_ok=True)
            
    def sync_intelligence_to_inbox(self, source_files: Optional[List[str]] = None):
        """
        将情报采集系统的输出复制到 00-Inbox
        """
        if source_files is None:
            # 自动发现 intelligence 目录下的 .md 和 .json 文件
            source_files = []
            if self.intelligence_path.exists():
                source_files.extend(self.intelligence_path.rglob("*.md"))
                source_files.extend(self.intelligence_path.rglob("*.json"))
        
        copied = []
        for src in source_files:
            src = Path(src)
            if not src.exists():
                continue
            dst = self.dirs["inbox"] / f"{src.stem}_{datetime.now().strftime('%Y%m%d')}{src.suffix}"
            shutil.copy2(src, dst)
            copied.append(str(dst))
            
        return copied
    
    def classify_from_inbox(self):
        """
        简单的分类逻辑:
        - 包含 arxiv/academic/paper 的 -> 学术研究
        - 包含 wechat/xiaohongshu/bilibili/douyin 的 -> 新媒体情报
        - 包含 36kr/techcrunch/finance 的 -> 财经科技
        - 包含 case/partner 的 -> 案例研究
        """
        classified = []
        for f in self.dirs["inbox"].glob("*.md"):
            content = f.read_text(encoding='utf-8').lower()
            
            target_dir = None
            if any(k in content for k in ['arxiv', 'paper', 'academic', '学术']):
                target_dir = self.dirs["areas"]["academic"]
            elif any(k in content for k in ['wechat', 'xiaohongshu', 'bilibili', 'douyin', '新媒体']):
                target_dir = self.dirs["areas"]["social"]
            elif any(k in content for k in ['36kr', 'techcrunch', 'finance', '财经', '融资']):
                target_dir = self.dirs["areas"]["techfinance"]
            elif any(k in content for k in ['case', 'partner', '合伙人', '案例']):
                target_dir = self.dirs["areas"]["cases"]
            else:
                target_dir = self.dirs["areas"]["techfinance"]  # 默认
                
            dst = target_dir / f.name
            shutil.move(str(f), str(dst))
            classified.append({
                'file': f.name,
                'target': str(target_dir)
            })
            
        return classified
    
    def generate_weekly_report(self) -> str:
        """生成每周周报模板（保存到 03-Projects）"""
        today = datetime.now()
        week_start = today - __import__('datetime').timedelta(days=today.weekday())
        
        lines = [
            f"# 情报周报 - {week_start.strftime('%Y年第%W周')}",
            f"**生成时间**: {today.strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 本周新增情报",
            ""
        ]
        
        for area_name, area_path in self.dirs["areas"].items():
            count = len(list(area_path.glob("*.md")))
            lines.append(f"- {area_name}: {count} 篇")
            
        lines.extend([
            "",
            "## 关键洞察",
            "- 待填写...",
            "",
            "## 行动项",
            "- [ ] 待填写...",
            ""
        ])
        
        content = "\n".join(lines)
        report_path = self.dirs["projects"] / f"weekly_report_{today.strftime('%Y%m%d')}.md"
        report_path.write_text(content, encoding='utf-8')
        
        return str(report_path)
    
    def run_sync_pipeline(self):
        """执行完整同步流水线"""
        print("[1/3] 同步情报到 Inbox...")
        copied = self.sync_intelligence_to_inbox()
        print(f"  复制了 {len(copied)} 个文件")
        
        print("[2/3] 从 Inbox 分类到 Areas...")
        classified = self.classify_from_inbox()
        print(f"  分类了 {len(classified)} 个文件")
        
        print("[3/3] 生成周报模板...")
        report_path = self.generate_weekly_report()
        print(f"  周报已生成: {report_path}")
        
        return {
            'copied': copied,
            'classified': classified,
            'weekly_report': report_path
        }


def main():
    sync = ObsidianSync()
    result = sync.run_sync_pipeline()
    print("\nObsidian Vault 同步完成。")
    print(f"- Inbox 文件数: {len(result['copied'])}")
    print(f"- 分类文件数: {len(result['classified'])}")
    print(f"- 周报路径: {result['weekly_report']}")


if __name__ == "__main__":
    main()
