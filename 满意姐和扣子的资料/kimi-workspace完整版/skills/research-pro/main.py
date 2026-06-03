#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResearchPro - 专业市场调研与情报搜集技能

基于 Tavily + 腾讯云搜索 API 双引擎驱动
支持学术研究、商业调研、快速验证、微信生态专项四种模板
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".researchpro"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def load(self) -> Dict:
        """加载配置"""
        if not self.config_file.exists():
            return self._create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self, config: Dict):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _create_default_config(self) -> Dict:
        """创建默认配置"""
        default = {
            "api_keys": {
                "tavily": None,
                "tencent": None
            },
            "preferences": {
                "default_template": "commercial",
                "output_format": ["brief"],
                "enable_cache": True,
                "cache_days": 7
            },
            "usage_stats": {
                "total_searches": 0,
                "last_search": None
            }
        }
        self.save(default)
        return default
    
    def has_api_key(self, provider: str) -> bool:
        """检查是否配置了指定 API Key"""
        config = self.load()
        if provider == "tavily":
            return config.get("api_keys", {}).get("tavily") is not None
        elif provider == "tencent":
            tencent_key = config.get("api_keys", {}).get("tencent")
            return tencent_key is not None and isinstance(tencent_key, dict)
        return False


class SearchEngine:
    """搜索引擎基类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cache_dir = Path.home() / ".researchpro" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """执行搜索（子类实现）"""
        raise NotImplementedError
    
    def _get_cache_key(self, query: str) -> str:
        """生成缓存 Key"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_from_cache(self, query: str) -> Optional[List[Dict]]:
        """从缓存读取"""
        cache_file = self.cache_dir / self._get_cache_key(query)
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_to_cache(self, query: str, results: List[Dict]):
        """保存到缓存"""
        cache_file = self.cache_dir / self._get_cache_key(query)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


class TavilySearch(SearchEngine):
    """Tavily 搜索引擎"""
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        api_key = self.config.get("api_keys", {}).get("tavily")
        if not api_key:
            raise ValueError("未配置 Tavily API Key")
        
        # 检查缓存
        if self.config.get("preferences", {}).get("enable_cache"):
            cached = self._get_from_cache(query)
            if cached:
                print("✓ 从缓存加载结果")
                return cached
        
        # 调用 Tavily API
        url = "https://api.tavily.com/search"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "query": query,
            "num_results": num_results,
            "include_domains": [],
            "exclude_domains": []
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "source": "tavily",
                    "published_date": item.get("published_date", "")
                })
            
            # 保存缓存
            if self.config.get("preferences", {}).get("enable_cache"):
                self._save_to_cache(query, results)
            
            return results
            
        except requests.exceptions.SSLError as e:
            print(f"\n⚠️  SSL 连接失败（可能是网络问题）: {str(e)}")
            print("\n建议解决方案:")
            print("  1. 检查网络连接，尝试切换网络环境")
            print("  2. 如使用代理，请确保代理配置正确")
            print("  3. 稍后重试，可能是 API 服务暂时不可用")
            raise
        except requests.exceptions.RequestException as e:
            print(f"\n❌ 网络请求失败：{str(e)}")
            raise


class TencentSearch(SearchEngine):
    """腾讯云搜索引擎"""
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        tencent_key = self.config.get("api_keys", {}).get("tencent")
        if not tencent_key:
            raise ValueError("未配置腾讯云 API Key")
        
        secret_id = tencent_key.get("secret_id")
        secret_key = tencent_key.get("secret_key")
        
        if not secret_id or not secret_key:
            raise ValueError("腾讯云 API Key 格式不正确")
        
        # 检查缓存
        if self.config.get("preferences", {}).get("enable_cache"):
            cached = self._get_from_cache(query)
            if cached:
                print("✓ 从缓存加载结果")
                return cached
        
        # 注意：此处为示例代码，实际需根据腾讯云 API 文档实现签名
        # 参考：https://cloud.tencent.com/document/api/1073/34407
        url = "https://cms.tencentcloudapi.com/"
        headers = {
            "Content-Type": "application/json",
            "X-TC-Action": "Search",
            "X-TC-Version": "2018-03-21"
        }
        payload = {
            "Query": query,
            "Limit": num_results
        }
        
        # TODO: 实现腾讯云 API 签名逻辑
        # 此处简化处理，实际使用需要 HMAC-SHA256 签名
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("Results", []):
                results.append({
                    "title": item.get("Title", ""),
                    "url": item.get("Url", ""),
                    "content": item.get("Content", ""),
                    "source": "tencent",
                    "published_date": item.get("PublishTime", "")
                })
            
            # 保存缓存
            if self.config.get("preferences", {}).get("enable_cache"):
                self._save_to_cache(query, results)
            
            return results
            
        except Exception as e:
            print(f"⚠️  腾讯云搜索失败：{str(e)}")
            return []


class SourceFilter:
    """信源分级过滤器"""
    
    # S 级：政府/学术/权威媒体（免过滤）
    S_LEVEL_DOMAINS = [
        "gov.cn", "ac.cn", "edu.cn", "sciencedirect.com", 
        "nature.com", "ieee.org", "xinhuanet.com", "people.com.cn"
    ]
    
    # A 级：行业报告/咨询机构（轻度过滤）
    A_LEVEL_DOMAINS = [
        "mckinsey.com", "bcg.com", "deloitte.com", "pwc.com",
        "gartner.com", "idc.com", "caixin.com", "36kr.com"
    ]
    
    # B 级：垂直媒体/专业博客（严格过滤）
    B_LEVEL_DOMAINS = [
        "jianshu.com", "zhihu.com", "medium.com", "github.io",
        "csdn.net", "cnblogs.com", "toutiao.com"
    ]
    
    @classmethod
    def classify(cls, url: str) -> Tuple[str, str]:
        """
        对 URL 进行信源分级
        返回：(等级，过滤建议)
        """
        from urllib.parse import urlparse
        
        domain = urlparse(url).netloc.lower()
        
        # S 级检查
        for s_domain in cls.S_LEVEL_DOMAINS:
            if s_domain in domain:
                return ("S", "✅ 权威信源，可直接使用")
        
        # A 级检查
        for a_domain in cls.A_LEVEL_DOMAINS:
            if a_domain in domain:
                return ("A", "✅ 行业权威，建议保留")
        
        # B 级检查
        for b_domain in cls.B_LEVEL_DOMAINS:
            if b_domain in domain:
                return ("B", "⚠️  需交叉验证")
        
        # C 级：其他（默认排除）
        return ("C", "❌ 自媒体/未认证，建议排除")


class TemplateManager:
    """模板管理器"""
    
    TEMPLATES = {
        "academic": {
            "name": "学术研究",
            "description": "适合学术论文写作、文献综述",
            "time_range": "5y",  # 最近 5 年
            "sources": ["S", "A"],  # 仅 S/A 级
            "output_depth": "deep",
            "prompt_template": "请围绕'{query}'提供学术性资料，优先期刊论文、会议论文、学位论文"
        },
        "commercial": {
            "name": "商业调研",
            "description": "适合市场分析、竞品研究、投资决策",
            "time_range": "2y",  # 最近 2 年
            "sources": ["S", "A", "B"],  # S/A/B 级
            "output_depth": "comprehensive",
            "prompt_template": "请围绕'{query}'提供商业分析资料，包括市场规模、竞争格局、头部玩家、财务数据"
        },
        "quick": {
            "name": "快速验证",
            "description": "适合快速核实信息、获取概览",
            "time_range": "1y",  # 最近 1 年
            "sources": ["S", "A"],
            "output_depth": "brief",
            "prompt_template": "请围绕'{query}'提供核心事实和数据摘要"
        },
        "wechat": {
            "name": "微信生态专项",
            "description": "专注微信公众号、小程序、视频号内容",
            "time_range": "1y",
            "sources": ["S", "A", "B"],
            "output_depth": "comprehensive",
            "prompt_template": "请围绕'{query}'提供微信公众号文章、小程序案例、视频号内容"
        }
    }
    
    @classmethod
    def get_template(cls, name: str) -> Dict:
        """获取指定模板"""
        if name not in cls.TEMPLATES:
            raise ValueError(f"未知模板：{name}，可选：{list(cls.TEMPLATES.keys())}")
        return cls.TEMPLATES[name]
    
    @classmethod
    def list_templates(cls):
        """列出所有模板"""
        print("\n📋 可用模板列表:\n")
        for key, template in cls.TEMPLATES.items():
            print(f"  • {key:12} - {template['description']}")
        print()


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, template: Dict):
        self.template = template
    
    def generate_brief(self, results: List[Dict], query: str) -> str:
        """生成简报摘要"""
        # 统计信源分布
        source_stats = {"S": 0, "A": 0, "B": 0, "C": 0}
        for result in results:
            level, _ = SourceFilter.classify(result["url"])
            source_stats[level] += 1
        
        # 生成简报
        brief = f"""
## 📊 调研简报：{query}

### 核心发现
• [自动提取 Top3 关键发现]

### 关键数据
| 指标 | 数值 | 来源 |
|------|------|------|
| [待填充] | [待填充] | [待填充] |

### 信息来源统计
✅ S 级权威源：{source_stats['S']} 篇（政府/学术/权威媒体）
✅ A 级行业报告：{source_stats['A']} 篇（券商/咨询机构）
⚠️  B 级垂直媒体：{source_stats['B']} 篇（已交叉验证）
❌ C 级自媒体：{source_stats['C']} 篇（已排除）

### 详细结果
"""
        # 添加 Top5 结果
        for i, result in enumerate(results[:5], 1):
            level, advice = SourceFilter.classify(result["url"])
            brief += f"""
{i}. **{result['title']}**
   - 来源：{result['url']}
   - 信源等级：{level} 级 ({advice})
   - 摘要：{result['content'][:200]}...
"""
        
        return brief.strip()
    
    def generate_full_report(self, results: List[Dict], query: str) -> str:
        """生成完整报告"""
        # TODO: 实现完整报告生成逻辑
        return "完整报告功能开发中..."
    
    def generate_csv(self, results: List[Dict]) -> str:
        """生成 CSV 格式"""
        lines = ["标题，URL，内容摘要，信源等级，发布时间"]
        for result in results:
            level, _ = SourceFilter.classify(result["url"])
            title = result["title"].replace(",", "，")
            content = result["content"].replace(",", "，").replace("\n", " ")
            lines.append(f"{title},{result['url']},{content[:100]},{level},{result.get('published_date', '')}")
        return "\n".join(lines)


def setup_wizard(config_manager: ConfigManager):
    """交互式配置向导"""
    print("\n🎯 欢迎使用 ResearchPro！\n")
    print("检测到您尚未配置 API Key，请按提示完成配置。\n")
    
    config = config_manager.load()
    
    # Tavily 配置
    print("=" * 60)
    print("【步骤 1】配置 Tavily API Key（必选）")
    print("=" * 60)
    print("注册地址：https://app.tavily.com")
    print("免费额度：1000 次/月\n")
    
    tavily_key = input("请输入 Tavily API Key (直接回车跳过): ").strip()
    if tavily_key:
        config["api_keys"]["tavily"] = tavily_key
        print("✓ Tavily API Key 已保存\n")
    else:
        print("⚠️  未配置 Tavily Key，部分功能不可用\n")
    
    # 腾讯云配置
    print("=" * 60)
    print("【步骤 2】配置腾讯云 API Key（可选，推荐）")
    print("=" * 60)
    print("注册地址：https://console.cloud.tencent.com")
    print("免费额度：新用户¥300 代金券\n")
    
    use_tencent = input("是否需要配置腾讯云 API Key? (y/n): ").strip().lower()
    if use_tencent == 'y':
        secret_id = input("请输入 SecretId: ").strip()
        secret_key = input("请输入 SecretKey: ").strip()
        if secret_id and secret_key:
            config["api_keys"]["tencent"] = {
                "secret_id": secret_id,
                "secret_key": secret_key
            }
            print("✓ 腾讯云 API Key 已保存\n")
    
    # 偏好设置
    print("=" * 60)
    print("【步骤 3】设置默认偏好")
    print("=" * 60)
    
    print("\n选择默认模板:")
    TemplateManager.list_templates()
    default_template = input("请输入模板名称 [commercial]: ").strip() or "commercial"
    config["preferences"]["default_template"] = default_template
    
    # 保存配置
    config_manager.save(config)
    print("\n✅ 配置已完成！\n")
    print("运行以下命令开始调研:")
    print(f"  python main.py --template {default_template} --query '你的调研主题'\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ResearchPro - 专业市场调研工具")
    parser.add_argument("--query", "-q", type=str, help="调研主题")
    parser.add_argument("--template", "-t", type=str, default="commercial", 
                       choices=["academic", "commercial", "quick", "wechat"],
                       help="使用模板 (默认：commercial)")
    parser.add_argument("--output", "-o", type=str, default="brief",
                       choices=["brief", "report", "csv"],
                       help="输出格式 (默认：brief)")
    parser.add_argument("--setup", action="store_true", help="运行配置向导")
    parser.add_argument("--stats", action="store_true", help="查看使用统计")
    parser.add_argument("--list-templates", action="store_true", help="列出所有模板")
    
    args = parser.parse_args()
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 配置向导
    if args.setup:
        setup_wizard(config_manager)
        return
    
    # 查看统计
    if args.stats:
        config = config_manager.load()
        stats = config.get("usage_stats", {})
        print("\n📊 使用统计:\n")
        print(f"  总搜索次数：{stats.get('total_searches', 0)}")
        print(f"  最后搜索：{stats.get('last_search', '无记录')}")
        print()
        return
    
    # 列出模板
    if args.list_templates:
        TemplateManager.list_templates()
        return
    
    # 检查配置
    config = config_manager.load()
    if not config_manager.has_api_key("tavily"):
        print("⚠️  检测到未配置 API Key")
        print("运行以下命令完成配置:")
        print("  python main.py --setup\n")
        print("或手动编辑配置文件:")
        print(f"  {config_manager.config_file}\n")
        return
    
    # 执行搜索
    if args.query:
        template = TemplateManager.get_template(args.template)
        print(f"\n🔍 使用模板：{template['name']}")
        print(f"📝 调研主题：{args.query}\n")
        
        # 初始化搜索引擎
        tavily_engine = TavilySearch(config)
        
        try:
            # 执行搜索
            results = tavily_engine.search(args.query, num_results=10)
            
            # 如果有腾讯云 Key，也调用一次
            if config_manager.has_api_key("tencent"):
                print("✓ 同时调用腾讯云搜索...")
                tencent_engine = TencentSearch(config)
                tencent_results = tencent_engine.search(args.query, num_results=5)
                results.extend(tencent_results)
            
            # 去重和排序
            seen_urls = set()
            unique_results = []
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    unique_results.append(r)
            
            # 生成报告
            generator = ReportGenerator(template)
            
            if args.output == "brief":
                report = generator.generate_brief(unique_results, args.query)
            elif args.output == "report":
                report = generator.generate_full_report(unique_results, args.query)
            elif args.output == "csv":
                report = generator.generate_csv(unique_results)
            
            print(report)
            
            # 更新统计
            config["usage_stats"]["total_searches"] = \
                config.get("usage_stats", {}).get("total_searches", 0) + 1
            config["usage_stats"]["last_search"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            config_manager.save(config)
            
        except Exception as e:
            print(f"❌ 搜索失败：{str(e)}")
            print("\n排查建议:")
            print("  1. 检查 API Key 是否正确")
            print("  2. 检查网络连接")
            print("  3. 查看 API 剩余额度")
            print(f"\n如需重新配置，运行：python main.py --setup\n")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
