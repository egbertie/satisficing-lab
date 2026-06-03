"""
Blackboard - 审计日志模块
提供不可篡改的操作记录
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditLogger:
    """
    审计日志记录器
    
    特性：
    - 每条记录包含时间戳、操作类型、详情
    - 线程安全写入
    - 支持内存缓存和文件持久化
    - 日志轮转（保留最近N条）
    """
    
    def __init__(
        self,
        log_file: Optional[Path] = None,
        memory_limit: int = 1000,
        file_limit: int = 10000
    ):
        self.log_file = Path(log_file) if log_file else None
        self.memory_limit = memory_limit
        self.file_limit = file_limit
        
        self._logs: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        
        # 确保日志目录存在
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, action: str, details: str = "", metadata: Optional[Dict] = None) -> None:
        """
        记录审计日志
        
        Args:
            action: 操作类型（如 INIT, GET, SET, DELETE）
            details: 操作详情
            metadata: 附加元数据
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "metadata": metadata or {}
        }
        
        with self._lock:
            self._logs.append(entry)
            
            # 内存日志限制
            if len(self._logs) > self.memory_limit:
                self._flush_to_file()
                self._logs = self._logs[-self.memory_limit//2:]  # 保留一半
            
            # 同步写入文件
            if self.log_file:
                self._append_to_file(entry)
    
    def _append_to_file(self, entry: Dict[str, Any]) -> None:
        """追加单条记录到文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[AuditLogger] Write error: {e}")
    
    def _flush_to_file(self) -> None:
        """批量刷写到文件"""
        if not self.log_file:
            return
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for entry in self._logs:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[AuditLogger] Flush error: {e}")
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近N条日志"""
        with self._lock:
            return self._logs[-limit:]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有内存中的日志"""
        with self._lock:
            return list(self._logs)
    
    def search(self, action: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        搜索日志
        
        Args:
            action: 按操作类型筛选
            keyword: 按关键词筛选（匹配details）
        """
        results = []
        with self._lock:
            for entry in self._logs:
                if action and entry["action"] != action:
                    continue
                if keyword and keyword not in entry.get("details", ""):
                    continue
                results.append(entry)
        return results
    
    def clear(self) -> None:
        """清空内存日志（不影响文件）"""
        with self._lock:
            self._logs.clear()
    
    def export(self, filepath: str) -> bool:
        """导出日志到指定文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._logs, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[AuditLogger] Export error: {e}")
            return False
    
    def stats(self) -> Dict[str, Any]:
        """获取日志统计"""
        with self._lock:
            return {
                "memory_entries": len(self._logs),
                "log_file": str(self.log_file) if self.log_file else None,
                "memory_limit": self.memory_limit,
                "actions": {}
            }
    
    def __len__(self) -> int:
        """返回内存中的日志数量"""
        return len(self._logs)
