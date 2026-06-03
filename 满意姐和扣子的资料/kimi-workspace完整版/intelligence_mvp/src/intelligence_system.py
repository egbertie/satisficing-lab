#!/usr/bin/env python3
"""
项目情报采集系统 - MVP版本
基于项目情报采集系统技术方案实施
"""

import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import time

# 可选依赖
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("⚠️  feedparser未安装，RSS功能将使用简化实现")

class ProjectIntelligenceSystem:
    """项目情报采集系统"""
    
    def __init__(self, db_path: str = "data/intelligence.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """初始化数据库"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建情报表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT,
                content TEXT,
                summary TEXT,
                tags TEXT,
                publish_date TEXT,
                collect_date TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new',
                feishu_sent BOOLEAN DEFAULT 0
            )
        ''')
        
        # 创建数据源配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                url TEXT,
                config TEXT,
                status TEXT DEFAULT 'active',
                last_collect TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_data_source(self, name: str, source_type: str, url: str, config: Dict = None):
        """添加数据源"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO data_sources (name, type, url, config)
                VALUES (?, ?, ?, ?)
            ''', (name, source_type, url, json.dumps(config) if config else '{}'))
            conn.commit()
            print(f"✅ 数据源 '{name}' 添加成功")
        except Exception as e:
            print(f"❌ 添加数据源失败: {e}")
        finally:
            conn.close()
    
    def collect_from_rss(self, source_name: str, rss_url: str) -> List[Dict]:
        """
        从RSS源采集数据
        支持：36氪、IT桔子等提供RSS的源
        """
        print(f"\n{'='*70}")
        print(f"📡 从RSS采集: {source_name}")
        print(f"{'='*70}")
        
        # 简化版：如果feedparser不可用，返回模拟数据
        if not FEEDPARSER_AVAILABLE:
            print("⚠️  feedparser未安装，使用模拟数据演示")
            mock_data = [
                {
                    'source': source_name,
                    'title': f'[{source_name}] 某硬科技项目获得A轮融资',
                    'url': 'https://example.com/news/1',
                    'content': '这是一家专注于AI芯片研发的创业公司，本轮融资1亿元...',
                    'publish_date': '2026-04-04',
                    'tags': '融资,AI芯片'
                },
                {
                    'source': source_name,
                    'title': f'[{source_name}] 新材料领域重大突破',
                    'url': 'https://example.com/news/2',
                    'content': '某研究团队在新材料领域取得重大突破，已实现量产...',
                    'publish_date': '2026-04-03',
                    'tags': '新材料,科研'
                }
            ]
            print(f"模拟采集到 {len(mock_data)} 条数据")
            return mock_data
        
        try:
            feed = feedparser.parse(rss_url)
            collected = []
            
            print(f"发现 {len(feed.entries)} 条文章")
            
            for entry in feed.entries[:10]:  # 先采集前10条测试
                item = {
                    'source': source_name,
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'content': entry.get('summary', entry.get('description', '')),
                    'publish_date': entry.get('published', ''),
                    'tags': ''
                }
                collected.append(item)
                print(f"  📄 {item['title'][:50]}...")
            
            return collected
            
        except Exception as e:
            print(f"❌ RSS采集失败: {e}")
            return []
    
    def collect_from_api(self, source_name: str, api_url: str, params: Dict = None) -> List[Dict]:
        """
        从API采集数据
        支持：企名片、动脉网等提供API的源
        """
        print(f"\n{'='*70}")
        print(f"🔌 从API采集: {source_name}")
        print(f"{'='*70}")
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            data = response.json()
            
            # 根据数据源解析不同格式
            collected = self._parse_api_response(source_name, data)
            
            print(f"采集到 {len(collected)} 条数据")
            return collected
            
        except Exception as e:
            print(f"❌ API采集失败: {e}")
            return []
    
    def _parse_api_response(self, source_name: str, data: Dict) -> List[Dict]:
        """解析不同API的响应格式"""
        collected = []
        
        # 通用解析逻辑（简化版）
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and 'data' in data:
            items = data['data']
        elif isinstance(data, dict) and 'list' in data:
            items = data['list']
        else:
            items = []
        
        for item in items[:10]:  # 先采集前10条
            collected.append({
                'source': source_name,
                'title': item.get('title', item.get('name', 'Unknown')),
                'url': item.get('url', item.get('link', '')),
                'content': item.get('content', item.get('description', '')),
                'publish_date': item.get('publish_time', item.get('date', '')),
                'tags': item.get('tags', item.get('category', ''))
            })
        
        return collected
    
    def generate_summary(self, content: str) -> str:
        """
        AI摘要生成（简化版）
        完整版：调用Kimi API生成摘要
        简化版：提取前3句作为摘要
        """
        if not content:
            return ""
        
        # 简化版：提取前200字符
        summary = content[:200].strip()
        if len(content) > 200:
            summary += "..."
        
        return summary
    
    def save_to_db(self, items: List[Dict]):
        """保存到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for item in items:
            try:
                # 生成摘要
                summary = self.generate_summary(item['content'])
                
                cursor.execute('''
                    INSERT INTO intelligence 
                    (source, title, url, content, summary, tags, publish_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['source'],
                    item['title'],
                    item['url'],
                    item['content'],
                    summary,
                    item['tags'],
                    item['publish_date']
                ))
                saved_count += 1
            except Exception as e:
                print(f"  ⚠️  保存失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ 成功保存 {saved_count} 条情报")
        return saved_count
    
    def send_to_feishu(self, webhook_url: str, item: Dict) -> bool:
        """
        推送到飞书（简化版）
        完整版：使用飞书Webhook发送卡片消息
        简化版：打印到控制台模拟
        """
        print(f"\n{'='*70}")
        print(f"📤 推送到飞书")
        print(f"{'='*70}")
        
        message = {
            "title": item['title'],
            "source": item['source'],
            "summary": item['summary'],
            "url": item['url']
        }
        
        print(f"消息内容:")
        print(f"  标题: {message['title']}")
        print(f"  来源: {message['source']}")
        print(f"  摘要: {message['summary'][:100]}...")
        print(f"  链接: {message['url']}")
        
        # 简化版：模拟发送成功
        # 完整版：实际调用webhook_url
        print(f"\n✅ 模拟发送成功（完整版需要配置飞书Webhook）")
        return True
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总数量
        cursor.execute("SELECT COUNT(*) FROM intelligence")
        total = cursor.fetchone()[0]
        
        # 各源数量
        cursor.execute('''
            SELECT source, COUNT(*) as count 
            FROM intelligence 
            GROUP BY source
        ''')
        by_source = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 今日新增
        cursor.execute('''
            SELECT COUNT(*) FROM intelligence 
            WHERE date(collect_date) = date('now')
        ''')
        today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'today': today,
            'by_source': by_source
        }
    
    def run_collection(self):
        """执行采集任务"""
        print(f"\n{'='*70}")
        print(f"🚀 开始执行情报采集任务")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # 配置数据源（简化版，实际应从数据库读取）
        sources = [
            {
                'name': '36氪硬科技',
                'type': 'rss',
                'url': 'https://36kr.com/feed/hard-technology'  # 示例URL
            },
            {
                'name': 'IT桔子',
                'type': 'rss',
                'url': 'https://www.itjuzi.com/rss'  # 示例URL
            }
        ]
        
        total_collected = 0
        
        for source in sources:
            if source['type'] == 'rss':
                items = self.collect_from_rss(source['name'], source['url'])
            else:
                items = self.collect_from_api(source['name'], source['url'])
            
            if items:
                saved = self.save_to_db(items)
                total_collected += saved
            
            time.sleep(1)  # 礼貌性延迟
        
        print(f"\n{'='*70}")
        print(f"✅ 采集任务完成")
        print(f"总计采集: {total_collected} 条情报")
        print(f"{'='*70}")
        
        return total_collected

# CLI接口
if __name__ == "__main__":
    import sys
    
    system = ProjectIntelligenceSystem()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 intelligence_system.py collect       - 执行采集任务")
        print("  python3 intelligence_system.py stats         - 查看统计信息")
        print("  python3 intelligence_system.py test_feishu   - 测试飞书推送")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "collect":
        system.run_collection()
    
    elif command == "stats":
        stats = system.get_stats()
        print("\n=== 情报统计 ===")
        print(f"总计: {stats['total']} 条")
        print(f"今日: {stats['today']} 条")
        print("\n按源分布:")
        for source, count in stats['by_source'].items():
            print(f"  {source}: {count} 条")
    
    elif command == "test_feishu":
        test_item = {
            'title': '测试情报：某硬科技项目获得A轮融资',
            'source': '36氪',
            'summary': '这是一家专注于AI芯片研发的创业公司，本轮融资1亿元，由某知名VC领投...',
            'url': 'https://example.com/news/123'
        }
        system.send_to_feishu("https://open.feishu.cn/open-apis/bot/v2/hook/xxx", test_item)
    
    else:
        print(f"未知命令: {command}")
