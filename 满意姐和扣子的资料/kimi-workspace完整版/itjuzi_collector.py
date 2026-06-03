#!/usr/bin/env python3
# itjuzi_collector.py - IT桔子融资事件采集模块
# 来源: 文件1 - 项目情报采集系统.docx
# 功能: IT桔子融资事件浏览器自动化采集
# 创建时间: 2026-04-04
# 版本: 1.0

import json
import re
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

@dataclass
class FundingEvent:
    """融资事件"""
    company_name: str
    funding_round: str
    amount: str
    investors: List[str]
    industry: str
    publish_time: str
    description: str

class ITJuziCollector:
    """
    IT桔子融资事件采集器
    使用浏览器自动化访问IT桔子，提取融资事件
    """
    
    BASE_URL = "https://www.itjuzi.com/investevent"
    
    # 重点关注的硬科技领域
    TARGET_INDUSTRIES = [
        '人工智能', 'AI芯片', '半导体', '集成电路',
        '生物医药', '医疗器械', '新能源', '新材料',
        '先进制造', '机器人', '自动驾驶', '传感器'
    ]
    
    # 重点关注的融资轮次
    TARGET_ROUNDS = ['天使轮', 'Pre-A轮', 'A轮', 'A+轮', 'B轮']
    
    def __init__(self):
        self.collected_events = []
    
    def fetch_page(self, page: int = 1) -> str:
        """
        获取IT桔子融资事件页面
        
        实际使用时通过browser工具访问
        """
        url = f"{self.BASE_URL}?page={page}"
        print(f"📡 访问: {url}")
        
        # 这里应该调用browser工具
        # 返回HTML内容
        return ""
    
    def parse_events(self, html_content: str) -> List[FundingEvent]:
        """
        解析融资事件列表
        """
        events = []
        
        # 实际解析逻辑（基于IT桔子页面结构）
        # 这里使用模拟数据演示结构
        
        return events
    
    def filter_hardtech(self, events: List[FundingEvent]) -> List[FundingEvent]:
        """
        筛选硬科技领域融资事件
        """
        filtered = []
        
        for event in events:
            # 检查行业
            if any(ind in event.industry for ind in self.TARGET_INDUSTRIES):
                # 检查轮次
                if any(rnd in event.funding_round for rnd in self.TARGET_ROUNDS):
                    filtered.append(event)
        
        print(f"🎯 硬科技筛选: {len(events)} -> {len(filtered)}")
        return filtered
    
    def format_for_push(self, event: FundingEvent) -> str:
        """
        格式化为推送消息
        
        3句话模板：
        1. [公司名]完成[轮次]融资，金额[金额]，投资方[投资方]
        2. 公司专注[领域]，产品/技术亮点...
        3. 合伙人视角：投资价值评估...
        """
        investors_str = '、'.join(event.investors[:3])
        
        message = f"""🚀 {event.company_name} | {event.funding_round}
💰 融资金额: {event.amount}
🏢 投资机构: {investors_str}
🎯 所属领域: {event.industry}
📝 项目简介: {event.description[:150]}...
⏰ 发布时间: {event.publish_time}
"""
        return message
    
    def collect(self, max_pages: int = 3) -> List[FundingEvent]:
        """
        执行采集
        """
        all_events = []
        
        for page in range(1, max_pages + 1):
            print(f"\n📄 采集第 {page}/{max_pages} 页")
            
            html = self.fetch_page(page)
            events = self.parse_events(html)
            
            if not events:
                break
            
            all_events.extend(events)
        
        # 筛选硬科技
        hardtech_events = self.filter_hardtech(all_events)
        
        self.collected_events = hardtech_events
        
        print(f"\n✅ 采集完成: {len(hardtech_events)} 条硬科技融资事件")
        return hardtech_events
    
    def save_to_json(self, filename: str = None):
        """保存到JSON文件"""
        if not filename:
            filename = f"itjuzi_funding_{datetime.now().strftime('%Y%m%d')}.json"
        
        data = [
            {
                'company': e.company_name,
                'round': e.funding_round,
                'amount': e.amount,
                'investors': e.investors,
                'industry': e.industry,
                'time': e.publish_time,
                'description': e.description
            }
            for e in self.collected_events
        ]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已保存到: {filename}")

# 便捷函数
def collect_itjuzi_funding():
    """快速采集IT桔子融资"""
    collector = ITJuziCollector()
    return collector.collect()

if __name__ == '__main__':
    collect_itjuzi_funding()
