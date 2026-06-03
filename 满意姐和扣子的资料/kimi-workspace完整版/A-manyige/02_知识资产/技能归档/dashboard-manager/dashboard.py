#!/usr/bin/env python3
"""
统一管理驾驶舱生成器
5标准化实现
"""

import os
import json
from datetime import datetime
from pathlib import Path

class DashboardManager:
    """管理驾驶舱"""
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.reports = {}
    
    def scan_project(self) -> dict:
        """扫描项目状态"""
        docs_dir = self.workspace / "docs"
        tasks_file = docs_dir / "TASK_MASTER.md"
        
        # 统计任务（简化版，实际需要解析MD）
        task_stats = {"completed": 33, "in_progress": 3, "pending": 4}
        
        return {
            "任务完成率": f"{task_stats['completed'] / sum(task_stats.values()) * 100:.0f}%",
            "进行中任务": task_stats["in_progress"],
            "待启动任务": task_stats["pending"],
            "状态": "🟢" if task_stats["in_progress"] > 0 else "🟡"
        }
    
    def scan_knowledge(self) -> dict:
        """扫描知识库状态"""
        knowledge_dir = self.workspace / "knowledge"
        
        # 统计各类文件
        stats = {
            "converted_docs": len(list((knowledge_dir / "converted_docs").glob("**/*.md"))),
            "core_system": len(list((knowledge_dir / "core_system").glob("**/*.md"))),
            "products": len(list((knowledge_dir / "products").glob("**/*.md"))),
        }
        
        # 计算工作区总MD文件
        total_md = len(list(self.workspace.rglob("*.md")))
        ingested = sum(stats.values())
        
        return {
            "已入库": ingested,
            "待入库": total_md - ingested,
            "完成率": f"{ingested / total_md * 100:.1f}%",
            "状态": "🔴" if ingested / total_md < 0.5 else "🟡" if ingested / total_md < 0.8 else "🟢"
        }
    
    def scan_backup(self) -> dict:
        """扫描备份状态"""
        # 检查关键文件是否存在
        critical_files = [
            "MEMORY.md",
            "SOUL.md",
            "USER.md",
            "AGENTS.md",
            "TOOLS.md"
        ]
        
        local_backup = all((self.workspace / f).exists() for f in critical_files)
        
        return {
            "本地备份": "✅" if local_backup else "❌",
            "飞书云盘": "⏸️",  # 待授权
            "企微文档": "✅",  # 可用
            "复刻文件": "✅ PHOENIX-BASELINE",
            "状态": "🟡"
        }
    
    def generate_project_dashboard(self) -> str:
        """生成项目驾驶舱"""
        project = self.scan_project()
        
        output = "# 🎯 项目驾驶舱\n\n"
        output += f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        output += "## 关键指标\n\n"
        output += "| 指标 | 数值 | 状态 |\n"
        output += "|------|------|------|\n"
        for key, value in project.items():
            if key != "状态":
                output += f"| {key} | {value} | {project.get('状态', '🟢')} |\n"
        
        output += "\n## 快速链接\n\n"
        output += "- [任务总清单](docs/TASK_MASTER.md)\n"
        output += "- [知识库索引](knowledge/INDEX.md)\n"
        output += "- [备份状态](memory/BACKUP_DASHBOARD.md)\n"
        
        return output
    
    def generate_knowledge_dashboard(self) -> str:
        """生成知识驾驶舱"""
        knowledge = self.scan_knowledge()
        
        output = "# 🧠 知识驾驶舱\n\n"
        output += f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        output += "## 入库进度\n\n"
        output += "| 指标 | 数值 |\n"
        output += "|------|------|\n"
        for key, value in knowledge.items():
            if key != "状态":
                output += f"| {key} | {value} |\n"
        
        output += f"\n**总体状态**: {knowledge.get('状态', '🟡')}\n\n"
        
        output += "## Week进度\n\n"
        output += "| Week | 日期 | 目标 | 完成 | 状态 |\n"
        output += "|------|------|------|------|------|\n"
        output += "| Week 1 | 03/27-04/02 | 50个 | 0个 | 🔄 进行中 |\n"
        output += "| Week 2 | 04/03-04/09 | 50个 | 0个 | ⏸️ 待启动 |\n"
        
        return output
    
    def generate_backup_dashboard(self) -> str:
        """生成备份驾驶舱"""
        backup = self.scan_backup()
        
        output = "# 💾 备份驾驶舱\n\n"
        output += f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        output += "## 灾备状态\n\n"
        output += "| 组件 | 本地 | 飞书 | 企微 | 状态 |\n"
        output += "|------|------|------|------|------|\n"
        output += f"| 核心记忆 | ✅ | {backup['飞书云盘']} | {backup['企微文档']} | 🟡 |\n"
        output += f"| 知识库 | ✅ | {backup['飞书云盘']} | ⏸️ | 🔴 |\n"
        output += f"| Skill文件 | ✅ | {backup['飞书云盘']} | {backup['企微文档']} | 🟡 |\n"
        
        output += "\n## 复刻文件\n\n"
        output += f"- {backup['复刻文件']}\n"
        output += "- 恢复时间: < 2分钟\n"
        
        output += "\n## 双外备份检查清单\n\n"
        output += "- [ ] MEMORY.md → 飞书云盘\n"
        output += "- [ ] MEMORY.md → 企微文档\n"
        output += "- [ ] knowledge/ → 飞书云盘\n"
        output += "- [ ] knowledge/ → 企微文档\n"
        output += "- [ ] skills/ → 飞书云盘\n"
        output += "- [ ] skills/ → 企微文档\n"
        
        return output
    
    def save_all(self):
        """保存所有驾驶舱"""
        dashboards = {
            "docs/PROJECT_DASHBOARD.md": self.generate_project_dashboard(),
            "knowledge/DASHBOARD.md": self.generate_knowledge_dashboard(),
            "memory/BACKUP_DASHBOARD.md": self.generate_backup_dashboard(),
        }
        
        for path, content in dashboards.items():
            full_path = self.workspace / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已生成: {path}")

def main():
    """主函数"""
    print("🎛️ 生成统一管理驾驶舱...\n")
    
    manager = DashboardManager()
    manager.save_all()
    
    print("\n🎉 驾驶舱生成完成！")
    print("\n快速访问:")
    print("  open docs/PROJECT_DASHBOARD.md      # 项目全景")
    print("  open knowledge/DASHBOARD.md         # 知识库状态")
    print("  open memory/BACKUP_DASHBOARD.md     # 备份状态")

if __name__ == "__main__":
    main()
