#!/usr/bin/env python3
"""
recovery_checker.py
恢复条件检查器 - 检查API可用性、Token充足性等
"""

import os
import time
import json
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class RecoveryChecker:
    """
    恢复条件检查器
    
    检查以下条件：
    1. API可用性
    2. Token充足性
    3. 速率限制状态
    4. 系统资源
    """
    
    def __init__(self, cooldown_seconds: int = 60):
        self.cooldown_seconds = cooldown_seconds
        self.last_checks = {
            "api": 0,
            "token": 0,
            "rate_limit": 0,
            "system": 0
        }
        self._cache = {}
        self._cache_time = 0
        self._cache_ttl = 10  # 缓存10秒
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return time.time() - self._cache_time < self._cache_ttl
    
    def check_all(self, use_cache: bool = True) -> Dict[str, Tuple[bool, str]]:
        """
        检查所有恢复条件
        
        Returns:
            Dict[条件名, (是否通过, 说明)]
        """
        if use_cache and self._is_cache_valid():
            return self._cache
        
        results = {
            "api_available": self._check_api(),
            "token_sufficient": self._check_token(),
            "rate_limit_ok": self._check_rate_limit(),
            "system_resources_ok": self._check_system()
        }
        
        self._cache = results
        self._cache_time = time.time()
        return results
    
    def _check_api(self) -> Tuple[bool, str]:
        """
        检查API连通性
        
        简化实现：假设API可用
        实际应该调用轻量级健康检查端点
        """
        current_time = time.time()
        if current_time - self.last_checks["api"] < self.cooldown_seconds:
            return (True, "API检查冷却中，假设可用")
        
        self.last_checks["api"] = current_time
        
        # 这里可以添加实际的API健康检查
        # 例如：尝试访问一个轻量级端点
        try:
            # 简化：检查环境变量是否存在
            if os.environ.get('GITHUB_TOKEN') or os.environ.get('OPENAI_API_KEY'):
                return (True, "API密钥存在")
            return (True, "无API密钥检查，假设可用")
        except Exception as e:
            return (False, f"API检查失败: {e}")
    
    def _check_token(self) -> Tuple[bool, str]:
        """检查Token是否充足"""
        current_time = time.time()
        if current_time - self.last_checks["token"] < self.cooldown_seconds:
            return (True, "Token检查冷却中")
        
        self.last_checks["token"] = current_time
        
        try:
            # 读取token监控状态（兼容新旧路径）
            token_files = [
                '/root/.openclaw/workspace/memory/token-dynamic-tracker.json',
                '/root/.openclaw/workspace/memory/token-weekly-monitor.json',
            ]
            consumed_pct = None
            for token_file in token_files:
                if os.path.exists(token_file):
                    with open(token_file, 'r') as f:
                        data = json.load(f)
                    # 新结构
                    if 'snapshots' in data and len(data['snapshots']) > 0:
                        consumed_pct = data['snapshots'][-1].get('token_consumed_pct')
                    # 旧结构备用
                    elif 'currentStatus' in data:
                        consumed_pct = data['currentStatus'].get('percentage')
                    if consumed_pct is not None:
                        break

            if consumed_pct is not None:
                # 消耗低于85%认为充足（留15%缓冲）
                if consumed_pct < 85:
                    return (True, f"Token充足 ({consumed_pct}%消耗)")
                else:
                    return (False, f"Token紧张 ({consumed_pct}%消耗)")

            return (True, "无Token状态文件，假设充足")
        except Exception as e:
            return (True, f"Token检查异常，假设充足: {e}")
    
    def _check_rate_limit(self) -> Tuple[bool, str]:
        """检查速率限制是否已清除"""
        current_time = time.time()
        if current_time - self.last_checks["rate_limit"] < self.cooldown_seconds:
            return (True, "速率限制检查冷却中")
        
        self.last_checks["rate_limit"] = current_time
        
        # 简化实现：等待足够时间后假设已清除
        # 实际应该检查API返回的rate limit headers
        return (True, "假设速率限制已清除")
    
    def _check_system(self) -> Tuple[bool, str]:
        """检查系统资源"""
        current_time = time.time()
        if current_time - self.last_checks["system"] < self.cooldown_seconds:
            return (True, "系统检查冷却中")
        
        self.last_checks["system"] = current_time
        
        try:
            # 尝试导入psutil
            import psutil
            
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            issues = []
            
            if cpu > 90:
                issues.append(f"CPU过高({cpu}%)")
            if memory.percent > 90:
                issues.append(f"内存过高({memory.percent}%)")
            if disk.percent > 95:
                issues.append(f"磁盘过高({disk.percent}%)")
            
            if issues:
                return (False, f"系统资源紧张: {', '.join(issues)}")
            
            return (True, f"系统资源正常 CPU:{cpu}% 内存:{memory.percent}% 磁盘:{disk.percent}%")
            
        except ImportError:
            return (True, "无psutil，跳过系统检查")
        except Exception as e:
            return (True, f"系统检查异常，假设正常: {e}")
    
    def can_recover(self) -> bool:
        """是否可以恢复（所有条件都满足）"""
        results = self.check_all()
        return all(result[0] for result in results.values())
    
    def get_recovery_blockers(self) -> List[str]:
        """获取阻碍恢复的条件列表"""
        results = self.check_all()
        blockers = []
        for name, (passed, message) in results.items():
            if not passed:
                blockers.append(f"{name}: {message}")
        return blockers
    
    def format_status(self) -> str:
        """格式化状态报告"""
        results = self.check_all()
        lines = ["恢复条件检查:", "=" * 40]
        
        for name, (passed, message) in results.items():
            icon = "✅" if passed else "❌"
            lines.append(f"{icon} {name}: {message}")
        
        overall = "可以恢复" if self.can_recover() else "不能恢复"
        lines.append("=" * 40)
        lines.append(f"总体: {overall}")
        
        blockers = self.get_recovery_blockers()
        if blockers:
            lines.append("\n阻碍:")
            for blocker in blockers:
                lines.append(f"  - {blocker}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    checker = RecoveryChecker(cooldown_seconds=5)
    print(checker.format_status())
    print()
    print(f"可以恢复: {checker.can_recover()}")
