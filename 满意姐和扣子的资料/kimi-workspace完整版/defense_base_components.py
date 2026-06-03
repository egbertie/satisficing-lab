#!/usr/bin/env python3
"""
统一防御系统 - 基础组件库
提供公共功能和工具函数，减少代码重复
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class BaseComponent:
    """
    基础组件类
    所有防御系统组件的基类，提供通用功能
    """
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.workspace = "/root/.openclaw/workspace"
        self._ensure_workspace()
    
    def _ensure_workspace(self):
        """确保工作空间存在"""
        os.makedirs(self.workspace, exist_ok=True)
    
    def get_timestamp(self) -> str:
        """获取标准时间戳"""
        return datetime.now().isoformat()
    
    def get_date_string(self, days_offset: int = 0) -> str:
        """获取日期字符串"""
        from datetime import timedelta
        date = datetime.now() + timedelta(days=days_offset)
        return date.strftime('%Y-%m-%d')
    
    def load_json(self, filepath: str, default: Any = None) -> Any:
        """安全加载JSON文件"""
        if default is None:
            default = {}
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  加载JSON失败 {filepath}: {e}")
        return default
    
    def save_json(self, filepath: str, data: Any, indent: int = 2):
        """安全保存JSON文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else self.workspace, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存JSON失败 {filepath}: {e}")
            return False
    
    def append_jsonl(self, filepath: str, data: Dict):
        """追加JSONL格式"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
            return True
        except Exception as e:
            print(f"❌ 追加JSONL失败 {filepath}: {e}")
            return False
    
    def generate_checksum(self, data: Any) -> str:
        """生成数据校验和"""
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_checksum(self, data: Any, stored_checksum: str) -> bool:
        """验证数据校验和"""
        return self.generate_checksum(data) == stored_checksum
    
    def get_file_stats(self, filepath: str) -> Optional[Dict]:
        """获取文件统计信息"""
        try:
            stat = os.stat(filepath)
            return {
                'size': stat.st_size,
                'mtime': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'exists': True
            }
        except:
            return {'exists': False}
    
    def ensure_dir(self, *paths) -> str:
        """确保目录存在并返回路径"""
        full_path = os.path.join(self.workspace, *paths)
        os.makedirs(full_path, exist_ok=True)
        return full_path

class MetricsCollector(BaseComponent):
    """
    指标收集器
    统一收集和存储各类指标数据
    """
    
    def __init__(self, metrics_name: str):
        super().__init__(f"metrics_{metrics_name}")
        self.metrics_file = f"{self.workspace}/.{metrics_name}_metrics.json"
        self.data = self.load_json(self.metrics_file, {
            'records': [],
            'counters': {},
            'created_at': self.get_timestamp()
        })
    
    def record(self, **kwargs):
        """记录一条指标"""
        record = {
            'timestamp': self.get_timestamp(),
            **kwargs
        }
        self.data['records'].append(record)
        # 保留最近200条
        self.data['records'] = self.data['records'][-200:]
        self._save()
    
    def increment(self, counter_name: str, value: int = 1):
        """增加计数器"""
        if 'counters' not in self.data:
            self.data['counters'] = {}
        self.data['counters'][counter_name] = self.data['counters'].get(counter_name, 0) + value
        self._save()
    
    def get_counter(self, counter_name: str) -> int:
        """获取计数器值"""
        return self.data.get('counters', {}).get(counter_name, 0)
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """获取最近的记录"""
        return self.data['records'][-count:]
    
    def get_stats(self, days: int = 7) -> Dict:
        """获取统计信息"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        recent = [
            r for r in self.data['records']
            if datetime.fromisoformat(r['timestamp']) > cutoff
        ]
        
        return {
            'total_records': len(self.data['records']),
            'recent_records': len(recent),
            'counters': self.data.get('counters', {})
        }
    
    def _save(self):
        """保存数据"""
        self.save_json(self.metrics_file, self.data)

class IndexManager(BaseComponent):
    """
    索引管理器
    统一管理各类索引文件
    """
    
    def __init__(self, index_name: str):
        super().__init__(f"index_{index_name}")
        self.index_file = f"{self.workspace}/.{index_name}_index.json"
        self.index = self.load_json(self.index_file, {})
    
    def add(self, key: str, value: Dict):
        """添加索引项"""
        if key not in self.index:
            self.index[key] = []
        self.index[key].append(value)
        self._save()
    
    def get(self, key: str) -> List[Dict]:
        """获取索引项"""
        return self.index.get(key, [])
    
    def search(self, keyword: str) -> List[Dict]:
        """搜索索引"""
        results = []
        for key, values in self.index.items():
            if keyword.lower() in key.lower():
                results.extend(values)
        return results
    
    def get_all_keys(self) -> List[str]:
        """获取所有键"""
        return list(self.index.keys())
    
    def _save(self):
        """保存索引"""
        self.save_json(self.index_file, self.index)

class HistoryManager(BaseComponent):
    """
    历史记录管理器
    统一管理历史记录，支持限制条数
    """
    
    def __init__(self, history_name: str, max_records: int = 100):
        super().__init__(f"history_{history_name}")
        self.history_file = f"{self.workspace}/.{history_name}_history.json"
        self.max_records = max_records
        self.records = self.load_json(self.history_file, [])
    
    def add(self, record: Dict):
        """添加记录"""
        record['timestamp'] = self.get_timestamp()
        self.records.append(record)
        # 限制条数
        self.records = self.records[-self.max_records:]
        self._save()
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """获取最近记录"""
        return self.records[-count:]
    
    def find_similar(self, query: str, threshold: float = 0.6) -> List[Dict]:
        """查找相似记录（简单关键词匹配）"""
        query_words = set(query.lower().split())
        results = []
        
        for record in self.records:
            # 从记录中提取可搜索文本
            text = record.get('query', '') + ' ' + record.get('content', '')
            text_words = set(text.lower().split())
            
            if query_words and text_words:
                overlap = len(query_words & text_words) / len(query_words | text_words)
                if overlap >= threshold:
                    results.append({
                        'record': record,
                        'similarity': overlap
                    })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def clear(self):
        """清空历史"""
        self.records = []
        self._save()
    
    def _save(self):
        """保存历史"""
        self.save_json(self.history_file, self.records)

# 快捷函数
def quick_timestamp() -> str:
    """快速获取时间戳"""
    return datetime.now().isoformat()

def quick_hash(content: str) -> str:
    """快速生成哈希"""
    return hashlib.sha256(content.encode()).hexdigest()[:12]

def format_bytes(size: int) -> str:
    """格式化字节大小"""
    for unit in ['B', 'KB', 'MB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"

if __name__ == "__main__":
    # 测试基础组件
    print("=" * 60)
    print("🔧 基础组件库测试")
    print("=" * 60)
    
    # 测试BaseComponent
    base = BaseComponent("test")
    print(f"\n[测试1] BaseComponent")
    print(f"   时间戳: {base.get_timestamp()}")
    print(f"   校验和测试: {base.generate_checksum({'test': 'data'})[:16]}...")
    
    # 测试MetricsCollector
    print(f"\n[测试2] MetricsCollector")
    metrics = MetricsCollector("test")
    metrics.record(action="test", value=1)
    metrics.increment("test_counter")
    stats = metrics.get_stats()
    print(f"   记录数: {stats['total_records']}")
    print(f"   计数器: {stats['counters']}")
    
    # 测试IndexManager
    print(f"\n[测试3] IndexManager")
    index = IndexManager("test")
    index.add("keyword1", {"data": "value1"})
    index.add("keyword1", {"data": "value2"})
    results = index.get("keyword1")
    print(f"   索引项数: {len(results)}")
    
    # 测试HistoryManager
    print(f"\n[测试4] HistoryManager")
    history = HistoryManager("test", max_records=5)
    history.add({"query": "测试查询", "result": "测试结果"})
    recent = history.get_recent(1)
    print(f"   最近记录: {recent[0]['query'] if recent else '无'}")
    
    print("\n" + "=" * 60)
    print("✅ 基础组件库测试完成")
    print("=" * 60)
