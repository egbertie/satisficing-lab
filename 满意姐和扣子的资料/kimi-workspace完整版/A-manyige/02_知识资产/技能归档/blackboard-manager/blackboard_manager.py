#!/usr/bin/env python3
"""
blackboard-manager: 共享内存状态管理
实现Worker间状态共享（Blackboard模式）

作者: 满意妞
版本: 1.0.0
日期: 2026-03-28
"""

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import copy


@dataclass
class StateEntry:
    """状态条目"""
    key: str
    value: Any
    version: int = 1
    writer_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "key": self.key,
            "value": self.value,
            "version": self.version,
            "writer_id": self.writer_id,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "StateEntry":
        """从字典反序列化"""
        return cls(
            key=data["key"],
            value=data["value"],
            version=data.get("version", 1),
            writer_id=data.get("writer_id", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


class BlackboardManager:
    """
    Blackboard管理器 - 共享内存状态管理
    
    实现Blackboard设计模式，允许多个Worker共享状态
    通过乐观锁（版本号）处理并发写入
    """
    
    def __init__(
        self,
        storage_path: str = "~/.openclaw/system-v2/blackboard/state.yaml",
        auto_save_interval: int = 300,  # 5分钟自动保存
    ):
        """
        初始化Blackboard管理器
        
        Args:
            storage_path: 状态存储路径
            auto_save_interval: 自动保存间隔（秒）
        """
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._state: Dict[str, StateEntry] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()
        self._auto_save_interval = auto_save_interval
        self._last_save = time.time()
        
        # 加载已有状态
        self._load_state()
    
    def _load_state(self):
        """从存储加载状态"""
        if self.storage_path.exists():
            try:
                import yaml
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                
                for key, entry_data in data.items():
                    self._state[key] = StateEntry.from_dict(entry_data)
            except Exception as e:
                print(f"[Blackboard] 加载状态失败: {e}")
    
    def _save_state(self):
        """保存状态到存储"""
        try:
            import yaml
            data = {key: entry.to_dict() for key, entry in self._state.items()}
            
            # 原子写入（先写临时文件，再重命名）
            temp_path = self.storage_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=True)
            
            temp_path.replace(self.storage_path)
            self._last_save = time.time()
            
        except Exception as e:
            print(f"[Blackboard] 保存状态失败: {e}")
    
    def read(self, key: str, default: Any = None) -> Tuple[Any, int]:
        """
        读取状态
        
        Args:
            key: 状态键
            default: 默认值（如果键不存在）
            
        Returns:
            (值, 版本号)
        """
        with self._lock:
            if key in self._state:
                entry = self._state[key]
                return copy.deepcopy(entry.value), entry.version
            return default, 0
    
    def write(
        self,
        key: str,
        value: Any,
        writer_id: str = "",
        expected_version: Optional[int] = None,
    ) -> Tuple[bool, int, str]:
        """
        写入状态（乐观锁）
        
        Args:
            key: 状态键
            value: 状态值
            writer_id: 写入者ID
            expected_version: 期望的当前版本（乐观锁）
            
        Returns:
            (成功标志, 新版本号, 消息)
        """
        with self._lock:
            current_entry = self._state.get(key)
            current_version = current_entry.version if current_entry else 0
            
            # 乐观锁检查
            if expected_version is not None and current_version != expected_version:
                return (
                    False,
                    current_version,
                    f"版本冲突: 期望 {expected_version}, 实际 {current_version}",
                )
            
            # 写入新状态
            new_entry = StateEntry(
                key=key,
                value=copy.deepcopy(value),
                version=current_version + 1,
                writer_id=writer_id,
            )
            self._state[key] = new_entry
            
            # 自动保存检查
            if time.time() - self._last_save > self._auto_save_interval:
                self._save_state()
            
            # 通知订阅者
            self._notify_subscribers(key, new_entry)
            
            return True, new_entry.version, "写入成功"
    
    def delete(self, key: str, expected_version: Optional[int] = None) -> Tuple[bool, str]:
        """
        删除状态
        
        Args:
            key: 状态键
            expected_version: 期望的当前版本
            
        Returns:
            (成功标志, 消息)
        """
        with self._lock:
            if key not in self._state:
                return False, "键不存在"
            
            current_version = self._state[key].version
            
            # 乐观锁检查
            if expected_version is not None and current_version != expected_version:
                return False, f"版本冲突: 期望 {expected_version}, 实际 {current_version}"
            
            del self._state[key]
            
            # 自动保存检查
            if time.time() - self._last_save > self._auto_save_interval:
                self._save_state()
            
            return True, "删除成功"
    
    def subscribe(self, key: str, callback: Callable[[str, Any, int], None]):
        """
        订阅状态变更
        
        Args:
            key: 状态键
            callback: 回调函数(键, 新值, 新版本)
        """
        with self._lock:
            if key not in self._subscribers:
                self._subscribers[key] = []
            self._subscribers[key].append(callback)
    
    def unsubscribe(self, key: str, callback: Callable):
        """取消订阅"""
        with self._lock:
            if key in self._subscribers and callback in self._subscribers[key]:
                self._subscribers[key].remove(callback)
    
    def _notify_subscribers(self, key: str, entry: StateEntry):
        """通知订阅者"""
        if key in self._subscribers:
            for callback in self._subscribers[key]:
                try:
                    callback(key, entry.value, entry.version)
                except Exception as e:
                    print(f"[Blackboard] 订阅者回调失败: {e}")
    
    def get_all_keys(self) -> List[str]:
        """获取所有状态键"""
        with self._lock:
            return list(self._state.keys())
    
    def get_snapshot(self) -> Dict[str, Any]:
        """
        获取状态快照
        
        Returns:
            所有状态的副本
        """
        with self._lock:
            return {
                key: {
                    "value": copy.deepcopy(entry.value),
                    "version": entry.version,
                    "writer_id": entry.writer_id,
                    "timestamp": entry.timestamp,
                }
                for key, entry in self._state.items()
            }
    
    def force_save(self):
        """强制保存状态"""
        with self._lock:
            self._save_state()
    
    def clear(self):
        """清空所有状态（谨慎使用）"""
        with self._lock:
            self._state.clear()
            self._save_state()


def main():
    """CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Blackboard Manager - 共享内存状态")
    parser.add_argument("--read", type=str, help="读取状态键")
    parser.add_argument("--write", type=str, help="写入状态键")
    parser.add_argument("--value", type=str, help="写入的值（JSON格式）")
    parser.add_argument("--writer", type=str, default="cli", help="写入者ID")
    parser.add_argument("--list", action="store_true", help="列出所有键")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    manager = BlackboardManager()
    
    if args.read:
        value, version = manager.read(args.read)
        print(f"{args.read} = {json.dumps(value, ensure_ascii=False)} (v{version})")
    
    elif args.write:
        if args.value is None:
            print("❌ 需要 --value 参数")
            exit(1)
        
        try:
            value = json.loads(args.value)
        except json.JSONDecodeError:
            value = args.value  # 非JSON，作为字符串
        
        success, version, msg = manager.write(args.write, value, args.writer)
        if success:
            print(f"✅ {args.write} = {json.dumps(value, ensure_ascii=False)} (v{version})")
        else:
            print(f"❌ {msg}")
            exit(1)
    
    elif args.list:
        keys = manager.get_all_keys()
        if keys:
            print("📋 所有状态键:")
            for key in keys:
                value, version = manager.read(key)
                print(f"  • {key} = {json.dumps(value, ensure_ascii=False)[:50]}... (v{version})")
        else:
            print("📭 无状态")
    
    elif args.test:
        print("🧪 请运行: python3 -m pytest test_blackboard_manager.py")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
