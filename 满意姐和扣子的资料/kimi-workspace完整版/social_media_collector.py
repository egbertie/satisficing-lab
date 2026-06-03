#!/usr/bin/env python3
"""
social_media_collector.py - 新媒体情报采集框架
来源: 新媒体情报员_v1.0.docx - 新媒体情报员模块实用化改造
功能: 微信公众号/小红书/B站/抖音等平台的内容监控框架
创建时间: 2026-04-04
说明: 由于平台反爬和API限制，本框架采用"聚合源+RSS-Bridge"的Token友好策略
"""

import json
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class SocialMediaCollector:
    """
    新媒体情报采集框架
    核心策略: 不直接抓取平台，而是通过RSS-Bridge/第三方聚合获取前3条精华
    """
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = workspace
        self.data_path = Path(workspace) / "intelligence" / "social_media"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # 平台聚合源配置（需配合 RSS-Bridge 或 WeChatRSS 使用）
        self.platforms = {
            "wechat": {
                "name": "微信公众号",
                "sources": ["新榜", "清博指数", "RSS-Bridge(WeChat)"],
                "keywords": ["硬科技", "合伙人", "创业", "融资"],
                "note": "由于微信反爬严格，建议使用新榜/清博的公开榜单或RSS-Bridge"
            },
            "xiaohongshu": {
                "name": "小红书",
                "sources": ["千瓜数据", "新红数据"],
                "keywords": ["创业干货", "合伙人选择", "创始人IP"],
                "note": "小红书无公开API，建议通过第三方数据平台获取趋势报告"
            },
            "bilibili": {
                "name": "B站",
                "sources": ["B站公开搜索", "RSS-Bridge"],
                "keywords": ["创业", "科技", "商业思维"],
                "note": "可通过B站搜索API获取前10条结果"
            },
            "douyin": {
                "name": "抖音",
                "sources": ["巨量算数", "蝉妈妈"],
                "keywords": ["商业思维", "合伙人"],
                "note": "抖音无公开API，依赖第三方数据平台"
            }
        }
        
    def get_platform_guide(self, platform: str) -> Dict:
        """获取指定平台的采集指南"""
        return self.platforms.get(platform, {})
    
    def generate_collection_plan(self, topics: Optional[List[str]] = None) -> str:
        """生成新媒体情报采集执行计划（Markdown）"""
        topics = topics or ["硬科技创业", "合伙人匹配", "创始人决策"]
        
        lines = [
            f"# 新媒体情报采集计划 - {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## 执行策略",
            "**核心原则**: 不直接对抗平台反爬，通过聚合源+RSS-Bridge实现Token友好的轻量监控。",
            "",
            "## 监控主题",
        ]
        for t in topics:
            lines.append(f"- {t}")
        lines.append("")
        lines.append("## 平台配置")
        lines.append("")
        
        for key, cfg in self.platforms.items():
            lines.extend([
                f"### {cfg['name']} (`{key}`)",
                f"- **推荐数据源**: {', '.join(cfg['sources'])}",
                f"- **关键词**: {', '.join(cfg['keywords'])}",
                f"- **限制说明**: {cfg['note']}",
                ""
            ])
            
        lines.extend([
            "## RSS-Bridge 部署建议",
            "```bash",
            "# 1. 使用 RSS-Bridge 公共实例或自建",
            "# 2. 配置 WeChat/Bilibili/Douyin 的 Bridge",
            "# 3. 产出 RSS feed 后，由 intelligence_collection_system.py 统一抓取",
            "```",
            "",
            "## GitHub Actions 自动化参考",
            "```yaml",
            "name: 新媒体情报采集",
            "on:",
            "  schedule:",
            "    - cron: '0 8 * * *'  # 每天08:00",
            "jobs:",
            "  collect:",
            "    runs-on: ubuntu-latest",
            "    steps:",
            "      - uses: actions/checkout@v3",
            "      - name: 运行情报采集",
            "        run: python3 social_media_collector.py",
            "```",
            ""
        ])
        
        return "\n".join(lines)
    
    def fetch_bilibili_search(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """
        B站搜索API（公开接口，Token友好）
        注意: 非官方API，可能变更
        """
        results = []
        try:
            url = f"https://api.bilibili.com/x/web-interface/search/type?keyword={urllib.parse.quote(keyword)}&search_type=video"
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            if data.get('data', {}).get('result'):
                for item in data['data']['result'][:max_results]:
                    results.append({
                        'title': item.get('title', '').replace('<em class=\"keyword\">', '').replace('</em>', ''),
                        'bvid': item.get('bvid', ''),
                        'link': f"https://bilibili.com/video/{item.get('bvid', '')}",
                        'description': item.get('description', '')[:200],
                        'platform': 'bilibili',
                        'fetch_time': datetime.now().isoformat()
                    })
        except Exception as e:
            results.append({
                'title': 'B站搜索异常',
                'error': str(e),
                'platform': 'bilibili',
                'fetch_time': datetime.now().isoformat()
            })
            
        return results
    
    def save_daily_report(self, content: str):
        """保存日报到本地"""
        filename = self.data_path / f"social_media_plan_{datetime.now().strftime('%Y%m%d')}.md"
        filename.write_text(content, encoding='utf-8')
        return str(filename)


def main():
    collector = SocialMediaCollector()
    plan = collector.generate_collection_plan()
    path = collector.save_daily_report(plan)
    print(f"新媒体情报采集计划已生成: {path}")
    print(plan)


if __name__ == "__main__":
    main()
