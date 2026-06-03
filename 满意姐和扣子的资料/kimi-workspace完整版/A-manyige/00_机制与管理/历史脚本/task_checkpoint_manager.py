#!/usr/bin/env python3
"""
任务执行Checkpoint管理器
用途: 为所有任务提供断点续传能力
规则: 每个长时间任务必须集成此管理器
"""

import json
import os
from datetime import datetime
from pathlib import Path

class TaskCheckpointManager:
    """任务Checkpoint管理器"""
    
    def __init__(self, task_name):
        self.task_name = task_name
        self.checkpoint_dir = Path(f"/root/.openclaw/workspace/memory/checkpoints/{task_name}")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / "latest.json"
    
    def save_progress(self, step, data):
        """保存进度"""
        checkpoint = {
            "task_name": self.task_name,
            "step": step,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        # 同时保存历史版本
        history_file = self.checkpoint_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(history_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"✅ Checkpoint saved: {self.task_name} @ step {step}")
        return checkpoint
    
    def load_progress(self):
        """加载进度"""
        if not self.checkpoint_file.exists():
            return None
        
        with open(self.checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
        
        print(f"✅ Checkpoint loaded: {self.task_name} @ step {checkpoint['step']}")
        return checkpoint
    
    def resume_if_exists(self):
        """如果存在Checkpoint，返回断点位置"""
        checkpoint = self.load_progress()
        if checkpoint:
            return checkpoint["step"], checkpoint["data"]
        return None, None
    
    def clear(self):
        """清除Checkpoint（任务完成时）"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            print(f"✅ Checkpoint cleared: {self.task_name}")

# 使用示例
if __name__ == "__main__":
    # 示例: 长时间任务使用Checkpoint
    manager = TaskCheckpointManager("methodology_extraction")
    
    # 检查是否有断点
    step, data = manager.resume_if_exists()
    if step:
        print(f"Resuming from step {step}")
    else:
        print("Starting fresh")
        step = 0
    
    # 模拟长时间任务
    for i in range(step, 10):
        print(f"Processing step {i}...")
        # 处理...
        
        # 每步保存Checkpoint
        manager.save_progress(i, {"processed": i * 100})
    
    # 任务完成，清除Checkpoint
    manager.clear()
    print("Task completed!")
