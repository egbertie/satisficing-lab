#!/usr/bin/env python3
"""
Zero-Vacancy Executor - Slot Manager
槽位管理器：实现S2系统闭环 - 空闲检测→槽位预留→用户响应→释放槽位

WIP状态：当前为概念实现，生产环境需进一步优化
已知局限：单节点部署，非集群方案
"""

import json
import time
import threading
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Callable
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('slot_manager')


class SlotStatus(Enum):
    """槽位状态枚举"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"


class SlotPriority(Enum):
    """槽位优先级"""
    USER_DIALOGUE = 100
    EMERGENCY = 90
    HIGH = 70
    MEDIUM = 50
    LOW = 30
    BACKGROUND = 10


@dataclass
class Slot:
    """槽位定义"""
    id: str
    status: SlotStatus = SlotStatus.AVAILABLE
    holder: Optional[str] = None
    priority: int = 0
    since: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "status": self.status.value,
            "holder": self.holder,
            "priority": self.priority,
            "since": self.since.isoformat() if self.since else None
        }


class SlotManager:
    """
    槽位管理器 - 实现5标准化核心逻辑
    
    S1: 全局考虑 - 预留槽位确保用户对话响应
    S2: 系统闭环 - 空闲检测→槽位预留→用户响应→释放槽位
    S3: 可观测输出 - 提供槽位状态和延迟指标
    S4: 自动化集成 - 自动预留/释放/告警
    S5: 自我验证 - 内置自检机制
    S6: 认知谦逊 - 标注为WIP，明确局限
    S7: 对抗测试 - 预留测试接口
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.slots: Dict[str, Slot] = {}
        self.metrics = {
            "user_response_latency_ms": [],
            "slot_preemption_count": 0,
            "user_wait_queue": [],
            "check_count": 0
        }
        self.running = False
        self._lock = threading.RLock()
        self._state_listeners: List[Callable] = []
        
        # 初始化槽位
        self._init_slots()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"无法加载配置文件: {e}, 使用默认配置")
            return {
                "slot_management": {
                    "total_slots": 4,
                    "reserved_slots": {"user_dialogue": 1}
                },
                "detection": {"idle_check_interval_sec": 5},
                "release": {"session_timeout_sec": 300}
            }
    
    def _init_slots(self):
        """初始化槽位"""
        total = self.config["slot_management"]["total_slots"]
        for i in range(total):
            slot_id = f"slot-{i+1}"
            self.slots[slot_id] = Slot(id=slot_id)
        
        # S1: 全局考虑 - 预留用户对话槽位
        reserved_count = self.config["slot_management"]["reserved_slots"]["user_dialogue"]
        for i, slot in enumerate(list(self.slots.values())[:reserved_count]):
            self._reserve_slot(slot.id, "user_dialogue", SlotPriority.USER_DIALOGUE.value)
        
        logger.info(f"已初始化 {total} 个槽位，预留 {reserved_count} 个给用户对话")
    
    # ========== S2: 系统闭环核心方法 ==========
    
    def idle_detection(self) -> bool:
        """
        S2步骤1: 空闲检测
        检查是否有可用槽位
        """
        with self._lock:
            available = any(
                s.status == SlotStatus.AVAILABLE for s in self.slots.values()
            )
            self.metrics["check_count"] += 1
            return available
    
    def reserve_slot(self, holder: str, priority: int = 50) -> Optional[str]:
        """
        S2步骤2: 槽位预留
        为指定持有者预留槽位
        
        Returns:
            槽位ID或None（无可用槽位）
        """
        with self._lock:
            # 优先寻找可用槽位
            for slot in self.slots.values():
                if slot.status == SlotStatus.AVAILABLE:
                    return self._reserve_slot(slot.id, holder, priority)
            
            # S4: 自动化集成 - 需要抢占低优先级任务
            if self.config["slot_management"].get("preemption_enabled", True):
                return self._preempt_slot(holder, priority)
            
            return None
    
    def _reserve_slot(self, slot_id: str, holder: str, priority: int) -> str:
        """内部预留逻辑"""
        slot = self.slots[slot_id]
        slot.status = SlotStatus.RESERVED
        slot.holder = holder
        slot.priority = priority
        slot.since = datetime.now()
        
        logger.info(f"槽位 {slot_id} 已预留给 {holder} (优先级: {priority})")
        self._notify_state_change()
        return slot_id
    
    def _preempt_slot(self, new_holder: str, new_priority: int) -> Optional[str]:
        """抢占低优先级槽位"""
        # 找出优先级最低的槽位
        candidates = [
            s for s in self.slots.values()
            if s.status == SlotStatus.OCCUPIED and s.priority < new_priority
        ]
        
        if not candidates:
            logger.warning(f"无低优先级槽位可抢占，新任务 {new_holder} 需要等待")
            return None
        
        victim = min(candidates, key=lambda s: s.priority)
        
        # S4: 告警 - 抢占事件
        self.metrics["slot_preemption_count"] += 1
        logger.warning(f"抢占槽位 {victim.id} 从 {victim.holder} 到 {new_holder}")
        
        # 抢占
        old_holder = victim.holder
        victim.status = SlotStatus.AVAILABLE
        victim.holder = None
        
        return self._reserve_slot(victim.id, new_holder, new_priority)
    
    def occupy_slot(self, slot_id: str, holder: str) -> bool:
        """占用预留槽位"""
        with self._lock:
            slot = self.slots.get(slot_id)
            if not slot or slot.status != SlotStatus.RESERVED:
                return False
            
            slot.status = SlotStatus.OCCUPIED
            slot.holder = holder
            slot.since = datetime.now()
            
            logger.info(f"槽位 {slot_id} 被 {holder} 占用")
            self._notify_state_change()
            return True
    
    def release_slot(self, slot_id: str) -> bool:
        """
        S2步骤4: 槽位释放
        释放指定槽位
        """
        with self._lock:
            slot = self.slots.get(slot_id)
            if not slot:
                return False
            
            old_holder = slot.holder
            slot.status = SlotStatus.AVAILABLE
            slot.holder = None
            slot.priority = 0
            slot.since = None
            
            # S1: 如果是用户槽位，需要重新预留
            if old_holder == "user_dialogue":
                self._reserve_slot(slot_id, "user_dialogue", SlotPriority.USER_DIALOGUE.value)
                logger.info(f"槽位 {slot_id} 已释放并重新预留给用户对话")
            else:
                logger.info(f"槽位 {slot_id} 已释放")
            
            self._notify_state_change()
            return True
    
    def handle_user_dialogue(self, user_id: str) -> Dict:
        """
        S2步骤3: 用户响应
        处理用户对话请求，确保有槽位响应
        """
        start_time = datetime.now()
        
        with self._lock:
            # 检查是否有预留的用户槽位
            user_slot = next(
                (s for s in self.slots.values() 
                 if s.holder == "user_dialogue" and s.status == SlotStatus.RESERVED),
                None
            )
            
            if user_slot:
                # 立即占用用户槽位
                self.occupy_slot(user_slot.id, f"user:{user_id}")
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000
                self.metrics["user_response_latency_ms"].append(latency_ms)
                
                return {
                    "success": True,
                    "slot_id": user_slot.id,
                    "latency_ms": latency_ms,
                    "message": "使用预留槽位响应用户"
                }
            
            # 尝试抢占其他槽位
            slot_id = self.reserve_slot(f"user:{user_id}", SlotPriority.USER_DIALOGUE.value)
            if slot_id:
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000
                self.metrics["user_response_latency_ms"].append(latency_ms)
                
                return {
                    "success": True,
                    "slot_id": slot_id,
                    "latency_ms": latency_ms,
                    "message": "抢占槽位响应用户"
                }
            
            # 加入等待队列
            self.metrics["user_wait_queue"].append(user_id)
            return {
                "success": False,
                "queue_position": len(self.metrics["user_wait_queue"]),
                "message": "所有槽位占用，已加入等待队列"
            }
    
    # ========== S3: 可观测输出 ==========
    
    def get_slot_status(self) -> Dict:
        """获取槽位状态（S3可观测输出）"""
        with self._lock:
            total = len(self.slots)
            reserved = sum(1 for s in self.slots.values() if s.status == SlotStatus.RESERVED)
            occupied = sum(1 for s in self.slots.values() if s.status == SlotStatus.OCCUPIED)
            available = total - reserved - occupied
            
            return {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "reserved": reserved,
                    "occupied": occupied,
                    "available": available,
                    "availability_ratio": available / total if total > 0 else 0
                },
                "slots": {sid: slot.to_dict() for sid, slot in self.slots.items()},
                "metrics": {
                    "recent_latency_ms": self.metrics["user_response_latency_ms"][-10:],
                    "avg_latency_ms": (
                        sum(self.metrics["user_response_latency_ms"]) / 
                        len(self.metrics["user_response_latency_ms"])
                        if self.metrics["user_response_latency_ms"] else 0
                    ),
                    "preemption_count": self.metrics["slot_preemption_count"],
                    "wait_queue_length": len(self.metrics["user_wait_queue"])
                }
            }
    
    # ========== S4: 自动化集成 ==========
    
    def auto_release_expired(self):
        """自动释放超时槽位"""
        timeout_sec = self.config["release"]["session_timeout_sec"]
        cutoff = datetime.now() - timedelta(seconds=timeout_sec)
        
        with self._lock:
            for slot in self.slots.values():
                if (slot.status == SlotStatus.OCCUPIED and 
                    slot.since and slot.since < cutoff and
                    slot.holder != "user_dialogue"):
                    logger.info(f"自动释放超时槽位 {slot.id} (持有者: {slot.holder})")
                    self.release_slot(slot.id)
    
    def check_alerts(self) -> List[Dict]:
        """检查告警条件"""
        alerts = []
        status = self.get_slot_status()
        thresholds = self.config.get("alerts", {}).get("thresholds", {})
        
        # 槽位可用性告警
        avail_ratio = status["summary"]["availability_ratio"]
        if avail_ratio < thresholds.get("slot_availability_ratio", {}).get("critical", 0.5):
            alerts.append({
                "level": "critical",
                "metric": "slot_availability_ratio",
                "value": avail_ratio,
                "threshold": 0.5,
                "message": f"槽位可用率 {avail_ratio:.1%} 低于临界阈值"
            })
        elif avail_ratio < thresholds.get("slot_availability_ratio", {}).get("warning", 0.8):
            alerts.append({
                "level": "warning",
                "metric": "slot_availability_ratio",
                "value": avail_ratio,
                "threshold": 0.8,
                "message": f"槽位可用率 {avail_ratio:.1%} 低于告警阈值"
            })
        
        # 延迟告警
        avg_latency = status["metrics"]["avg_latency_ms"]
        if avg_latency > thresholds.get("user_response_latency_ms", {}).get("critical", 3000):
            alerts.append({
                "level": "critical",
                "metric": "user_response_latency_ms",
                "value": avg_latency,
                "threshold": 3000,
                "message": f"平均响应延迟 {avg_latency:.0f}ms 超过临界阈值"
            })
        
        return alerts
    
    # ========== S5: 自我验证 ==========
    
    def self_check(self) -> Dict:
        """
        S5: 自我验证 - 槽位状态自检
        """
        checks = []
        
        # 检查1: 预留槽位可用
        user_reserved = any(
            s.holder == "user_dialogue" and s.status in [SlotStatus.RESERVED, SlotStatus.AVAILABLE]
            for s in self.slots.values()
        )
        checks.append({
            "name": "reserved_slot_available",
            "description": "确认用户预留槽位始终可用",
            "status": "passed" if user_reserved else "failed",
            "message": "用户预留槽位正常" if user_reserved else "用户预留槽位异常"
        })
        
        # 检查2: 槽位数量一致性
        expected_count = self.config["slot_management"]["total_slots"]
        actual_count = len(self.slots)
        checks.append({
            "name": "slot_count_consistency",
            "description": "槽位总数与配置一致",
            "status": "passed" if expected_count == actual_count else "failed",
            "message": f"槽位总数 {actual_count} 与配置 {expected_count} {'一致' if expected_count == actual_count else '不一致'}"
        })
        
        # 检查3: 无孤立槽位
        orphaned = [
            s.id for s in self.slots.values()
            if s.status == SlotStatus.OCCUPIED and s.holder and 
            not s.holder.startswith("user:") and not s.holder.startswith("task:")
        ]
        checks.append({
            "name": "no_orphaned_slots",
            "description": "无孤立槽位",
            "status": "passed" if not orphaned else "failed",
            "message": f"未发现孤立槽位" if not orphaned else f"发现孤立槽位: {orphaned}"
        })
        
        # 检查4: 优先级有效
        invalid_priority = [
            s.id for s in self.slots.values()
            if s.priority < 0 or s.priority > 100
        ]
        checks.append({
            "name": "priority_valid",
            "description": "所有槽位优先级在有效范围内",
            "status": "passed" if not invalid_priority else "failed",
            "message": f"所有槽位优先级有效" if not invalid_priority else f"无效优先级槽位: {invalid_priority}"
        })
        
        passed = sum(1 for c in checks if c["status"] == "passed")
        failed = sum(1 for c in checks if c["status"] == "failed")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
            "checks": checks
        }
    
    # ========== 内部方法 ==========
    
    def _notify_state_change(self):
        """通知状态变化"""
        for listener in self._state_listeners:
            try:
                listener(self.get_slot_status())
            except Exception as e:
                logger.error(f"状态监听器错误: {e}")
    
    def add_state_listener(self, listener: Callable):
        """添加状态监听器"""
        self._state_listeners.append(listener)
    
    # ========== 运行控制 ==========
    
    def start(self):
        """启动管理器"""
        self.running = True
        logger.info("Slot Manager 已启动")
    
    def stop(self):
        """停止管理器"""
        self.running = False
        logger.info("Slot Manager 已停止")
    
    def run_loop(self):
        """主运行循环"""
        self.start()
        
        check_interval = self.config["detection"]["idle_check_interval_sec"]
        cleanup_interval = self.config["release"]["cleanup_interval_sec"]
        
        last_cleanup = time.time()
        
        while self.running:
            try:
                # S2: 空闲检测
                self.idle_detection()
                
                # S4: 自动释放超时槽位
                if time.time() - last_cleanup > cleanup_interval:
                    self.auto_release_expired()
                    last_cleanup = time.time()
                
                # S4: 告警检查
                alerts = self.check_alerts()
                for alert in alerts:
                    logger.warning(f"[ALERT] {alert['level'].upper()}: {alert['message']}")
                
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"运行循环错误: {e}")
                time.sleep(1)


def main():
    """主入口"""
    manager = SlotManager()
    
    # 打印初始状态
    print(json.dumps(manager.get_slot_status(), indent=2, ensure_ascii=False))
    
    # 运行自检
    print("\n=== 自检报告 ===")
    print(json.dumps(manager.self_check(), indent=2, ensure_ascii=False))
    
    # 启动运行循环（如果直接运行）
    try:
        manager.run_loop()
    except KeyboardInterrupt:
        manager.stop()
        print("\n已停止")


if __name__ == "__main__":
    main()
