#!/usr/bin/env python3
"""
生成恢复摘要 - 零Token上下文恢复
"""

import json
import os
import sys
from datetime import datetime

def generate_summary():
    workspace = "/root/.openclaw/workspace"
    memory_dir = f"{workspace}/memory"
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "session_id": os.environ.get("CLAW_SESSION_ID", "main"),
        "active_context": {},
        "recent_files": [],
        "pending_tasks": [],
        "last_memory": None,
        "checkpoints_available": 0
    }
    
    # 读取今日记忆文件
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = f"{memory_dir}/{today}.md"
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取最近的活动（最近500字符）
                if "##" in content:
                    sections = content.split("##")
                    if len(sections) > 1:
                        last_section = "##" + sections[-1][:800]
                        summary["last_memory"] = last_section.strip()
        except Exception as e:
            summary["last_memory"] = f"读取记忆文件出错: {e}"
    
    # 列出最近修改的文件
    try:
        import subprocess
        result = subprocess.run(
            ["find", workspace, "-type", "f", "-mmin", "-60", "-not", "-path", "*/.*", "-not", "-path", "*/checkpoints/*"],
            capture_output=True, text=True, timeout=10
        )
        files = [f for f in result.stdout.strip().split("\n") if f.strip()]
        summary["recent_files"] = files[:15]
    except Exception:
        pass
    
    # 读取TASK_MASTER.md获取待办
    task_files = [
        f"{workspace}/docs/TASK_MASTER.md",
        f"{workspace}/TASK_MASTER.md",
        f"{workspace}/HEARTBEAT.md"
    ]
    for task_file in task_files:
        if os.path.exists(task_file):
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取In Progress或TODO部分
                    for marker in ["### In Progress", "## In Progress", "### TODO", "## 进行中"]:
                        if marker in content:
                            section = content.split(marker)[1].split("###")[0].split("##")[0]
                            tasks = [
                                line.strip().lstrip("- *•").strip()
                                for line in section.split("\n")
                                if line.strip() and any(line.strip().startswith(p) for p in ["-", "*", "•", "[ ]", "[x]"])
                            ]
                            summary["pending_tasks"] = tasks[:8]
                            break
                    if summary["pending_tasks"]:
                        break
            except Exception:
                continue
    
    # 统计可用检查点
    checkpoint_dir = f"{os.path.expanduser('~')}/.openclaw/immortal-state/checkpoints"
    if os.path.exists(checkpoint_dir):
        try:
            checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith('.tar.gz')]
            summary["checkpoints_available"] = len(checkpoints)
        except Exception:
            pass
    
    # 保存摘要
    summary_path = f"{workspace}/.claw-resume-summary.json"
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"📝 恢复摘要已生成: {summary_path}")
        print(f"   最近文件: {len(summary['recent_files'])} 个")
        print(f"   待办任务: {len(summary['pending_tasks'])} 个")
        print(f"   可用检查点: {summary['checkpoints_available']} 个")
    except Exception as e:
        print(f"❌ 保存摘要失败: {e}")
        return None
    
    return summary

if __name__ == "__main__":
    summary = generate_summary()
    sys.exit(0 if summary else 1)
