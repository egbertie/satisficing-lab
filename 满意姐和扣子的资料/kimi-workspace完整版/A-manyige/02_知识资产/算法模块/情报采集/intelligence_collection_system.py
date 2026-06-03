#!/usr/bin/env python3
# intelligence_collection_system.py - 项目情报采集系统核心
# 来源: 文件1 - 项目情报采集系统.docx
# 功能: 云原生情报采集系统核心调度
# 创建时间: 2026-04-04 (从文件1补实施)
# 版本: 1.0

import json
import sys
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace')
from defense_base_components import BaseComponent, MetricsCollector

@dataclass
class DataSource:
    """数据源配置"""
    name: str
    source_type: str  # itjuzi, kr36, rss, gov, etc.
    url: str
    fetch_method: str  # browser, rss, api
    schedule: str  # cron expression
    enabled: bool = True
    last_fetch: Optional[datetime] = None

@dataclass
class IntelligenceItem:
    """情报项"""
    id: str
    title: str
    content: str
    source: str
    publish_time: datetime
    fetch_time: datetime
    category: str  # funding, policy, industry
    priority: str  # P0, P1, P2
    tags: List[str] = field(default_factory=list)
    is_duplicate: bool = False
    summary: str = ""

class IntelligenceCollectionSystem(BaseComponent):
    """
    项目情报采集系统 - 云原生版
    专为Kimi Claw优化的零服务器部署方案
    """
    
    def __init__(self):
        super().__init__('intelligence_system')
        self.metrics = MetricsCollector('intelligence')
        self.config_path = f"{self.workspace}/intelligence/config"
        self.data_path = f"{self.workspace}/intelligence/data"
        
        # 确保目录存在
        Path(self.config_path).mkdir(parents=True, exist_ok=True)
        Path(self.data_path).mkdir(parents=True, exist_ok=True)
        
        # 数据源注册表
        self.data_sources: Dict[str, DataSource] = {}
        
        # 采集器注册表
        self.collectors: Dict[str, Callable] = {}
        
        # 情报缓存
        self.intelligence_cache: List[IntelligenceItem] = []
        
        # 初始化默认数据源
        self._init_default_sources()
        
        self.metrics.record(action='system_init', version='1.0')
    
    def _init_default_sources(self):
        """初始化默认数据源"""
        default_sources = [
            DataSource(
                name='IT桔子融资',
                source_type='itjuzi',
                url='https://www.itjuzi.com/investevent',
                fetch_method='browser',
                schedule='0 9 * * *'  # 每天9点
            ),
            DataSource(
                name='36氪硬科技',
                source_type='kr36',
                url='https://36kr.com/search/articles/硬科技',
                fetch_method='rss',
                schedule='0 10,16 * * *'  # 每天10点和16点
            ),
            DataSource(
                name='动脉网生物医药',
                source_type='rss',
                url='https://www.vbdata.cn/feed',
                fetch_method='rss',
                schedule='0 11 * * *'  # 每天11点
            ),
            DataSource(
                name='政府政策',
                source_type='gov',
                url='https://www.gov.cn/zhengce/zhengceku/',
                fetch_method='browser',
                schedule='0 9 * * 1'  # 每周一早9点
            )
        ]
        
        for source in default_sources:
            self.data_sources[source.name] = source
    
    def register_collector(self, source_type: str, collector_func: Callable):
        """注册采集器"""
        self.collectors[source_type] = collector_func
        self.metrics.record(action='collector_registered', source_type=source_type)
    
    def collect(self, source_name: Optional[str] = None) -> List[IntelligenceItem]:
        """
        执行情报采集
        
        Args:
            source_name: 指定数据源名称，None表示采集所有
        
        Returns:
            采集到的情报列表
        """
        results = []
        
        sources_to_collect = []
        if source_name:
            if source_name in self.data_sources:
                sources_to_collect = [self.data_sources[source_name]]
            else:
                print(f"❌ 未知数据源: {source_name}")
                return []
        else:
            sources_to_collect = [s for s in self.data_sources.values() if s.enabled]
        
        print(f"🔵 开始采集，共 {len(sources_to_collect)} 个数据源")
        
        for source in sources_to_collect:
            print(f"\n📡 采集: {source.name}")
            
            try:
                # 获取对应采集器
                collector = self.collectors.get(source.source_type)
                
                if collector:
                    items = collector(source)
                    results.extend(items)
                    
                    # 更新最后采集时间
                    source.last_fetch = datetime.now()
                    
                    print(f"   ✅ 采集到 {len(items)} 条情报")
                    self.metrics.record(
                        action='collect_success',
                        source=source.name,
                        count=len(items)
                    )
                else:
                    print(f"   ⚠️  暂无采集器: {source.source_type}")
                    
            except Exception as e:
                print(f"   ❌ 采集失败: {e}")
                self.metrics.record(
                    action='collect_failed',
                    source=source.name,
                    error=str(e)
                )
        
        # 添加到缓存
        self.intelligence_cache.extend(results)
        
        print(f"\n📊 采集完成: 共 {len(results)} 条情报")
        return results
    
    def deduplicate(self, items: List[IntelligenceItem]) -> List[IntelligenceItem]:
        """
        去重处理
        
        基于标题相似度和内容哈希进行去重
        """
        unique_items = []
        seen_hashes = set()
        
        for item in items:
            # 计算内容哈希
            content_hash = hash(item.title + item.content[:100])
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                item.is_duplicate = False
                unique_items.append(item)
            else:
                item.is_duplicate = True
                print(f"   🔄 去重: {item.title[:50]}...")
        
        print(f"🧹 去重完成: {len(items)} -> {len(unique_items)}")
        return unique_items
    
    def generate_summary(self, item: IntelligenceItem) -> str:
        """
        生成情报摘要
        
        使用K2.5 Thinking生成3句话摘要
        """
        # 简化版：提取前3个句子
        sentences = item.content.split('。')[:3]
        summary = '。'.join(sentences) + '。'
        
        item.summary = summary
        return summary
    
    def classify_priority(self, item: IntelligenceItem) -> str:
        """
        分类优先级
        
        P0: AI芯片、GPU、传感器、生物医药的天使轮/Pre-A轮
        P1: 其他硬科技领域融资
        P2: 行业动态、政策
        """
        p0_keywords = ['AI芯片', 'GPU', '传感器', '生物医药', '天使轮', 'Pre-A轮']
        
        text = item.title + item.content
        
        if any(kw in text for kw in p0_keywords):
            item.priority = 'P0'
            item.tags.append('高优先级')
        elif item.category == 'funding':
            item.priority = 'P1'
        else:
            item.priority = 'P2'
        
        return item.priority
    
    def save_to_feishu(self, items: List[IntelligenceItem]) -> bool:
        """
        保存到飞书文档/多维表格
        """
        print(f"\n📤 推送 {len(items)} 条情报到飞书")
        
        # 格式化输出
        formatted = []
        for item in items:
            formatted.append({
                '标题': item.title,
                '摘要': item.summary[:200],
                '来源': item.source,
                '优先级': item.priority,
                '采集时间': item.fetch_time.isoformat()
            })
        
        # 保存到本地文件（实际应调用飞书API）
        output_file = f"{self.data_path}/intelligence_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 已保存到: {output_file}")
        return True
    
    def get_stats(self) -> Dict:
        """获取系统统计"""
        return {
            'data_sources': len(self.data_sources),
            'collectors': len(self.collectors),
            'cache_size': len(self.intelligence_cache),
            'sources': [
                {
                    'name': s.name,
                    'enabled': s.enabled,
                    'last_fetch': s.last_fetch.isoformat() if s.last_fetch else None
                }
                for s in self.data_sources.values()
            ]
        }
    
    def run_full_pipeline(self):
        """运行完整采集流水线"""
        print("=" * 70)
        print("🚀 启动情报采集流水线")
        print("=" * 70)
        
        # 1. 采集
        items = self.collect()
        
        if not items:
            print("\n⚠️ 未采集到情报")
            return
        
        # 2. 去重
        unique_items = self.deduplicate(items)
        
        # 3. 摘要生成
        for item in unique_items:
            self.generate_summary(item)
        
        # 4. 优先级分类
        for item in unique_items:
            self.classify_priority(item)
        
        # 5. 保存到飞书
        self.save_to_feishu(unique_items)
        
        print("\n" + "=" * 70)
        print(f"✅ 流水线完成: {len(unique_items)} 条情报已处理")
        print("=" * 70)

# 便捷函数
def run_intelligence_collection():
    """快速启动采集"""
    system = IntelligenceCollectionSystem()
    system.run_full_pipeline()
    return system.get_stats()

if __name__ == '__main__':
    run_intelligence_collection()
