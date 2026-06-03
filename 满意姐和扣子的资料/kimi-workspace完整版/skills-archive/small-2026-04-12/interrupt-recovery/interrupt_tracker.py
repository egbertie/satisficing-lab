#!/usr/bin/env python3
"""
interrupt_tracker.py
中断状态追踪器 - 保存和恢复任务执行状态
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List, Any

STATE_FILE = os.path.join(os.path.dirname(__file__), 'state', 'interrupt_state.json')

class InterruptTracker:
    """追踪任务执行状态，支持中断恢复"""
    
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """加载状态文件"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ 状态文件损坏，创建新状态: {e}")
                return {"sessions": [], "version": "1.0"}
        return {"sessions": [], "version": "1.0"}
    
    def _save_state(self):
        """保存状态文件"""
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        try:
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"❌ 无法保存状态: {e}")
    
    def start_task(self, task_id: str, task_type: str, total_steps: int, 
                   context: Optional[Dict] = None) -> Dict:
        """开始新任务"""
        session = {
            "session_id": datetime.now().isoformat(),
            "start_time": datetime.now().isoformat(),
            "current_task": {
                "id": task_id,
                "type": task_type,
                "status": "running",
                "progress": 0.0,
                "current_step": 0,
                "total_steps": total_steps,
                "checkpoint": None,
                "context": context or {}
            },
            "interruptions": [],
            "recovery_history": []
        }
        self.state["sessions"].append(session)
        # 只保留最近20个会话，避免文件过大
        self.state["sessions"] = self.state["sessions"][-20:]
        self._save_state()
        return session
    
    def update_progress(self, step: int, checkpoint: str, 
                       extra_data: Optional[Dict] = None):
        """更新进度"""
        if not self.state["sessions"]:
            return
        
        current = self.state["sessions"][-1]
        task = current["current_task"]
        
        task["current_step"] = step
        task["checkpoint"] = checkpoint
        task["progress"] = step / task["total_steps"] if task["total_steps"] > 0 else 0
        
        if extra_data:
            task["context"].update(extra_data)
        
        self._save_state()
    
    def mark_interrupted(self, reason: str, error_details: Optional[str] = None):
        """标记中断"""
        if not self.state["sessions"]:
            return
        
        current = self.state["sessions"][-1]
        current["current_task"]["status"] = "interrupted"
        
        interruption = {
            "time": datetime.now().isoformat(),
            "reason": reason,
            "error_details": error_details,
            "recovery_attempts": 0,
            "next_retry": None
        }
        current["interruptions"].append(interruption)
        self._save_state()
    
    def mark_recovering(self) -> bool:
        """标记恢复中，返回是否应该继续"""
        if not self.state["sessions"]:
            return False
        
        current = self.state["sessions"][-1]
        current["current_task"]["status"] = "recovering"
        
        if current["interruptions"]:
            last = current["interruptions"][-1]
            last["recovery_attempts"] = last.get("recovery_attempts", 0) + 1
        
        self._save_state()
        return True
    
    def mark_completed(self, result: Optional[Dict] = None):
        """标记完成"""
        if not self.state["sessions"]:
            return
        
        current = self.state["sessions"][-1]
        current["current_task"]["status"] = "completed"
        current["current_task"]["progress"] = 1.0
        current["end_time"] = datetime.now().isoformat()
        
        if result:
            current["result"] = result
        
        self._save_state()
    
    def get_last_interrupted(self) -> Optional[Dict]:
        """获取最近的中断任务"""
        for session in reversed(self.state["sessions"]):
            status = session.get("current_task", {}).get("status")
            if status in ["interrupted", "recovering"]:
                return session
        return None
    
    def should_retry(self, max_retries: int = 4) -> bool:
        """检查是否应该重试"""
        interrupted = self.get_last_interrupted()
        if not interrupted:
            return False
        
        interruptions = interrupted.get("interruptions", [])
        if not interruptions:
            return False
        
        last = interruptions[-1]
        attempts = last.get("recovery_attempts", 0)
        return attempts < max_retries
    
    def get_recovery_info(self) -> Optional[Dict]:
        """获取恢复信息"""
        interrupted = self.get_last_interrupted()
        if not interrupted:
            return None
        
        task = interrupted["current_task"]
        interruptions = interrupted.get("interruptions", [])
        
        if not interruptions:
            return None
        
        last = interruptions[-1]
        
        return {
            "task_id": task["id"],
            "task_type": task["type"],
            "checkpoint": task["checkpoint"],
            "current_step": task["current_step"],
            "total_steps": task["total_steps"],
            "progress": task["progress"],
            "context": task.get("context", {}),
            "interruption_reason": last["reason"],
            "attempts": last.get("recovery_attempts", 0),
            "interrupted_at": last["time"]
        }
    
    def list_recent_sessions(self, limit: int = 5) -> List[Dict]:
        """列出最近的会话"""
        return self.state.get("sessions", [])[-limit:]


if __name__ == "__main__":
    # 简单测试
    tracker = InterruptTracker()
    
    # 测试开始任务
    session = tracker.start_task("test-001", "skill_creation", 5, 
                                  {"target": "interrupt-recovery"})
    print(f"✅ 任务开始: {session['current_task']['id']}")
    
    # 测试更新进度
    tracker.update_progress(2, "step_2_completed", {"files_created": 1})
    print(f"✅ 进度更新: step 2")
    
    # 测试中断
    tracker.mark_interrupted("api_rate_limit", "Too many requests")
    print(f"⚠️ 任务中断: api_rate_limit")
    
    # 测试恢复信息
    info = tracker.get_recovery_info()
    print(f"📊 恢复信息: {info}")
    
    # 测试是否应该重试
    should = tracker.should_retry()
    print(f"🔄 应该重试: {should}")
    
    # 标记完成（清理测试数据）
    tracker.mark_completed({"test": True})
    print(f"✅ 测试完成")
