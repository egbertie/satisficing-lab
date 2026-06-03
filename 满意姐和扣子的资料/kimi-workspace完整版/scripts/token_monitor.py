#!/usr/bin/env python3
"""
Token消耗监控脚本
实时监控API调用Token消耗，生成报告和告警

用法:
    python3 token_monitor.py --report daily    # 生成日报
    python3 token_monitor.py --report weekly   # 生成周报
    python3 token_monitor.py --check           # 检查预算状态
    python3 token_monitor.py --alert 80        # 设置80%预算告警
"""

import json
import sqlite3
import argparse
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class TokenUsage:
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_yuan: float
    task_type: str
    success: bool


@dataclass
class BudgetAlert:
    level: str  # 'info', 'warning', 'critical'
    message: str
    current_usage: int
    budget_limit: int
    percentage: float
    recommendation: str


class TokenMonitor:
    """Token消耗监控系统"""
    
    def __init__(self, db_path: str = "/opt/sri-agent-os/data/token_usage.db"):
        self.db_path = db_path
        self.budget_daily = 10000  # 每日预算：10K tokens
        self.budget_monthly = 300000  # 每月预算：300K tokens
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                cost_yuan REAL,
                task_type TEXT,
                success BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON token_usage(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def record_usage(self, model: str, prompt_tokens: int, completion_tokens: int,
                     task_type: str, success: bool = True):
        """记录一次Token使用"""
        total = prompt_tokens + completion_tokens
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO token_usage 
            (timestamp, model, prompt_tokens, completion_tokens, total_tokens, cost_yuan, task_type, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            model,
            prompt_tokens,
            completion_tokens,
            total,
            cost,
            task_type,
            success
        ))
        
        conn.commit()
        conn.close()
        
        # 实时检查是否需要告警
        alert = self._check_budget_alert()
        if alert and alert.level in ['warning', 'critical']:
            self._send_alert(alert)
    
    def _calculate_cost(self, model: str, prompt: int, completion: int) -> float:
        """计算成本（人民币）"""
        # Kimi模型定价（示例）
        pricing = {
            'kimi-k2p5': {'prompt': 0.012, 'completion': 0.012},  # 每1K tokens
            'kimi-k1.5': {'prompt': 0.006, 'completion': 0.006},
            'default': {'prompt': 0.01, 'completion': 0.01}
        }
        
        p = pricing.get(model, pricing['default'])
        cost = (prompt / 1000 * p['prompt']) + (completion / 1000 * p['completion'])
        return round(cost, 4)
    
    def get_daily_report(self, date: str = None) -> Dict:
        """生成日报"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 当日统计
        cursor.execute('''
            SELECT 
                COUNT(*) as call_count,
                SUM(prompt_tokens) as total_prompt,
                SUM(completion_tokens) as total_completion,
                SUM(total_tokens) as total_tokens,
                SUM(cost_yuan) as total_cost,
                AVG(success) as success_rate
            FROM token_usage
            WHERE date(timestamp) = ?
        ''', (date,))
        
        row = cursor.fetchone()
        
        # 按任务类型统计
        cursor.execute('''
            SELECT task_type, SUM(total_tokens) as tokens
            FROM token_usage
            WHERE date(timestamp) = ?
            GROUP BY task_type
            ORDER BY tokens DESC
        ''', (date,))
        
        task_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 按模型统计
        cursor.execute('''
            SELECT model, SUM(total_tokens) as tokens
            FROM token_usage
            WHERE date(timestamp) = ?
            GROUP BY model
            ORDER BY tokens DESC
        ''', (date,))
        
        model_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        total_tokens = row[3] or 0
        budget_usage = (total_tokens / self.budget_daily) * 100
        
        return {
            'date': date,
            'summary': {
                'call_count': row[0] or 0,
                'total_prompt_tokens': row[1] or 0,
                'total_completion_tokens': row[2] or 0,
                'total_tokens': total_tokens,
                'total_cost_yuan': round(row[4] or 0, 2),
                'success_rate': round((row[5] or 1) * 100, 1)
            },
            'budget': {
                'daily_limit': self.budget_daily,
                'used': total_tokens,
                'remaining': self.budget_daily - total_tokens,
                'usage_percentage': round(budget_usage, 1)
            },
            'breakdown': {
                'by_task': task_breakdown,
                'by_model': model_breakdown
            },
            'recommendations': self._generate_recommendations(budget_usage, task_breakdown)
        }
    
    def get_weekly_report(self) -> Dict:
        """生成周报"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                date(timestamp) as day,
                SUM(total_tokens) as daily_tokens,
                SUM(cost_yuan) as daily_cost
            FROM token_usage
            WHERE timestamp >= ?
            GROUP BY date(timestamp)
            ORDER BY day
        ''', (start_date.isoformat(),))
        
        daily_data = []
        total_tokens = 0
        total_cost = 0
        
        for row in cursor.fetchall():
            daily_data.append({
                'date': row[0],
                'tokens': row[1],
                'cost': round(row[2], 2)
            })
            total_tokens += row[1]
            total_cost += row[2]
        
        conn.close()
        
        # 计算趋势
        if len(daily_data) >= 2:
            first_half = sum(d['tokens'] for d in daily_data[:len(daily_data)//2])
            second_half = sum(d['tokens'] for d in daily_data[len(daily_data)//2:])
            trend = 'increasing' if second_half > first_half else 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'summary': {
                'total_tokens': total_tokens,
                'total_cost_yuan': round(total_cost, 2),
                'daily_average': round(total_tokens / 7, 0),
                'budget_usage_percentage': round((total_tokens / (self.budget_daily * 7)) * 100, 1)
            },
            'daily_breakdown': daily_data,
            'trend': trend,
            'recommendations': self._generate_weekly_recommendations(trend, total_tokens)
        }
    
    def _check_budget_alert(self) -> Optional[BudgetAlert]:
        """检查预算告警"""
        today = datetime.now().strftime('%Y-%m-%d')
        report = self.get_daily_report(today)
        
        usage_pct = report['budget']['usage_percentage']
        
        if usage_pct >= 100:
            return BudgetAlert(
                level='critical',
                message=f'今日Token预算已用完！({report["budget"]["used"]}/{self.budget_daily})',
                current_usage=report['budget']['used'],
                budget_limit=self.budget_daily,
                percentage=usage_pct,
                recommendation='立即启用本地LLM或暂停非关键任务'
            )
        elif usage_pct >= 80:
            return BudgetAlert(
                level='warning',
                message=f'今日Token预算即将用完 ({usage_pct:.0%})',
                current_usage=report['budget']['used'],
                budget_limit=self.budget_daily,
                percentage=usage_pct,
                recommendation='减少非必要调用，启用分级处理Pipeline'
            )
        elif usage_pct >= 50:
            return BudgetAlert(
                level='info',
                message=f'今日Token预算已使用 {usage_pct:.0%}',
                current_usage=report['budget']['used'],
                budget_limit=self.budget_daily,
                percentage=usage_pct,
                recommendation='正常监控中'
            )
        
        return None
    
    def _send_alert(self, alert: BudgetAlert):
        """发送告警（可集成飞书/邮件等）"""
        alert_msg = f"""
[Token预算告警]
级别: {alert.level.upper()}
消息: {alert.message}
使用: {alert.current_usage}/{alert.budget_limit} ({alert.percentage:.1f}%)
建议: {alert.recommendation}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        print(alert_msg)
        
        # 这里可以集成飞书Webhook
        # self._send_feishu_alert(alert_msg)
    
    def _generate_recommendations(self, budget_usage: float, task_breakdown: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if budget_usage > 80:
            recommendations.append('🔴 预算即将耗尽，请立即启用本地LLM或暂停非关键任务')
        elif budget_usage > 50:
            recommendations.append('🟡 预算使用过半，建议使用分级处理Pipeline优化')
        
        if task_breakdown:
            top_task = max(task_breakdown.items(), key=lambda x: x[1])
            if top_task[1] > 3000:
                recommendations.append(f'💡 "{top_task[0]}"消耗最多Token({top_task[1]}T)，建议优化')
        
        if not recommendations:
            recommendations.append('🟢 Token使用正常，继续保持')
        
        return recommendations
    
    def _generate_weekly_recommendations(self, trend: str, total_tokens: int) -> List[str]:
        """生成周报建议"""
        recommendations = []
        
        if trend == 'increasing':
            recommendations.append('📈 Token消耗呈上升趋势，建议审查使用模式')
        
        weekly_budget = self.budget_daily * 7
        if total_tokens > weekly_budget:
            recommendations.append(f'🔴 周度预算超支({total_tokens}/{weekly_budget})，需立即优化')
        elif total_tokens > weekly_budget * 0.8:
            recommendations.append('🟡 周度预算即将用完，建议启用边缘预处理')
        
        return recommendations
    
    def export_to_json(self, output_path: str):
        """导出数据到JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM token_usage ORDER BY timestamp DESC LIMIT 1000')
        columns = [description[0] for description in cursor.description]
        
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(columns, row)))
        
        conn.close()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已导出到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Token消耗监控')
    parser.add_argument('--report', choices=['daily', 'weekly'], help='生成报告类型')
    parser.add_argument('--check', action='store_true', help='检查预算状态')
    parser.add_argument('--alert', type=int, help='设置预算告警阈值(%)')
    parser.add_argument('--export', type=str, help='导出数据到JSON文件')
    
    args = parser.parse_args()
    
    monitor = TokenMonitor()
    
    if args.report == 'daily':
        report = monitor.get_daily_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif args.report == 'weekly':
        report = monitor.get_weekly_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif args.check:
        alert = monitor._check_budget_alert()
        if alert:
            print(f"告警级别: {alert.level}")
            print(f"消息: {alert.message}")
            print(f"建议: {alert.recommendation}")
        else:
            print("✅ 预算状态正常")
    
    elif args.export:
        monitor.export_to_json(args.export)
    
    else:
        # 默认显示今日摘要
        report = monitor.get_daily_report()
        print(f"""
╔════════════════════════════════════════╗
║      Token消耗监控 - 今日摘要           ║
╠════════════════════════════════════════╣
║ 调用次数: {report['summary']['call_count']:>20} ║
║ 总Token:  {report['summary']['total_tokens']:>20,} ║
║ 总成本:   ¥{report['summary']['total_cost_yuan']:>18} ║
║ 成功率:   {report['summary']['success_rate']:>19}% ║
╠════════════════════════════════════════╣
║ 预算使用: {report['budget']['usage_percentage']:>19}% ║
║ 剩余:     {report['budget']['remaining']:>20,} ║
╚════════════════════════════════════════╝
        """)
        
        for rec in report['recommendations']:
            print(f"  {rec}")


if __name__ == "__main__":
    main()
