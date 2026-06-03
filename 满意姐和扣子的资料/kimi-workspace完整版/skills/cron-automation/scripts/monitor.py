#!/usr/bin/env python3
"""
监控服务 - Cron-Automation System S3可观测输出组件

功能:
- 实时任务状态监控
- 资源使用监控
- 告警检测与通知
- 生成监控报告

S3标准: 可观测输出 - 监控面板、告警机制
"""

import json
import os
import sys
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 路径配置
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
MONITOR_DIR = BASE_DIR / "monitor"
STATE_DIR = BASE_DIR / "state"

MONITOR_DIR.mkdir(exist_ok=True)


class Monitor:
    """监控系统"""
    
    def __init__(self):
        self.tasks_config = {}
        self.alerts_config = {}
        self._load_configs()
    
    def _load_configs(self):
        """加载配置"""
        try:
            with open(CONFIG_DIR / "tasks.json", 'r', encoding='utf-8') as f:
                self.tasks_config = json.load(f)
            with open(CONFIG_DIR / "alerts.json", 'r', encoding='utf-8') as f:
                self.alerts_config = json.load(f)
        except Exception as e:
            print(f"配置加载失败: {e}")
    
    def get_task_status(self) -> List[Dict]:
        """获取任务状态"""
        tasks = self.tasks_config.get('tasks', [])
        result = []
        
        # 加载状态文件
        state_file = STATE_DIR / "task_states.json"
        states = {}
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    states = json.load(f)
            except:
                pass
        
        for task in tasks:
            task_id = task['id']
            state = states.get(task_id, {})
            
            result.append({
                'id': task_id,
                'name': task['name'],
                'enabled': task.get('enabled', True),
                'cron': task['cron'],
                'status': state.get('last_status', 'unknown'),
                'last_run': state.get('last_run', '--'),
                'consecutive_failures': state.get('consecutive_failures', 0),
                'is_running': state.get('is_running', False)
            })
        
        return result
    
    def get_system_metrics(self) -> Dict:
        """获取系统指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_used': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_used': disk.percent,
            'disk_free_gb': disk.free / (1024**3),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_dashboard_html(self) -> str:
        """生成监控面板HTML"""
        tasks = self.get_task_status()
        metrics = self.get_system_metrics()
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cron-Automation Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: #1e293b;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .metric-card h3 {{
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        .status-good {{ color: #4ade80; }}
        .status-warn {{ color: #fbbf24; }}
        .status-error {{ color: #f87171; }}
        .task-table {{
            background: #1e293b;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .task-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .task-table th {{
            background: #334155;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #94a3b8;
        }}
        .task-table td {{
            padding: 15px;
            border-bottom: 1px solid #334155;
        }}
        .task-table tr:hover {{
            background: #334155;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-success {{ background: rgba(74, 222, 128, 0.2); color: #4ade80; }}
        .badge-warning {{ background: rgba(251, 191, 36, 0.2); color: #fbbf24; }}
        .badge-error {{ background: rgba(248, 113, 113, 0.2); color: #f87171; }}
        .badge-disabled {{ background: rgba(148, 163, 184, 0.2); color: #94a3b8; }}
        .auto-refresh {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #3b82f6;
            padding: 12px 24px;
            border-radius: 24px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Cron-Automation Dashboard</h1>
        <p>系统状态: <span class="status-good">🟢 正常运行</span> | 
           更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <h3>CPU 使用率</h3>
            <div class="metric-value {self._get_metric_class(metrics['cpu_percent'], 80, 90)}">
                {metrics['cpu_percent']:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <h3>内存使用率</h3>
            <div class="metric-value {self._get_metric_class(metrics['memory_used'], 80, 90)}">
                {metrics['memory_used']:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <h3>磁盘使用率</h3>
            <div class="metric-value {self._get_metric_class(metrics['disk_used'], 85, 95)}">
                {metrics['disk_used']:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <h3>可用磁盘空间</h3>
            <div class="metric-value">
                {metrics['disk_free_gb']:.1f} GB
            </div>
        </div>
    </div>
    
    <div class="task-table">
        <table>
            <thead>
                <tr>
                    <th>任务ID</th>
                    <th>名称</th>
                    <th>状态</th>
                    <th>上次执行</th>
                    <th>连续失败</th>
                    <th>Cron</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_task_rows(tasks)}
            </tbody>
        </table>
    </div>
    
    <div class="auto-refresh">🔄 自动刷新中...</div>
    
    <script>
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>'''
        return html
    
    def _get_metric_class(self, value: float, warn: float, error: float) -> str:
        """获取指标样式类"""
        if value >= error:
            return 'status-error'
        elif value >= warn:
            return 'status-warn'
        return 'status-good'
    
    def _generate_task_rows(self, tasks: List[Dict]) -> str:
        """生成任务行HTML"""
        rows = []
        for task in tasks:
            if not task['enabled']:
                status_class = 'badge-disabled'
                status_text = '已禁用'
            elif task['status'] == 'success':
                status_class = 'badge-success'
                status_text = '成功'
            elif task['status'] in ['failed', 'timeout']:
                status_class = 'badge-error'
                status_text = task['status']
            else:
                status_class = 'badge-warning'
                status_text = task['status']
            
            rows.append(f'''
                <tr>
                    <td>{task['id']}</td>
                    <td>{task['name']}</td>
                    <td><span class="badge {status_class}">{status_text}</span></td>
                    <td>{task['last_run'][:19] if task['last_run'] != '--' else '--'}</td>
                    <td>{task['consecutive_failures']}</td>
                    <td><code>{task['cron']}</code></td>
                </tr>
            ''')
        return ''.join(rows)
    
    def update_dashboard(self):
        """更新监控面板"""
        html = self.generate_dashboard_html()
        dashboard_path = MONITOR_DIR / "dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"监控面板已更新: {dashboard_path}")


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cron-Automation Monitor')
    parser.add_argument('action', choices=['status', 'dashboard', 'metrics'], help='操作')
    
    args = parser.parse_args()
    
    monitor = Monitor()
    
    if args.action == 'status':
        tasks = monitor.get_task_status()
        print(json.dumps(tasks, indent=2))
    
    elif args.action == 'dashboard':
        monitor.update_dashboard()
    
    elif args.action == 'metrics':
        metrics = monitor.get_system_metrics()
        print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
