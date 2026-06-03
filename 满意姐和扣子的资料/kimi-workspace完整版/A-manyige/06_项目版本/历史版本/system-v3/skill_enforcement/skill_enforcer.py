#!/usr/bin/env python3
"""
全局Skill强制执行系统 - 终极解决方案
满意妞直接执行 - 2026-03-31

核心原则：所有任务必须通过Skill框架执行
绕过Skill = 物理上不可能
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 全局配置
WORKSPACE = Path("/root/.openclaw/workspace")
SKILL_REGISTRY = WORKSPACE / "system-v3/skill_enforcement/skill_registry.json"
EXECUTION_LOG = WORKSPACE / "logs/skill_enforcement/execution.log"
VIOLATION_LOG = WORKSPACE / "logs/skill_enforcement/violations.log"
BLOCKED_LOG = WORKSPACE / "logs/skill_enforcement/blocked.log"

# 强制Skill清单 - 所有任务必须通过对应的Skill
MANDATORY_SKILLS = {
    # 知识管理类
    "knowledge_ingest": {
        "patterns": ["ingest", "knowledge.*import", "文件入库"],
        "skill_name": "super-knowledge-ingest",
        "mandatory": True
    },
    "doc_fetch": {
        "patterns": ["fetch.*doc", "获取文档", "读取文档"],
        "skill_name": "feishu-fetch-doc",
        "mandatory": True
    },
    "doc_create": {
        "patterns": ["create.*doc", "创建文档", "新建文档"],
        "skill_name": "feishu-create-doc",
        "mandatory": True
    },
    "doc_update": {
        "patterns": ["update.*doc", "更新文档", "修改文档"],
        "skill_name": "feishu-update-doc",
        "mandatory": True
    },
    
    # 日历类
    "calendar_event": {
        "patterns": ["calendar.*event", "日程", "会议", "create.*meeting"],
        "skill_name": "feishu-calendar-event",
        "mandatory": True
    },
    "calendar_freebusy": {
        "patterns": ["freebusy", "忙闲", "空闲时间"],
        "skill_name": "feishu-calendar-freebusy",
        "mandatory": True
    },
    
    # 任务类
    "task_create": {
        "patterns": ["create.*task", "创建任务", "新建待办"],
        "skill_name": "feishu-task-task",
        "mandatory": True
    },
    "tasklist_manage": {
        "patterns": ["tasklist", "任务清单", "清单管理"],
        "skill_name": "feishu-task-tasklist",
        "mandatory": True
    },
    
    # IM消息类
    "im_send": {
        "patterns": ["send.*message", "发送消息", "发消息"],
        "skill_name": "feishu-im-user-message",
        "mandatory": True
    },
    "im_search": {
        "patterns": ["search.*message", "搜索消息", "查找消息"],
        "skill_name": "feishu-im-user-search-messages",
        "mandatory": True
    },
    
    # 文档表格类
    "sheet_read": {
        "patterns": ["read.*sheet", "读取表格", "电子表格"],
        "skill_name": "feishu-sheet",
        "mandatory": True
    },
    "bitable_record": {
        "patterns": ["bitable", "多维表格", "记录操作"],
        "skill_name": "feishu-bitable-app-table-record",
        "mandatory": True
    },
    
    # 知识库类
    "wiki_manage": {
        "patterns": ["wiki", "知识库", "空间节点"],
        "skill_name": "feishu-wiki-space-node",
        "mandatory": True
    },
    
    # 搜索类
    "doc_search": {
        "patterns": ["search.*doc", "搜索文档", "查找文档"],
        "skill_name": "feishu-search-doc-wiki",
        "mandatory": True
    },
    
    # 用户类
    "user_search": {
        "patterns": ["search.*user", "搜索用户", "查找员工"],
        "skill_name": "feishu-search-user",
        "mandatory": True
    },
    
    # 文件类
    "drive_upload": {
        "patterns": ["upload", "上传文件", "云盘上传"],
        "skill_name": "feishu-drive-self-upload",
        "mandatory": True
    },
    "drive_download": {
        "patterns": ["download", "下载文件", "云盘下载"],
        "skill_name": "feishu-drive-file",
        "mandatory": True
    },
    
    # 内部系统类
    "blue_army": {
        "patterns": ["blue.*army", "蓝军", "审计"],
        "skill_name": "blue-auditor",
        "mandatory": True
    },
    "baseline_check": {
        "patterns": ["baseline", "基线检查", "启动检查"],
        "skill_name": "baseline-checker",
        "mandatory": True
    },
    "meta_cognitive": {
        "patterns": ["meta.*cognitive", "元认知", "认知进化"],
        "skill_name": "meta-cognitive-evolver",
        "mandatory": True
    },
    "scenario_plan": {
        "patterns": ["scenario", "场景规划", "沙盘"],
        "skill_name": "scenario-planner",
        "mandatory": True
    },
    "what_if": {
        "patterns": ["what.*if", "假设分析", "推演"],
        "skill_name": "what-if-engine",
        "mandatory": True
    }
}

class SkillEnforcer:
    """Skill强制执行器"""
    
    def __init__(self):
        self.execution_count = 0
        self.violation_count = 0
        self.blocked_count = 0
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        for log_dir in [EXECUTION_LOG.parent, VIOLATION_LOG.parent, BLOCKED_LOG.parent]:
            log_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(EXECUTION_LOG, "a") as f:
            f.write(log_entry + "\n")
    
    def log_violation(self, violation_type, details, cmd=None):
        """记录违规"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        violation = {
            "timestamp": timestamp,
            "type": violation_type,
            "details": details,
            "command": cmd,
            "enforcement_action": "BLOCKED"
        }
        
        with open(VIOLATION_LOG, "a") as f:
            f.write(json.dumps(violation) + "\n")
        
        self.violation_count += 1
        self.log(f"🚨 违规 #{self.violation_count}: {violation_type}", "ERROR")
        self.log(f"   详情: {details}", "ERROR")
        
        # 同时记录到阻断日志
        with open(BLOCKED_LOG, "a") as f:
            f.write(f"[{timestamp}] BLOCKED: {violation_type}\n")
            f.write(f"  Command: {cmd}\n")
            f.write(f"  Details: {details}\n\n")
    
    def detect_task_type(self, cmd):
        """检测任务类型"""
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        cmd_lower = cmd_str.lower()
        
        detected_skills = []
        
        for task_id, config in MANDATORY_SKILLS.items():
            for pattern in config["patterns"]:
                if pattern.lower() in cmd_lower:
                    detected_skills.append({
                        "task_id": task_id,
                        "skill_name": config["skill_name"],
                        "mandatory": config["mandatory"]
                    })
                    break
        
        return detected_skills
    
    def is_skill_invocation(self, cmd):
        """检测是否通过Skill调用"""
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        
        skill_indicators = [
            "openclaw skill run",
            "skills/",
            "skill.py",
            "--validate",
            "--test",
            "run.py"
        ]
        
        for indicator in skill_indicators:
            if indicator in cmd_str:
                return True
        
        return False
    
    def enforce(self, cmd, context=None):
        """
        强制执行Skill框架
        
        返回:
            (success: bool, skill_name: str, message: str)
        """
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        self.execution_count += 1
        
        self.log(f"[{self.execution_count}] 检查任务: {cmd_str[:80]}...")
        
        # 1. 检测任务类型
        detected_skills = self.detect_task_type(cmd)
        
        if not detected_skills:
            # 未识别为强制Skill任务，允许执行但记录
            self.log("  ℹ️  未识别为强制Skill任务，允许执行")
            return (True, None, "未强制要求Skill")
        
        # 2. 检查是否通过Skill调用
        if self.is_skill_invocation(cmd):
            self.log(f"  ✅ 通过Skill框架调用: {detected_skills[0]['skill_name']}")
            return (True, detected_skills[0]['skill_name'], "Skill调用合规")
        
        # 3. 违规！必须使用Skill但未使用
        skill_info = detected_skills[0]
        violation_msg = (
            f"任务类型 '{skill_info['task_id']}' 必须通过Skill '{skill_info['skill_name']}' 执行，"
            f"但实际使用直接命令执行"
        )
        
        self.log_violation(
            "MANDATORY_SKILL_BYPASS",
            violation_msg,
            cmd_str
        )
        
        self.blocked_count += 1
        
        # 4. 返回阻断信息
        error_msg = f"""
🚨 **执行被阻断 - 必须使用Skill框架**

任务类型: {skill_info['task_id']}
强制Skill: {skill_info['skill_name']}

❌ 您的命令: {cmd_str[:100]}

✅ 正确用法:
    openclaw skill run {skill_info['skill_name']} [参数]

或:
    python3 skills/{skill_info['skill_name']}/run.py [参数]

⚠️  直接执行脚本已被禁止。所有任务必须通过对应的Skill框架执行。

📊 这是第 {self.blocked_count} 次Skill绕过被阻断。
"""
        
        self.log("  ❌ 执行被阻断 - 必须使用Skill框架", "ERROR")
        
        return (False, skill_info['skill_name'], error_msg)
    
    def get_stats(self):
        """获取统计信息"""
        return {
            "execution_count": self.execution_count,
            "violation_count": self.violation_count,
            "blocked_count": self.blocked_count,
            "compliance_rate": (
                (self.execution_count - self.violation_count) / self.execution_count * 100
                if self.execution_count > 0 else 100
            )
        }

def main():
    """主函数 - 作为命令行工具使用"""
    if len(sys.argv) < 2:
        print("用法: python3 skill_enforcer.py '<command>'")
        print("示例: python3 skill_enforcer.py 'python3 my_script.py'")
        sys.exit(1)
    
    cmd = sys.argv[1:]
    enforcer = SkillEnforcer()
    
    success, skill_name, message = enforcer.enforce(cmd)
    
    if not success:
        print(message)
        sys.exit(1)
    else:
        print(f"✅ 检查通过: {message}")
        sys.exit(0)

if __name__ == "__main__":
    main()
