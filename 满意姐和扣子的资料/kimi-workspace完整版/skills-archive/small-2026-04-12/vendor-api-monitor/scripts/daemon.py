#!/usr/bin/env python3
"""
监控守护进程 - 持续执行 API 监控
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.probe import APIProbe


class MonitorDaemon:
    """监控守护进程"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.running = False
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 信号处理
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _load_config(self) -> dict:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            print(f"警告: 配置文件 {self.config_path} 不存在，使用默认配置")
            return {'monitors': [], 'alerts': {'enabled': False}}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _signal_handler(self, signum, frame):
        """处理终止信号"""
        print(f"\n收到信号 {signum}，正在停止...")
        self.running = False
    
    def _save_metric(self, result: dict):
        """保存指标到文件"""
        data_file = self.data_dir / "metrics.jsonl"
        with open(data_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    def _check_alerts(self, result: dict):
        """检查是否需要触发告警"""
        if not self.config.get('alerts', {}).get('enabled'):
            return
        
        alerts_config = self.config.get('alerts', {})
        rules = alerts_config.get('rules', [])
        
        for rule in rules:
            condition = rule.get('condition', '')
            severity = rule.get('severity', 'info')
            
            # 简单的条件解析
            triggered = False
            if 'availability' in condition and not result.get('success'):
                triggered = True
            elif 'latency' in condition:
                threshold = int(condition.split('>')[-1].strip())
                if result.get('response_time_ms', 0) > threshold:
                    triggered = True
            
            if triggered:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'severity': severity,
                    'rule': rule.get('name'),
                    'vendor': result.get('vendor'),
                    'endpoint': result.get('endpoint'),
                    'message': rule.get('message', '').format(**result)
                }
                
                # 保存告警
                alerts_file = Path("reports/alerts.json")
                alerts_file.parent.mkdir(exist_ok=True)
                
                alerts = []
                if alerts_file.exists():
                    with open(alerts_file, 'r', encoding='utf-8') as f:
                        try:
                            alerts = json.load(f)
                        except json.JSONDecodeError:
                            alerts = []
                
                alerts.append(alert)
                
                # 保留最近100条告警
                alerts = alerts[-100:]
                
                with open(alerts_file, 'w', encoding='utf-8') as f:
                    json.dump(alerts, f, indent=2, ensure_ascii=False)
                
                # 控制台输出
                print(f"⚠️ 告警 [{severity.upper()}] {alert['message']}")
    
    def _run_probe_cycle(self):
        """执行一轮探测"""
        monitors = self.config.get('monitors', [])
        
        for monitor_config in monitors:
            if not monitor_config.get('enabled', True):
                continue
            
            try:
                probe = APIProbe(monitor_config)
                result = probe.probe()
                
                # 保存指标
                self._save_metric(result)
                
                # 检查告警
                self._check_alerts(result)
                
                # 输出状态
                status = "✅" if result['success'] else "❌"
                print(f"{status} {result['vendor']}/{result['name']}: "
                      f"{result['response_time_ms']}ms")
                
            except Exception as e:
                print(f"❌ 探测失败 {monitor_config.get('name')}: {e}")
    
    def run(self, once: bool = False):
        """运行守护进程"""
        print(f"🚀 监控守护进程启动")
        print(f"配置文件: {self.config_path}")
        print(f"数据目录: {self.data_dir}")
        print(f"监控目标: {len([m for m in self.config.get('monitors', []) if m.get('enabled', True)])} 个")
        print("-" * 50)
        
        if once:
            self._run_probe_cycle()
            return
        
        self.running = True
        last_reload = time.time()
        
        while self.running:
            # 每小时重新加载配置
            if time.time() - last_reload > 3600:
                self.config = self._load_config()
                last_reload = time.time()
                print("[配置已重新加载]")
            
            self._run_probe_cycle()
            
            # 等待下一个周期
            interval = self.config.get('metrics', {}).get('availability', {}).get('check_interval', 60)
            
            # 分段等待以便快速响应信号
            for _ in range(interval):
                if not self.running:
                    break
                time.sleep(1)
        
        print("\n👋 监控守护进程已停止")


def main():
    parser = argparse.ArgumentParser(description='API 监控守护进程')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')
    parser.add_argument('--once', '-o', action='store_true', help='只执行一次')
    
    args = parser.parse_args()
    
    daemon = MonitorDaemon(args.config)
    daemon.run(once=args.once)


if __name__ == '__main__':
    main()
