#!/usr/bin/env python3
"""
对抗测试脚本 - 模拟 API 故障场景
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ChaosHTTPHandler(BaseHTTPRequestHandler):
    """模拟故障的 HTTP 处理器"""
    
    config = {
        'fault_type': 'none',
        'latency_ms': 0,
        'error_rate': 0,
        'status_code': 200
    }
    
    def log_message(self, format, *args):
        pass  # 静默日志
    
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def _handle_request(self):
        import random
        
        fault = self.config['fault_type']
        
        # 模拟延迟
        if fault == 'latency' or self.config['latency_ms'] > 0:
            time.sleep(self.config['latency_ms'] / 1000)
        
        # 模拟超时
        if fault == 'timeout':
            time.sleep(30)  # 长时间等待
            return
        
        # 模拟错误率
        if fault == 'error' or self.config['error_rate'] > 0:
            if random.random() < (self.config['error_rate'] / 100):
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'{"error": "internal server error"}')
                return
        
        # 模拟特定状态码
        if fault == 'status':
            self.send_response(self.config['status_code'])
            self.end_headers()
            self.wfile.write(json.dumps({"error": "simulated error"}).encode())
            return
        
        # 正常响应
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "fault_simulation": fault if fault != 'none' else None
        }).encode())


class ChaosServer:
    """故障模拟服务器"""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.server = None
        self.thread = None
        
    def start(self, fault_type: str = 'none', **kwargs):
        """启动故障模拟服务器"""
        ChaosHTTPHandler.config['fault_type'] = fault_type
        for k, v in kwargs.items():
            ChaosHTTPHandler.config[k] = v
        
        self.server = HTTPServer(('127.0.0.1', self.port), ChaosHTTPHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"故障模拟服务器启动: http://127.0.0.1:{self.port}")
        print(f"故障类型: {fault_type}")
        
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.shutdown()
            print("故障模拟服务器已停止")


def run_with_fault(fault_type: str, duration: int, **kwargs):
    """运行指定时长的故障测试"""
    server = ChaosServer()
    
    try:
        server.start(fault_type, **kwargs)
        print(f"\n测试将持续 {duration} 秒...")
        print(f"测试 URL: http://127.0.0.1:8765/test")
        print("\n你可以在其他终端运行:")
        print(f"  python3 scripts/probe.py -u http://127.0.0.1:8765/test -n chaos_test\n")
        
        time.sleep(duration)
        
    except KeyboardInterrupt:
        print("\n测试被中断")
    finally:
        server.stop()


def main():
    parser = argparse.ArgumentParser(description='API 对抗测试工具')
    parser.add_argument('--fault', '-f', 
                       choices=['none', 'timeout', 'latency', 'error', 'status'],
                       default='none',
                       help='故障类型')
    parser.add_argument('--duration', '-d', type=int, default=60,
                       help='测试持续时间(秒)')
    parser.add_argument('--latency', '-l', type=int, default=5000,
                       help='模拟延迟(毫秒)')
    parser.add_argument('--error-rate', '-e', type=int, default=50,
                       help='错误率百分比')
    parser.add_argument('--status-code', '-s', type=int, default=500,
                       help='模拟的 HTTP 状态码')
    parser.add_argument('--test-probe', '-t', action='store_true',
                       help='同时运行探测测试')
    
    args = parser.parse_args()
    
    kwargs = {}
    if args.fault == 'latency':
        kwargs['latency_ms'] = args.latency
    elif args.fault == 'error':
        kwargs['error_rate'] = args.error_rate
    elif args.fault == 'status':
        kwargs['status_code'] = args.status_code
    
    if args.test_probe:
        # 在后台启动测试
        server = ChaosServer()
        server.start(args.fault, **kwargs)
        
        # 运行探测
        import subprocess
        time.sleep(1)  # 等待服务器启动
        
        print(f"\n执行探测测试...")
        for i in range(5):
            result = subprocess.run(
                ['python3', 'scripts/probe.py', '-u', 'http://127.0.0.1:8765/test', 
                 '-n', f'chaos_{i}', '-j'],
                capture_output=True,
                text=True
            )
            data = json.loads(result.stdout)
            status = "✅" if data['success'] else "❌"
            print(f"{status} 探测 {i+1}: {data['response_time_ms']}ms - {data.get('error', 'OK')}")
            time.sleep(2)
        
        server.stop()
    else:
        run_with_fault(args.fault, args.duration, **kwargs)


if __name__ == '__main__':
    main()
