#!/usr/bin/env python3
"""
Resource Arbitrage Monitor
全球资源套利监控系统

功能:
- 自动资源扫描
- 套利机会监控
- 告警通知
- 报表生成
- 可观测输出 (S3)
- 自动化集成 (S4)

作者: OpenClaw Agent
版本: v1.0
日期: 2026-03-27
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict
import threading

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resource_arbitrage import (
    ArbitrageEngine, ArbitrageConfig, ArbitrageOpportunity,
    ResourceInstance, RegionInfo, PricingInfo, ResourceSpec,
    Provider, ResourceType
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/resource_arbitrage_monitor.log')
    ]
)
logger = logging.getLogger('ArbitrageMonitor')


class MetricsCollector:
    """指标收集器 - S3: 可观测输出"""
    
    def __init__(self):
        self.metrics = {
            'opportunities_found': 0,
            'opportunities_executed': 0,
            'opportunities_rejected': 0,
            'total_savings_predicted': 0.0,
            'total_savings_actual': 0.0,
            'migrations_successful': 0,
            'migrations_failed': 0,
            'scan_count': 0,
            'last_scan_time': None,
            'average_decision_time_ms': 0
        }
        self.history: List[Dict] = []
    
    def record_opportunity(self, opportunity: ArbitrageOpportunity, decision: str):
        """记录套利机会"""
        self.metrics['opportunities_found'] += 1
        self.metrics['total_savings_predicted'] += opportunity.monthly_savings
        
        if decision == 'ACCEPT':
            self.metrics['opportunities_executed'] += 1
        else:
            self.metrics['opportunities_rejected'] += 1
        
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'opportunity_id': opportunity.opportunity_id,
            'savings': opportunity.monthly_savings,
            'decision': decision
        })
    
    def record_migration(self, success: bool, actual_savings: float = 0):
        """记录迁移结果"""
        if success:
            self.metrics['migrations_successful'] += 1
            self.metrics['total_savings_actual'] += actual_savings
        else:
            self.metrics['migrations_failed'] += 1
    
    def record_scan(self):
        """记录扫描"""
        self.metrics['scan_count'] += 1
        self.metrics['last_scan_time'] = datetime.now().isoformat()
    
    def get_dashboard_data(self) -> Dict:
        """获取面板数据"""
        return {
            'metrics': self.metrics,
            'active_opportunities': self.metrics['opportunities_found'] - 
                                   self.metrics['opportunities_executed'] - 
                                   self.metrics['opportunities_rejected'],
            'success_rate': (self.metrics['migrations_successful'] / 
                           (self.metrics['migrations_successful'] + 
                            self.metrics['migrations_failed']) * 100
                           if (self.metrics['migrations_successful'] + 
                               self.metrics['migrations_failed']) > 0 else 0),
            'prediction_accuracy': (
                (1 - abs(self.metrics['total_savings_predicted'] - 
                        self.metrics['total_savings_actual']) / 
                 self.metrics['total_savings_predicted']) * 100
                if self.metrics['total_savings_predicted'] > 0 else 0
            )
        }


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self.webhook_url = os.getenv('ARBITRAGE_WEBHOOK_URL', '')
        self.email_enabled = os.getenv('ARBITRAGE_EMAIL_ENABLED', 'false').lower() == 'true'
    
    def send_opportunity_alert(self, opportunity: ArbitrageOpportunity):
        """发送套利机会告警"""
        message = f"""
🎯 **套利机会发现**

- 源区域: {opportunity.source.region.code}
- 目标区域: {opportunity.target.region.code}
- 月节省: ${opportunity.monthly_savings:.2f}
- ROI回收期: {opportunity.roi_months:.1f}月
- 风险评分: {opportunity.risk_score:.2f}
- 置信度: {opportunity.confidence:.1%}

建议尽快评估执行。
        """
        
        logger.info(f"发送告警: {message}")
        
        # 实际实现中这里会调用飞书/钉钉/Slack API
        if self.webhook_url:
            self._send_webhook(message)
    
    def send_daily_report(self, metrics: Dict):
        """发送日报"""
        report = f"""
📊 **套利监控日报** ({datetime.now().strftime('%Y-%m-%d')})

**今日统计:**
- 扫描次数: {metrics.get('scan_count', 0)}
- 发现机会: {metrics.get('opportunities_found', 0)}
- 执行迁移: {metrics.get('opportunities_executed', 0)}
- 预测节省: ${metrics.get('total_savings_predicted', 0):.2f}

**累计数据:**
- 成功迁移: {metrics.get('migrations_successful', 0)}
- 实际节省: ${metrics.get('total_savings_actual', 0):.2f}
- 成功率: {metrics.get('success_rate', 0):.1f}%
        """
        
        logger.info(f"发送日报: {report}")
        
        if self.webhook_url:
            self._send_webhook(report)
    
    def _send_webhook(self, message: str):
        """发送Webhook"""
        import requests
        
        try:
            # 简化实现，实际使用时应根据具体平台调整格式
            payload = {
                'msg_type': 'text',
                'content': {'text': message}
            }
            # requests.post(self.webhook_url, json=payload)
            logger.info(f"Webhook已发送 (模拟)")
        except Exception as e:
            logger.error(f"Webhook发送失败: {e}")


class ResourceScanner:
    """资源扫描器 - S4: 自动化集成"""
    
    def __init__(self):
        self.providers = []
        self.scan_interval_minutes = 5
    
    def get_current_resources(self) -> List[ResourceInstance]:
        """获取当前资源列表"""
        logger.info("扫描当前资源...")
        
        # 模拟从云平台获取的资源
        resources = [
            ResourceInstance(
                instance_id="i-prod-001",
                spec=ResourceSpec(
                    resource_type=ResourceType.COMPUTE,
                    cpu_cores=16,
                    memory_gb=64,
                    storage_gb=1000,
                    network_mbps=10000
                ),
                region=RegionInfo(
                    code="us-east-1",
                    provider=Provider.AWS,
                    name="US East (N. Virginia)",
                    timezone="EST",
                    currency="USD",
                    latency_to_user=50
                ),
                current_pricing=PricingInfo(
                    on_demand_hourly=0.768,
                    reserved_1y_hourly=0.48,
                    reserved_3y_hourly=0.32,
                    spot_hourly=0.24
                ),
                current_cost_monthly=560.64,
                utilization_rate=0.80,
                data_volume_gb=800,
                sla_requirement=0.999,
                created_at=datetime.now(),
                tags={'env': 'production', 'team': 'platform'}
            ),
            ResourceInstance(
                instance_id="i-prod-002",
                spec=ResourceSpec(
                    resource_type=ResourceType.COMPUTE,
                    cpu_cores=8,
                    memory_gb=32,
                    storage_gb=500,
                    network_mbps=5000
                ),
                region=RegionInfo(
                    code="us-west-2",
                    provider=Provider.AWS,
                    name="US West (Oregon)",
                    timezone="PST",
                    currency="USD",
                    latency_to_user=80
                ),
                current_pricing=PricingInfo(
                    on_demand_hourly=0.384,
                    reserved_1y_hourly=0.24,
                    reserved_3y_hourly=0.16,
                    spot_hourly=0.12
                ),
                current_cost_monthly=280.32,
                utilization_rate=0.65,
                data_volume_gb=400,
                sla_requirement=0.99,
                created_at=datetime.now(),
                tags={'env': 'production', 'team': 'backend'}
            )
        ]
        
        logger.info(f"发现 {len(resources)} 个资源")
        return resources
    
    def get_global_pricing(self, spec: ResourceSpec) -> List[Tuple[RegionInfo, PricingInfo]]:
        """获取全球定价数据"""
        logger.info("获取全球定价数据...")
        
        # 模拟定价数据
        pricing_data = [
            (
                RegionInfo(
                    code="us-east-1",
                    provider=Provider.AWS,
                    name="US East (N. Virginia)",
                    timezone="EST",
                    currency="USD",
                    latency_to_user=50
                ),
                PricingInfo(
                    on_demand_hourly=0.768,
                    reserved_1y_hourly=0.48,
                    reserved_3y_hourly=0.32,
                    spot_hourly=0.24
                )
            ),
            (
                RegionInfo(
                    code="eu-west-1",
                    provider=Provider.AWS,
                    name="EU (Ireland)",
                    timezone="GMT",
                    currency="EUR",
                    latency_to_user=120
                ),
                PricingInfo(
                    on_demand_hourly=0.65,
                    reserved_1y_hourly=0.41,
                    reserved_3y_hourly=0.27,
                    spot_hourly=0.20
                )
            ),
            (
                RegionInfo(
                    code="ap-southeast-1",
                    provider=Provider.AWS,
                    name="Asia Pacific (Singapore)",
                    timezone="SGT",
                    currency="SGD",
                    latency_to_user=180
                ),
                PricingInfo(
                    on_demand_hourly=0.80,
                    reserved_1y_hourly=0.50,
                    reserved_3y_hourly=0.35,
                    spot_hourly=0.25
                )
            ),
            (
                RegionInfo(
                    code="us-west-2",
                    provider=Provider.AWS,
                    name="US West (Oregon)",
                    timezone="PST",
                    currency="USD",
                    latency_to_user=80
                ),
                PricingInfo(
                    on_demand_hourly=0.768,
                    reserved_1y_hourly=0.48,
                    reserved_3y_hourly=0.32,
                    spot_hourly=0.24
                )
            ),
        ]
        
        return pricing_data


class ArbitrageMonitor:
    """套利监控系统 - 主控制器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = ArbitrageConfig()
        self.engine = ArbitrageEngine(self.config)
        self.scanner = ResourceScanner()
        self.metrics = MetricsCollector()
        self.notifier = NotificationManager()
        
        self.running = False
        self.opportunities_cache: List[ArbitrageOpportunity] = []
        
        logger.info("套利监控系统初始化完成")
    
    def scan_once(self):
        """执行单次扫描"""
        logger.info("=" * 60)
        logger.info("开始资源扫描")
        logger.info("=" * 60)
        
        try:
            # 1. 获取当前资源
            current_resources = self.scanner.get_current_resources()
            
            # 2. 获取全球定价
            global_pricing = []
            for resource in current_resources:
                pricing = self.scanner.get_global_pricing(resource.spec)
                global_pricing.extend(pricing)
            
            # 3. 发现套利机会
            opportunities = self.engine.find_opportunities(
                current_resources, global_pricing
            )
            
            # 4. 更新缓存
            self.opportunities_cache = opportunities
            
            # 5. 决策处理
            high_value_ops = []
            for opp in opportunities:
                decision = self.engine.make_decision(opp)
                self.metrics.record_opportunity(opp, decision.decision.value)
                
                # 高价值机会告警
                if opp.monthly_savings >= 100:
                    high_value_ops.append((opp, decision))
                    self.notifier.send_opportunity_alert(opp)
                
                logger.info(f"机会 {opp.opportunity_id}: {decision.decision.value} - {decision.reason}")
            
            # 6. 记录扫描
            self.metrics.record_scan()
            
            logger.info(f"扫描完成，发现 {len(opportunities)} 个机会")
            
            # 7. 输出面板数据
            dashboard = self.metrics.get_dashboard_data()
            logger.info(f"面板数据: {json.dumps(dashboard, indent=2, default=str)}")
            
        except Exception as e:
            logger.error(f"扫描失败: {e}", exc_info=True)
    
    def generate_report(self, report_type: str = 'daily') -> str:
        """生成报表 - S3可观测输出"""
        metrics = self.metrics.metrics
        dashboard = self.metrics.get_dashboard_data()
        
        if report_type == 'daily':
            report = f"""
# 套利监控日报 - {datetime.now().strftime('%Y-%m-%d')}

## 今日统计
- 扫描次数: {metrics['scan_count']}
- 发现套利机会: {metrics['opportunities_found']}
- 已执行: {metrics['opportunities_executed']}
- 已拒绝: {metrics['opportunities_rejected']}
- 预测节省总额: ${metrics['total_savings_predicted']:.2f}

## 累计数据
- 成功迁移: {metrics['migrations_successful']}
- 失败迁移: {metrics['migrations_failed']}
- 实际节省: ${metrics['total_savings_actual']:.2f}
- 成功率: {dashboard['success_rate']:.1f}%
- 预测准确率: {dashboard['prediction_accuracy']:.1f}%

## 当前活跃机会
{len(self.opportunities_cache)} 个套利机会等待处理

## 建议行动
"""
            # 添加具体建议
            for opp in self.opportunities_cache[:5]:
                report += f"- 考虑迁移到 {opp.target.region.code}，月节省 ${opp.monthly_savings:.2f}\n"
            
            return report
        
        elif report_type == 'weekly':
            return f"""
# 套利监控周报 - {datetime.now().strftime('%Y年第%W周')}

## 本周摘要
- 累计发现机会: {metrics['opportunities_found']}
- 执行迁移: {metrics['opportunities_executed']}
- 累计节省: ${metrics['total_savings_actual']:.2f}
- 成功率: {dashboard['success_rate']:.1f}%

## 趋势分析
(基于历史数据分析)

## 下周建议
1. 继续监控 eu-west-1 区域价格
2. 评估预留实例购买策略
3. 审查高成本资源利用率
"""
        
        return ""
    
    def stop(self):
        """停止监控"""
        self.running = False
        logger.info("监控系统已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Resource Arbitrage Monitor')
    parser.add_argument('--scan', action='store_true', help='执行单次扫描')
    parser.add_argument('--report', type=str, choices=['daily', 'weekly'], 
                       help='生成报表')
    
    args = parser.parse_args()
    
    monitor = ArbitrageMonitor()
    
    if args.scan:
        monitor.scan_once()
    
    elif args.report:
        report = monitor.generate_report(args.report)
        print(report)
    
    else:
        # 默认执行单次扫描并显示结果
        monitor.scan_once()
        print("\n" + "=" * 60)
        print("扫描完成！查看日志获取详细信息:")
        print("  tail -f /tmp/resource_arbitrage_monitor.log")
        print("=" * 60)


if __name__ == "__main__":
    main()
