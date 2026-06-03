#!/usr/bin/env python3
"""
数据验证脚本 - 验证监控数据的准确性
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DataValidator:
    """数据验证器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.errors = []
        self.warnings = []
    
    def _load_metrics(self) -> list:
        """加载所有指标数据"""
        metrics = []
        data_file = self.data_dir / "metrics.jsonl"
        
        if not data_file.exists():
            return metrics
        
        with open(data_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())
                    record['_line_num'] = line_num
                    metrics.append(record)
                except json.JSONDecodeError as e:
                    self.errors.append(f"行 {line_num}: JSON 解析错误 - {e}")
        
        return metrics
    
    def validate_schema(self, metrics: list) -> bool:
        """验证数据模式"""
        required_fields = ['name', 'vendor', 'endpoint', 'timestamp', 'success', 'response_time_ms']
        
        for record in metrics:
            line_num = record.get('_line_num', '?')
            for field in required_fields:
                if field not in record:
                    self.errors.append(f"行 {line_num}: 缺少必需字段 '{field}'")
        
        return len(self.errors) == 0
    
    def validate_consistency(self, metrics: list) -> bool:
        """验证数据一致性"""
        for record in metrics:
            line_num = record.get('_line_num', '?')
            
            # 验证响应时间非负
            if record.get('response_time_ms', 0) < 0:
                self.errors.append(f"行 {line_num}: 响应时间为负值")
            
            # 验证状态码范围
            status_code = record.get('status_code')
            if status_code is not None and (status_code < 100 or status_code > 599):
                self.warnings.append(f"行 {line_num}: 异常状态码 {status_code}")
            
            # 验证成功状态与错误信息一致性
            if record.get('success') and record.get('error'):
                self.warnings.append(f"行 {line_num}: 成功但有错误信息 '{record['error']}'")
            
            if not record.get('success') and not record.get('error'):
                self.warnings.append(f"行 {line_num}: 失败但无错误信息")
            
            # 验证时间戳格式
            try:
                datetime.fromisoformat(record.get('timestamp', ''))
            except (ValueError, TypeError):
                self.errors.append(f"行 {line_num}: 无效的时间戳格式")
        
        return len(self.errors) == 0
    
    def validate_timeline(self, metrics: list) -> bool:
        """验证时间线连续性"""
        if not metrics:
            return True
        
        # 按厂商分组检查
        by_vendor = {}
        for record in metrics:
            vendor = record.get('vendor', 'unknown')
            if vendor not in by_vendor:
                by_vendor[vendor] = []
            by_vendor[vendor].append(record)
        
        for vendor, records in by_vendor.items():
            # 按时间排序
            sorted_records = sorted(records, key=lambda x: x.get('timestamp', ''))
            
            # 检查时间间隔
            timestamps = [datetime.fromisoformat(r['timestamp']) for r in sorted_records if 'timestamp' in r]
            
            for i in range(1, len(timestamps)):
                gap = (timestamps[i] - timestamps[i-1]).total_seconds()
                # 如果间隔超过10分钟，发出警告
                if gap > 600:
                    self.warnings.append(f"{vendor}: 检测到 {gap/60:.1f} 分钟的数据缺口")
        
        return True
    
    def validate_against_benchmark(self, benchmark_url: str = "https://httpbin.org/get") -> dict:
        """使用基准 API 验证监控逻辑"""
        import requests
        
        result = {
            'benchmark_url': benchmark_url,
            'test_time': datetime.now().isoformat(),
            'success': False,
            'details': []
        }
        
        try:
            # 直接测试
            start = datetime.now()
            response = requests.get(benchmark_url, timeout=10)
            direct_latency = (datetime.now() - start).total_seconds() * 1000
            
            # 通过 probe 测试
            from scripts.probe import APIProbe
            probe_config = {
                'name': 'benchmark',
                'vendor': 'benchmark',
                'endpoint': benchmark_url,
                'method': 'GET',
                'timeout': 10
            }
            probe = APIProbe(probe_config)
            probe_result = probe.probe()
            
            # 对比结果
            latency_diff = abs(direct_latency - probe_result['response_time_ms'])
            result['direct_latency'] = round(direct_latency, 2)
            result['probe_latency'] = probe_result['response_time_ms']
            result['latency_diff_ms'] = round(latency_diff, 2)
            result['success'] = probe_result['success']
            
            if latency_diff > 100:  # 差异超过100ms
                result['details'].append(f"延迟测量差异较大: {latency_diff:.2f}ms")
            
            if not probe_result['success'] and response.status_code == 200:
                result['details'].append("监控逻辑误判成功请求为失败")
            
            if probe_result['success'] and response.status_code != 200:
                result['details'].append("监控逻辑误判失败请求为成功")
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def run_validation(self, benchmark: bool = False) -> dict:
        """运行完整验证"""
        print("🔍 开始数据验证...")
        
        metrics = self._load_metrics()
        print(f"加载了 {len(metrics)} 条指标记录")
        
        # 运行验证
        self.validate_schema(metrics)
        self.validate_consistency(metrics)
        self.validate_timeline(metrics)
        
        result = {
            'validated_at': datetime.now().isoformat(),
            'total_records': len(metrics),
            'errors': self.errors,
            'warnings': self.warnings,
            'valid': len(self.errors) == 0
        }
        
        if benchmark:
            result['benchmark'] = self.validate_against_benchmark()
        
        return result
    
    def print_report(self, result: dict):
        """打印验证报告"""
        print("\n" + "="*50)
        print("📋 验证报告")
        print("="*50)
        print(f"验证时间: {result['validated_at']}")
        print(f"记录总数: {result['total_records']}")
        print(f"验证结果: {'✅ 通过' if result['valid'] else '❌ 失败'}")
        
        if result['errors']:
            print(f"\n❌ 错误 ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print(f"\n⚠️ 警告 ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if 'benchmark' in result:
            bench = result['benchmark']
            print(f"\n📊 基准测试:")
            print(f"  直接延迟: {bench.get('direct_latency')}ms")
            print(f"  探测延迟: {bench.get('probe_latency')}ms")
            print(f"  差异: {bench.get('latency_diff_ms')}ms")
            if bench.get('details'):
                for detail in bench['details']:
                    print(f"  ⚠️ {detail}")
        
        print("="*50)


def main():
    parser = argparse.ArgumentParser(description='验证监控数据准确性')
    parser.add_argument('--data-dir', '-d', default='data', help='数据目录')
    parser.add_argument('--benchmark', '-b', action='store_true', help='运行基准测试')
    parser.add_argument('--json', '-j', action='store_true', help='JSON 输出')
    
    args = parser.parse_args()
    
    validator = DataValidator(args.data_dir)
    result = validator.run_validation(benchmark=args.benchmark)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        validator.print_report(result)
    
    sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
