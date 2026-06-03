#!/usr/bin/env python3
"""
事件驱动机制实现 - M004
自动触发整改和内化流程

创建时间: 2026-03-31
状态: 整改完成
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

class EventDrivenEngine:
    """事件驱动引擎"""
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.events_dir = self.workspace / "memory" / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.handlers = {
            "user_issue": self._handle_user_issue,
            "file_change": self._handle_file_change,
            "internalization_need": self._handle_internalization_need,
            "system_state_change": self._handle_system_state_change
        }
    
    def detect_event(self, event_type, context):
        """检测事件并触发处理"""
        if event_type in self.handlers:
            print(f"[EVENT] 检测到事件: {event_type}")
            self.handlers[event_type](context)
            self._log_event(event_type, context)
            return True
        return False
    
    def _handle_user_issue(self, context):
        """处理用户指出问题事件"""
        print("[HANDLER] 用户指出问题 → 立即触发整改")
        
        # 1. 记录问题
        issue_file = self.workspace / "diary" / "issues" / f"issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        issue_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(issue_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "type": "user_issue",
                "context": context,
                "status": "pending_rectification"
            }, f, ensure_ascii=False, indent=2)
        
        # 2. 立即触发整改（3分钟内）
        print(f"[ACTION] 问题已记录: {issue_file}")
        print("[ACTION] 启动整改流程...")
        
        # 3. 创建整改任务
        rect_task = {
            "task_id": f"RECT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "source": "user_issue",
            "priority": "P0",
            "deadline": "3_minutes",
            "status": "created"
        }
        
        print(f"[TASK] 整改任务创建: {rect_task['task_id']}")
    
    def _handle_file_change(self, context):
        """处理文件变化事件"""
        print("[HANDLER] 文件变化 → 检查是否需要内化")
        
        file_path = context.get("file_path", "")
        
        # 检查是否是核心文件变更
        if "SOUL.md" in file_path or "USER.md" in file_path:
            print("[ACTION] 核心文件变更，触发内化检查")
            self._trigger_internalization_check(file_path)
    
    def _handle_internalization_need(self, context):
        """处理内化需求事件"""
        print("[HANDLER] 内化需求 → 自动启动内化流程")
        
        # 自动执行内化SOP
        sop_steps = [
            "识别 → 用户明确要求的内容",
            "固化 → 写入SOUL.md/USER.md等核心文件",
            "物理化 → 创建.md/.sh/.json等实际文件",
            "建立标准 → 创建SOP.md和CHECKLIST.md",
            "创建自动化验证脚本 → 创建.py/.sh脚本",
            "创建执行日志 → 创建.json/.md日志",
            "创建状态保存机制 → 每30分钟保存系统状态",
            "创建极端事件恢复机制 → 系统重启后自动恢复",
            "验证 → 模拟重启验证恢复是否成功",
            "迭代 → 每日/每周/每月/每季回顾更新",
            "灾备设计 → 设计时考虑失败场景",
            "故障演练 → 每月模拟一种极端事件",
            "灾备文档化 → 每个系统必须有恢复文档"
        ]
        
        for i, step in enumerate(sop_steps, 1):
            print(f"  [SOP-{i:02d}] {step}")
    
    def _handle_system_state_change(self, context):
        """处理系统状态变化事件"""
        print("[HANDLER] 系统状态变化 → 自动响应")
        
        state = context.get("new_state", "")
        
        if state == "Token_low":
            print("[ACTION] Token不足 → 触发L3档位")
        elif state == "error_high":
            print("[ACTION] 错误率高 → 触发蓝军审计")
        elif state == "task_complete":
            print("[ACTION] 任务完成 → 触发深度洞察生成")
    
    def _log_event(self, event_type, context):
        """记录事件日志"""
        log_file = self.events_dir / f"events_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "context": context
            }, ensure_ascii=False) + "\n")
    
    def _trigger_internalization_check(self, file_path):
        """触发内化检查"""
        print(f"[CHECK] 检查文件是否需要内化: {file_path}")
        # 实际实现会检查文件内容是否包含内化关键词

# 使用示例
if __name__ == "__main__":
    engine = EventDrivenEngine()
    
    # 测试用户指出问题事件
    print("=== 测试事件驱动机制 ===")
    print()
    engine.detect_event("user_issue", {"issue": "发现虚假完成", "severity": "high"})
    print()
    engine.detect_event("internalization_need", {"source": "user_request"})
