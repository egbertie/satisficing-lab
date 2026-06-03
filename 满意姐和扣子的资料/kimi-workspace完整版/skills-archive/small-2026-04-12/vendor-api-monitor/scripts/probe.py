#!/usr/bin/env python3
"""
API 探测脚本 - 执行单个 API 端点健康检查
"""

import argparse
import json
import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def resolve_env_vars(value):
    """解析环境变量占位符 ${VAR_NAME}"""
    if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
        var_name = value[2:-1]
        return os.getenv(var_name, value)
    return value


class APIProbe:
    """API 探测执行器"""
    
    def __init__(self, config: Dict):
        self.name = config.get('name', 'unknown')
        self.vendor = config.get('vendor', 'unknown')
        self.endpoint = config.get('endpoint', '')
        self.method = config.get('method', 'GET').upper()
        self.headers = {k: resolve_env_vars(v) for k, v in config.get('headers', {}).items()}
        self.params = {k: resolve_env_vars(v) for k, v in config.get('params', {}).items()}
        self.body = config.get('body', '')
        self.timeout = config.get('timeout', 10)
        
    def probe(self) -> Dict:
        """执行探测并返回结果"""
        start_time = time.time()
        result = {
            "name": self.name,
            "vendor": self.vendor,
            "endpoint": self.endpoint,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "response_time_ms": 0,
            "status_code": None,
            "error": None
        }
        
        try:
            # 解析 body
            json_body = None
            if self.body:
                try:
                    json_body = json.loads(self.body)
                except json.JSONDecodeError:
                    pass
            
            # 执行请求
            response = requests.request(
                method=self.method,
                url=self.endpoint,
                headers=self.headers,
                params=self.params if self.params else None,
                json=json_body if json_body else None,
                data=self.body if not json_body and self.body else None,
                timeout=self.timeout,
                allow_redirects=False
            )
            
            elapsed = (time.time() - start_time) * 1000
            result["response_time_ms"] = round(elapsed, 2)
            result["status_code"] = response.status_code
            result["success"] = 200 <= response.status_code < 300
            
            # 检查特定错误
            if response.status_code >= 500:
                result["error"] = f"Server error: {response.status_code}"
            elif response.status_code >= 400:
                result["error"] = f"Client error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            result["error"] = "timeout"
            result["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        except requests.exceptions.ConnectionError:
            result["error"] = "connection_error"
        except requests.exceptions.SSLError:
            result["error"] = "ssl_error"
        except Exception as e:
            result["error"] = str(e)
            
        return result


def main():
    parser = argparse.ArgumentParser(description='API 探测工具')
    parser.add_argument('--url', '-u', help='直接指定 URL')
    parser.add_argument('--method', '-m', default='GET', help='HTTP 方法')
    parser.add_argument('--timeout', '-t', type=int, default=10, help='超时时间(秒)')
    parser.add_argument('--vendor', '-v', default='generic', help='厂商名称')
    parser.add_argument('--name', '-n', default='probe', help='探测名称')
    parser.add_argument('--json', '-j', action='store_true', help='JSON 输出')
    
    args = parser.parse_args()
    
    if args.url:
        config = {
            'name': args.name,
            'vendor': args.vendor,
            'endpoint': args.url,
            'method': args.method,
            'timeout': args.timeout
        }
    else:
        print("错误: 必须指定 --url 或使用配置文件")
        sys.exit(1)
    
    probe = APIProbe(config)
    result = probe.probe()
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['name']}")
        print(f"   状态: {'成功' if result['success'] else '失败'}")
        print(f"   延迟: {result['response_time_ms']}ms")
        if result['status_code']:
            print(f"   HTTP: {result['status_code']}")
        if result['error']:
            print(f"   错误: {result['error']}")
    
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
