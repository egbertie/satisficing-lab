#!/usr/bin/env python3
# kr36_collector.py - 36氪硬科技文章采集模块
# 来源: 文件1 - 项目情报采集系统.docx
# 功能: 36氪硬科技RSS+搜索混合采集
# 创建时间: 2026-04-04
# 版本: 1.0

import json
import re
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Article:
    """文章"""
    title: str
    url: str
    summary: str
    author: str
    publish_time: str
    tags: List[str]
    content: str = ""

class KR36Collector:
    """
    36氪硬科技文章采集器
    RSS + 搜索混合方案
    """
    
    RSS_URL = "https://36kr.com/feed"
    SEARCH_KEYWORDS = ['硬科技', '半导体', '芯片', 'AI', '生物医药', '新能源']
    
    def __init__(self):
        self.articles = []
    
    def fetch_rss(self) -> List[Article]:
        """获取RSS feed"""
        print(f"📡 获取RSS: {self.RSS_URL}")
        
        # 实际应调用kimi_fetch或feedparser
        # 返回解析后的文章列表
        return []
    
    def search_articles(self, keyword: str) -> List[Article]:
        """搜索关键词文章"""
        print(f"🔍 搜索: {keyword}")
        
        search_url = f"https://36kr.com/search/articles/{keyword}"
        # 调用browser访问搜索结果
        return []
    
    def filter_hardtech(self, articles: List[Article]) -> List[Article]:
        """筛选硬科技相关文章"""
        hardtech_keywords = [
            '硬科技', '半导体', '芯片', 'AI', '人工智能',
            '生物医药', '新能源', '新材料', '先进制造',
            '机器人', '自动驾驶', '传感器', '量子计算'
        ]
        
        filtered = []
        for article in articles:
            text = article.title + article.summary
            if any(kw in text for kw in hardtech_keywords):
                filtered.append(article)
        
        return filtered
    
    def generate_summary(self, article: Article) -> str:
        """生成3句话摘要"""
        # 简化实现：返回原文摘要
        return article.summary[:200]
    
    def collect(self, use_rss: bool = True, use_search: bool = True) -> List[Article]:
        """
        执行采集
        """
        all_articles = []
        
        if use_rss:
            print("\n📰 RSS采集")
            rss_articles = self.fetch_rss()
            all_articles.extend(rss_articles)
        
        if use_search:
            print("\n🔍 搜索采集")
            for keyword in self.SEARCH_KEYWORDS:
                search_results = self.search_articles(keyword)
                all_articles.extend(search_results)
        
        # 去重
        unique_articles = self._deduplicate(all_articles)
        
        # 筛选硬科技
        hardtech_articles = self.filter_hardtech(unique_articles)
        
        self.articles = hardtech_articles
        
        print(f"\n✅ 采集完成: {len(hardtech_articles)} 篇硬科技文章")
        return hardtech_articles
    
    def _deduplicate(self, articles: List[Article]) -> List[Article]:
        """去重"""
        seen_urls = set()
        unique = []
        
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique.append(article)
        
        return unique
    
    def save(self, filename: str = None):
        """保存到文件"""
        if not filename:
            filename = f"kr36_articles_{datetime.now().strftime('%Y%m%d')}.json"
        
        data = [
            {
                'title': a.title,
                'url': a.url,
                'summary': a.summary,
                'author': a.author,
                'time': a.publish_time,
                'tags': a.tags
            }
            for a in self.articles
        ]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已保存到: {filename}")

# 便捷函数
def collect_kr36_articles():
    """快速采集36氪文章"""
    collector = KR36Collector()
    return collector.collect()

if __name__ == '__main__':
    collect_kr36_articles()
