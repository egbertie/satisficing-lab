#!/usr/bin/env python3
"""
academic_collector.py - 学术快讯采集器
来源: 新媒体情报员_v1.0.docx - 学术快讯模块实用化改造
功能: arXiv RSS + 学术文献追踪
创建时间: 2026-04-04
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import urllib.request
import urllib.error

@dataclass
class AcademicPaper:
    """学术文献项"""
    id: str
    title: str
    authors: str
    summary: str
    published: datetime
    updated: datetime
    primary_category: str
    link: str
    pdf_link: str = ""
    tags: List[str] = field(default_factory=list)
    relevance_score: float = 0.0

class AcademicCollector:
    """
    学术快讯采集器
    基于arXiv RSS/Atom API，Token友好设计
    """
    
    def __init__(self, query_keywords: Optional[List[str]] = None):
        self.query_keywords = query_keywords or [
            "partner selection", "venture capital", "decision making",
            "entrepreneurship", "hard technology", "intuition"
        ]
        self.source_name = "arXiv学术快讯"
        
    def fetch_arxiv(self, category: str = "cs.AI", max_results: int = 10) -> List[AcademicPaper]:
        """
        从arXiv获取最新论文摘要
        Token优化: 只读取摘要，不下载全文
        """
        papers = []
        try:
            # arXiv Atom API
            query = "+OR+".join([f"all:{kw.replace(' ', '%20')}" for kw in self.query_keywords])
            url = (
                f"http://export.arxiv.org/api/query?"
                f"search_query=cat:{category}+AND+({query})"
                f"&start=0&max_results={max_results}"
                f"&sortBy=submittedDate&sortOrder=descending"
            )
            
            with urllib.request.urlopen(url, timeout=15) as response:
                data = response.read().decode('utf-8')
                
            root = ET.fromstring(data)
            
            # arXiv Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper_id = entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else ""
                title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else ""
                summary = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ""
                published_str = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else ""
                updated_str = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else ""
                
                # Authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns)
                    if name is not None:
                        authors.append(name.text)
                
                # Category
                category_elem = entry.find('atom:category', ns)
                primary_cat = category_elem.get('term', 'cs.AI') if category_elem is not None else 'cs.AI'
                
                # Links
                pdf_link = ""
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf' or link.get('type') == 'application/pdf':
                        pdf_link = link.get('href', "")
                        break
                
                published = datetime.fromisoformat(published_str.replace('Z', '+00:00')) if published_str else datetime.now()
                updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00')) if updated_str else published
                
                paper = AcademicPaper(
                    id=paper_id.split('/abs/')[-1] if '/abs/' in paper_id else paper_id,
                    title=title,
                    authors=", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
                    summary=summary[:500] + "..." if len(summary) > 500 else summary,
                    published=published,
                    updated=updated,
                    primary_category=primary_cat,
                    link=paper_id,
                    pdf_link=pdf_link,
                    tags=[primary_cat]
                )
                papers.append(paper)
                
        except urllib.error.URLError as e:
            papers.append(AcademicPaper(
                id="error", title="arXiv连接失败", authors="System",
                summary=f"网络受限或arXiv API暂不可用: {e}",
                published=datetime.now(), updated=datetime.now(),
                primary_category="error", link=""
            ))
        except Exception as e:
            papers.append(AcademicPaper(
                id="error", title="解析异常", authors="System",
                summary=f"解析arXiv返回数据时出错: {e}",
                published=datetime.now(), updated=datetime.now(),
                primary_category="error", link=""
            ))
            
        return papers
    
    def generate_digest(self, papers: List[AcademicPaper], days_window: int = 7) -> str:
        """生成学术快讯简报（Markdown格式）"""
        from datetime import timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_window)
        recent = [p for p in papers if p.id != "error" and p.published >= cutoff]
        
        lines = [
            f"# 学术快讯 - {self.source_name}",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**追踪关键词**: {', '.join(self.query_keywords[:5])}...",
            f"**本周新论文**: {len(recent)} 篇",
            "",
            "---",
            ""
        ]
        
        for p in recent[:5]:
            lines.extend([
                f"## {p.title}",
                f"- **作者**: {p.authors}",
                f"- **分类**: {p.primary_category}",
                f"- **发布时间**: {p.published.strftime('%Y-%m-%d')}",
                f"- **链接**: {p.link}",
                f"- **摘要**: {p.summary}",
                ""
            ])
            
        if not recent:
            lines.append("*本周暂无匹配的新论文。*")
            
        return "\n".join(lines)


def main():
    collector = AcademicCollector()
    papers = collector.fetch_arxiv(max_results=10)
    digest = collector.generate_digest(papers)
    print(digest)


if __name__ == "__main__":
    main()
